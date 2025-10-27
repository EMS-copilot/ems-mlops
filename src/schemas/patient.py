from typing import ClassVar, Literal
from pydantic import BaseModel, Field, model_validator, ConfigDict
from .utils import Coord, get_constraints

constraints = get_constraints("patient")

class Patient(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    age: int = Field(**constraints.get("age", {}))
    sex: Literal["M", "F"]
    triage_level: int = Field(**constraints.get("triage_level", {}))
    symptom: str
    bp_systolic: int = Field(**constraints.get("bp_systolic", {}))
    hr: int = Field(**constraints.get("hr", {}))
    SYMPTOM_MAP: ClassVar[dict[int, list[str]]] = {int(k) : v for k, v in constraints["SYMPTOM_MAP"].items()}

    @model_validator(mode="after")
    def check_symptom_vs_triage(self):
        allowed = self.SYMPTOM_MAP[self.triage_level]
        if self.symptom not in allowed:
            raise ValueError(
                f"triage_level={self.triage_level}는 {allowed} 중 하나여야 함 (지금: {self.symptom})"
            )
        return self


class PatientWithLocation(Patient):
    location: Coord
