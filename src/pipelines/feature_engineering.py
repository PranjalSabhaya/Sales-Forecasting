"""
Feature Engineering Pipeline (Production Version)

Purpose
-------
- Convert wide M5 sales data into long format
- Build lag and rolling features safely at scale
- Use chunk-based processing to avoid memory overflow
- Ensure store-item level feature consistency

This module is used by training and inference pipelines.
"""

import pandas as pd
from pathlib import Path


# ------------------------------------------------------
# 1️⃣ Wide → Long Transformation
# ------------------------------------------------------
def build_sales_long(
    sales_df: pd.DataFrame,
    calendar_df: pd.DataFrame,
    output_path: str = None
) -> pd.DataFrame:
    """
    Convert wide M5 format into long format.

    Optionally writes to CSV if output_path provided.
    """

    id_columns = [
        "id",
        "item_id",
        "dept_id",
        "cat_id",
        "store_id",
        "state_id"
    ]

    day_columns = [
        c for c in sales_df.columns if c.startswith("d_")
    ]

    sales_long = sales_df.melt(
        id_vars=id_columns,
        value_vars=day_columns,
        var_name="d",
        value_name="sales"
    )

    sales_long = sales_long.merge(
        calendar_df,
        how="left",
        on="d"
    )

    sales_long["date"] = pd.to_datetime(
        sales_long["date"]
    )

    if output_path:
        Path(output_path).parent.mkdir(
            parents=True,
            exist_ok=True
        )
        sales_long.to_csv(
            output_path,
            index=False
        )

    return sales_long


# ------------------------------------------------------
# 2️⃣ Chunk-Based Feature Engineering
# ------------------------------------------------------
def build_features_chunked(
    input_path: str,
    output_path: str,
    chunksize: int = 2_000_000
):


    use_cols = [
        "item_id",
        "store_id",
        "date",
        "sales",
        "wday",
        "month",
        "year",
        "event_name_1",
    ]

    history = {}
    first_write = True

    reader = pd.read_csv(
        input_path,
        usecols=use_cols,
        parse_dates=["date"],
        chunksize=chunksize,
    )

    for chunk in reader:

        # Ensure correct ordering
        chunk = chunk.sort_values(
            ["store_id", "item_id", "date"]
        )

        processed = []

        for (store_id, item_id), g in chunk.groupby(
            ["store_id", "item_id"]
        ):

            key = (store_id, item_id)

            # Prepend history from previous chunk
            if key in history:
                g = pd.concat([history[key], g])

            # Lag features
            for lag in [7, 14, 28]:
                g[f"lag_{lag}"] = g["sales"].shift(lag)

            # Rolling mean features
            for win in [7, 14, 28]:
                g[f"rmean_{win}"] = (
                    g["sales"]
                    .shift(1)
                    .rolling(win)
                    .mean()
                )

            # Keep last 28 rows for next chunk
            history[key] = g.tail(28)

            # Remove incomplete lag rows
            g = g.iloc[28:]

            processed.append(g)

        if not processed:
            continue

        chunk_fe = pd.concat(
            processed,
            ignore_index=True
        )

        # Event flag
        chunk_fe["is_event"] = (
            chunk_fe["event_name_1"]
            .notna()
            .astype("int8")
        )

        # Remove NaNs from lag/rolling
        chunk_fe = chunk_fe.dropna()

        # Write incrementally
        Path(output_path).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        chunk_fe.to_csv(
            output_path,
            mode="w" if first_write else "a",
            header=first_write,
            index=False,
        )

        first_write = False

    print("✅ Feature engineering completed successfully.")
