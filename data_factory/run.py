import simpy

from data_factory.factory import (
    build_demo_hospitals,
    PoissonPatientSource,
    print_report,
)
from data_factory.system.default_engine import System
from src.schemas.patient import PatientWithLocation


def run_sim(hours: float = 48, lam_per_hour: float = 12.0, seed: int = 42):
    env = simpy.Environment()
    hospitals = build_demo_hospitals(seed=seed)
    sys = System(env, hospitals)

    # Stitch a Poisson source to the system
    src = PoissonPatientSource(env, lam_per_hour=lam_per_hour, seed=seed)

    def drive():
        # Iterate synthetic patients and start processes on the fly
        iterator = iter(src)
        end_time = hours * 60
        while env.now < end_time:
            nxt = next(iterator)
            if isinstance(nxt, PatientWithLocation):
                env.process(sys.process_patient(nxt))
            # if `nxt` is a Timeout (from yield env.timeout), SimPy will advance via env.run()
            env.run(until=min(env.now + 0.1, end_time))

    drive()
    print_report(sys.hospitals, sys.metrics)

if __name__ == "__main__":
    run_sim()