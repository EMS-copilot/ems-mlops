import os
import logging
from fastapi import FastAPI, Request, status, HTTPException
from contextlib import asynccontextmanager

from predictor import CustomPredictor 
from codes.schemas import PredictionRequestSchema
from codes import setup_logging

setup_logging()
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

MODEL_DIR = os.getenv("AIP_MODEL_DIR", ".") 
META_DIR = os.getenv("AIP_META_DIR", ".") 
FEATURE_DIR = os.getenv("AIP_FEATURE_DIR", ".")
logging.info("App startup: Running in PRODUCTION mode: Using AIP model and meta directories.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.predictor = CustomPredictor()
        app.state.predictor.load(artifact_uri=MODEL_DIR)
        logging.info("App startup: Predictor initialized successfully.")
    except Exception as e:
        logging.error(f"App startup: Error initializing predictor: {e}")
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

@app.post("/predict")
async def predict_endpoint(request: Request, request_data: PredictionRequestSchema):
    predictor = request.app.state.predictor
    if predictor is None:
        raise HTTPException(status_code=503, detail="Service Unavailable: Model not loaded.")

    try:
        predictions = []
        
        for instance in request_data.instances:
            instance_data = instance.model_dump()
            result = predictor.predict(instance_data) 
            predictions.append(result)
            
        return {"predictions": predictions}
    except Exception as e:
        logging.error(f"Predict endpoint: Prediction execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")