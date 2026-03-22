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
    top_input = output_dir / "top_regions_latest_year.csv"
    bottom_input = output_dir / "bottom_regions_latest_year.csv"
    dispersion_input = output_dir / "regional_dispersion_by_year.csv"
    heatmap_input = output_dir / "regions_heatmap_matrix.csv"
    rf_corr_input = output_dir / "rf_correlation_matrix.csv"
    regions_corr_input = output_dir / "regions_correlation_matrix.csv"

    output_file = output_dir / "analytical_tables.xlsx"

    print_info("Exporting analytical datasets to Excel workbook.")

    inputs = [
        rf_input,
        regions_input,
        top_input,
        bottom_input,
        dispersion_input,
        heatmap_input,
        rf_corr_input,
        regions_corr_input,
    ]

    if not any(path.exists() for path in inputs):
        print_warning("No analytical datasets found for Excel export. Skipping workbook creation.")
        return

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        if rf_input.exists():
            pd.read_csv(rf_input).to_excel(writer, sheet_name="rf_dynamics", index=False)
        if regions_input.exists():
            pd.read_csv(regions_input).to_excel(writer, sheet_name="regions_long", index=False)
        if top_input.exists():
            pd.read_csv(top_input).to_excel(writer, sheet_name="top_regions", index=False)
        if bottom_input.exists():
            pd.read_csv(bottom_input).to_excel(writer, sheet_name="bottom_regions", index=False)
        if dispersion_input.exists():
            pd.read_csv(dispersion_input).to_excel(writer, sheet_name="dispersion", index=False)
        if heatmap_input.exists():
            pd.read_csv(heatmap_input).to_excel(writer, sheet_name="heatmap_matrix", index=False)
        if rf_corr_input.exists():
            pd.read_csv(rf_corr_input).to_excel(writer, sheet_name="rf_corr", index=False)
        if regions_corr_input.exists():
            pd.read_csv(regions_corr_input).to_excel(writer, sheet_name="regions_corr", index=False)

    print_success(f"Saved analytical workbook: {output_file}")