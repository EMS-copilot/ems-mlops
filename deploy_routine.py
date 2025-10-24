from google.cloud import aiplatform
from google.cloud.aiplatform.prediction import LocalModel
import logging

logging.basicConfig(level=logging.INFO)

PROJECT_ID = "white-sunspot-473307-p3"
REGION = "asia-northeast3"
AR_REPO_NAME = "ems-copilot-docker"
MODEL_DISPLAY_NAME = "ems-wraper-routine-1"
ENDPOINT_DISPLAY_NAME = "ems-wrapper-routine-endpoint-1"

GCS_FEATURE_URI = "gs://ems_dummy_1/data/features.json"
GCS_META_URI = "gs://ems_dummy_1/data/hospital_meta.csv"

MODEL_ARTIFACT_URI = "gs://ems_dummy_1/model/model-8766129131327848448/tf-saved-model/2025-10-22T00:15:58.603467Z/predict/001/"

IMAGE_URI = f"{REGION}-docker.pkg.dev/{PROJECT_ID}/{AR_REPO_NAME}/tf-cpr-service:latest"
STAGING_BUCKET_URI = f"gs://{PROJECT_ID}-vertex-staging"

ENV_VARS_DICT = {
    "GCS_FEATURE_URI": GCS_FEATURE_URI,
    "GCS_META_URI": GCS_META_URI,
}

# ====================================================================
# Init Vertex AI
# ====================================================================
aiplatform.init(project=PROJECT_ID, location=REGION)

try:
    from predictor import CustomPredictor
except ImportError:
    logging.error(
        "Failed to import CustomPredictor. Ensure predictor.py is accessible."
    )
    exit(1)


# ====================================================================
# Build and Push CPR Image
# ====================================================================
logging.info(f"Building CPR image: {IMAGE_URI}")
local_model = LocalModel.build_cpr_model(
    src_dir=".",
    output_image_uri=IMAGE_URI,
    predictor=CustomPredictor,
    requirements_path="./requirements-routine.txt",
    base_image="python:3.9",
)
logging.info("Image successfully built locally.")

logging.info("Pushing image to Artifact Registry...")
local_model.push_image()
logging.info("Image push successful.")


# ====================================================================
# Upload Model
# ====================================================================
logging.info("Checking Model Registry for existing model...")
model_filter = f'display_name="{MODEL_DISPLAY_NAME}"'
existing_models = aiplatform.Model.list(filter=model_filter)

if existing_models:
    model = existing_models[0]
    logging.info(f"Existing Model found: {model.resource_name}. Reusing.")
else:
    logging.info("Model not found. Uploading new Model...")
    model = aiplatform.Model.upload(
        local_model=local_model,
        display_name=MODEL_DISPLAY_NAME,
        artifact_uri=MODEL_ARTIFACT_URI,
        serving_container_environment_variables=ENV_VARS_DICT, 
    )
    logging.info(f"Model uploaded successfully. Resource name: {model.resource_name}")


# # ====================================================================
# # Deploy Model to Endpoint
# # ====================================================================

# logging.info("Checking Endpoint Registry for existing endpoint...")
# endpoint_filter = f'display_name="{ENDPOINT_DISPLAY_NAME}"'
# existing_endpoints = aiplatform.Endpoint.list(filter=endpoint_filter)

# if existing_endpoints:
#     endpoint:aiplatform.Endpoint = existing_endpoints[0]
#     logging.info(f"Existing Endpoint found: {endpoint.resource_name}. Reusing.")
# else:
#     logging.info("Endpoint not found. Creating new Endpoint...")
#     endpoint:aiplatform.Endpoint = aiplatform.Endpoint.create(
#         display_name=ENDPOINT_DISPLAY_NAME,
#     )
#     logging.info(f"Endpoint created: {endpoint.uri}")


# logging.info(
#     f"Deploying Model {model.display_name} to Endpoint {endpoint.display_name}..."
# )

# model.deploy(
#     endpoint=endpoint, 
#     traffic_split={"0": 100}
# )

# logging.info("Deployment complete!")
# logging.info(f"Endpoint URL: {endpoint.uri}")
