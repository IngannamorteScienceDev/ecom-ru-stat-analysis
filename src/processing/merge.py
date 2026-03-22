import pandas as pd

from src.utils.paths import get_path
from src.utils.logging import print_info, print_success, print_warning


def build_master_dataset() -> None:
    """
    Build master processed datasets for RF and regions.
    """
    processed_dir = get_path("processed_data")
    processed_dir.mkdir(parents=True, exist_ok=True)

    rf_input = get_path("interim_data") / "rosstat_share_online_rf_clean.csv"
    rf_output = processed_dir / "master_rf_dataset.csv"

    regions_input = get_path("interim_data") / "rosstat_share_online_regions_clean.csv"
    regions_output = processed_dir / "master_regions_dataset.csv"

    print_info("Building processed master datasets.")

    if rf_input.exists():
        rf_df = pd.read_csv(rf_input)
        rf_df.to_csv(rf_output, index=False, encoding="utf-8-sig")
        print_success(f"Saved master RF dataset: {rf_output}")
    else:
        print_warning(f"RF clean dataset not found: {rf_input}")

    if regions_input.exists():
        regions_df = pd.read_csv(regions_input)
        regions_df.to_csv(regions_output, index=False, encoding="utf-8-sig")
        print_success(f"Saved master regional dataset: {regions_output}")
    else:
        print_warning(f"Regional clean dataset not found: {regions_input}")