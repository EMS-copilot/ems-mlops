import requests
import json

def test_input_schema():
    with open("test/data/input_api_schema.json", "r", encoding="utf-8") as f:
        input_data = json.load(f)

    url = "http://127.0.0.1:8000/test_preprocess"

    try:
        response = requests.post(url, json=input_data)

        if response.status_code == 200:
            print("Status code is 200 (OK)")
            print("Response body is correct")

        else:
            print(f"Status code is {response.status_code}")
            print(f"Unexpected response body: {response.json()}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        print("FastAPI 애플리케이션이 http://127.0.0.1:8000 에서 실행 중인지 확인하세요.")


if __name__ == "__main__":
    print(requests.get('http://127.0.0.1:8000/ping'))
    test_input_schema()
