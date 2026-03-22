from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.utils.paths import get_path, load_config
from src.utils.logging import print_info, print_success, print_warning
from src.utils.regions import normalize_region_name


def _read_factor_file(path: Path) -> pd.DataFrame:
    """
    Read factor file from CSV or Excel.
    """
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    raise ValueError(f"Unsupported factor file format: {path}")


def _merge_optional_factors(subjects_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge optional external factor files into the subjects dataset.
    Expected columns in each factor file:
    - region
    - year
    - value column with the same name as the config key
    """
    config = load_config()
    external_dir = get_path("external_data")
    result = subjects_df.copy()

    for factor_name, filename in config.get("external_factors", {}).items():
        factor_path = external_dir / filename

        if not factor_path.exists():
            print_warning(f"External factor file not found, skipping: {factor_path}")
            continue

        factor_df = _read_factor_file(factor_path)
        factor_df.columns = [col.strip().lower() for col in factor_df.columns]

        expected_cols = {"region", "year", factor_name}
        if not expected_cols.issubset(set(factor_df.columns)):
            print_warning(
                f"Factor file {factor_path.name} does not contain required columns: "
                f"region, year, {factor_name}"
            )
            continue

        factor_df = factor_df[["region", "year", factor_name]].copy()
        factor_df["region"] = factor_df["region"].astype(str).map(normalize_region_name)
        factor_df["year"] = pd.to_numeric(factor_df["year"], errors="coerce").astype("Int64")
        factor_df[factor_name] = pd.to_numeric(factor_df[factor_name], errors="coerce")

        result = result.merge(factor_df, on=["region", "year"], how="left")
        print_success(f"Merged external factor: {factor_name}")

    return result


def build_master_dataset() -> None:
    """
    Build master processed datasets for RF, all regional rows,
    subjects only, and federal districts only.
    """
    processed_dir = get_path("processed_data")
    processed_dir.mkdir(parents=True, exist_ok=True)

    rf_input = get_path("interim_data") / "rosstat_share_online_rf_clean.csv"
    regions_input = get_path("interim_data") / "rosstat_share_online_regions_clean.csv"

    rf_output = processed_dir / "master_rf_dataset.csv"
    all_regions_output = processed_dir / "master_regions_all_dataset.csv"
    subjects_output = processed_dir / "master_regions_subjects_dataset.csv"
    fd_output = processed_dir / "master_federal_districts_dataset.csv"

    print_info("Building processed master datasets.")

    if rf_input.exists():
        rf_df = pd.read_csv(rf_input)
        rf_df.to_csv(rf_output, index=False, encoding="utf-8-sig")
        print_success(f"Saved master RF dataset: {rf_output}")
    else:
        print_warning(f"RF clean dataset not found: {rf_input}")

    if regions_input.exists():
        regions_df = pd.read_csv(regions_input)
        regions_df.to_csv(all_regions_output, index=False, encoding="utf-8-sig")
        print_success(f"Saved master all-regions dataset: {all_regions_output}")

        subjects_df = regions_df[regions_df["territory_level"] == "subject"].copy()
        subjects_df = _merge_optional_factors(subjects_df)
        subjects_df.to_csv(subjects_output, index=False, encoding="utf-8-sig")
        print_success(f"Saved master subjects dataset: {subjects_output}")

        fd_df = regions_df[regions_df["territory_level"] == "federal_district"].copy()
        fd_df.to_csv(fd_output, index=False, encoding="utf-8-sig")
        print_success(f"Saved master federal districts dataset: {fd_output}")
    else:
        print_warning(f"Regional clean dataset not found: {regions_input}")