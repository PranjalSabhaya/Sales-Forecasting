import pandas as pd
from pathlib import Path


def load_raw_data(data_dir: str = "data/raw"):

    data_dir = Path(data_dir)

    sales_df = pd.read_csv(
        data_dir / "sales_train_validation.csv"
    )

    calendar_df = pd.read_csv(
        data_dir / "calendar.csv"
    )

    prices_df = pd.read_csv(
        data_dir / "sell_prices.csv"
    )

    return sales_df, calendar_df, prices_df
