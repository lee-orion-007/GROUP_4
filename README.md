# Garbage Detection System

This repo contains:
- backend: FastAPI app that loads `garbage_cnn_model.h5` and exposes `/health` and `/predict`.
- mobile: React Native (Expo) app that uploads images to the backend for prediction.

Place your trained `garbage_cnn_model.h5` into `backend/app/models/` and update `classes.json` if needed(I already provided it in this same directory).

See `backend/README.md` and `mobile/README.md` for run instructions.
# GROUP_4
