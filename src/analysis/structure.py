import pandas as pd

from src.utils.paths import get_path, load_config
from src.utils.logging import print_info, print_success, print_warning


def build_subject_rankings_latest() -> None:
    input_file = get_path("processed_data") / "master_regions_subjects_dataset_with_metrics.csv"
    output_dir = get_path("tables")
    output_dir.mkdir(parents=True, exist_ok=True)

    config = load_config()
    top_n = int(config["analysis"]["latest_top_n"])

    top_output = output_dir / "top_subjects_latest_year.csv"
    bottom_output = output_dir / "bottom_subjects_latest_year.csv"

    print_info("Building latest-year subject rankings.")

    if not input_file.exists():
        print_warning(f"Subjects dataset not found: {input_file}")
        return

    df = pd.read_csv(input_file)
    latest_year = int(df["year"].max())
    latest_df = df[df["year"] == latest_year].copy()

    top_df = latest_df.sort_values("share_online", ascending=False).head(top_n).reset_index(drop=True)
    bottom_df = latest_df.sort_values("share_online", ascending=True).head(top_n).reset_index(drop=True)

    top_df.to_csv(top_output, index=False, encoding="utf-8-sig")
    bottom_df.to_csv(bottom_output, index=False, encoding="utf-8-sig")

    print_success(f"Saved top subjects ranking: {top_output}")
    print_success(f"Saved bottom subjects ranking: {bottom_output}")


def build_subject_growth_tables() -> None:
    input_file = get_path("processed_data") / "master_regions_subjects_dataset_with_metrics.csv"
    output_dir = get_path("tables")
    output_dir.mkdir(parents=True, exist_ok=True)

    abs_output = output_dir / "top_subjects_absolute_increase.csv"
    cagr_output = output_dir / "top_subjects_cagr.csv"
    first_last_output = output_dir / "subjects_first_last_comparison.csv"

    print_info("Building full-period growth tables for subjects.")

    if not input_file.exists():
        print_warning(f"Subjects dataset not found: {input_file}")
        return

    df = pd.read_csv(input_file)

    first_last = (
        df.groupby("region")
        .agg(
            first_year=("year", "min"),
            last_year=("year", "max"),
            first_value=("share_online", "first"),
            last_value=("share_online", "last"),
        )
        .reset_index()
    )

    first_last["absolute_increase"] = first_last["last_value"] - first_last["first_value"]

    periods = first_last["last_year"] - first_last["first_year"]
    first_last["cagr"] = (
        ((first_last["last_value"] / first_last["first_value"]) ** (1 / periods)) - 1
    )
    first_last.loc[(first_last["first_value"] <= 0) | (periods <= 0), "cagr"] = None

    first_last.to_csv(first_last_output, index=False, encoding="utf-8-sig")
    first_last.sort_values("absolute_increase", ascending=False).head(15).to_csv(abs_output, index=False, encoding="utf-8-sig")
    first_last.sort_values("cagr", ascending=False).head(15).to_csv(cagr_output, index=False, encoding="utf-8-sig")

    print_success(f"Saved first-last comparison table: {first_last_output}")
    print_success(f"Saved top absolute increase table: {abs_output}")
    print_success(f"Saved top CAGR table: {cagr_output}")


def build_subject_quartiles_by_year() -> None:
    input_file = get_path("processed_data") / "master_regions_subjects_dataset_with_metrics.csv"
    output_dir = get_path("tables")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "subjects_quartiles_by_year.csv"

    print_info("Calculating yearly quartiles for subject-level distribution.")

    if not input_file.exists():
        print_warning(f"Subjects dataset not found: {input_file}")
        return

    df = pd.read_csv(input_file)

    rows = []
    for year, group in df.groupby("year"):
        rows.append(
            {
                "year": year,
                "min": group["share_online"].min(),
                "q1": group["share_online"].quantile(0.25),
                "median": group["share_online"].median(),
                "q3": group["share_online"].quantile(0.75),
                "max": group["share_online"].max(),
                "mean": group["share_online"].mean(),
            }
        )

    pd.DataFrame(rows).sort_values("year").to_csv(output_file, index=False, encoding="utf-8-sig")
    print_success(f"Saved subject quartiles table: {output_file}")


def build_subject_outlier_table() -> None:
    input_file = get_path("processed_data") / "master_regions_subjects_dataset_with_metrics.csv"
    output_dir = get_path("tables")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "subject_outliers_latest_year.csv"

    config = load_config()
    k = float(config["analysis"]["outlier_iqr_multiplier"])

    print_info("Detecting latest-year outliers among subjects.")

    if not input_file.exists():
        print_warning(f"Subjects dataset not found: {input_file}")
        return

    df = pd.read_csv(input_file)
    latest_year = int(df["year"].max())
    latest_df = df[df["year"] == latest_year].copy()

    q1 = latest_df["share_online"].quantile(0.25)
    q3 = latest_df["share_online"].quantile(0.75)
    iqr = q3 - q1
    upper_bound = q3 + k * iqr
    lower_bound = q1 - k * iqr

    outliers = latest_df[
        (latest_df["share_online"] > upper_bound) | (latest_df["share_online"] < lower_bound)
    ].copy()
    outliers["lower_bound"] = lower_bound
    outliers["upper_bound"] = upper_bound
    outliers.to_csv(output_file, index=False, encoding="utf-8-sig")

    print_success(f"Saved latest-year outlier table: {output_file}")


def build_federal_district_tables() -> None:
    input_file = get_path("processed_data") / "master_federal_districts_dataset_with_metrics.csv"
    output_dir = get_path("tables")
    output_dir.mkdir(parents=True, exist_ok=True)

    latest_output = output_dir / "federal_districts_latest_year.csv"

    print_info("Building federal district summary table.")

    if not input_file.exists():
        print_warning(f"Federal districts dataset not found: {input_file}")
        return

    df = pd.read_csv(input_file)
    latest_year = int(df["year"].max())
    latest_df = df[df["year"] == latest_year].sort_values("share_online", ascending=False)

    latest_df.to_csv(latest_output, index=False, encoding="utf-8-sig")
    print_success(f"Saved federal districts latest-year table: {latest_output}")


def build_heatmap_matrix() -> None:
    input_file = get_path("processed_data") / "master_regions_subjects_dataset_with_metrics.csv"
    output_dir = get_path("tables")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "subjects_heatmap_matrix.csv"

    config = load_config()
    top_n = int(config["analysis"]["heatmap_top_n"])

    print_info("Building reduced subject heatmap matrix.")

    if not input_file.exists():
        print_warning(f"Subjects dataset not found: {input_file}")
        return

    df = pd.read_csv(input_file)
    latest_year = int(df["year"].max())
    latest_top_regions = (
        df[df["year"] == latest_year]
        .sort_values("share_online", ascending=False)
        .head(top_n)["region"]
        .tolist()
    )

    pivot = (
        df[df["region"].isin(latest_top_regions)]
        .pivot(index="region", columns="year", values="share_online")
        .sort_index()
    )
    pivot.to_csv(output_file, encoding="utf-8-sig")

    print_success(f"Saved reduced heatmap matrix: {output_file}")