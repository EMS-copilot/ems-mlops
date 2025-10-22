import os
from fastapi import FastAPI, Request, status, HTTPException
from contextlib import asynccontextmanager

from predictor import CustomPredictor 
from schemas import InputSchema

MODEL_DIR = os.environ.get("AIP_MODEL_DIR", ".") 

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    애플리케이션 시작 시 한 번만 모델을 로드합니다.
    """
    try:
        #app.state.predictor = CustomPredictor(MODEL_DIR)
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
    return {"status": "ready"}

@app.post("/test_input", status_code=status.HTTP_200_OK)
def test_input(input_data: InputSchema):
    """
    입력 스키마의 유효성을 검사하기 위한 테스트 엔드포인트입니다.
    """
    return {"status": "success", "message": "Input data is valid."}

@app.post("/predict")
async def predict_endpoint(request: Request, request_data: InputSchema):
    predictor = request.app.state.predictor
    if predictor is None:
        raise HTTPException(status_code=503, detail="Service Unavailable: Model not loaded.")

    try:
        raw_instances = [item.model_dump() for item in request_data.instances]
        
        predictions = predictor.predict(raw_instances)
        
        return {"predictions": predictions}
        
    except Exception as e:
        print(f"Prediction execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")