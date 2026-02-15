import pandas as pd
from app.core.model_loader import load_model
from app.services.feature_builder import build_features_from_raw


FEATURES = [
    "lag_7", "lag_14", "lag_28",
    "rmean_7", "rmean_14", "rmean_28",
    "wday", "month", "year",
    "is_event"
]


def make_prediction(raw_data: dict):

    model = load_model()

    feature_dict = build_features_from_raw(raw_data)

    df = pd.DataFrame([feature_dict])

    prediction = model.predict(df[FEATURES])[0]

    return float(prediction)
