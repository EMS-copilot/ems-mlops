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

# Vertex AI 표준 요청 형식을 위한 스키마
class PredictionRequestSchema(BaseModel):
    """
    Vertex AI Prediction API에서 기대하는 최상위 JSON 구조입니다.
    데이터는 'instances'라는 키의 리스트 안에 담겨 옵니다.
    """
    instances: List[InputSchema]
    
