from dataclasses import dataclass

@dataclass
class GlobalMetrics:
    total_patients: int = 0
    prehospital_deaths: int = 0
    inhospital_deaths: int = 0
    arrived: int = 0
    discharged: int = 0
