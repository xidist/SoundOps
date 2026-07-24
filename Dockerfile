FROM python:3.12-slim

ARG APP_VERSION=0.1.0

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    SOUNDOPS_APP_VERSION=${APP_VERSION} \
    HF_HOME=/home/soundops/.cache/huggingface \
    HF_HUB_DISABLE_TELEMETRY=1

RUN apt-get update \
    && apt-get install --no-install-recommends -y ca-certificates ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 10001 soundops \
    && useradd --uid 10001 --gid soundops --create-home --shell /usr/sbin/nologin soundops

WORKDIR /app

COPY requirements-base.txt requirements.txt ./

# CPU-only PyTorch keeps the image smaller and works on Minikube without GPU setup.
RUN python -m pip install --upgrade pip \
    && python -m pip install --index-url https://download.pytorch.org/whl/cpu "torch>=2.6,<3.0" \
    && python -m pip install -r requirements.txt

COPY --chown=soundops:soundops app ./app

USER 10001:10001

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
