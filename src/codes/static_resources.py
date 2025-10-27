import io
import csv
import json
import logging

from typing import List, Dict, Callable
from dataclasses import dataclass
from collections.abc import Mapping


@dataclass(frozen=True)
class StaticResources:
    features: List[str]
    hospital_meta: Mapping[str, dict]


def load_features(gcs_uri: str, download_func: Callable[[str], bytes]) -> List[str]:
    logging.info(f"Loading features from GCS: {gcs_uri}")

    data_bytes = download_func(gcs_uri)
    features = json.loads(data_bytes.decode("utf-8"))

    if not isinstance(features, list):
        raise TypeError("Features file must contain a list of strings.")

    return features


def load_hospital_meta(
    gcs_uri: str, download_func: Callable[[str], bytes]
) -> Dict[str, dict]:
    logging.info(f"Loading hospital metadata from GCS: {gcs_uri}")

    data_bytes = download_func(gcs_uri)
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


def get_static(feature_uri: str, meta_uri: str, download_func: Callable[[str], bytes]):
    return StaticResources(
        load_features(feature_uri, download_func),
        load_hospital_meta(meta_uri, download_func),
    )
