from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.analysis.metrics import add_basic_metrics
from src.analysis.structure import (
    build_regional_rankings,
    build_regional_dispersion_table,
    build_heatmap_matrix,
)
from src.analysis.factors import build_correlation_outputs
from src.viz.plots import (
    plot_share_online_dynamics,
    plot_rf_growth_rates,
    plot_top_bottom_regions,
    plot_regions_boxplot,
    plot_regions_heatmap,
    plot_forecast_with_history,
)
from src.viz.export import export_main_table
from src.utils.logging import print_step, print_success


if __name__ == "__main__":
    print_step("ANALYSIS AND EXPORT")
    add_basic_metrics()
    build_regional_rankings()
    build_regional_dispersion_table()
    build_heatmap_matrix()
    build_correlation_outputs()
    plot_share_online_dynamics()
    plot_rf_growth_rates()
    plot_top_bottom_regions()
    plot_regions_boxplot()
    plot_regions_heatmap()
    plot_forecast_with_history()
    export_main_table()
    print_success("Analysis and export stage completed.")