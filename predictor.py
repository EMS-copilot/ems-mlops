import os
import logging
from typing import List, Dict, Any
import tensorflow as tf
import struct2tensor.ops.gen_decode_proto_sparse

from codes import (
    StaticResources,
    BatchInfo,
    download_all_artifacts,
    custom_preprocess,
    custom_postprocess,
)


class CustomPredictor:
    def __init__(self) -> None:
        self._model: Any = None
        self._input_key: str = None
        self._static = StaticResources(
            os.getenv("AIP_FEATURE_DIR"), os.getenv("AIP_META_DIR")
        )
        self._batch_info = BatchInfo()
        logging.info("Static resources initialized.")

    def load(self, artifact_uri):
        local_model_path = download_all_artifacts(artifact_uri)

        try:
            self._model = tf.saved_model.load(local_model_path)
            print("TensorFlow SavedModel successfully loaded.")

            inference_func = self._model.signatures["serving_default"]
            self._input_key = list(inference_func.structured_input_signature[1].keys())[
                0
            ]
            print(f"Model expects input tensor key: {self._input_key}")

        except Exception as e:
            raise RuntimeError(
                f"Failed to load TensorFlow SavedModel from {local_model_path}: {e}"
            )

    def preprocess(self, request_body: Dict) -> List:  # input_json: input_api_schema
        self._batch_info.update(request_body)
        instances = custom_preprocess(
            request_body, self._static.features, self._static.hospital_meta
        )
        logging.debug(f"instances: {instances}")

        return instances  # tf.Tensor

    def infer(self, instances) -> tf.Tensor:
        inference_func = self._model.signatures["serving_default"]
        predictions = inference_func(**{self._input_key: tf.constant(instances)})
        logging.debug(f"predictions: {predictions}")

        return predictions  # tf.Tensor

    def postprocess(self, predictions) -> Dict:
        results = custom_postprocess(predictions, self._batch_info)
        logging.debug(f"results: {results}")

        return results  # output_api_schema

    def predict(self, request_body: Dict[str, List]) -> Dict[str, List]:
        if self._model is None:
            raise RuntimeError("Model has not been loaded.")
        if self._input_key is None:
            raise RuntimeError("Model input key not identified during load.")

        instances = self.preprocess(request_body)
        predictions = self.infer(instances)
        results = self.postprocess(predictions)

        return results


if __name__ == "__main__":
    import json

    with open(os.getenv("LOCAL_INPUT_SCHEMA"), "r") as f:
        data = json.load(f)

    predictor = CustomPredictor()
    predictor.load(os.getenv("AIP_MODEL_DIR"))
    print(predictor.predict(data))
