import pandas as pd 

REQUIRED_COLUMNS = [
    "item_id",
    "store_id",
    "date",
    "sales"
]


def validate_schema(df: pd.DataFrame):
    missing_cols = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing_cols:
        raise ValueError(
            f"Missing required columns: {missing_cols}"
        )

def validate_nulls(df: pd.DataFrame):
    null_counts = df[REQUIRED_COLUMNS].isna().sum()
    if null_counts.any():
        raise ValueError(
            f"Null values found:\n{null_counts}"
        )

def validate_sales_values(df: pd.DataFrame):
    if (df["sales"] < 0).any():
        raise ValueError("Negative sales values detected")

def warn_sales_drift(df: pd.DataFrame, reference_mean: float = 1.0):
    current_mean = df["sales"].mean()

    if current_mean > reference_mean * 3:
        print(
            "Warning: Sales mean is significantly higher than expected "
            f"({current_mean:.2f} vs reference {reference_mean})"
        )

def run_data_validation(df: pd.DataFrame):

    validate_schema(df)
    validate_nulls(df)
    validate_sales_values(df)
    warn_sales_drift(df)

    print("Data validation passed")
