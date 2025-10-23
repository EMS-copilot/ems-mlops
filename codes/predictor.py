import pandas as pd
from typing import List, Dict
import logging


class CustomPredictor:
    def __init__(
        self,
        feature_dir: str = "data/features.json",
        meta_dir: str = "data/hospital_meta.csv",
    ) -> None:
        from codes import StaticResources

        self._infer = None
        self._static = StaticResources(feature_dir, meta_dir)
        self.index = []
        self.method = {}

    def load_model(self, model_path):
        from codes import load_infer

        self._infer = load_infer(model_path)

    def preprocess(self, input_json: Dict) -> List:
        from codes import custom_preprocess, parse_batch_info

        self.index, self.method = parse_batch_info(input_json)
        instances = custom_preprocess(
            input_json, self._static.features, self._static.hospital_meta
        )
        return instances

    def predict(self, input: Dict):
        input_tensors = self.preprocess(input)
        logging.debug(f"Input tensors for model inference: {input_tensors}")

        predictions = self._infer(inputs=input_tensors)
        logging.info(f"result for model inference: {predictions}")

        return predictions

    def postprocess(self, prediction_results) -> Dict:
        return {"predictions": prediction_results.tolist()}

if __name__ == '__main__':
    import json

    with open("data/input_api_schema.json", "r") as f:    
        data = json.load(f)
    
    predictor = CustomPredictor()
    predictor.load_model('./local_model_assets/predict/001/')
    print(predictor.predict(data))