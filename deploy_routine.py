from google.cloud import aiplatform
from google.cloud.aiplatform.prediction import LocalModel
import logging

logging.basicConfig(level=logging.INFO)

PROJECT_ID = "white-sunspot-473307-p3"  
REGION = "asia-northeast3"               
AR_REPO_NAME = "ems-copilot-docker"           
MODEL_DISPLAY_NAME = "ems-wraper-routine"
ENDPOINT_DISPLAY_NAME = "ems-wrapper-routine-endpoint"

GCS_FEATURE_URI = "gs://ems_dummy_1/data/features.json" 
GCS_META_URI = "gs://ems_dummy_1/data/hospital_meta.csv"        

MODEL_ARTIFACT_URI = "gs://ems_dummy_1/model/model-8766129131327848448/tf-saved-model/2025-10-22T00:15:58.603467Z/predict/001/" 

IMAGE_URI = f"{REGION}-docker.pkg.dev/{PROJECT_ID}/{AR_REPO_NAME}/tf-cpr-service:latest"

aiplatform.init(project=PROJECT_ID, location=REGION)


try:
    from predictor import CustomPredictor 
except ImportError:
    logging.error("Failed to import CustomPredictor. Ensure predictor.py is accessible.")
    exit(1)


logging.info(f"Building CPR image: {IMAGE_URI}")

local_model = LocalModel.build_cpr_model(
    staging_bucket=f"gs://{PROJECT_ID}-vertex-staging",  
    image_uri=IMAGE_URI,
    predictor=CustomPredictor,
    requirements_path="./requirements-routine.txt",  
)

logging.info("Image successfully built locally.")

logging.info("Pushing image to Artifact Registry...")
local_model.push_image()
logging.info("Image push successful.")


logging.info("Uploading Model to Vertex AI Model Registry...")

model = aiplatform.Model.upload(
    local_model=local_model,
    display_name=MODEL_DISPLAY_NAME,
    artifact_uri=MODEL_ARTIFACT_URI,
)

logging.info(f"Model uploaded successfully. Resource Name: {model.resource_name}")
logging.info(f"Deploying Model to Endpoint: {ENDPOINT_DISPLAY_NAME}...")

endpoint = aiplatform.Endpoint.create(
    display_name=ENDPOINT_DISPLAY_NAME,
)

model.deploy(
    endpoint=endpoint,
    machine_type="n1-standard-2",  
    min_replica_count=1,
    max_replica_count=1,
    
    env_vars={
        "GCS_FEATURE_URI": GCS_FEATURE_URI,
        "GCS_META_URI": GCS_META_URI,
    }
)

logging.info("Deployment complete!")
logging.info(f"Endpoint URL: {endpoint.uri}")

