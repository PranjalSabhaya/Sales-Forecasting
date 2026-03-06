import joblib
from pathlib import Path

MODEL_PATH = Path(__file__).resolve().parent.parent.parent / "models/lightgbm/model.pkl"

model = None

def load_model():
    global model
    if model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError("Model file not found.")
        model = joblib.load(MODEL_PATH)
    return model

def get_model():
    return model