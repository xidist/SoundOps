from __future__ import annotations

import os
from dataclasses import dataclass


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str = "SoundOps"
    app_version: str = "0.1.0"
    model_id: str = "MIT/ast-finetuned-audioset-10-10-0.4593"
    top_k: int = 5
    max_upload_mb: int = 15
    device: int = -1
    preload_model: bool = True

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            app_name=os.getenv("SOUNDOPS_APP_NAME", "SoundOps"),
            app_version=os.getenv("SOUNDOPS_APP_VERSION", "0.1.0"),
            model_id=os.getenv(
                "SOUNDOPS_MODEL_ID",
                "MIT/ast-finetuned-audioset-10-10-0.4593",
            ),
            top_k=int(os.getenv("SOUNDOPS_TOP_K", "5")),
            max_upload_mb=int(os.getenv("SOUNDOPS_MAX_UPLOAD_MB", "15")),
            device=int(os.getenv("SOUNDOPS_DEVICE", "-1")),
            preload_model=_env_bool("SOUNDOPS_PRELOAD_MODEL", True),
        )

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024
