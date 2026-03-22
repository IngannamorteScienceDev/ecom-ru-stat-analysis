import matplotlib.pyplot as plt
import pandas as pd

from src.utils.paths import get_path
from src.utils.logging import get_logger, print_info, print_success, print_warning

logger = get_logger(__name__)


def plot_share_online_dynamics() -> None:
    """
    Plot dynamics of online sales share and save it as PNG.
    """
    input_file = get_path("processed_data") / "master_dataset_with_metrics.csv"
    output_dir = get_path("figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "share_online_dynamics.png"

    print_info("Generating main dynamics plot for online sales share.")

    if not input_file.exists():
        logger.warning("Dataset for plotting not found: %s", input_file)
        print_warning(f"Dataset for plotting not found: {input_file}")
        return

    df = pd.read_csv(input_file).sort_values("year")

    plt.figure(figsize=(10, 6))
    plt.plot(df["year"], df["share_online"], marker="o")
    plt.title("Dynamics of online sales share in retail turnover")
    plt.xlabel("Year")
    plt.ylabel("Share of online sales, %")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()

    logger.info("Saved plot: %s", output_file)
    print_success(f"Saved plot: {output_file}")