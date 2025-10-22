from typing import Annotated, ClassVar, Literal
from pydantic import BaseModel, Field, model_validator, ConfigDict
from .utils import Coord


class Patient(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: str
    age: Annotated[int, Field(ge=0, le=120)]
    sex: Literal["M", "F"]
    triage_level: Annotated[int, Field(ge=1, le=5)]
    symptom: str
    bp_systolic: Annotated[int, Field(ge=40, le=200)]
    hr: Annotated[int, Field(ge=30, le=200)]

    SYMPTOM_MAP: ClassVar[dict[int, list[str]]] = {
        1: ["shock", "coma"],
        2: ["bleeding", "chest_pain"],
        3: ["fever", "흉통"],
        4: ["cough", "dizziness"],
        5: ["mild", "headache"],
    }

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
