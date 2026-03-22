import pandas as pd

from src.utils.paths import get_path
from src.utils.logging import get_logger

logger = get_logger(__name__)


def build_master_dataset() -> None:
    """
    Build a master analytical dataset.

    In the initial version, the master dataset equals the cleaned Rosstat dataset.
    Later it can be extended with income, population, CPI, and payment indicators.
    """
    input_file = get_path("interim_data") / "rosstat_share_online_clean.csv"
    output_dir = get_path("processed_data")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "master_dataset.csv"

    if not input_file.exists():
        logger.warning("Input file not found: %s", input_file)
        return

    df = pd.read_csv(input_file)
    df.to_csv(output_file, index=False, encoding="utf-8-sig")
    logger.info("Saved master dataset: %s", output_file)