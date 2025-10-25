import os
import logging

from google.cloud import aiplatform
from deploy import get_local_model


logging.basicConfig(level=logging.INFO)

# ====================================================================
# Init Vertex AI
# ====================================================================
aiplatform.init(project=os.getenv("PROJECT_ID"), location=os.getenv("REGION"))

# ====================================================================
# Build and Push CPR Image
# ====================================================================
logging.info(f"Building CPR image: {os.getenv('IMAGE_URI')}")
local_model = get_local_model()
logging.info("Pushing image to Artifact Registry...")
local_model.push_image() 
logging.info("Image push successful.")


# ====================================================================
# Upload Model
# ====================================================================
logging.info("Checking Model Registry for existing model...")
model_filter = f'display_name="{os.getenv("MODEL_DISPLAY_NAME")}"'
existing_models = aiplatform.Model.list(filter=model_filter)

if existing_models:
    model = existing_models[0]
    logging.info(f"Existing Model found: {model.resource_name}. Reusing.")
else:
    logging.info("Model not found. Uploading new Model...")
    model = aiplatform.Model.upload(
        local_model=local_model,
        display_name=os.getenv("MODEL_DISPLAY_NAME"),
        artifact_uri=os.getenv("AIP_MODEL_DIR"),
    )
    logging.info(f"Model uploaded successfully. Resource name: {model.resource_name}")


# # ====================================================================
# # Deploy Model to Endpoint
# # ====================================================================

logging.info("Checking Endpoint Registry for existing endpoint...")
endpoint_filter = f'display_name="{os.getenv("ENDPOINT_DISPLAY_NAME")}"'
existing_endpoints = aiplatform.Endpoint.list(filter=endpoint_filter)

if existing_endpoints:
    endpoint: aiplatform.Endpoint = existing_endpoints[0]
    logging.info(f"Existing Endpoint found: {endpoint.resource_name}. Reusing.")
else:
    logging.info("Endpoint not found. Creating new Endpoint...")
    endpoint: aiplatform.Endpoint = aiplatform.Endpoint.create(
        display_name=os.getenv("ENDPOINT_DISPLAY_NAME"),
    )
    logging.info(f"Endpoint created: {endpoint}")


logging.info(
    f"Deploying Model {model.display_name} to Endpoint {endpoint.display_name}..."
)

model.deploy(
    endpoint=endpoint,
    service_account=os.getenv("SERVICE_ACCOUNT"),
    traffic_split={"0": 100},
)

logging.info("Deployment complete!")
logging.info(f"Endpoint URL: {endpoint}")
