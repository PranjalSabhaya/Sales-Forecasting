import os
import requests
from pathlib import Path


def download_file(url: str, output_path: str):

    output_path = Path(output_path)

    if output_path.exists():
        print(f"File already exists: {output_path}")
        return

    print(f"Downloading {url}...")

    response = requests.get(url, stream=True,timeout=60)

    response.raise_for_status()

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"Downloaded: {output_path}")