import json
import os
import logging

from deploy import get_local_model


logging.basicConfig(level=logging.INFO)

logging.info("\n--- Starting Local Test Deployment ---")

local_model = get_local_model()

try:
    with local_model.deploy_to_local_endpoint(
        artifact_uri=os.getenv('AIP_MODEL_DIR'),
        credential_path=os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
    ) as local_endpoint:
        logging.info("Local Endpoint Deployed. Running Health Check...")

        health_check_response = local_endpoint.run_health_check()

        logging.info(f"Health Check Status: {health_check_response.status_code}")
        if health_check_response.status_code == 200:
            logging.info("Model Server is Healthy.")
        else:
            logging.error("Model Server Failed Health Check.")

        logging.info("Sending prediction request...")
        predict_response = local_endpoint.predict(request_file="data/input_api_schema.json")

        logging.info(f"Prediction Status: {predict_response.status_code}")

        if predict_response.status_code == 200:
            content = predict_response.content.decode("utf-8")
            logging.info(f"Prediction Result: {json.loads(content)}")


except Exception as e:
    logging.error(f"Local deployment or prediction failed: {e}")

finally:
    logging.info("Local Test Finished.")
