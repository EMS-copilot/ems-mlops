import json
from pathlib import Path
from typing import Annotated
from pydantic import BaseModel, Field


def _load_all_constraints() -> dict:
    constraints_path = Path(__file__).parent.parent.parent / "data" / "constraints.json"
    if not constraints_path.exists():
        return {}
    with open(constraints_path, "r") as f:
        return json.load(f)

ALL_CONSTRAINTS = _load_all_constraints()

def get_constraints(model_name: str) -> dict:
    return ALL_CONSTRAINTS.get(model_name, {})


class Coord(BaseModel):
    x: Annotated[int, Field(ge=0, le=100)]
    y: Annotated[int, Field(ge=0, le=100)]
