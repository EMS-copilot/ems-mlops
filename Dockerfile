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

COPY app.py ./app.py
COPY codes/ ./codes/
COPY predictor.py ./predictor.py

ENV PYTHONUNBUFFERED=1
ENV PORT=8080

EXPOSE ${PORT}
CMD gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:${AIP_HTTP_PORT:-8080}
