from typing import List

import simpy

from data_factory.core import EventHooks
from data_factory.stratagies import EuclidTravel, TriageTiming, DefaultAcceptance
from data_factory.system.metric import GlobalMetrics
from data_factory.types import (
    HospitalWithLocation,
    SimHospitalState,
    ARLog,
    PatientWithLocation,
)


# ----- System -----
class System:
    def __init__(self, env: simpy.Environment, hospitals: List[HospitalWithLocation]):
        self.env = env
        self.hospitals = [SimHospitalState(h) for h in hospitals]
        self.travel = EuclidTravel()
        self.timing = TriageTiming()
        self.arlog = ARLog()
        self.acceptance = DefaultAcceptance(self.arlog)
        self.hooks = EventHooks()
        self.metrics = GlobalMetrics()

    def process_patient(self, p: PatientWithLocation):
        self.metrics.total_patients += 1
        call_start = self.env.now
        sorted_h = sorted(
            self.hospitals,
            key=lambda h: self.travel.minutes(p.location, h.static.location),
        )
        accepted = None
        eta = 0.0
        for h in sorted_h:
            if self.acceptance.on_call(self.env.now, p, h):
                accepted = h
                eta = self.travel.minutes(p.location, h.static.location)
                break
        while accepted is None:
            elapsed = self.env.now - call_start
            if elapsed >= self.timing.death_time(p):
                self.metrics.prehospital_deaths += 1
                nearest = min(
                    self.hospitals,
                    key=lambda h: self.travel.minutes(p.location, h.static.location),
                )
                nearest.prehospital_deaths += 1
                return
            yield self.env.timeout(5)
            for h in sorted_h:
                if self.acceptance.on_call(self.env.now, p, h):
                    accepted = h
                    eta = self.travel.minutes(p.location, h.static.location)
                    break
        tta = self.env.now - call_start
        accepted.time_to_accept_sum += tta
        accepted.time_to_accept_n += 1
        yield self.env.timeout(eta)
        since = self.env.now - call_start
        if since >= self.timing.death_time(p):
            self.metrics.prehospital_deaths += 1
            accepted.prehospital_deaths += 1
            return
        if not self.acceptance.on_door(self.env.now, p, accepted):
            accepted.door_rejects += 1
            return self.env.process(self.process_patient(p))
        self.metrics.arrived += 1
        accepted.arrivals_accepted += 1
        if since > self.timing.golden_time(p):
            self.metrics.inhospital_deaths += 1
            accepted.inhospital_deaths += 1
            return
        tri = p.triage_level
        accepted.occupy(tri)
        yield self.env.timeout(self.timing.recovery_time(p))
        accepted.release(tri)
        self.metrics.discharged += 1
        accepted.discharges += 1
