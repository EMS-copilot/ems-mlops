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
ENV PORT=8080

# Local Path
ENV LOCAL_META_PATH="data/hospital_meta.csv"
ENV LOCAL_FEATURE_PATH="data/features.json"
ENV LOCAL_INPUT_PATH="data/input_api_schema.json"
ENV LOCAL_CONSTRAINT_PATH="data/constraints.json"

ENV AIP_BUCKET_URI="gs://ems_dummy_1"
ENV AIP_MODEL_DIR="${AIP_BUCKET_URI}/model/model-8766129131327848448/tf-saved-model/2025-10-22T00:15:58.603467Z/predict/001"
ENV AIP_FEATURE_PATH="${AIP_BUCKET_URI}/${LOCAL_FEATURE_PATH}"
ENV AIP_META_PATH="${AIP_BUCKET_URI}/${LOCAL_META_PATH}"
ENV AIP_CONSTRAINT_PATH="${AIP_BUCKET_URI}/${LOCAL_CONSTRAINT_PATH}"

EXPOSE ${PORT}
CMD gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:${AIP_HTTP_PORT:-8080}
