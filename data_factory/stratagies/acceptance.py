from random import random

from data_factory.core import AcceptanceStrategy
from data_factory.types import ARLog, AROutcome, PatientWithLocation, SimHospitalState


class DefaultAcceptance(AcceptanceStrategy):
    def __init__(self, arlog: ARLog):
        self.arlog = arlog

    def on_call(
        self, minute: float, patient: PatientWithLocation, hosp: SimHospitalState, distance_km: float
    ) -> bool:
        hosp.calls_received += 1
        ok = False
        if hosp.static.has_er and hosp.occupancy_ok(minute, patient.triage_level):
            hosp.calls_accepted += 1
            ok = True
        if (
            not ok
            and patient.triage_level == 1
            and (hosp.static.is_regional_center or hosp.static.specialist_oncall)
        ):
            if random() < 0.2:
                hosp.calls_accepted += 1
                ok = True
        eff = hosp.effective_capacity(minute)
        self.arlog.add(
            AROutcome(
                patient.id,
                hosp.static.hospital_id,
                "call",
                ok,
                minute,
                patient.triage_level,
                patient.bp_systolic,
                patient.hr,
                {"icu": hosp.occ_icu, "er": hosp.occ_er, "hosp": hosp.occ_hosp},
                {"icu": eff[0], "er": eff[1], "hosp": eff[2]},
                distance_km,
            )
        )
        return ok

    def on_door(
        self, minute: float, patient: PatientWithLocation, hosp: SimHospitalState, distance_km: float
    ) -> bool:
        ok = hosp.occupancy_ok(minute, patient.triage_level)
        eff = hosp.effective_capacity(minute)
        self.arlog.add(
            AROutcome(
                patient.id,
                hosp.static.hospital_id,
                "door",
                ok,
                minute,
                patient.triage_level,
                patient.bp_systolic,
                patient.hr,
                {"icu": hosp.occ_icu, "er": hosp.occ_er, "hosp": hosp.occ_hosp},
                {"icu": eff[0], "er": eff[1], "hosp": eff[2]},
                distance_km,
            )
        )
        return ok
