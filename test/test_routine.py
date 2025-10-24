import json
import os
import logging

from google.cloud.aiplatform.prediction import LocalModel
from predictor import CustomPredictor


logging.basicConfig(level=logging.INFO)

REQUEST_FILE_PATH = "data/input_api_schema.json"
PROJECT_ID = "white-sunspot-473307-p3"
REGION = "asia-northeast3"
AR_REPO_NAME = "ems-copilot-docker"
MODEL_DISPLAY_NAME = "ems-wraper-routine"
ENDPOINT_DISPLAY_NAME = "ems-wrapper-routine-endpoint"

GCS_FEATURE_URI = "gs://ems_dummy_1/data/features.json"
GCS_META_URI = "gs://ems_dummy_1/data/hospital_meta.csv"

MODEL_ARTIFACT_URI = "gs://ems_dummy_1/model/model-8766129131327848448/tf-saved-model/2025-10-22T00:15:58.603467Z/predict/001/"

IMAGE_URI = f"{REGION}-docker.pkg.dev/{PROJECT_ID}/{AR_REPO_NAME}/tf-cpr-service:latest"
STAGING_BUCKET_URI = f"gs://{PROJECT_ID}-vertex-staging"

logging.info("\n--- Starting Local Test Deployment ---")

local_model = LocalModel.build_cpr_model(
    src_dir=".",
    output_image_uri=IMAGE_URI, 
    predictor=CustomPredictor,
    requirements_path="./requirements-routine.txt",
    base_image= "python:3.9",
)

try:
    with local_model.deploy_to_local_endpoint(
        artifact_uri=MODEL_ARTIFACT_URI,
        env_vars={
            "GCS_FEATURE_URI": GCS_FEATURE_URI,
            "GCS_META_URI": GCS_META_URI,
        },
    ) as local_endpoint:

        logging.info("Local Endpoint Deployed. Running Health Check...")

        health_check_response = local_endpoint.run_health_check()
        
        logging.info(f"Health Check Status: {health_check_response.status_code}")
        if health_check_response.status_code == 200:
            logging.info("Model Server is Healthy.")
        else:
            logging.error("Model Server Failed Health Check.")

        logging.info("Sending prediction request...")
        predict_response = local_endpoint.predict(
            request_file=REQUEST_FILE_PATH 
        )
        
        logging.info(f"Prediction Status: {predict_response.status_code}")
        
        if predict_response.status_code == 200:
            content = predict_response.content.decode("utf-8")
            logging.info(f"Prediction Result: {json.loads(content)}")


except Exception as e:
    logging.error(f"Local deployment or prediction failed: {e}")

finally:
    # 임시 요청 파일 삭제
    if os.path.exists(REQUEST_FILE_PATH):
        os.remove(REQUEST_FILE_PATH)
    logging.info("Local Test Finished.")