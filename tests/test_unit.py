import os
import json

import pytest

from src.predictor import CustomPredictor
from src.backend import LocalBackend


@pytest.fixture(scope="module")
def predictor():
    pred = CustomPredictor(
        os.getenv("LOCAL_FEATURE_FILE"),
        os.getenv("LOCAL_META_FILE"),
        LocalBackend,
    )
    pred.load(os.getenv("LOCAL_MODEL_DIR"))
    return pred


@pytest.fixture
def input_data():
    with open("data/input_api_schema.json", "r") as f:
        return json.load(f)


def test_model_load(predictor):
    assert all(v is not None for v in [predictor._model, predictor._input_key])


def test_pipeline_steps(predictor, input_data):
    for instance in input_data["instances"]:
        pre = predictor.preprocess(instance)
        infer = predictor.infer(pre)
        post = predictor.postprocess(infer)
        assert isinstance(post, dict)


def test_full_pipeline(predictor, input_data):
    for instance in input_data["instances"]:
        output = predictor.predict(instance)
        assert isinstance(output, dict)
