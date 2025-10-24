import tensorflow as tf
import logging

def load_model(path):
    import struct2tensor.ops.gen_decode_proto_sparse

    try:
        model = tf.saved_model.load(path)
        return model
    except Exception as e:
        logging.error(f"model load fail:{e}")


def load_infer(path):
    try:
        return load_model(path).signatures["serving_default"]
    except Exception as e:
        logging.error(f"signiture load fail:{e}")
