from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.config import Settings
from app.metrics import (
    BUILD_INFO,
    INFERENCE_SECONDS,
    MODEL_READY,
    PREDICTIONS,
    UPLOAD_BYTES,
)
from app.model import HuggingFaceAudioClassifier, ModelNotReadyError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

ALLOWED_CONTENT_TYPES = {
    "application/octet-stream",
    "audio/flac",
    "audio/m4a",
    "audio/mpeg",
    "audio/mp3",
    "audio/ogg",
    "audio/wav",
    "audio/wave",
    "audio/x-m4a",
    "audio/x-wav",
}


def create_app(
    settings: Settings | None = None,
    classifier: Any | None = None,
) -> FastAPI:
    settings = settings or Settings.from_env()
    classifier = classifier or HuggingFaceAudioClassifier(settings)
    load_task: asyncio.Task[None] | None = None

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        nonlocal load_task

        BUILD_INFO.info(
            {
                "version": settings.app_version,
                "model": settings.model_id,
            }
        )

        if settings.preload_model:
            async def load_model() -> None:
                try:
                    await asyncio.to_thread(classifier.load)
                except Exception:
                    # The classifier records the error for /readyz and logs the traceback.
                    MODEL_READY.set(0)

            load_task = asyncio.create_task(
                load_model(),
                name="soundops-model-loader",
            )

        yield

        if load_task and not load_task.done():
            load_task.cancel()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "A Kubernetes-ready audio classification API built with "
            "FastAPI and Hugging Face Transformers."
        ),
        lifespan=lifespan,
    )

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def index() -> HTMLResponse:
        ui_path = Path(__file__).with_name("ui.html")
        return HTMLResponse(ui_path.read_text(encoding="utf-8"))

    @app.get("/healthz", tags=["operations"])
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/readyz", tags=["operations"])
    async def readyz() -> Response:
        if classifier.ready:
            MODEL_READY.set(1)
            return JSONResponse(
                {
                    "status": "ready",
                    "model": classifier.model_id,
                }
            )

        MODEL_READY.set(0)
        detail = {
            "status": "not-ready",
            "model": classifier.model_id,
        }
        if getattr(classifier, "error", None):
            detail["error"] = classifier.error
        return JSONResponse(detail, status_code=503)

    @app.get("/metrics", include_in_schema=False)
    async def metrics() -> Response:
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST,
        )

    @app.post("/predict", tags=["inference"])
    async def predict(
    file: Annotated[
        UploadFile,
        File(
            description="Audio file such as WAV, MP3, FLAC, M4A, or OGG.",
        ),
    ],
) -> dict[str, Any]:
        content_type = (file.content_type or "").lower()
        if content_type and (
            content_type not in ALLOWED_CONTENT_TYPES
            and not content_type.startswith("audio/")
        ):
            raise HTTPException(
                status_code=415,
                detail=f"Unsupported media type: {content_type}",
            )

        audio_bytes = await file.read(settings.max_upload_bytes + 1)
        await file.close()

        if not audio_bytes:
            raise HTTPException(status_code=400, detail="The uploaded file is empty.")

        if len(audio_bytes) > settings.max_upload_bytes:
            raise HTTPException(
                status_code=413,
                detail=(
                    f"File exceeds the {settings.max_upload_mb} MB upload limit."
                ),
            )

        UPLOAD_BYTES.observe(len(audio_bytes))

        if not classifier.ready:
            MODEL_READY.set(0)
            PREDICTIONS.labels(status="not_ready").inc()
            raise HTTPException(
                status_code=503,
                detail="The model is still loading. Retry after /readyz returns 200.",
            )

        started = time.perf_counter()
        try:
            results = await asyncio.to_thread(
                classifier.predict,
                audio_bytes,
                settings.top_k,
            )
        except ModelNotReadyError as exc:
            PREDICTIONS.labels(status="not_ready").inc()
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except Exception as exc:
            PREDICTIONS.labels(status="error").inc()
            logger.exception("Inference failed for file %s", file.filename)
            raise HTTPException(
                status_code=500,
                detail="Audio inference failed. Inspect the application logs.",
            ) from exc

        elapsed = time.perf_counter() - started
        INFERENCE_SECONDS.observe(elapsed)
        PREDICTIONS.labels(status="success").inc()

        return {
            "filename": file.filename,
            "content_type": content_type or None,
            "bytes": len(audio_bytes),
            "model": classifier.model_id,
            "inference_seconds": round(elapsed, 4),
            "predictions": results,
        }

    return app


app = create_app()
