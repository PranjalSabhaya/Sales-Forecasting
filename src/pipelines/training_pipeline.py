
"""
Training Pipeline (Offline)

NOTE:
-----
The final LightGBM model used in production was trained during
the experimentation phase (notebooks).

This pipeline exists to:
- Document the training process
- Enable reproducibility if retraining is required
- Ensure feature parity with inference

It is NOT executed during deployment.
"""


import json
import joblib
from pathlib import Path

from lightgbm import LGBMRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

from src.pipelines.data_ingestion import load_raw_data
from src.pipelines.feature_engineering import (
    build_sales_long,
    build_features
)


FEATURES = [
    "lag_7", "lag_14", "lag_28",
    "rmean_7", "rmean_14", "rmean_28",
    "wday", "month", "year",
    "is_event"
]

HORIZON = 28
MODEL_DIR = Path("models/lightgbm")


def evaluate(y_true, y_pred):
    return {
        "MAE": mean_absolute_error(y_true, y_pred),
        "RMSE": mean_squared_error(y_true, y_pred, squared=False)
    }

def train_model(
    raw_data_dir: str = "data/raw",
    overwrite: bool = False
):
    """
    Optional offline training function.

    WARNING:
    --------
    This function retrains the model and overwrites the
    existing model artifact if overwrite=True.
    """

    if MODEL_DIR.exists() and not overwrite:
        raise RuntimeError(
            "Model already exists. Set overwrite=True to retrain."
        )

    # Load raw data
    sales_df, calendar_df, _ = load_raw_data(raw_data_dir)

    # Feature engineering
    sales_long = build_sales_long(sales_df, calendar_df)
    fe_df = build_features(sales_long)

    # Time-aware split
    train_df = fe_df.groupby(["store_id", "item_id"]).head(-HORIZON)
    valid_df = fe_df.groupby(["store_id", "item_id"]).tail(HORIZON)

    X_train = train_df[FEATURES]
    y_train = train_df["sales"]

    X_valid = valid_df[FEATURES]
    y_valid = valid_df["sales"]

    # Train LightGBM
    model = LGBMRegressor(
        num_leaves=63,
        n_estimators=400,
        min_child_samples=50,
        max_depth=8,
        learning_rate=0.01,
        lambda_l2=5,
        lambda_l1=1,
        feature_fraction=1.0,
        bagging_freq=1,
        bagging_fraction=0.6,
        objective="regression",
        eval_metric="l1",
        random_state=42,
        n_jobs=1)


    model.fit(X_train, y_train)

    # Evaluate
    preds = model.predict(X_valid)
    metrics = evaluate(y_valid, preds)

    # Save artifacts
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, MODEL_DIR / "model.pkl")

    with open(MODEL_DIR / "metadata.json", "w") as f:
        json.dump({
            "model": "LightGBM",
            "metrics": metrics,
            "features": FEATURES,
            "horizon": HORIZON
        }, f, indent=4)

    return model, metrics

