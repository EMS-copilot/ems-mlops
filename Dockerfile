FROM python:3.9-slim AS base

WORKDIR /app

# uv 설치
RUN pip install --no-cache-dir uv

# pyproject.toml, uv.lock 먼저 복사 → 의존성 설치
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# 소스코드 복사 (원하는 것만)
COPY app.py ./app.py
COPY codes/ ./codes/

# 실행 커맨드 (app.py 안에 FastAPI app이 있다고 가정)
CMD ["uv", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
