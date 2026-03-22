import pandas as pd

from src.utils.paths import get_path
from src.utils.logging import get_logger

logger = get_logger(__name__)


def export_main_table() -> None:
    """
    Export the main analytical dataset to Excel for thesis use.
    """
    input_file = get_path("processed_data") / "master_dataset_with_metrics.csv"
    output_dir = get_path("tables")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "main_dataset.xlsx"

    if not input_file.exists():
        logger.warning("Dataset for export not found: %s", input_file)
        return

    df = pd.read_csv(input_file)
    df.to_excel(output_file, index=False)
    logger.info("Saved Excel table: %s", output_file)