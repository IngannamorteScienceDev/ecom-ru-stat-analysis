import pandas as pd

from src.utils.paths import get_path
from src.utils.logging import print_info, print_success, print_warning


def build_correlation_outputs() -> None:
    """
    Build correlation matrices for available processed datasets.
    """
    rf_input = get_path("processed_data") / "master_rf_dataset_with_metrics.csv"
    regions_input = get_path("processed_data") / "master_regions_dataset_with_metrics.csv"
    output_dir = get_path("tables")
    output_dir.mkdir(parents=True, exist_ok=True)

    rf_output = output_dir / "rf_correlation_matrix.csv"
    regions_output = output_dir / "regions_correlation_matrix.csv"

    print_info("Building correlation outputs for available numeric variables.")

    if rf_input.exists():
        rf_df = pd.read_csv(rf_input)
        rf_num = rf_df.select_dtypes(include=["number"])
        if rf_num.shape[1] >= 2:
            rf_num.corr().to_csv(rf_output, encoding="utf-8-sig")
            print_success(f"Saved RF correlation matrix: {rf_output}")
    else:
        print_warning(f"RF dataset not found: {rf_input}")

    if regions_input.exists():
        regions_df = pd.read_csv(regions_input)
        regions_num = regions_df.select_dtypes(include=["number"])
        if regions_num.shape[1] >= 2:
            regions_num.corr().to_csv(regions_output, encoding="utf-8-sig")
            print_success(f"Saved regional correlation matrix: {regions_output}")
    else:
        print_warning(f"Regional dataset not found: {regions_input}")