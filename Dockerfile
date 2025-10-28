# ====================================================================
# STAGE 1: builder
# ====================================================================
FROM python:3.9 AS builder

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential gcc g++ cmake libhdf5-dev libblas-dev liblapack-dev curl && \
    rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

COPY pyproject.toml uv.lock ./
RUN uv sync --group container --frozen --no-dev

# ====================================================================
# STAGE 2: runtime
# ====================================================================
FROM python:3.9-slim AS runtime

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY src/. .

ENV PYTHONUNBUFFERED=1

ENV AIP_BUCKET_URI="gs://ems_dummy_1"
ENV AIP_MODEL_DIR="${AIP_BUCKET_URI}/model/model-8766129131327848448/tf-saved-model/2025-10-22T00:15:58.603467Z/predict/001"
ENV AIP_FEATURE_FILE="${AIP_BUCKET_URI}/data/features.json"
ENV AIP_META_FILE="${AIP_BUCKET_URI}/data/hospital_meta.csv"
ENV AIP_CONSTRAINT_FILE="${AIP_BUCKET_URI}/data/constraints.json"

CMD gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:${AIP_HTTP_PORT:-8080}
