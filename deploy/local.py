import os
from google.cloud.aiplatform.prediction import LocalModel

ENV_VARS_DICT = {
    "AIP_FEATURE_DIR": os.getenv('AIP_FEATURE_DIR'),
    "AIP_META_DIR": os.getenv('AIP_META_DIR'),
}

def get_local_cpr_model():
    try:
        from src.predictor import CustomPredictor
    except ImportError:
        return None

    
    local_model = LocalModel.build_cpr_model(
        src_dir=".",
        output_image_uri=os.getenv("IMAGE_URI"),
        predictor=CustomPredictor,
        requirements_path="./requirements-routine.txt",
        base_image="python:3.9",
    )
    container_spec_pb = local_model.serving_container_spec._pb
    env_field_descriptor = container_spec_pb.DESCRIPTOR.fields_by_name["env"]
    EnvVar = env_field_descriptor.message_type._concrete_class
    local_model.serving_container_spec.env = [
        EnvVar(name=key, value=value) for key, value in ENV_VARS_DICT.items()
    ]
    return local_model

