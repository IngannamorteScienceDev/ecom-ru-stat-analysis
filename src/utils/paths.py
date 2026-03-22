from pathlib import Path
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config" / "config.yaml"


def load_config() -> dict:
    """
    Load YAML configuration.
    """
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_path(key: str) -> Path:
    """
    Get a project path from config paths section.
    """
    config = load_config()
    rel_path = config["paths"][key]
    return PROJECT_ROOT / rel_path