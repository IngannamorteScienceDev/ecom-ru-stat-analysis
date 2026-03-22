import pandas as pd

from src.utils.paths import get_path
from src.utils.logging import print_info, print_success, print_warning


def _add_rf_metrics() -> None:
    input_file = get_path("processed_data") / "master_rf_dataset.csv"
    output_file = get_path("processed_data") / "master_rf_dataset_with_metrics.csv"

    if not input_file.exists():
        print_warning(f"RF master dataset not found: {input_file}")
        return

    df = pd.read_csv(input_file).sort_values("year").reset_index(drop=True)

    y = "share_online"
    df["abs_change"] = df[y].diff()
    df["growth_rate_pct"] = (df[y] / df[y].shift(1)) * 100
    df["growth_increment_pct"] = ((df[y] / df[y].shift(1)) - 1) * 100

    first_value = df[y].iloc[0]
    last_value = df[y].iloc[-1]
    periods = len(df) - 1

    if periods > 0 and first_value > 0:
        cagr = (last_value / first_value) ** (1 / periods) - 1
    else:
        cagr = None

    df["cagr_total"] = cagr
    df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print_success(f"Saved RF dataset with metrics: {output_file}")


def _add_regions_metrics() -> None:
    input_file = get_path("processed_data") / "master_regions_dataset.csv"
    output_file = get_path("processed_data") / "master_regions_dataset_with_metrics.csv"

    if not input_file.exists():
        print_warning(f"Regional master dataset not found: {input_file}")
        return

    df = pd.read_csv(input_file).sort_values(["region", "year"]).reset_index(drop=True)

    df["abs_change"] = df.groupby("region")["share_online"].diff()
    df["growth_rate_pct"] = (
        df.groupby("region")["share_online"].transform(lambda s: s / s.shift(1) * 100)
    )
    df["growth_increment_pct"] = (
        df.groupby("region")["share_online"].transform(lambda s: (s / s.shift(1) - 1) * 100)
    )

    df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print_success(f"Saved regional dataset with metrics: {output_file}")


def add_basic_metrics() -> None:
    """
    Add statistical metrics to RF and regional datasets.
    """
    print_info("Calculating basic metrics for RF and regional datasets.")
    _add_rf_metrics()
    _add_regions_metrics()