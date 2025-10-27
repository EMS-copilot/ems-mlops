from pydantic import BaseModel, ConfigDict, Field, field_validator
from .utils import Coord, get_constraints

constraints = get_constraints("patient")


class Patient(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    sex: str
    symptom: str
    age: int = Field(**constraints.get("age", {}))
    triage_level: int = Field(**constraints.get("triage_level", {}))
    bp_systolic: float = Field(**constraints.get("bp_systolic", {}))
    hr: float = Field(**constraints.get("hr", {}))

    @field_validator("sex", "symptom")
    def validate_allowed(cls, v, field):
        allowed = constraints["patient"][field.field_name]["allowed"]
        if v not in allowed:
            raise ValueError(f"{field.field_name} must be one of {allowed}, got {v!r}")
        return v


class PatientWithLocation(Patient):
    location: Coord
