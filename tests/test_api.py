import pytest
import requests


def test_ping(host):
    resp = requests.get(f"{host}/ping")
    assert resp.status_code == 200, f"Ping failed at {host}: {resp.text}"


@pytest.mark.parametrize(
    "input_file",
    [
        "data/input_api_schema.json",
    ],
)
def test_predict(host, input_file, load_json):
    input_data = load_json(input_file)
    resp = requests.post(f"{host}/predict", json=input_data)

    if "error" not in input_file:
        assert resp.status_code == 200, f"Predict failed at {host}: {resp.text}"
        resp_json = resp.json()
        assert "predictions" in resp_json, "Missing 'predictions' key"
    else:
        assert resp.status_code != 200, f"Expected error at {host}, got {resp.text}"
