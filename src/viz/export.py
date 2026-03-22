import pandas as pd

from src.utils.paths import get_path
from src.utils.logging import print_info, print_success, print_warning


def export_main_table() -> None:
    """
    Export all key analytical datasets and summary tables to one Excel workbook.
    """
    output_dir = get_path("tables")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "analytical_tables.xlsx"

    print_info("Exporting analytical datasets to Excel workbook.")

    files = {
        "rf_dynamics": get_path("processed_data") / "master_rf_dataset_with_metrics.csv",
        "subjects_long": get_path("processed_data") / "master_regions_subjects_dataset_with_metrics.csv",
        "federal_districts": get_path("processed_data") / "master_federal_districts_dataset_with_metrics.csv",
        "top_subjects": output_dir / "top_subjects_latest_year.csv",
        "bottom_subjects": output_dir / "bottom_subjects_latest_year.csv",
        "growth_compare": output_dir / "subjects_first_last_comparison.csv",
        "top_abs_increase": output_dir / "top_subjects_absolute_increase.csv",
        "top_cagr": output_dir / "top_subjects_cagr.csv",
        "quartiles": output_dir / "subjects_quartiles_by_year.csv",
        "outliers": output_dir / "subject_outliers_latest_year.csv",
        "fd_latest": output_dir / "federal_districts_latest_year.csv",
        "heatmap_matrix": output_dir / "subjects_heatmap_matrix.csv",
        "factor_corr": output_dir / "subjects_factor_correlation_matrix.csv",
        "factor_reg": output_dir / "subjects_factor_regression_coefficients.csv",
        "factor_fit": output_dir / "subjects_factor_regression_fit.csv",
    }

    existing_files = {sheet: path for sheet, path in files.items() if path.exists()}
    if not existing_files:
        print_warning("No analytical datasets found for Excel export. Skipping workbook creation.")
        return

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        for sheet_name, path in existing_files.items():
            pd.read_csv(path).to_excel(writer, sheet_name=sheet_name[:31], index=False)

    print_success(f"Saved analytical workbook: {output_file}")