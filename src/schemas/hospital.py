from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, create_model
from .utils import get_constraints

constraints = get_constraints("hospital")

class HospitalNoMeta(BaseModel):
    model_config = ConfigDict(extra="ignore")
    hospital_id: str
    hospital_capacity: int = Field(**constraints.get("hospital_capacity", {}))
    icu_beds: float = Field(**constraints.get("icu_beds", {}))
    er_beds: float = Field(**constraints.get("er_beds", {}))

Hospital = create_model(
    "Hospital",
    hospital_area=(Literal[tuple(constraints["hospital_area"])], ...),
    is_24h=(bool, ...),
    has_er=(bool, ...),
    is_regional_center=(bool, ...),
    specialist_oncall=(bool, ...),
)
