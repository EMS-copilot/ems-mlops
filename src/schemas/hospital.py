from pydantic import BaseModel, ConfigDict, Field, field_validator
from .utils import Coord, get_constraints

constraints = get_constraints("hospital")


class HospitalNoMeta(BaseModel):
    model_config = ConfigDict(extra="ignore")
    hospital_id: str
    hospital_capacity: int = Field(**constraints.get("hospital_capacity", {}))
    icu_beds: float = Field(**constraints.get("icu_beds", {}))
    er_beds: float = Field(**constraints.get("er_beds", {}))


class Hospital(HospitalNoMeta):
    hospital_area: str
    is_24h: bool
    has_er: bool
    is_regional_center: bool
    specialist_oncall: bool

    @field_validator("hospital_area")
    def validate_hospital_area(cls, v: str):
        allowed = constraints["hospital"]["hospital_area"]
        if v not in allowed:
            raise ValueError(f"hospital_area must be one of {allowed}, got {v!r}")
        return v


class HospitalWithLocation(Hospital):
    location: Coord
