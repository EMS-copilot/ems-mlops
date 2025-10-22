import tensorflow as tf
import pandas as pd
from typing import List, Any, Dict

class CustomPredictor():
    def __init__(self, model_dir: str, meta_dir:str = None) -> None:
        from codes import StaticResource, BatchInfo
        self._static = StaticResource(model_dir, meta_dir)
        self._batch = BatchInfo([])

    def preprocess(self, prediction_input: dict) -> list:
        from codes.preprocess import custom_preprocess

        instances, self._batch.index = custom_preprocess(prediction_input, self._static.hospital_meta)
        return instances

    def predict(self, instances:list):
        import logging
        infer = self._static.model.signatures["serving_default"]
        input_df = pd.DataFrame(instances)
        logging.info(f"Input DataFrame for prediction: {input_df}")
        input_tensors = {
            name: tf.constant(input_df[name].values, dtype=tf.string if input_df[name].dtype == 'object' else tf.float32)
            for name in input_df.columns
        }
        logging.info(f"Input tensors for model inference: {input_tensors}")
        predictions = infer(**input_tensors)
        return predictions

    def postprocess(self, prediction_results) -> dict:

        return {"predictions": prediction_results.tolist()}