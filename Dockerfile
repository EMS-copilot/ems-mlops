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
RUN uv sync --frozen --no-dev

# ====================================================================
# STAGE 2: runtime
# ====================================================================
FROM python:3.9-slim AS runtime

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY app.py ./app.py
COPY codes/ ./codes/
COPY local_model_assets ./local_model_assets/
COPY data/ ./data/ 

ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV AIP_MODEL_DIR="gs://ems_dummy_1/model/model-8766129131327848448/tf-saved-model/2025-10-22T00:15:58.603467Z/predict/001"
ENV AIP_META_DIR="gs://ems_dummy_1/data/hospital_meta.csv"
ENV LOCAL_MODEL_DIR="./local_model_assets/predict/001"
ENV LOCAL_META_DIR="./data/hospital_meta.csv"
ENV LOCAL_FEATURE_DIR="./data/features.json"
ENV LOCAL_INPUT_SCHEMA="data/input_api_schema.json"
ENV AIP_MODEL_DOWNLOAD_DIR="gs://ems_dummy_1/model/model-8766129131327848448/tf-saved-model/2025-10-22T00:15:58.603467Z"
ENV LOCAL_MODEL_DOWNLOAD_DIR="./local_model_assets"
ENV TEST_ENV="true"

EXPOSE ${PORT}
CMD gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:${AIP_HTTP_PORT:-8080}
