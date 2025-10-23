from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import List


@dataclass(frozen=True)
class StaticResources:
    features: List[str]
    hospital_meta: Mapping[str, dict]

    def __init__(self, feature_dir, meta_dir):
        object.__setattr__(
            self, "features", load_features(feature_dir)
        )
        object.__setattr__(
            self, "hospital_meta", MappingProxyType(load_hospital_meta(meta_dir))
        )


def load_features(path):
    import json

    with open(path, "r", encoding="utf-8") as f:
        features = json.load(f)

    return features


def load_hospital_meta(path) -> dict:
    import csv

    hospital_meta = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            hospital_meta[row["hospital_id"]] = {
                k: v for k, v in row.items() if k != "hospital_id"
            }

    return hospital_meta
