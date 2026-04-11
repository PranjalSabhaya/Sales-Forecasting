import os
from pathlib import Path
import gdown
import pandas as pd


def download_file(url: str, output_path: str):
    """
    Download file from Google Drive safely.
    Handles large files + virus warning page using gdown.
    """

    output_path = Path(output_path)

    # 🔥 Remove existing (possibly corrupted) file
    if output_path.exists():
        print(f"⚠️ Removing existing file: {output_path}")
        output_path.unlink()

    print(f"⬇️ Downloading from Google Drive...")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # ✅ CRITICAL: fuzzy=True handles Drive links properly
    gdown.download(url, str(output_path), quiet=False, fuzzy=True)

    # 🔍 Basic size validation (avoid HTML download)
    size = os.path.getsize(output_path)

    print(f"📦 Downloaded file size: {size / (1024 * 1024):.2f} MB")

    if size < 1_000_000:  # <1MB → definitely wrong file
        raise ValueError(
            "❌ Downloaded file is too small → likely HTML, not actual data."
        )

    print(f"✅ Download successful: {output_path}")


def validate_parquet(file_path: str):
    """
    Validate parquet file integrity before usage.
    """

    try:
        df = pd.read_parquet(file_path)
        print(f"✅ Parquet validation successful. Rows: {len(df)}")

    except Exception as e:
        raise ValueError(
            f"❌ Invalid parquet file: {file_path}\nError: {e}"
        )