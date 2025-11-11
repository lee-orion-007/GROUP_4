"""
FastAPI app for serving the garbage detection model.
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time
import tempfile
import os

from .model_loader import load_model_and_classes, get_input_shape, predict_image
from .utils import validate_image_file, now_iso

app = FastAPI(title="Garbage Detection API", version="1.0")

# Allow CORS for development (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

# Globals
MODEL = None
CLASS_NAMES = None
INPUT_SHAPE = (224, 224, 3)


@app.on_event("startup")
def startup_event():
    """
    Load the model and class names on API startup.
    """
    global MODEL, CLASS_NAMES, INPUT_SHAPE
    MODEL, CLASS_NAMES = load_model_and_classes()
    INPUT_SHAPE = get_input_shape()
    try:
        import tensorflow as _tf
        framework = "keras" if isinstance(MODEL, _tf.keras.Model) else "unknown"
    except Exception:
        framework = "unknown"
    print(f"[INFO] Loaded {framework} model with {len(CLASS_NAMES)} classes.")


@app.get("/health")
def health():
    """
    Health check endpoint.
    """
    return {"status": "ok", "time": now_iso()}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """
    Accepts an uploaded image file, runs prediction using the CNN model,
    and returns the predicted garbage type with confidence.
    """
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    try:
        validate_image_file(file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image too large (max 5MB).")

    # Save temp file for prediction
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        # Run prediction
        result = predict_image(tmp_path)
        os.remove(tmp_path)

        return JSONResponse(content=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.get("/")
def root():
    return {"message": "Garbage Detection API. Use /predict to get predictions or /docs for Swagger UI."}
