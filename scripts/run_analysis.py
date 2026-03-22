from src.analysis.metrics import add_basic_metrics
from src.viz.plots import plot_share_online_dynamics
from src.viz.export import export_main_table
from src.utils.logging import print_step, print_success


if __name__ == "__main__":
    print_step("ANALYSIS AND EXPORT")
    add_basic_metrics()
    plot_share_online_dynamics()
    export_main_table()
    print_success("Analysis and export stage completed.")