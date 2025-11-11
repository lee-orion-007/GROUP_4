"""
Small debug utility to inspect the loaded Keras model, class mapping, and run  predictions
on one or more sample images. Prints model.summary(), input shape, and raw softmax
probabilities so we can see why one class might dominate.

Usage (from backend folder, with venv activated):
python app/debug_predict.py --images app/tests/sample_images/ --topk 6

Or test a single image:
python app/debug_predict.py --images path/to/image.jpg

This script deliberately prints raw float probabilities and mapping so you can inspect
ordering and preprocessing.
"""
import argparse
import os
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image

from app.model_loader import load_model_and_classes, get_input_shape


def load_img_array(img_path, target_size):
    img = image.load_img(img_path, target_size=target_size)
    arr = image.img_to_array(img) / 255.0
    arr = np.expand_dims(arr, axis=0)
    return arr


def main(args):
    # Load model and classes
    model, class_map = load_model_and_classes()

    print("Loaded model:")
    try:
        model.summary()
    except Exception as e:
        print(f"(model.summary() failed: {e})")

    print('\nModel input shape:', model.input_shape)
    print('Model output shape:', model.output_shape)

    print('\nClass mapping (from classes.json):')
    print(json.dumps(class_map, indent=2))

    # Resolve images
    img_paths = []
    for p in args.images:
        if os.path.isdir(p):
            for root, _, files in os.walk(p):
                for f in files:
                    if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                        img_paths.append(os.path.join(root, f))
        elif os.path.isfile(p):
            img_paths.append(p)
        else:
            print(f"Warning: path not found: {p}")

    if not img_paths:
        print("No images found to test. Provide a path or directory with images.")
        return

    target = get_input_shape()[:2]
    print('\nUsing target size (H, W):', target)

    for ip in img_paths[: args.limit]:
        arr = load_img_array(ip, target_size=target)
        preds = model.predict(arr)
        probs = preds[0]

        # If last layer isn't softmax, apply softmax for interpretability
        if probs.sum() < 0.99 or probs.sum() > 1.01:
            probs = tf.nn.softmax(probs).numpy()

        top_idx = np.argmax(probs)
        mapped = class_map.get(str(top_idx), f"Class {top_idx}")

        print('\n===', ip)
        print('argmax index:', int(top_idx), 'mapped:', mapped)
        print('raw probs:')
        for i, p in enumerate(probs):
            name = class_map.get(str(i), str(i))
            print(f"  {i} {name:12s}: {p:.6f}")

        # top-k
        k = args.topk
        order = (-probs).argsort()[:k]
        print('\nTop k:')
        for idx in order:
            print(f"  {class_map.get(str(idx),'?'):12s}: {probs[idx]:.6f}")


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--images', '-i', nargs='+', required=True,
                    help='Image file(s) or directories to test')
    ap.add_argument('--topk', type=int, default=3)
    ap.add_argument('--limit', type=int, default=10, help='Limit number of files to test')
    args = ap.parse_args()
    main(args)
