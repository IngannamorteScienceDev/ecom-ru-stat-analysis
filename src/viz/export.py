import pandas as pd

from src.utils.paths import get_path
from src.utils.logging import get_logger, print_info, print_success, print_warning

logger = get_logger(__name__)


def export_main_table() -> None:
    """
    Export the main analytical dataset to Excel for thesis use.
    """
    input_file = get_path("processed_data") / "master_dataset_with_metrics.csv"
    output_dir = get_path("tables")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "main_dataset.xlsx"

    print_info("Exporting main analytical dataset to Excel.")

    if not input_file.exists():
        logger.warning("Dataset for export not found: %s", input_file)
        print_warning(f"Dataset for export not found: {input_file}")
        return

    df = pd.read_csv(input_file)
    df.to_excel(output_file, index=False)
    logger.info("Saved Excel table: %s", output_file)
    print_success(f"Saved Excel table: {output_file}")