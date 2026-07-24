from __future__ import annotations

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


class FakeClassifier:
    model_id = "fake/audio-model"
    error = None

    def __init__(self, ready: bool = True) -> None:
        self.ready = ready

    def load(self) -> None:
        return None

    def predict(self, audio_bytes: bytes, top_k: int):
        assert audio_bytes
        return [
            {"label": "Music", "score": 0.82},
            {"label": "Guitar", "score": 0.11},
        ][:top_k]


def test_health_and_readiness() -> None:
    app = create_app(classifier=FakeClassifier())
    with TestClient(app) as client:
        assert client.get("/healthz").json() == {"status": "ok"}
        ready = client.get("/readyz")
        assert ready.status_code == 200
        assert ready.json()["model"] == "fake/audio-model"


def test_not_ready_returns_503() -> None:
    app = create_app(classifier=FakeClassifier(ready=False))
    with TestClient(app) as client:
        response = client.get("/readyz")
        assert response.status_code == 503
        assert response.json()["status"] == "not-ready"


def test_predict_audio() -> None:
    app = create_app(classifier=FakeClassifier())
    with TestClient(app) as client:
        response = client.post(
            "/predict",
            files={"file": ("sample.wav", b"RIFFdemo", "audio/wav")},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["filename"] == "sample.wav"
    assert payload["predictions"][0]["label"] == "Music"
    assert payload["model"] == "fake/audio-model"


def test_rejects_non_audio_file() -> None:
    app = create_app(classifier=FakeClassifier())
    with TestClient(app) as client:
        response = client.post(
            "/predict",
            files={"file": ("notes.txt", b"not audio", "text/plain")},
        )

    assert response.status_code == 415


def test_rejects_oversized_upload() -> None:
    settings = Settings(max_upload_mb=1)
    app = create_app(settings=settings, classifier=FakeClassifier())
    with TestClient(app) as client:
        response = client.post(
            "/predict",
            files={
                "file": (
                    "large.wav",
                    b"x" * (settings.max_upload_bytes + 1),
                    "audio/wav",
                )
            },
        )

    assert response.status_code == 413
