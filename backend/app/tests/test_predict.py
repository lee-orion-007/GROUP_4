import os
import io
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert "status" in r.json()

@pytest.mark.parametrize("img_path", [
    "tests/sample_images/sample.jpg",
])
def test_predict_endpoint(img_path):
    # file must exist for the test to run
    p = os.path.join(os.path.dirname(__file__), img_path.replace("tests/", ""))
    # adapt path
    p = os.path.join(os.path.dirname(__file__), os.path.basename(img_path))
    assert os.path.exists(p), f"Place a sample test image at {p}"
    with open(p, "rb") as f:
        files = {"file": ("sample.jpg", f, "image/jpeg")}
        r = client.post("/predict", files=files)
    assert r.status_code == 200, r.text
    j = r.json()
    assert "prediction" in j
    assert "confidence" in j
    assert "top_k" in j
