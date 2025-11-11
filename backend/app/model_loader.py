"""
Model loader utility - loads the Keras model once and reads class mapping.
Also provides a prediction function returning human-readable class names.
"""
import os
import json
import time
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image

# Paths
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "garbage_cnn_model.h5")
CLASSES_PATH = os.path.join(os.path.dirname(__file__), "models", "classes.json")

_model = None
_class_names = None


def load_model_and_classes(model_path: str = None, classes_path: str = None):
    """
    Loads the trained Keras model and its class name mapping (from classes.json).
    """
    global _model, _class_names
    mp = model_path or MODEL_PATH
    cp = classes_path or CLASSES_PATH

    if _model is not None:
        return _model, _class_names

    if not os.path.exists(mp):
        raise FileNotFoundError(f"Model file not found at {mp}. Place your model at this path.")

    # Load the Keras model
    _model = tf.keras.models.load_model(mp)

    # Load class mapping (if exists)
    if os.path.exists(cp):
        with open(cp, "r") as f:
            try:
                _class_names = json.load(f)
            except Exception:
                _class_names = None

    # Fallback if no JSON found
    if _class_names is None:
        out_shape = _model.output_shape
        num_classes = out_shape[-1] if out_shape else 1
        _class_names = {str(i): f"Class {i}" for i in range(num_classes)}

    return _model, _class_names


def get_input_shape():
    """
    Returns the model's expected input shape as a tuple (height, width, channels)
    """
    global _model
    if _model is None:
        load_model_and_classes()
    shape = _model.input_shape
    if isinstance(shape, tuple):
        if len(shape) == 4:
            return tuple(shape[1:])
        elif len(shape) == 3:
            return tuple(shape)
    return (224, 224, 3)


def predict_image(img_path: str):
    """
    Runs a prediction on an image and returns the readable label and confidence.
    """
    global _model, _class_names
    if _model is None or _class_names is None:
        load_model_and_classes()

    # Get input size
    height, width, _ = get_input_shape()

    # Preprocess the image
    img = image.load_img(img_path, target_size=(height, width))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    start_time = time.time()

    # Make prediction
    predictions = _model.predict(img_array)
    latency = (time.time() - start_time) * 1000  # in ms

    # Process results
    probs = predictions[0]
    top_indices = probs.argsort()[-3:][::-1]

    # Map indices to class names
    top_results = []
    for i in top_indices:
        class_name = _class_names.get(str(i), f"Class {i}")
        confidence = float(probs[i]) * 100
        top_results.append((class_name, confidence))

    # Get best prediction
    best_idx = int(np.argmax(probs))
    predicted_label = _class_names.get(str(best_idx), f"Class {best_idx}")
    confidence = float(probs[best_idx]) * 100

    # Return structured result
    return {
        "prediction": predicted_label,
        "confidence": float(probs[best_idx]),  # Return as decimal (0.0-1.0) instead of string
        "latency": latency / 1000.0,  # Return latency in seconds instead of ms
        "top_k": [{"class": label, "confidence": float(conf) / 100.0} for label, conf in top_results]
    }
