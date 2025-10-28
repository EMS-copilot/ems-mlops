import csv
import random
from typing import List, Iterator, Union

import simpy

from data_factory.types import (
    HospitalWithLocation,
    PatientWithLocation,
    SimHospitalState,
    Coord,
)
from data_factory.system.metric import GlobalMetrics


def build_demo_hospitals(seed: int) -> List[HospitalWithLocation]:
    """
    Builds a list of hospitals from the hospital_meta.csv file.
    Randomly assigns locations and capacities.
    """
    hospitals = []
    rng = random.Random(seed)
    with open("/home/esillileu/ems-mlops/data/hospital_meta.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            hospitals.append(
                HospitalWithLocation(
                    hospital_id=row["hospital_id"],
                    hospital_name=row["hospital_name"],
                    hospital_area=row["hospital_area"].strip(),
                    is_24h=row["is_24h"] == "1",
                    is_regional_center=row["is_regional_center"] == "1",
                    has_er=row["has_er"] == "1",
                    specialist_oncall=rng.choice([True, False]),
                    hospital_capacity=rng.randint(20, 80),
                    icu_beds=rng.randint(5, 20),
                    er_beds=rng.randint(5, 20),
                    location=Coord(x=rng.randint(0, 100), y=rng.randint(0, 100)),
                )
            )
    return hospitals


class PoissonPatientSource:
    """
    Generates patients according to a Poisson process.
    """

    def __init__(self, env: simpy.Environment, lam_per_hour: float, seed: int):
        self.env = env
        self.lam_per_hour = lam_per_hour
        self.rng = random.Random(seed)
        self._patient_id_counter = 0

        self.symptoms = {
            "의식저하": [1, 2],
            "호흡곤란": [1, 2, 3],
            "뇌졸중": [1, 2, 3],
            "발열": [2, 3, 4],
            "출혈": [1, 2, 3],
            "두통": [2, 3, 4],
            "복통": [2, 3, 4],
            "외상": [1, 2, 3, 4],
            "흉통": [1, 2, 3],
            "경련": [1, 2],
            "화상": [1, 2, 3, 4],
            "중독": [1, 2, 3],
        }
        self.symptom_list = list(self.symptoms.keys())

    def __iter__(self) -> Iterator[Union[PatientWithLocation, simpy.Timeout]]:
        while True:
            # Wait for the next patient arrival
            inter_arrival_time = self.rng.expovariate(self.lam_per_hour / 60)
            yield self.env.timeout(inter_arrival_time)

            # Generate a new patient
            self._patient_id_counter += 1
            symptom = self.rng.choice(self.symptom_list)
            triage = self.rng.choice(self.symptoms[symptom])

            patient = PatientWithLocation(
                id=f"P-{self._patient_id_counter:06d}",
                sex=self.rng.choice(["M", "F"]),
                symptom=symptom,
                age=self.rng.randint(1, 100),
                triage_level=triage,
                bp_systolic=self.rng.uniform(80, 180),
                hr=self.rng.uniform(50, 150),
                location=Coord(x=self.rng.randint(0, 100), y=self.rng.randint(0, 100)),
            )
            yield patient


def print_report(hospitals: List[SimHospitalState], metrics: GlobalMetrics):
    """
    Prints a summary report of the simulation.
    """
    print("--- Simulation Report ---")
    print("\nGlobal Metrics:")
    print(f"  Total patients: {metrics.total_patients}")
    print(f"  Patients arrived at hospital: {metrics.arrived}")
    print(f"  Patients discharged: {metrics.discharged}")
    print(f"  Pre-hospital deaths: {metrics.prehospital_deaths}")
    print(f"  In-hospital deaths: {metrics.inhospital_deaths}")

    print("\nHospital-specific Metrics:")
    for h in sorted(hospitals, key=lambda x: x.static.hospital_id):
        print(f"\n  - Hospital: {h.static.hospital_name} ({h.static.hospital_id})")
        print(f"    Calls received: {h.calls_received}")
        print(f"    Calls accepted: {h.calls_accepted}")
        print(f"    Arrivals accepted: {h.arrivals_accepted}")
        print(f"    Door rejects: {h.door_rejects}")
        print(f"    Discharged: {h.discharges}")
        print(f"    Pre-hospital deaths (attributed): {h.prehospital_deaths}")
        print(f"    In-hospital deaths: {h.inhospital_deaths}")
        if h.time_to_accept_n > 0:
            avg_tta = h.time_to_accept_sum / h.time_to_accept_n
            print(f"    Average time to acceptance: {avg_tta:.2f} minutes")
