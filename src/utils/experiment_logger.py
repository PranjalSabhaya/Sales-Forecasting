"""
Lightweight CSV-based experiment tracking for offline model training.
Logs model details, metrics, features, and timestamps for reproducibility.

"""


import csv
from pathlib import Path
from datetime import datetime


# Path to experiment log file
EXPERIMENT_LOG_PATH = Path("experiments/experiment_log.csv")


def initialize_log():

    if not EXPERIMENT_LOG_PATH.exists():
        EXPERIMENT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

        with open(EXPERIMENT_LOG_PATH, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp",
                "model_name",
                "horizon",
                "features",
                "mae",
                "rmse",
                "notes"
            ])


def log_experiment(
    model_name: str,
    horizon: int,
    features: list,
    mae: float,
    rmse: float,
    notes: str = ""
):

    initialize_log()

    with open(EXPERIMENT_LOG_PATH, mode="a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.utcnow().isoformat(),
            model_name,
            horizon,
            "|".join(features),
            round(float(mae), 4),
            round(float(rmse), 4),
            notes
        ])
