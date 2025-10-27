from math import hypot

from data_factory.core import TravelTimeService
from data_factory.types import Coord

class EuclidTravel(TravelTimeService):
    def __init__(self, speed_kmph: float = 40.0):
        self.speed_kmph = speed_kmph

    def minutes(self, a: Coord, b: Coord) -> float:
        dist_km = hypot(a.x - b.x, a.y - b.y)
        return (dist_km / self.speed_kmph) * 60.0