import requests
import json
import logging
from codes.logger_config import setup_logging

setup_logging()


def test_input_schema():
    with open("test/data/input_api_schema.json", "r", encoding="utf-8") as f:
        input_data = json.load(f)

    url = "http://127.0.0.1:8000/test_preprocess"

    try:
        response = requests.post(url, json=input_data)

        if response.status_code == 200:
            logging.info("Test Preprocess endpoint: Status code is 200 (OK)")
            logging.info("Test Preprocess endpoint: Response body is correct")
            logging.info(f"Test Preprocess endpoint: Response: {response.json()}")

        else:
            logging.error(
                f"Test Preprocess endpoint: Status code is {response.status_code}"
            )
            logging.error(
                f"Test Preprocess endpoint: Unexpected response body: {response.json()}"
            )

    except requests.exceptions.RequestException as e:
        logging.error(f"Test Preprocess endpoint: An error occurred: {e}")
        logging.error(
            "Test Preprocess endpoint: Ensure FastAPI application is running at http://127.0.0.1:8000."
        )


def test_predict_endpoint():
    with open("test/data/input_api_schema.json", "r", encoding="utf-8") as f:
        input_data = json.load(f)

    url = "http://127.0.0.1:8000/predict"

    try:
        response = requests.post(url, json=input_data)

        if response.status_code == 200:
            logging.info("Predict endpoint: Status code is 200 (OK)")
            response_json = response.json()
            if "predictions" in response_json:
                logging.info("Predict endpoint: Response contains 'predictions' key.")
                logging.info(f"Predictions: {response_json['predictions']}")
            else:
                logging.error(
                    "Predict endpoint: Response does not contain 'predictions' key."
                )
        else:
            logging.error(f"Predict endpoint: Status code is {response.status_code}")
            logging.error(
                f"Predict endpoint: Unexpected response body: {response.json()}"
            )

    except requests.exceptions.RequestException as e:
        logging.error(f"Predict endpoint: An error occurred: {e}")
        logging.error(
            "Predict endpoint: FastAPI 애플리케이션이 http://127.0.0.1:8000 에서 실행 중인지 확인하세요."
        )


if __name__ == "__main__":
    logging.info(f"Ping endpoint: {requests.get('http://127.0.0.1:8000/ping')}")
    test_input_schema()
    test_predict_endpoint()
