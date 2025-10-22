import tensorflow as tf
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

@dataclass(slots=True, frozen=True)
class StaticResource:
    model:Any
    hospital_meta: Mapping[str, dict]

    def __init__(self, model_dir, meta_dir = "data/hospital_meta.csv"):
        object.__setattr__(self, "model", load_model(model_dir))
        object.__setattr__(self, "hospital_meta", MappingProxyType(load_hospital_meta(meta_dir)))

def load_model(path):
    return tf.saved_model.load(path)

def load_hospital_meta(path) -> dict:
    import csv
    
    hospital_meta = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            hospital_meta[row["hospital_id"]] = {k: v for k, v in row.items() if k != "hospital_id"}
    
    return hospital_meta

