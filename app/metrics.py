from prometheus_client import Counter, Gauge, Histogram, Info

PREDICTIONS = Counter(
    "soundops_predictions_total",
    "Total audio prediction requests.",
    ["status"],
)

INFERENCE_SECONDS = Histogram(
    "soundops_inference_seconds",
    "Time spent performing model inference.",
    buckets=(0.1, 0.25, 0.5, 1, 2, 5, 10, 20, 60),
)

UPLOAD_BYTES = Histogram(
    "soundops_upload_bytes",
    "Uploaded audio file sizes.",
    buckets=(1024, 10_000, 100_000, 1_000_000, 5_000_000, 15_000_000),
)

MODEL_READY = Gauge(
    "soundops_model_ready",
    "Whether the model is ready to serve predictions.",
)

BUILD_INFO = Info(
    "soundops_build",
    "SoundOps build and model metadata.",
)
