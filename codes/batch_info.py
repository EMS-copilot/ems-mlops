from typing import Dict, List
from dataclasses import dataclass, field


@dataclass
class BatchInfo:
    patient_id: str = field(default_factory=str)
    hospital_ids: List[str] = field(default_factory=list)
    method: Dict = field(default_factory=dict)

    def update(self, data: Dict) -> Dict:
        self.patient_id = data["patient"]["id"]
        self.hospital_ids = [i["hospital_id"] for i in data["candidate_hospitals"]]
        self.method = data["result_method"]
