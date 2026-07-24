from __future__ import annotations

import logging
import threading
from typing import Any

from app.config import Settings

logger = logging.getLogger(__name__)


class ModelNotReadyError(RuntimeError):
    """Raised when inference is requested before the model is ready."""


class HuggingFaceAudioClassifier:
    """Thread-safe, lazily loaded Hugging Face audio classifier."""

    def __init__(self, settings: Settings) -> None:
        self.model_id = settings.model_id
        self.device = settings.device
        self._pipeline: Any | None = None
        self._ready = threading.Event()
        self._load_lock = threading.Lock()
        self.error: str | None = None

    @property
    def ready(self) -> bool:
        return self._ready.is_set() and self._pipeline is not None

    def load(self) -> None:
        if self.ready:
            return

        with self._load_lock:
            if self.ready:
                return

            logger.info("Loading Hugging Face model: %s", self.model_id)
            try:
                # Imported here so unit tests do not need PyTorch or Transformers.
                from transformers import pipeline

                self._pipeline = pipeline(
                    task="audio-classification",
                    model=self.model_id,
                    device=self.device,
                )
                self.error = None
                self._ready.set()
                logger.info("Model is ready: %s", self.model_id)
            except Exception as exc:
                self.error = f"{type(exc).__name__}: {exc}"
                logger.exception("Model loading failed")
                raise

    def predict(self, audio_bytes: bytes, top_k: int) -> list[dict[str, Any]]:
        if not self.ready:
            raise ModelNotReadyError("The audio model is still loading.")

        assert self._pipeline is not None
        raw_results = self._pipeline(audio_bytes, top_k=top_k)
        return [
            {
                "label": str(item["label"]),
                "score": round(float(item["score"]), 6),
            }
            for item in raw_results
        ]
