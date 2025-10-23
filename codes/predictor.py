import os
from typing import List, Dict
import logging


class CustomPredictor:
    def __init__(
        self,
        feature_dir: str = os.environ.get("LOCAL_FEATURE_DIR"),
        meta_dir: str = os.environ.get("LOCAL_META_DIR"),
    ) -> None:
        from codes import StaticResources, BatchInfo

        self._infer = None
        self._static = StaticResources(feature_dir, meta_dir)
        self._batch_info = BatchInfo()

    def load_model(self, model_path):
        from codes import load_infer

        self._infer = load_infer(model_path)

    def preprocess(self, input_json: Dict) -> List:
        from codes import custom_preprocess

        self._batch_info.update(input_json)
        instances = custom_preprocess(
            input_json, self._static.features, self._static.hospital_meta
        )
        return instances

    def predict(self, input: Dict) -> Dict:             # input_api_schema 
        input_tensors = self.preprocess(input)          # tf.Tensor
        logging.debug(f"input_tensors: {input_tensors}")

        predictions = self._infer(inputs=input_tensors) # {'outputs':tf.Tensor}
        logging.info(f"predictions: {predictions}")

        results = self.postprocess(predictions)         # output_api_schema
        logging.info(f"results: {results}")

        return results

    def postprocess(self, data) -> Dict:
        from codes import custom_postprocess

        return custom_postprocess(data, self._batch_info)


if __name__ == "__main__":
    import json

    with open(os.environ.get("LOCAL_INPUT_SCHEMA"), "r") as f:
        data = json.load(f)

    predictor = CustomPredictor()
    predictor.load_model(os.environ.get("LOCAL_MODEL_DIR"))
    predictor.predict(data)
