import os
from pathlib import Path
import gdown
import pandas as pd


def download_file(url: str, output_path: str):
    """
    Download file from Google Drive safely.
    Skips download if file already exists.
    """

    output_path = Path(output_path)

    # ✅ Skip if already exists (IMPORTANT FIX)
    if output_path.exists():
        print(f"✅ File already exists, skipping download: {output_path}")
        return

    print(f"⬇️ Downloading from Google Drive...")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # ✅ Handles large files + Drive warnings
    gdown.download(url, str(output_path), quiet=False, fuzzy=True)

    # 🔍 Validate size (avoid HTML download)
    size = os.path.getsize(output_path)
    print(f"📦 Downloaded file size: {size / (1024 * 1024):.2f} MB")

    if size < 1_000_000:
        raise ValueError("❌ File too small → likely invalid download")

    print(f"✅ Download successful: {output_path}")


def validate_parquet(file_path: str):
    """
    Validate parquet file integrity
    """
    try:
        df = pd.read_parquet(file_path)
        print(f"✅ Parquet validation successful. Rows: {len(df)}")

    except Exception as e:
        raise ValueError(f"❌ Invalid parquet file: {file_path}\nError: {e}")