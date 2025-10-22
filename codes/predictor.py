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
        INPUT_FEATURES = [
            'age', 'sex', 'triage_level', 'symptom', 'bp_systolic', 'hr', 'icu_beds', 
            'er_beds', 'specialist_oncall', 'hospital_capacity', 'hospital_area', 
            'is_24h', 'is_regional_center', 'has_er', 'distance_km', 'eta_minutes'
        ]
        input_tensors = {}
        for feature in INPUT_FEATURES:
                if feature not in input_df.columns:
                    print(f"error missing '{feature}'")
                    continue
                    
                series = input_df[feature]
                
                tensor = tf.constant(series.values.astype(str), dtype=tf.string)
                input_tensors[feature] = tensor

                
        logging.info(f"Input tensors for model inference: {input_tensors}")
        predictions = infer(**input_tensors)
        return predictions

    def postprocess(self, prediction_results) -> dict:

        return {"predictions": prediction_results.tolist()}