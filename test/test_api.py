import requests
import json

def test_input_schema():
    with open('data/input_api_schema.json', "r", encoding="utf-8") as f:
        input_data = json.load(f)

    url = "http://127.0.0.1:8000/test_preprocess"

    try:
        response = requests.post(url, json=input_data)

        if response.status_code == 200:
            print("Test Preprocess endpoint: Status code is 200 (OK)")
            print("Test Preprocess endpoint: Response body is correct")
            print(f"Test Preprocess endpoint: Response: {response.json()}")

        else:
            print(
                f"Test Preprocess endpoint: Status code is {response.status_code}"
            )
            print(
                f"Test Preprocess endpoint: Unexpected response body: {response.json()}"
            )

    except requests.exceptions.RequestException as e:
        print(f"Test Preprocess endpoint: An error occurred: {e}")
        print(
            "Test Preprocess endpoint: Ensure FastAPI application is running at http://127.0.0.1:8000."
        )


def test_predict_endpoint():
    with open("data/input_api_schema.json", "r", encoding="utf-8") as f:
        input_data = json.load(f)

    url = "http://127.0.0.1:8000/predict"

    try:
        response = requests.post(url, json=input_data)

        if response.status_code == 200:
            print("Predict endpoint: Status code is 200 (OK)")
            response_json = response.json()
            if "predictions" in response_json:
                print("Predict endpoint: Response contains 'predictions' key.")
                print(f"Predictions: {response_json}")
            else:
                print(
                    "Predict endpoint: Response does not contain 'predictions' key."
                )
        else:
            print(f"Predict endpoint: Status code is {response.status_code}")
            print(
                f"Predict endpoint: Unexpected response body: {response.json()}"
            )

    except requests.exceptions.RequestException as e:
        print(f"Predict endpoint: An error occurred: {e}")
        print(
            "Predict endpoint: FastAPI 애플리케이션이 http://127.0.0.1:8000 에서 실행 중인지 확인하세요."
        )


if __name__ == "__main__":
    print(f"Ping endpoint: {requests.get('http://127.0.0.1:8000/ping')}")
    test_input_schema()
    test_predict_endpoint()
