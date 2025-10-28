from typing import Dict, List, Any, Tuple, Literal
from dataclasses import dataclass, asdict

# all outer types import from here
from src.schemas.hospital import HospitalWithLocation
from src.schemas.utils import Coord
from src.schemas.patient import PatientWithLocation


@dataclass
class AROutcome:
    patient_id: str
    hospital_id: str
    stage: Literal["call", "door"]
    decision: bool
    minute: float
    triage: int
    bp_systolic: float
    hr: float
    hosp_occ: Dict[str, int]
    hosp_eff_cap: Dict[str, int]
    distance_km: float


class ARLog:
    def __init__(self):
        self.records: List[AROutcome] = []

    def add(self, rec: AROutcome):
        self.records.append(rec)

    def as_dicts(self) -> List[Dict[str, Any]]:
        return [asdict(r) for r in self.records]


@dataclass
class SimHospitalState:
    static: HospitalWithLocation
    occ_icu: int = 0
    occ_er: int = 0
    occ_hosp: int = 0
    calls_received: int = 0
    calls_accepted: int = 0
    arrivals_accepted: int = 0
    door_rejects: int = 0
    prehospital_deaths: int = 0
    inhospital_deaths: int = 0
    discharges: int = 0
    time_to_accept_sum: float = 0.0
    time_to_accept_n: int = 0
    night_start: int = 22
    night_end: int = 6
    night_penalty: float = 0.7

    def is_night(self, minute: float) -> bool:
        hour = int(minute // 60) % 24
        if self.static.is_24h:
            return False
        if self.night_start < self.night_end:
            return self.night_start <= hour < self.night_end
        return hour >= self.night_start or hour < self.night_end

    def effective_capacity(self, minute: float) -> Tuple[int, int, int]:
        p = (
            1.0
            if self.static.is_24h or not self.is_night(minute)
            else self.night_penalty
        )
        eff_icu = max(0, int(round(self.static.icu_beds * p)))
        eff_er = max(0, int(round(self.static.er_beds * p)))
        eff_h = max(0, int(round(self.static.hospital_capacity * p)))
        return eff_icu, eff_er, eff_h

    def occupancy_ok(self, minute: float, triage: int) -> bool:
        eff_icu, eff_er, eff_h = self.effective_capacity(minute)
        need_icu = 1 if triage <= 2 else 0
        need_er = 1
        need_h = 1 if triage == 3 else 0
        return (
            self.occ_icu + need_icu <= eff_icu
            and self.occ_er + need_er <= eff_er
            and self.occ_hosp + need_h <= eff_h
        )

    def occupy(self, triage: int):
        if triage <= 2:
            self.occ_icu += 1
        self.occ_er += 1
        if triage == 3:
            self.occ_hosp += 1

    def release(self, triage: int):
        if triage <= 2 and self.occ_icu > 0:
            self.occ_icu -= 1
        if self.occ_er > 0:
            self.occ_er -= 1
        if triage == 3 and self.occ_hosp > 0:
            self.occ_hosp -= 1
