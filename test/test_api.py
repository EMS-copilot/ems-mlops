import requests
import json

def test_input_schema(host):
    with open('data/input_api_schema.json', "r", encoding="utf-8") as f:
        input_data = json.load(f)

    url = f"{host}/test_preprocess"

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
            f"Test Preprocess endpoint: Ensure FastAPI application is running at {host}."
        )


def test_predict_endpoint(host):
    with open("data/input_api_schema.json", "r", encoding="utf-8") as f:
        input_data = json.load(f)

    url = f"{host}/predict"

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
            f"Predict endpoint: FastAPI 애플리케이션이 {host} 에서 실행 중인지 확인하세요."
        )


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="명령행 인자 테스트 예제")
    parser.add_argument(
        "--host",
        type=str,
        default="http://127.0.0.1:8000",
        help="FastAPI 애플리케이션의 호스트 URL",
    )
    args = parser.parse_args()
    host = args.host
    print(f"Testing FastAPI application at {host}")
    print(f"Ping endpoint: {requests.get(f'{host}/ping')}")
    test_input_schema(host)
    test_predict_endpoint(host)
