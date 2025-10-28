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
        current_location = p.location
        
        # deepcopy is required, because this list will be mutated
        hospitals_to_try = self.hospitals[:]

        while True:
            elapsed = self.env.now - call_start
            if elapsed >= self.timing.death_time(p):
                self.metrics.prehospital_deaths += 1
                # find nearest hospital for metric attribution
                nearest = min(
                    self.hospitals,
                    key=lambda h: self.travel.distance_km(current_location, h.static.location),
                )
                nearest.prehospital_deaths += 1
                return

            hospitals_to_try.sort(
                key=lambda h: self.travel.distance_km(current_location, h.static.location)
            )

            accepted_hosp = None
            dist_km = 0.0
            for h in hospitals_to_try:
                dist_km = self.travel.distance_km(current_location, h.static.location)
                if self.acceptance.on_call(self.env.now, p, h, dist_km):
                    accepted_hosp = h
                    break
            
            if accepted_hosp is None:
                yield self.env.timeout(5)
                continue

            # travel to hospital
            travel_time = self.travel.minutes(current_location, accepted_hosp.static.location)
            
            tta = self.env.now - call_start
            accepted_hosp.time_to_accept_sum += tta
            accepted_hosp.time_to_accept_n += 1

            yield self.env.timeout(travel_time)

            # check for death during travel
            since_call = self.env.now - call_start
            if since_call >= self.timing.death_time(p):
                self.metrics.prehospital_deaths += 1
                accepted_hosp.prehospital_deaths += 1
                return

            # at door
            dist_km = self.travel.distance_km(p.location, accepted_hosp.static.location)
            if self.acceptance.on_door(self.env.now, p, accepted_hosp, dist_km):
                self.metrics.arrived += 1
                accepted_hosp.arrivals_accepted += 1

                if since_call > self.timing.golden_time(p):
                    self.metrics.inhospital_deaths += 1
                    accepted_hosp.inhospital_deaths += 1
                    return
                
                # occupy bed and recover
                tri = p.triage_level
                accepted_hosp.occupy(tri)
                yield self.env.timeout(self.timing.recovery_time(p))
                accepted_hosp.release(tri)
                self.metrics.discharged += 1
                accepted_hosp.discharges += 1
                return  # end of patient journey
            else:
                # rejected at door, try next hospital
                accepted_hosp.door_rejects += 1
                current_location = accepted_hosp.static.location
                hospitals_to_try = [h for h in hospitals_to_try if h.static.hospital_id != accepted_hosp.static.hospital_id]
                if not hospitals_to_try:
                    # no more hospitals to try
                    # this is effectively a prehospital death, but we will not count it dually
                    return
