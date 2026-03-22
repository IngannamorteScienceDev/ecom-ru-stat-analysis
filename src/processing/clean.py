from pathlib import Path
import pandas as pd

from src.utils.paths import get_path
from src.utils.logging import get_logger, print_info, print_success, print_warning

logger = get_logger(__name__)


def clean_main_dataset() -> None:
    """
    Clean the main Rosstat-based dataset.
    """
    raw_file = get_path("raw_data") / "rosstat_share_online_raw.csv"
    interim_dir = get_path("interim_data")
    interim_dir.mkdir(parents=True, exist_ok=True)
    output_file = interim_dir / "rosstat_share_online_clean.csv"

    print_info("Starting cleaning of the main Rosstat dataset.")

    if not raw_file.exists():
        logger.warning("Raw dataset not found: %s", raw_file)
        print_warning(f"Raw dataset not found: {raw_file}")
        return

    df = pd.read_csv(raw_file)
    df.columns = [col.strip().lower() for col in df.columns]

    if "year" not in df.columns or "share_online" not in df.columns:
        raise ValueError("Dataset must contain 'year' and 'share_online' columns.")

    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["share_online"] = pd.to_numeric(df["share_online"], errors="coerce")

    df = (
        df.dropna(subset=["year", "share_online"])
        .drop_duplicates(subset=["year"])
        .sort_values("year")
        .reset_index(drop=True)
    )

    df.to_csv(output_file, index=False, encoding="utf-8-sig")
    logger.info("Saved cleaned dataset: %s", output_file)
    print_success(f"Saved cleaned dataset: {output_file}")
    print_info(f"Clean dataset shape: {df.shape}")