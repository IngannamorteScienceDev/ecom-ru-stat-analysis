import pandas as pd

from src.utils.paths import get_path
from src.utils.logging import print_info, print_success, print_warning


def export_main_table() -> None:
    """
    Export RF and regional analytical datasets to Excel.
    """
    output_dir = get_path("tables")
    output_dir.mkdir(parents=True, exist_ok=True)

    rf_input = get_path("processed_data") / "master_rf_dataset_with_metrics.csv"
    regions_input = get_path("processed_data") / "master_regions_dataset_with_metrics.csv"
    output_file = output_dir / "analytical_tables.xlsx"

    print_info("Exporting analytical datasets to Excel workbook.")

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        if rf_input.exists():
            pd.read_csv(rf_input).to_excel(writer, sheet_name="rf_dynamics", index=False)
        else:
            print_warning(f"RF metrics dataset not found: {rf_input}")

        if regions_input.exists():
            pd.read_csv(regions_input).to_excel(writer, sheet_name="regions_long", index=False)
        else:
            print_warning(f"Regional metrics dataset not found: {regions_input}")

    print_success(f"Saved analytical workbook: {output_file}")