import pandas as pd

from src.utils.paths import get_path
from src.utils.logging import print_info, print_success, print_warning


def _add_time_series_metrics(df: pd.DataFrame, group_col: str | None = None) -> pd.DataFrame:
    """
    Add growth metrics to a time series dataframe.
    """
    result = df.copy()

    if group_col is None:
        result = result.sort_values("year").reset_index(drop=True)
        result["abs_change"] = result["share_online"].diff()
        result["growth_rate_pct"] = (result["share_online"] / result["share_online"].shift(1)) * 100
        result["growth_increment_pct"] = ((result["share_online"] / result["share_online"].shift(1)) - 1) * 100

        first_value = result["share_online"].iloc[0]
        last_value = result["share_online"].iloc[-1]
        periods = len(result) - 1
        result["cagr_total"] = (last_value / first_value) ** (1 / periods) - 1 if periods > 0 and first_value > 0 else None
        return result

    result = result.sort_values([group_col, "year"]).reset_index(drop=True)
    result["abs_change"] = result.groupby(group_col)["share_online"].diff()
    result["growth_rate_pct"] = result.groupby(group_col)["share_online"].transform(lambda s: s / s.shift(1) * 100)
    result["growth_increment_pct"] = result.groupby(group_col)["share_online"].transform(lambda s: (s / s.shift(1) - 1) * 100)
    return result


def add_basic_metrics() -> None:
    """
    Add statistical metrics to RF, subjects, and federal districts datasets.
    """
    print_info("Calculating basic metrics for RF, subjects, and federal districts datasets.")

    rf_input = get_path("processed_data") / "master_rf_dataset.csv"
    subjects_input = get_path("processed_data") / "master_regions_subjects_dataset.csv"
    fd_input = get_path("processed_data") / "master_federal_districts_dataset.csv"

    rf_output = get_path("processed_data") / "master_rf_dataset_with_metrics.csv"
    subjects_output = get_path("processed_data") / "master_regions_subjects_dataset_with_metrics.csv"
    fd_output = get_path("processed_data") / "master_federal_districts_dataset_with_metrics.csv"

    if rf_input.exists():
        rf_df = pd.read_csv(rf_input)
        rf_df = _add_time_series_metrics(rf_df, group_col=None)
        rf_df.to_csv(rf_output, index=False, encoding="utf-8-sig")
        print_success(f"Saved RF dataset with metrics: {rf_output}")
    else:
        print_warning(f"RF master dataset not found: {rf_input}")

    if subjects_input.exists():
        subjects_df = pd.read_csv(subjects_input)
        subjects_df = _add_time_series_metrics(subjects_df, group_col="region")
        subjects_df.to_csv(subjects_output, index=False, encoding="utf-8-sig")
        print_success(f"Saved subjects dataset with metrics: {subjects_output}")
    else:
        print_warning(f"Subjects dataset not found: {subjects_input}")

    if fd_input.exists():
        fd_df = pd.read_csv(fd_input)
        fd_df = _add_time_series_metrics(fd_df, group_col="region")
        fd_df.to_csv(fd_output, index=False, encoding="utf-8-sig")
        print_success(f"Saved federal districts dataset with metrics: {fd_output}")
    else:
        print_warning(f"Federal districts dataset not found: {fd_input}")