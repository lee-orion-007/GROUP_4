# Backend (FastAPI) - Garbage Detection

## Prereqs
- Python 3.10+
- pip
- (optional) Docker

## Setup (local)
1. Create virtual env:
   python -m venv venv
   source venv/bin/activate   # or venv\Scripts\activate on Windows
2. Install:
   pip install -r requirements.txt
3. Place your model:
   backend/app/models/garbage_cnn_model.h5(Already Placed)
   backend/app/models/classes.json (Already Placed)
4. Run:
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Open docs: http://localhost:8000/docs

## Run tests
From `backend` folder:
   pytest -q

## Docker
Build:
   docker build -t garbage-api:latest .
Run:
   docker run -p 8000:8000 -v $(pwd)/app/models:/app/models garbage-api:latest
