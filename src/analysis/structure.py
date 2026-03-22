import pandas as pd

from src.utils.paths import get_path
from src.utils.logging import print_info, print_success, print_warning


def build_regional_rankings() -> None:
    """
    Build top/bottom regional rankings for the latest available year.
    """
    input_file = get_path("processed_data") / "master_regions_dataset_with_metrics.csv"
    output_dir = get_path("tables")
    output_dir.mkdir(parents=True, exist_ok=True)

    top_output = output_dir / "top_regions_latest_year.csv"
    bottom_output = output_dir / "bottom_regions_latest_year.csv"

    print_info("Building regional rankings for the latest available year.")

    if not input_file.exists():
        print_warning(f"Regional dataset not found: {input_file}")
        return

    df = pd.read_csv(input_file)
    latest_year = int(df["year"].max())
    latest_df = df[df["year"] == latest_year].copy()

    top_df = latest_df.sort_values("share_online", ascending=False).head(15).reset_index(drop=True)
    bottom_df = latest_df.sort_values("share_online", ascending=True).head(15).reset_index(drop=True)

    top_df.to_csv(top_output, index=False, encoding="utf-8-sig")
    bottom_df.to_csv(bottom_output, index=False, encoding="utf-8-sig")

    print_success(f"Saved top regions ranking: {top_output}")
    print_success(f"Saved bottom regions ranking: {bottom_output}")


def build_regional_dispersion_table() -> None:
    """
    Build yearly dispersion statistics for regions.
    """
    input_file = get_path("processed_data") / "master_regions_dataset_with_metrics.csv"
    output_dir = get_path("tables")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "regional_dispersion_by_year.csv"

    print_info("Calculating regional dispersion statistics by year.")

    if not input_file.exists():
        print_warning(f"Regional dataset not found: {input_file}")
        return

    df = pd.read_csv(input_file)

    grouped = (
        df.groupby("year")["share_online"]
        .agg(["mean", "median", "min", "max", "std"])
        .reset_index()
        .rename(
            columns={
                "mean": "mean_share_online",
                "median": "median_share_online",
                "min": "min_share_online",
                "max": "max_share_online",
                "std": "std_share_online",
            }
        )
    )

    grouped["variation_coeff_pct"] = grouped["std_share_online"] / grouped["mean_share_online"] * 100
    grouped.to_csv(output_file, index=False, encoding="utf-8-sig")

    print_success(f"Saved regional dispersion table: {output_file}")


def build_heatmap_matrix() -> None:
    """
    Build region-year matrix for heatmap plotting and export.
    """
    input_file = get_path("processed_data") / "master_regions_dataset_with_metrics.csv"
    output_dir = get_path("tables")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "regions_heatmap_matrix.csv"

    print_info("Building region-year matrix for heatmap visualization.")

    if not input_file.exists():
        print_warning(f"Regional dataset not found: {input_file}")
        return

    df = pd.read_csv(input_file)
    pivot = df.pivot(index="region", columns="year", values="share_online")
    pivot.to_csv(output_file, encoding="utf-8-sig")

    print_success(f"Saved heatmap matrix: {output_file}")