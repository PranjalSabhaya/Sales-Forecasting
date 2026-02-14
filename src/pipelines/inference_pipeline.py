import joblib
import pandas as pd
from pathlib import Path

from src.utils.config_loader import load_config
from src.utils.data_validation import run_data_validation


def run_inference(config_path: str):

    config = load_config(config_path)

    feature_path = config["data"]["feature_path"]
    output_path = config["data"]["prediction_output"]
    model_path = config["model"]["model_path"]
    features = config["features"]
    horizon = config.get("horizon", 28)

    # --------------------------------------------------
    # Load processed feature data
    # --------------------------------------------------

    if not Path(feature_path).exists():
        raise FileNotFoundError(
            "Feature file not found. Run feature engineering first."
        )

    df = pd.read_csv(
        feature_path,
        parse_dates=["date"]
    )

    print("Loaded feature dataset:", df.shape)

    if df.empty:
        raise ValueError("Feature dataset is empty.")

    # Optional validation
    run_data_validation(df)

    # --------------------------------------------------
    # Select last horizon rows per group
    # --------------------------------------------------

    df = df.sort_values(["store_id", "item_id", "date"])

    df["rank"] = (
        df.groupby(["store_id", "item_id"])["date"]
        .rank(method="first", ascending=True)
    )

    df["max_rank"] = (
        df.groupby(["store_id", "item_id"])["rank"]
        .transform("max")
    )

    inference_df = df[df["rank"] > df["max_rank"] - horizon].copy()

    print("Inference dataset shape:", inference_df.shape)

    # --------------------------------------------------
    # Load model
    # --------------------------------------------------

    model = joblib.load(model_path)

    # --------------------------------------------------
    # Predict
    # --------------------------------------------------

    inference_df["prediction"] = model.predict(
        inference_df[features]
    )

    # --------------------------------------------------
    # Save predictions
    # --------------------------------------------------

    Path(output_path).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    inference_df.to_csv(
        output_path,
        index=False
    )

    print("✅ Predictions saved to:", output_path)

    return inference_df
