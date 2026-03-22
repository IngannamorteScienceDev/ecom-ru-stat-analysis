from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.clean_project import clean_directory_contents, clean_python_cache, TARGET_DIRS
from src.processing.clean import clean_main_dataset
from src.processing.merge import build_master_dataset
from src.analysis.metrics import add_basic_metrics
from src.analysis.structure import (
    build_subject_rankings_latest,
    build_subject_growth_tables,
    build_subject_quartiles_by_year,
    build_subject_outlier_table,
    build_federal_district_tables,
    build_heatmap_matrix,
)
from src.analysis.factors import build_factor_outputs
from src.modeling.forecast import run_forecast_stub
from src.viz.plots import (
    plot_share_online_dynamics,
    plot_rf_growth_rates,
    plot_top_bottom_subjects,
    plot_subject_growth_leaders,
    plot_subject_first_last_scatter,
    plot_subject_quartiles,
    plot_subjects_boxplot_latest,
    plot_subjects_heatmap,
    plot_federal_district_dynamics,
    plot_forecast_with_history,
)
from src.viz.export import export_main_table
from src.utils.logging import print_step, print_success


def run_cleanup() -> None:
    for target_dir in TARGET_DIRS:
        clean_directory_contents(target_dir)
    clean_python_cache(PROJECT_ROOT)


if __name__ == "__main__":
    print_step("FULL PIPELINE")

    run_cleanup()

    print_step("PREPARE")
    clean_main_dataset()
    build_master_dataset()

    print_step("METRICS")
    add_basic_metrics()

    print_step("STRUCTURE ANALYSIS")
    build_subject_rankings_latest()
    build_subject_growth_tables()
    build_subject_quartiles_by_year()
    build_subject_outlier_table()
    build_federal_district_tables()
    build_heatmap_matrix()

    print_step("FACTOR ANALYSIS")
    build_factor_outputs()

    print_step("FORECASTING")
    run_forecast_stub()

    print_step("VISUALIZATION")
    plot_share_online_dynamics()
    plot_rf_growth_rates()
    plot_top_bottom_subjects()
    plot_subject_growth_leaders()
    plot_subject_first_last_scatter()
    plot_subject_quartiles()
    plot_subjects_boxplot_latest()
    plot_subjects_heatmap()
    plot_federal_district_dynamics()
    plot_forecast_with_history()

    print_step("EXPORT")
    export_main_table()

    print_success("Full pipeline completed successfully.")