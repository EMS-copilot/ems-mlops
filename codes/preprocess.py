from typing import List, Dict

import tensorflow as tf


def custom_preprocess(
    data: Dict, feature: Dict = None, hospital_meta: Dict = None
) -> tf.Tensor:
    batch = to_batch(data, feature, hospital_meta)
    example_batch = [to_tf_example(i).SerializeToString() for i in batch]
    input_tensors = tf.constant(example_batch, dtype=tf.string)
    return input_tensors


def _feature(data: str):
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[data.encode("utf-8")]))


def _convert_types(data: Dict) -> Dict:
    converted_data = data.copy()

    for key, value in converted_data.items():
        if value is not None:
            converted_data[key] = str(value)
        else:
            converted_data[key] = None

    return converted_data


def parse_batch_info(data: Dict) -> Dict:
    index = [i["hospital_id"] for i in data["candidate_hospitals"]]
    method = data["result_method"]
    return index, method


def to_batch(data: Dict, feature: List, hospital_meta: Dict) -> Dict:
    patient_info = {k: v for k, v in data["patient"].items()}
    patient_info = _convert_types(patient_info)  # Apply type conversion

    batch = []
    for hospital in data["candidate_hospitals"]:
        hid = hospital["hospital_id"]
        hospital_info = {k: v for k, v in hospital.items() if k != "hospital_id"}
        hospital_info["specialist_oncall"] = "0.0"
        hospital_info = _convert_types(hospital_info)
        meta_info = hospital_meta.get(hid, {})
        meta_info = _convert_types(meta_info)

        combined_info = {**patient_info, **hospital_info, **meta_info}

        filtered_instance = {key: combined_info.get(key) for key in feature}
        filtered_instance["triage_level"] = "Level" + filtered_instance["triage_level"]
        batch.append(filtered_instance)
    return batch


def to_tf_example(data: Dict):
    example = tf.train.Example(
        features=tf.train.Features(feature={k: _feature(v) for k, v in data.items()})
    )
    return example


if __name__ == "__main__":
    import json
    
    from codes.static_resources import load_hospital_meta, load_features

    with open("data/input_api_schema.json", "r") as f:
        data = json.load(f)

    print(
        custom_preprocess(
            data,
            load_features("data/features.json"),
            load_hospital_meta("data/hospital_meta.csv"),
        )
    )
