import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

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


def plot_rf_growth_rates() -> None:
    """
    Plot RF annual growth increments.
    """
    input_file = get_path("processed_data") / "master_rf_dataset_with_metrics.csv"
    output_dir = get_path("figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "rf_growth_increment_pct.png"

    print_info("Generating RF annual growth increments plot.")

    if not input_file.exists():
        print_warning(f"RF dataset for plotting not found: {input_file}")
        return

    df = pd.read_csv(input_file).sort_values("year")

    plt.figure(figsize=(10, 6))
    plt.bar(df["year"].astype(str), df["growth_increment_pct"])
    plt.title("Annual growth increments of online sales share, Russian Federation")
    plt.xlabel("Year")
    plt.ylabel("Growth increment, %")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()

    print_success(f"Saved RF growth increments plot: {output_file}")


def plot_top_bottom_regions() -> None:
    """
    Plot top and bottom regions by latest-year online share.
    """
    input_file = get_path("processed_data") / "master_regions_dataset_with_metrics.csv"
    output_dir = get_path("figures")
    output_dir.mkdir(parents=True, exist_ok=True)

    top_output = output_dir / "top_regions_latest_year.png"
    bottom_output = output_dir / "bottom_regions_latest_year.png"

    print_info("Generating top and bottom regional ranking plots.")

    if not input_file.exists():
        print_warning(f"Regional dataset for plotting not found: {input_file}")
        return

    df = pd.read_csv(input_file)
    latest_year = int(df["year"].max())
    latest_df = df[df["year"] == latest_year].copy()

    top_df = latest_df.sort_values("share_online", ascending=False).head(15).sort_values("share_online")
    bottom_df = latest_df.sort_values("share_online", ascending=True).head(15).sort_values("share_online")

    plt.figure(figsize=(10, 7))
    plt.barh(top_df["region"], top_df["share_online"])
    plt.title(f"Top 15 regions by online sales share, {latest_year}")
    plt.xlabel("Share of online sales, %")
    plt.ylabel("Region")
    plt.tight_layout()
    plt.savefig(top_output, dpi=300)
    plt.close()

    plt.figure(figsize=(10, 7))
    plt.barh(bottom_df["region"], bottom_df["share_online"])
    plt.title(f"Bottom 15 regions by online sales share, {latest_year}")
    plt.xlabel("Share of online sales, %")
    plt.ylabel("Region")
    plt.tight_layout()
    plt.savefig(bottom_output, dpi=300)
    plt.close()

    print_success(f"Saved top regions plot: {top_output}")
    print_success(f"Saved bottom regions plot: {bottom_output}")


def plot_regions_boxplot() -> None:
    """
    Plot regional distribution for the latest year.
    """
    input_file = get_path("processed_data") / "master_regions_dataset_with_metrics.csv"
    output_dir = get_path("figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "regions_boxplot_latest_year.png"

    print_info("Generating regional distribution boxplot.")

    if not input_file.exists():
        print_warning(f"Regional dataset for plotting not found: {input_file}")
        return

    df = pd.read_csv(input_file)
    latest_year = int(df["year"].max())
    latest_df = df[df["year"] == latest_year].copy()

    plt.figure(figsize=(8, 6))
    plt.boxplot(latest_df["share_online"].dropna())
    plt.title(f"Regional distribution of online sales share, {latest_year}")
    plt.ylabel("Share of online sales, %")
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()

    print_success(f"Saved regional boxplot: {output_file}")


def plot_regions_heatmap() -> None:
    """
    Plot heatmap of region-year online sales share matrix.
    """
    input_file = get_path("processed_data") / "master_regions_dataset_with_metrics.csv"
    output_dir = get_path("figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "regions_heatmap.png"

    print_info("Generating heatmap for region-year online sales share matrix.")

    if not input_file.exists():
        print_warning(f"Regional dataset for plotting not found: {input_file}")
        return

    df = pd.read_csv(input_file)
    pivot = df.pivot(index="region", columns="year", values="share_online")

    plt.figure(figsize=(12, 18))
    sns.heatmap(pivot, cmap="viridis", cbar=True)
    plt.title("Heatmap of online sales share by region and year")
    plt.xlabel("Year")
    plt.ylabel("Region")
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()

    print_success(f"Saved regions heatmap: {output_file}")


def plot_forecast_with_history() -> None:
    """
    Plot historical RF series together with baseline forecast.
    """
    history_file = get_path("processed_data") / "master_rf_dataset_with_metrics.csv"
    forecast_file = get_path("models") / "forecast_rf_values.csv"
    output_dir = get_path("figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "rf_history_and_forecast.png"

    print_info("Generating historical-plus-forecast plot.")

    if not history_file.exists():
        print_warning(f"RF history dataset not found: {history_file}")
        return

    if not forecast_file.exists():
        print_warning(f"Forecast dataset not found: {forecast_file}")
        return

    history_df = pd.read_csv(history_file).sort_values("year")
    forecast_df = pd.read_csv(forecast_file).sort_values("year")

    plt.figure(figsize=(10, 6))
    plt.plot(history_df["year"], history_df["share_online"], marker="o", label="History")
    plt.plot(forecast_df["year"], forecast_df["forecast_share_online"], marker="o", linestyle="--", label="Forecast")
    plt.title("Online sales share in retail turnover: history and forecast")
    plt.xlabel("Year")
    plt.ylabel("Share of online sales, %")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()

    print_success(f"Saved history and forecast plot: {output_file}")