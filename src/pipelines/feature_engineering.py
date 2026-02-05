import pandas as pd 

def build_sales_long(
    sales_df: pd.DataFrame,
    calendar_df: pd.DataFrame
) -> pd.DataFrame:

    id_columns = [
        "id",
        "item_id",
        "dept_id",
        "cat_id",
        "store_id",
        "state_id"
    ]

    day_columns = [c for c in sales_df.columns if c.startswith("d_")]

    # Wide → long
    sales_long = sales_df.melt(
        id_vars=id_columns,
        value_vars=day_columns,
        var_name="d",
        value_name="sales"
    )

    # Merge calendar
    sales_long = sales_long.merge(
        calendar_df,
        how="left",
        on="d"
    )

    # Convert date
    sales_long["date"] = pd.to_datetime(sales_long["date"])

    return sales_long

def build_features(df: pd.DataFrame) -> pd.DataFrame:


    df["sales"] = df["sales"].astype("int16")
    df["wday"] = df["wday"].astype("int8")
    df["month"] = df["month"].astype("int8")
    df["year"] = df["year"].astype("int16")


    df = df.sort_values(
        ["store_id", "item_id", "date"]
    )

    group_cols = ["store_id", "item_id"]


    for lag in [7, 14, 28]:
        df[f"lag_{lag}"] = (
            df.groupby(group_cols)["sales"]
              .shift(lag)
        )


    for win in [7, 14, 28]:
        df[f"rmean_{win}"] = (
            df.groupby(group_cols)["sales"]
              .shift(1)
              .rolling(win)
              .mean()
        )

    df["is_event"] = df["event_name_1"].notna().astype("int8")

    df = df.dropna().reset_index(drop=True)

    return df
