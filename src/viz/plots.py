import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.utils.paths import get_path, load_config
from src.utils.logging import print_info, print_success, print_warning


def plot_share_online_dynamics() -> None:
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


def plot_top_bottom_subjects() -> None:
    input_file = get_path("processed_data") / "master_regions_subjects_dataset_with_metrics.csv"
    output_dir = get_path("figures")
    output_dir.mkdir(parents=True, exist_ok=True)

    top_output = output_dir / "top_subjects_latest_year.png"
    bottom_output = output_dir / "bottom_subjects_latest_year.png"

    config = load_config()
    top_n = int(config["analysis"]["latest_top_n"])

    print_info("Generating top and bottom subject ranking plots.")

    if not input_file.exists():
        print_warning(f"Subjects dataset for plotting not found: {input_file}")
        return

    df = pd.read_csv(input_file)
    latest_year = int(df["year"].max())
    latest_df = df[df["year"] == latest_year].copy()

    top_df = latest_df.sort_values("share_online", ascending=False).head(top_n).sort_values("share_online")
    bottom_df = latest_df.sort_values("share_online", ascending=True).head(top_n).sort_values("share_online")

    plt.figure(figsize=(10, 7))
    plt.barh(top_df["region"], top_df["share_online"])
    plt.title(f"Top {top_n} subjects by online sales share, {latest_year}")
    plt.xlabel("Share of online sales, %")
    plt.ylabel("Subject")
    plt.tight_layout()
    plt.savefig(top_output, dpi=300)
    plt.close()

    plt.figure(figsize=(10, 7))
    plt.barh(bottom_df["region"], bottom_df["share_online"])
    plt.title(f"Bottom {top_n} subjects by online sales share, {latest_year}")
    plt.xlabel("Share of online sales, %")
    plt.ylabel("Subject")
    plt.tight_layout()
    plt.savefig(bottom_output, dpi=300)
    plt.close()

    print_success(f"Saved top subjects plot: {top_output}")
    print_success(f"Saved bottom subjects plot: {bottom_output}")


def plot_subject_growth_leaders() -> None:
    input_file = get_path("tables") / "subjects_first_last_comparison.csv"
    output_dir = get_path("figures")
    output_dir.mkdir(parents=True, exist_ok=True)

    abs_output = output_dir / "top_subjects_absolute_increase.png"
    cagr_output = output_dir / "top_subjects_cagr.png"

    print_info("Generating full-period subject growth leader plots.")

    if not input_file.exists():
        print_warning(f"Comparison table not found: {input_file}")
        return

    df = pd.read_csv(input_file)

    top_abs = df.sort_values("absolute_increase", ascending=False).head(15).sort_values("absolute_increase")
    top_cagr = df.sort_values("cagr", ascending=False).head(15).sort_values("cagr")

    plt.figure(figsize=(10, 7))
    plt.barh(top_abs["region"], top_abs["absolute_increase"])
    plt.title("Top 15 subjects by absolute increase in online sales share")
    plt.xlabel("Absolute increase, p.p.")
    plt.ylabel("Subject")
    plt.tight_layout()
    plt.savefig(abs_output, dpi=300)
    plt.close()

    plt.figure(figsize=(10, 7))
    plt.barh(top_cagr["region"], top_cagr["cagr"] * 100)
    plt.title("Top 15 subjects by CAGR of online sales share")
    plt.xlabel("CAGR, %")
    plt.ylabel("Subject")
    plt.tight_layout()
    plt.savefig(cagr_output, dpi=300)
    plt.close()

    print_success(f"Saved absolute increase leaders plot: {abs_output}")
    print_success(f"Saved CAGR leaders plot: {cagr_output}")


def plot_subject_first_last_scatter() -> None:
    input_file = get_path("tables") / "subjects_first_last_comparison.csv"
    output_dir = get_path("figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "subjects_first_last_scatter.png"

    print_info("Generating first-vs-last-year scatter for subjects.")

    if not input_file.exists():
        print_warning(f"Comparison table not found: {input_file}")
        return

    df = pd.read_csv(input_file)

    plt.figure(figsize=(8, 8))
    plt.scatter(df["first_value"], df["last_value"], alpha=0.7)
    max_val = max(df["first_value"].max(), df["last_value"].max())
    plt.plot([0, max_val], [0, max_val], linestyle="--")
    plt.title("Subjects: first-year vs last-year online sales share")
    plt.xlabel("First-year value, %")
    plt.ylabel("Last-year value, %")
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()

    print_success(f"Saved first-last scatter plot: {output_file}")


def plot_subject_quartiles() -> None:
    input_file = get_path("tables") / "subjects_quartiles_by_year.csv"
    output_dir = get_path("figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "subjects_quartiles_by_year.png"

    print_info("Generating quartile dynamics plot for subjects.")

    if not input_file.exists():
        print_warning(f"Quartile table not found: {input_file}")
        return

    df = pd.read_csv(input_file)

    plt.figure(figsize=(10, 6))
    plt.plot(df["year"], df["q1"], label="Q1")
    plt.plot(df["year"], df["median"], label="Median")
    plt.plot(df["year"], df["q3"], label="Q3")
    plt.fill_between(df["year"], df["q1"], df["q3"], alpha=0.2)
    plt.title("Regional distribution of online sales share: quartiles by year")
    plt.xlabel("Year")
    plt.ylabel("Share of online sales, %")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()

    print_success(f"Saved quartile dynamics plot: {output_file}")


def plot_subjects_boxplot_latest() -> None:
    input_file = get_path("processed_data") / "master_regions_subjects_dataset_with_metrics.csv"
    output_dir = get_path("figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "subjects_boxplot_latest_year.png"

    print_info("Generating subject-level distribution boxplot.")

    if not input_file.exists():
        print_warning(f"Subjects dataset for plotting not found: {input_file}")
        return

    df = pd.read_csv(input_file)
    latest_year = int(df["year"].max())
    latest_df = df[df["year"] == latest_year].copy()

    plt.figure(figsize=(8, 6))
    plt.boxplot(latest_df["share_online"].dropna())
    plt.title(f"Subject-level distribution of online sales share, {latest_year}")
    plt.ylabel("Share of online sales, %")
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()

    print_success(f"Saved subject boxplot: {output_file}")


def plot_subjects_heatmap() -> None:
    input_file = get_path("tables") / "subjects_heatmap_matrix.csv"
    output_dir = get_path("figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "subjects_heatmap_top.png"

    print_info("Generating reduced subject heatmap.")

    if not input_file.exists():
        print_warning(f"Heatmap matrix not found: {input_file}")
        return

    df = pd.read_csv(input_file, index_col=0)

    plt.figure(figsize=(12, 14))
    sns.heatmap(df, cmap="viridis", cbar=True)
    plt.title("Top subjects by latest-year online sales share: heatmap")
    plt.xlabel("Year")
    plt.ylabel("Subject")
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()

    print_success(f"Saved reduced heatmap plot: {output_file}")


def plot_federal_district_dynamics() -> None:
    input_file = get_path("processed_data") / "master_federal_districts_dataset_with_metrics.csv"
    output_dir = get_path("figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "federal_districts_dynamics.png"

    print_info("Generating federal districts dynamics plot.")

    if not input_file.exists():
        print_warning(f"Federal districts dataset for plotting not found: {input_file}")
        return

    df = pd.read_csv(input_file).sort_values(["region", "year"])

    plt.figure(figsize=(12, 7))
    for region, group in df.groupby("region"):
        plt.plot(group["year"], group["share_online"], marker="o", label=region)

    plt.title("Dynamics of online sales share by federal district")
    plt.xlabel("Year")
    plt.ylabel("Share of online sales, %")
    plt.legend(fontsize=8)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()

    print_success(f"Saved federal districts dynamics plot: {output_file}")


def plot_forecast_with_history() -> None:
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

    if {"lower_95", "upper_95"}.issubset(forecast_df.columns):
        plt.fill_between(
            forecast_df["year"],
            forecast_df["lower_95"],
            forecast_df["upper_95"],
            alpha=0.2,
            label="95% interval",
        )

    plt.title("Online sales share in retail turnover: history and forecast")
    plt.xlabel("Year")
    plt.ylabel("Share of online sales, %")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()

    print_success(f"Saved history and forecast plot: {output_file}")