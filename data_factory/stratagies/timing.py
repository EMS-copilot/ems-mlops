from data_factory.core import TimingModel
from data_factory.types import PatientWithLocation

class TriageTiming(TimingModel):
    def death_time(self, p: PatientWithLocation) -> float:
        return {1: 30, 2: 60, 3: 150, 4: 300, 5: 480}.get(p.triage_level, 150)

    def golden_time(self, p: PatientWithLocation) -> float:
        return {1: 15, 2: 30, 3: 75, 4: 180, 5: 240}.get(p.triage_level, 90)

    def recovery_time(self, p: PatientWithLocation) -> float:
        return {1: 420, 2: 300, 3: 180, 4: 120, 5: 60}.get(p.triage_level, 180)