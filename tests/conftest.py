import pytest
import json
from pathlib import Path

def pytest_addoption(parser):
    parser.addoption(
        "--host",
        action="store",
        default="http://127.0.0.1:8000",
        help="FastAPI host URL",
    )

@pytest.fixture(scope="session")
def host(request):
    return request.config.getoption("--host")

@pytest.fixture(scope="session")
def load_json():
    def _loader(filename: str):
        file_path = Path(filename)
        with file_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    return _loader