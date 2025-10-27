from .patient import Patient
from .hospital import HospitalNoMeta

from pydantic import BaseModel, ConfigDict
from typing import List, Dict


class CandidateHospital(HospitalNoMeta):
    distance_km: float
    eta_minutes: float


class ResultMethod(BaseModel):
    model_config = ConfigDict(extra="ignore")
    topK: int


class Prediction(BaseModel):
    hospital_id: str
    score: float
    explanations: Dict[str, float]


class InputSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    patient: Patient
    candidate_hospitals: List[CandidateHospital]
    result_method: ResultMethod


class OutputSchema(BaseModel):
    patient_id: str
    result_method: str
    predictions: List[Prediction]


class PredictionRequestSchema(BaseModel):
    instances: List[InputSchema]
