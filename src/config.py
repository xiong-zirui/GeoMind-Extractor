import yaml
from pathlib import Path

def load_config():
    """Loads the configuration from config.yml."""
    config_path = Path(__file__).parent.parent / "config.yml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config

config = load_config()
