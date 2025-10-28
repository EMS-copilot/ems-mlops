from typing import Protocol, Iterator

from data_factory.types import SimHospitalState, PatientWithLocation, Coord


class AcceptanceStrategy(Protocol):
    def on_call(
        self, minute: float, patient: "PatientWithLocation", hosp: "SimHospitalState"
    ) -> bool: ...
    def on_door(
        self, minute: float, patient: "PatientWithLocation", hosp: "SimHospitalState"
    ) -> bool: ...


class TravelTimeService(Protocol):
    def minutes(self, a: Coord, b: Coord) -> float: ...


class TimingModel(Protocol):
    def death_time(self, patient: "PatientWithLocation") -> float: ...
    def golden_time(self, patient: "PatientWithLocation") -> float: ...
    def recovery_time(self, patient: "PatientWithLocation") -> float: ...


class PatientSource(Protocol):
    def __iter__(self) -> Iterator["PatientWithLocation"]: ...


class EventHooks:
    def __init__(self, on_call=None, on_dispatch=None, on_door=None, on_outcome=None):
        self.on_call = on_call
        self.on_dispatch = on_dispatch
        self.on_door = on_door
        self.on_outcome = on_outcome
