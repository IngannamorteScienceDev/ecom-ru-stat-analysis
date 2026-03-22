from pathlib import Path
import pandas as pd

from src.utils.paths import get_path
from src.utils.logging import get_logger

logger = get_logger(__name__)


def collect_rosstat_stub() -> None:
    """
    Placeholder collector for Rosstat data.

    In the first project version, this function creates a template dataset
    that can later be replaced with real imported Rosstat XLS/XLSX files.
    """
    raw_dir = get_path("raw_data")
    raw_dir.mkdir(parents=True, exist_ok=True)

    output_file = raw_dir / "rosstat_share_online_template.csv"

    if output_file.exists():
        logger.info("Rosstat template already exists: %s", output_file)
        return

    df = pd.DataFrame(
        {
            "year": list(range(2014, 2026)),
            "share_online": [0.7, 0.9, 1.1, 1.3, 1.7, 2.0, 3.9, 4.8, 5.7, 6.4, 7.2, 8.0],
        }
    )
    df.to_csv(output_file, index=False, encoding="utf-8-sig")
    logger.info("Created Rosstat template dataset: %s", output_file)