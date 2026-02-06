import joblib
from pathlib import Path
import pandas as pd

from src.utils.config_loader import load_config
from src.pipelines.data_ingestion import load_raw_data
from src.pipelines.feature_engineering import (
    build_sales_long,
    build_features
)


def run_inference(config_path: str):
    config = load_config(config_path)

    raw_data_dir = config["data"]["raw_dir"]
    output_path = config["data"]["prediction_output"]
    model_path = config["model"]["model_path"]
    features = config["features"]

    sales_df, calendar_df, _ = load_raw_data(raw_data_dir)

    sales_long = build_sales_long(sales_df, calendar_df)
    fe_df = build_features(sales_long)

    model = joblib.load(model_path)

    fe_df["prediction"] = model.predict(fe_df[features])

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fe_df.to_csv(output_path, index=False)

    return fe_df

