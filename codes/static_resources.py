import json
import csv
import io

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import List, Dict

from codes.gcs_utils import download_single_file_to_memory


def load_features(gcs_uri: str) -> List[str]:
    print(f"Loading features from GCS: {gcs_uri}")

    data_bytes = download_single_file_to_memory(gcs_uri)
    features = json.loads(data_bytes.decode("utf-8"))

    if not isinstance(features, list):
        raise TypeError("Features file must contain a list of strings.")

    return features


def load_hospital_meta(gcs_uri: str) -> Dict[str, dict]:
    print(f"Loading hospital metadata from GCS: {gcs_uri}")

    data_bytes = download_single_file_to_memory(gcs_uri)
    data_stream = io.StringIO(data_bytes.decode("utf-8"))

    reader = csv.DictReader(data_stream)
    hospital_meta = {}
    for row in reader:
        if "hospital_id" not in row:
            raise ValueError("CSV header must contain 'hospital_id'")

        hospital_meta[row["hospital_id"]] = {
            k: v for k, v in row.items() if k != "hospital_id"
        }

    return hospital_meta


@dataclass(frozen=True)
class StaticResources:
    features: List[str]
    hospital_meta: Mapping[str, dict]

    def __init__(self, feature_uri: str, meta_uri: str):
        object.__setattr__(self, "features", load_features(feature_uri))
        object.__setattr__(
            self, "hospital_meta", MappingProxyType(load_hospital_meta(meta_uri))
        )
