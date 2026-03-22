from src.analysis.metrics import add_basic_metrics
from src.viz.plots import plot_share_online_dynamics
from src.viz.export import export_main_table


if __name__ == "__main__":
    add_basic_metrics()
    plot_share_online_dynamics()
    export_main_table()