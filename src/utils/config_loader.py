import yaml
from pathlib import Path


def load_config(config_path: str):
    """
    Load YAML configuration file.
    """
    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    return config
