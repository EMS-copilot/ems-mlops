import os
from fastapi import FastAPI, Request, status, HTTPException
from pydantic import BaseModel
from typing import List, Any, Dict
from contextlib import asynccontextmanager

from predictor import CustomPredictor 

MODEL_DIR = os.environ.get("AIP_MODEL_DIR", ".") 

# ----------------------------------------------------
# 1. Pydantic을 이용한 요청 데이터 구조 정의
# ----------------------------------------------------

# class InstanceItem(BaseModel):
#     feature_A: float
#     feature_B: float

# class PredictRequest(BaseModel):
#     instances: List[InstanceItem]

# ----------------------------------------------------
# 2. FastAPI 애플리케이션 초기화
# ----------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    애플리케이션 시작 시 한 번만 모델을 로드합니다.
    """
    try:
        app.state.predictor = CustomPredictor(MODEL_DIR)
        print("FastAPI: Predictor initialized successfully.")
    except Exception as e:
        print(f"FastAPI: Error initializing predictor: {e}")
        raise RuntimeError("Model loading failed.")
    yield

app = FastAPI(
    title="Custom TF Predictor with FastAPI",
    version="1.0",
    lifespan=lifespan
)

@app.get("/ping", status_code=status.HTTP_200_OK)
def ping():
    """
    Vertex AI 헬스 체크 엔드포인트
    """
    return {"status": "ready"}

@app.post("/predict")
async def predict_endpoint(request: Request, request_data: PredictRequest):
    """
    추론 엔드포인트
    Pydantic이 자동으로 유효성 검사를 수행합니다.
    """
    predictor = request.app.state.predictor
    if predictor is None:
        raise HTTPException(status_code=503, detail="Service Unavailable: Model not loaded.")

    try:
        raw_instances = [item.dict() for item in request_data.instances]
        
        predictions = predictor.predict(raw_instances)
        
        return {"predictions": predictions}
        
    except Exception as e:
        print(f"Prediction execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")