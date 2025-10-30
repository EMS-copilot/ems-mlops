import json
import os
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, Field

from src.utils.gcs_utils import download_single_file_to_memory


def _load_constraints(gcs_uri):
    try:
        constraints_path = Path(__file__).parent.parent.parent / os.getenv("LOCAL_CONSTRAINT_FILE")

        if constraints_path.exists():
            with open(constraints_path, "r") as f:
                return json.load(f)
    except Exception as e:
        print(f'constraint file does not exist : {e}')

    print(f"Loading schema constraint from GCS: {gcs_uri}")
    return _load_all_constraints(gcs_uri)


def _load_all_constraints(gcs_uri: str) -> dict:
    try:
        raw_bytes = download_single_file_to_memory(gcs_uri)
        return json.loads(raw_bytes.decode("utf-8"))
    except FileNotFoundError:
        return {}
    except Exception as e:
        raise RuntimeError(f"Failed to load constraints: {e}")


ALL_CONSTRAINTS = _load_constraints(os.getenv("AIP_CONSTRAINT_FILE"))


def get_constraints() -> dict:
    global ALL_CONSTRAINTS
    return ALL_CONSTRAINTS


class Coord(BaseModel):
    x: Annotated[int, Field(ge=0, le=100)]
    y: Annotated[int, Field(ge=0, le=100)]
