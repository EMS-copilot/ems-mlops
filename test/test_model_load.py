import os
import logging


def test_load_model(path = 'local_model_assets/predict/001'):
    import tensorflow as tf
    import struct2tensor.ops.gen_decode_proto_sparse

    try:
        model = tf.saved_model.load(path)
        inference_func = model.signatures["serving_default"]

        return list(inference_func.structured_input_signature[1].keys())[0]
    except Exception as e:
        logging.error(f'ERROR Load Model: {e}')


if __name__ == '__main__':
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
    
    test_load_model()