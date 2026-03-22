import matplotlib.pyplot as plt
import pandas as pd

from src.utils.paths import get_path
from src.utils.logging import print_info, print_success, print_warning


def plot_share_online_dynamics() -> None:
    """
    Plot RF dynamics of online sales share and save as PNG.
    """
    input_file = get_path("processed_data") / "master_rf_dataset_with_metrics.csv"
    output_dir = get_path("figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "share_online_rf_dynamics.png"

    print_info("Generating RF dynamics plot.")

    if not input_file.exists():
        print_warning(f"RF dataset for plotting not found: {input_file}")
        return

    df = pd.read_csv(input_file).sort_values("year")

    plt.figure(figsize=(10, 6))
    plt.plot(df["year"], df["share_online"], marker="o")
    plt.title("Dynamics of online sales share in retail turnover, Russian Federation")
    plt.xlabel("Year")
    plt.ylabel("Share of online sales, %")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()

    print_success(f"Saved RF dynamics plot: {output_file}")