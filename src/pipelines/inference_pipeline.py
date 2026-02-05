import joblib
from pathlib import Path
import pandas as pd

from src.pipelines.data_ingestion import load_raw_data
from src.pipelines.feature_engineering import (
    build_sales_long,
    build_features
)


MODEL_PATH = Path("models/lightgbm/model.pkl")

FEATURES = [
    "lag_7", "lag_14", "lag_28",
    "rmean_7", "rmean_14", "rmean_28",
    "wday", "month", "year",
    "is_event"
]


def run_inference(
    raw_data_dir: str = "data/raw",
    output_path: str = "data/predictions/forecast.csv"
):
    """
    Run inference using pre-trained LightGBM model.
    """

    sales_df, calendar_df, _ = load_raw_data(raw_data_dir)

    sales_long = build_sales_long(sales_df, calendar_df)
    fe_df = build_features(sales_long)

    model = joblib.load(MODEL_PATH)

    X = fe_df[FEATURES]
    fe_df["prediction"] = model.predict(X)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fe_df.to_csv(output_path, index=False)

    print(f"Predictions saved to: {output_path}")

    return fe_df
