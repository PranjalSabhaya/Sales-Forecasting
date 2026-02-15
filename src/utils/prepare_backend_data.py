import pandas as pd

INPUT_PATH = "data/interim/sales_long.csv"
OUTPUT_PATH = "data/backend/sales_history.parquet"

df = pd.read_csv(
    INPUT_PATH,
    usecols=["store_id", "item_id", "date", "sales"],
    parse_dates=["date"]
)

df.to_parquet(OUTPUT_PATH, index=False)

print("Backend sales history prepared.")
