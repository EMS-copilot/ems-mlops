from .patient import Patient
from .hospital import HospitalNoMeta

from pydantic import BaseModel, ConfigDict
from typing import List


class CandidateHospital(HospitalNoMeta):
    distance_km: float
    eta_minutes: float


class ResultMethod(BaseModel):
    model_config = ConfigDict(extra="ignore")
    topK: int


class InputSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    patient: Patient
    candidate_hospitals: List[CandidateHospital]
    result_method: ResultMethod
