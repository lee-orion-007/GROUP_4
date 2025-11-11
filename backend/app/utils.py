"""
Preprocessing & utility helpers used by the API.
"""
import io
import time
from PIL import Image
import numpy as np

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/jpg"}

def validate_image_file(upload_file) -> None:
    content_type = upload_file.content_type
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise ValueError("Invalid image type. Allowed: jpeg, jpg, png.")

def read_image_bytes(contents: bytes) -> Image.Image:
    return Image.open(io.BytesIO(contents))

def preprocess_pil_image(img: Image.Image, target_size=(224,224), rescale: bool = True):
    """
    Convert PIL image -> numpy array of shape (1, H, W, C), float32.
    Normalization uses scaling to [0,1] by default; adjust if your training pipeline differs.
    """
    img = img.convert("RGB")
    img = img.resize(target_size)
    arr = np.array(img).astype("float32")
    if rescale:
        arr = arr / 255.0
    arr = np.expand_dims(arr, axis=0)
    return arr

def now_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
