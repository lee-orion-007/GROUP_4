from pydantic import BaseModel
from typing import List, Dict

class TopKItem(BaseModel):
    class_name: str
    confidence: float

class PredictResponse(BaseModel):
    prediction: str
    class_id: int
    confidence: float
    top_k: List[Dict[str, float]]
    latency: float
