import os
from fastapi import FastAPI, Request, status, HTTPException
from contextlib import asynccontextmanager

from codes.predictor import CustomPredictor 
from codes.schemas import InputSchema

if os.environ.get("TEST_ENV", ".") == 'true': 
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
    MODEL_DIR = os.environ.get("LOCAL_MODEL_DIR", ".")
    META_DIR = os.environ.get("LOCAL_META_DIR", ".")
else: 
    MODEL_DIR = os.environ.get("AIP_MODEL_DIR", ".") 
    META_DIR = os.environ.get("AIP_META_DIR", ".") 

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.predictor = CustomPredictor(MODEL_DIR, META_DIR)
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
    print('called ping')
    return {"status": "ready"}

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
    

@app.post("/test_preprocess", status_code=status.HTTP_200_OK)
def test_input_preprocess(request: Request, input_data: InputSchema):
    try:
        instances = request.app.state.predictor.preprocess(input_data.model_dump())
    except Exception as e:
        print(f"Preprocessing failed: {e}")
        raise HTTPException(
            status_code=400,  
            detail=f"Invalid input: {str(e)}"
        )
    return {"status": "success", "message": "Input data is valid.", "instances":instances}