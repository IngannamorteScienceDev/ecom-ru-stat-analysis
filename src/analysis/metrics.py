import pandas as pd

from src.utils.paths import get_path
from src.utils.logging import get_logger, print_info, print_success, print_warning

logger = get_logger(__name__)


def add_basic_metrics() -> None:
    """
    Add chain growth metrics to the master dataset.
    """
    input_file = get_path("processed_data") / "master_dataset.csv"
    output_file = get_path("processed_data") / "master_dataset_with_metrics.csv"

    print_info("Calculating basic statistical indicators and growth metrics.")

    if not input_file.exists():
        logger.warning("Master dataset not found: %s", input_file)
        print_warning(f"Master dataset not found: {input_file}")
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
    logger.info("Saved dataset with metrics: %s", output_file)
    print_success(f"Saved dataset with metrics: {output_file}")