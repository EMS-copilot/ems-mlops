import tensorflow as tf
from typing import Dict
from codes.batch_info import BatchInfo


def custom_postprocess(data: tf.Tensor, batch_info: BatchInfo) -> Dict:
    method, value = method, value = next(iter(batch_info.method.items()))
    scores = data["outputs"].numpy().tolist()
    predictions = [
        {"hospital_id": k, "score": v, "explanations": {}}
        for k, v in zip(batch_info.hospital_ids, scores)
    ]
    sorted_predictions = sorted(predictions, key=lambda x: x["score"], reverse=True)
    return {
        "patient_id": batch_info.patient_id,
        "result_method": method,
        "predictions": sorted_predictions[:value],
    }
