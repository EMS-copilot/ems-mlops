import os
import tensorflow as tf
import logging
def test_load_model(path = 'local_model_assets/predict/001'):
    try:
        tf.saved_model.load(path)
    except Exception as e:
        logging.error(f'ERROR Load Model: {e}')

if __name__ == '__main__':
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

    test_load_model()