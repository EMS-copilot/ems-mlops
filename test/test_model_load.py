import os
import tensorflow as tf

def test_load_model(path = 'local_model_assets/predict/001'):
    import struct2tensor.ops.gen_decode_proto_sparse

    try:
        tf.saved_model.load(path)
    except Exception as e:
        print(f'ERROR Load Model: {e}')

if __name__ == '__main__':
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

    test_load_model()