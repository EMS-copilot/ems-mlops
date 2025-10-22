import os
import json
import numpy as np
import tensorflow as tf
from typing import List, Any, Dict

class CustomPredictor():
    """Default Predictor implementation for Sklearn models."""

    def __init__(self):
        self._static = None
        self._batch = None
        return

    def load(self, model_dir: str) -> None:
        """Loads the model artifact.

        Args:
            artifacts_uri (str):
                Required. The value of the environment variable AIP_STORAGE_URI.

        Raises:
            ValueError: If there's no required model files provided in the artifacts
                uri.
        """
        
        from codes import StaticResource, BatchInfo
        self._static = StaticResource(model_dir)
        self._batch = BatchInfo([])

    def preprocess(self, prediction_input: dict) -> np.ndarray:
        from codes.preprocess import custom_preprocess

        instances, self._batch.index = custom_preprocess(prediction_input, self._static.hospital_meta)
        return np.asarray(instances)

    def predict(self, instances: np.ndarray) -> np.ndarray:
        """Performs prediction.

        Args:
            instances (np.ndarray):
                Required. The instance(s) used for performing prediction.

        Returns:
            Prediction results.
        """
        return self._model.predict(instances)

    def postprocess(self, prediction_results: np.ndarray) -> dict:
        """Converts numpy array to a dict.
        Args:
            prediction_results (np.ndarray):
                Required. The prediction results.
        Returns:
            The postprocessed prediction results.
        """
        return {"predictions": prediction_results.tolist()}