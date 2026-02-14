"""
Training Pipeline (Offline - Production Grade)

This pipeline:
- Assumes feature engineering is already completed
- Reads processed feature CSV
- Performs time-aware split (vectorized)
- Trains final LightGBM model with early stopping
- Saves artifacts
- Logs experiment

Feature engineering must be run BEFORE this.
"""

import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path

from lightgbm import LGBMRegressor
from lightgbm import early_stopping, log_evaluation
from sklearn.metrics import mean_absolute_error, mean_squared_error

from src.utils.experiment_logger import log_experiment


# --------------------------------------------------
# Configuration
# --------------------------------------------------

FEATURES = [
    "lag_7", "lag_14", "lag_28",
    "rmean_7", "rmean_14", "rmean_28",
    "wday", "month", "year",
    "is_event"
]

HORIZON = 28
MODEL_DIR = Path("models/lightgbm")
MODEL_PATH = MODEL_DIR / "model.pkl"
FEATURE_DATA_PATH = Path("data/processed/train_fe.csv")


# --------------------------------------------------
# Evaluation
# --------------------------------------------------

def evaluate(y_true, y_pred):
    return {
        "MAE": mean_absolute_error(y_true, y_pred),
        "RMSE": np.sqrt(mean_squared_error(y_true, y_pred))
    }


# --------------------------------------------------
# Training Function
# --------------------------------------------------

def train_model(overwrite: bool = False):

    if not FEATURE_DATA_PATH.exists():
        raise FileNotFoundError(
            "Feature file not found. Run feature engineering first."
        )

    if MODEL_PATH.exists() and not overwrite:
        raise RuntimeError(
            f"Model already exists at {MODEL_PATH}. "
            "Set overwrite=True to retrain."
        )

    print("🚀 Starting offline training pipeline...")

    # --------------------------------------------------
    # Load feature-engineered data
    # --------------------------------------------------

    df = pd.read_csv(
        FEATURE_DATA_PATH,
        parse_dates=["date"]
    )

    print("Feature DataFrame shape:", df.shape)

    if df.empty:
        raise ValueError("Feature dataset is empty.")

    # Ensure correct ordering
    df = df.sort_values(["store_id", "item_id", "date"])

    # --------------------------------------------------
    # Vectorized Time-aware split
    # --------------------------------------------------

    df["rank"] = (
        df.groupby(["store_id", "item_id"])["date"]
        .rank(method="first", ascending=True)
    )

    df["max_rank"] = (
        df.groupby(["store_id", "item_id"])["rank"]
        .transform("max")
    )

    train_df = df[df["rank"] <= df["max_rank"] - HORIZON]
    valid_df = df[df["rank"] > df["max_rank"] - HORIZON]

    if train_df.empty:
        raise ValueError("Training dataset is empty after split.")

    print("📊 Train shape:", train_df.shape)
    print("📊 Valid shape:", valid_df.shape)

    X_train = train_df[FEATURES]
    y_train = train_df["sales"]

    X_valid = valid_df[FEATURES]
    y_valid = valid_df["sales"]

    # --------------------------------------------------
    # Train LightGBM with Early Stopping
    # --------------------------------------------------

    model = LGBMRegressor(
        num_leaves=63,
        n_estimators=2000,  # large upper bound
        min_child_samples=50,
        max_depth=8,
        learning_rate=0.01,
        lambda_l2=5,
        lambda_l1=1,
        feature_fraction=1.0,
        bagging_freq=1,
        bagging_fraction=0.6,
        objective="regression",
        random_state=42,
        n_jobs=-1
    )

    model.fit(
        X_train,
        y_train,
        eval_set=[(X_valid, y_valid)],
        eval_metric="l1",
        callbacks=[
        early_stopping(stopping_rounds=100),
        log_evaluation(period=100)]
    )

    # --------------------------------------------------
    # Evaluate
    # --------------------------------------------------

    preds = model.predict(X_valid)
    metrics = evaluate(y_valid, preds)

    print("📈 Validation Metrics:", metrics)

    # --------------------------------------------------
    # Save model
    # --------------------------------------------------

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    metadata = {
        "model": "LightGBM",
        "best_iteration": model.best_iteration_,
        "features": FEATURES,
        "horizon": HORIZON,
        "metrics": metrics
    }

    with open(MODEL_DIR / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=4)

    # --------------------------------------------------
    # Save Feature Importance
    # --------------------------------------------------

    importance_df = pd.DataFrame({
        "feature": FEATURES,
        "importance": model.feature_importances_
    }).sort_values("importance", ascending=False)

    importance_df.to_csv(
        MODEL_DIR / "feature_importance.csv",
        index=False
    )

    # --------------------------------------------------
    # Log experiment
    # --------------------------------------------------

    log_experiment(
        model_name="LightGBM",
        horizon=HORIZON,
        features=FEATURES,
        mae=metrics["MAE"],
        rmse=metrics["RMSE"],
        notes="Offline training pipeline with early stopping"
    )

    print("✅ Model saved, feature importance stored, experiment logged.")

    return model, metrics
