import pandas as pd

from src.utils.paths import get_path
from src.utils.logging import get_logger, print_info, print_success, print_warning

logger = get_logger(__name__)


def _clean_rf_dataset() -> None:
    """
    Clean Russian Federation time series dataset.
    """
    raw_file = get_path("raw_data") / "rosstat_share_online_rf_raw.csv"
    interim_dir = get_path("interim_data")
    interim_dir.mkdir(parents=True, exist_ok=True)
    output_file = interim_dir / "rosstat_share_online_rf_clean.csv"

    if not raw_file.exists():
        print_warning(f"RF raw dataset not found: {raw_file}")
        return

    df = pd.read_csv(raw_file)
    df.columns = [col.strip().lower() for col in df.columns]
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["share_online"] = pd.to_numeric(df["share_online"], errors="coerce")

    df = (
        df.dropna(subset=["year", "share_online"])
        .drop_duplicates(subset=["year"])
        .sort_values("year")
        .reset_index(drop=True)
    )

    df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print_success(f"Saved cleaned RF dataset: {output_file}")


def _clean_regions_dataset() -> None:
    """
    Clean regional long-format dataset.
    """
    raw_file = get_path("raw_data") / "rosstat_share_online_regions_raw.csv"
    interim_dir = get_path("interim_data")
    interim_dir.mkdir(parents=True, exist_ok=True)
    output_file = interim_dir / "rosstat_share_online_regions_clean.csv"

    if not raw_file.exists():
        print_warning(f"Regional raw dataset not found: {raw_file}")
        return

    df = pd.read_csv(raw_file)
    df.columns = [col.strip().lower() for col in df.columns]

    df["region"] = df["region"].astype(str).str.strip()
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["share_online"] = pd.to_numeric(df["share_online"], errors="coerce")

    df = (
        df.dropna(subset=["region", "year", "share_online"])
        .drop_duplicates(subset=["region", "year"])
        .sort_values(["region", "year"])
        .reset_index(drop=True)
    )

    df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print_success(f"Saved cleaned regional dataset: {output_file}")


def clean_main_dataset() -> None:
    """
    Clean all Rosstat datasets used in the project.
    """
    print_info("Starting cleaning of Rosstat RF and regional datasets.")
    _clean_rf_dataset()
    _clean_regions_dataset()