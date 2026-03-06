import pandas as pd
from pathlib import Path

DATA_PATH = Path("data/backend/sales_history.parquet")

sales_df = None


def load_sales_data():
    global sales_df
    if sales_df is None:
        if not DATA_PATH.exists():
            raise FileNotFoundError("Sales history file not found.")
        sales_df = pd.read_parquet(DATA_PATH)
    return sales_df


def get_sales_history(store_id: str, item_id: str):

    df = load_sales_data()

    history = df[
        (df["store_id"] == store_id) &
        (df["item_id"] == item_id)
    ].sort_values("date")

    if history.empty:
        raise ValueError("No history found for given store/item.")

    return history["sales"].tolist()
