import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status

from src.predictor import CustomPredictor
from src.schemas import PredictionRequestSchema
from src.utils import setup_logging

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

if os.getenv("LOCAL_ENV") == "true":
    from src.backend import LocalBackend as Backend

    MODEL_DIR = os.getenv("LOCAL_MODEL_DIR", ".")
    META_FILE = os.getenv("LOCAL_META_FILE", ".")
    FEATURE_FILE = os.getenv("LOCAL_FEATURE_FILE", ".")


else:
    from src.backend import GCSBackend as Backend

    MODEL_DIR = os.getenv("AIP_MODEL_DIR", ".")
    META_FILE = os.getenv("AIP_META_FILE", ".")
    FEATURE_FILE = os.getenv("AIP_FEATURE_FILE", ".")

setup_logging()
logging.info("App startup: Running in PRODUCTION mode: Using AIP model and meta directories.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.predictor = CustomPredictor(FEATURE_FILE, META_FILE, Backend)
        app.state.predictor.load(artifact_uri=MODEL_DIR)
        logging.info("App startup: Predictor initialized successfully.")
    except Exception as e:
        logging.error(f"App startup: Error initializing predictor: {e}")
        raise RuntimeError("Model loading failed.")
    yield


app = FastAPI(title="Custom TF Predictor with FastAPI", version="1.0", lifespan=lifespan)


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
