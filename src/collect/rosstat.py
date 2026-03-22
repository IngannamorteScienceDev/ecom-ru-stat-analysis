from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from src.utils.paths import get_path, load_config
from src.utils.logging import get_logger, print_info, print_success, print_warning

logger = get_logger(__name__)


def _clean_year_label(value) -> int | None:
    """
    Convert messy Rosstat year labels like '20222)' into integer year.
    """
    if pd.isna(value):
        return None

    text = str(value).strip()
    match = re.search(r"(20\d{2})", text)
    if match:
        return int(match.group(1))
    return None


def _clean_region_name(value: str) -> str:
    """
    Normalize region labels from Rosstat sheet.
    """
    text = str(value).strip()
    text = re.sub(r"\s+", " ", text)
    return text


def _get_source_file() -> Path:
    """
    Return the expected Rosstat Excel file path.
    """
    config = load_config()
    raw_dir = get_path("raw_data")
    filename = config["sources"]["rosstat"]["local_filename"]
    file_path = raw_dir / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"Rosstat source file not found: {file_path}. "
            f"Put the Excel file into data/raw/ with this exact name."
        )

    return file_path


def _extract_year_columns(df: pd.DataFrame) -> dict[int, str]:
    """
    Find columns that represent years.
    Returns mapping: year -> original column name.
    """
    year_map: dict[int, str] = {}

    for col in df.columns:
        year = _clean_year_label(col)
        if year is not None:
            year_map[year] = col

    return dict(sorted(year_map.items()))


def _find_region_column(df: pd.DataFrame) -> str:
    """
    Detect the first textual column that contains region names.
    """
    for col in df.columns:
        series = df[col].astype(str).str.strip()
        if series.str.contains("Российская Федерация", case=False, na=False).any():
            return col
    return df.columns[0]


def _prepare_raw_sheet(file_path: Path, sheet_name: str) -> pd.DataFrame:
    """
    Read Rosstat Excel sheet and flatten header into a single row.
    """
    raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

    header_row_idx = None
    for i in range(min(20, len(raw))):
        row_values = [str(x) for x in raw.iloc[i].tolist()]
        row_text = " ".join(row_values)
        if "2014" in row_text and "2015" in row_text:
            header_row_idx = i
            break

    if header_row_idx is None:
        raise ValueError("Could not locate header row with years in Rosstat sheet.")

    header = raw.iloc[header_row_idx].tolist()
    data = raw.iloc[header_row_idx + 1 :].copy()
    data.columns = header
    data = data.reset_index(drop=True)

    return data


def parse_rosstat_regions_dataset() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Parse Rosstat workbook into:
    1. national time series for Russian Federation
    2. regional long-format dataset
    """
    config = load_config()
    sheet_name = config["sources"]["rosstat"]["sheet_name"]
    file_path = _get_source_file()

    print_info(f"Reading Rosstat workbook: {file_path.name}")
    df = _prepare_raw_sheet(file_path, sheet_name)

    region_col = _find_region_column(df)
    year_map = _extract_year_columns(df)

    if not year_map:
        raise ValueError("No year columns were detected in the Rosstat dataset.")

    print_info(f"Detected region column: {region_col}")
    print_info(f"Detected years: {list(year_map.keys())}")

    keep_cols = [region_col] + list(year_map.values())
    df = df[keep_cols].copy()
    df = df.rename(columns={region_col: "region"})
    df["region"] = df["region"].astype(str).map(_clean_region_name)

    df = df[df["region"].notna()]
    df = df[df["region"].str.strip() != ""]
    df = df[df["region"].str.lower() != "nan"]

    rename_map = {orig_col: str(year) for year, orig_col in year_map.items()}
    df = df.rename(columns=rename_map)

    year_cols = [str(year) for year in year_map.keys()]
    for col in year_cols:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",", ".", regex=False)
            .str.replace("%", "", regex=False)
            .str.replace(" ", "", regex=False)
            .replace({"nan": None, "None": None, "": None})
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=year_cols, how="all").reset_index(drop=True)

    rf_mask = df["region"].str.contains("Российская Федерация", case=False, na=False)
    if not rf_mask.any():
        raise ValueError("Row 'Российская Федерация' was not found in the dataset.")

    rf_row = df.loc[rf_mask].iloc[0]
    national_df = pd.DataFrame(
        {
            "year": [int(col) for col in year_cols],
            "share_online": [rf_row[col] for col in year_cols],
        }
    ).dropna().reset_index(drop=True)

    regional_df = df.loc[~rf_mask].copy()
    regional_long = regional_df.melt(
        id_vars="region",
        value_vars=year_cols,
        var_name="year",
        value_name="share_online",
    )
    regional_long["year"] = pd.to_numeric(regional_long["year"], errors="coerce").astype("Int64")
    regional_long["share_online"] = pd.to_numeric(regional_long["share_online"], errors="coerce")
    regional_long = regional_long.dropna(subset=["year", "share_online"]).reset_index(drop=True)

    return national_df, regional_long


def collect_rosstat_real() -> None:
    """
    Parse the real Rosstat regional workbook and save intermediate raw CSV files.
    """
    raw_dir = get_path("raw_data")
    raw_dir.mkdir(parents=True, exist_ok=True)

    national_out = raw_dir / "rosstat_share_online_rf_raw.csv"
    regional_out = raw_dir / "rosstat_share_online_regions_raw.csv"

    try:
        national_df, regional_long = parse_rosstat_regions_dataset()
    except Exception as exc:
        logger.exception("Failed to parse Rosstat workbook: %s", exc)
        print_warning(f"Failed to parse Rosstat workbook: {exc}")
        raise

    national_df.to_csv(national_out, index=False, encoding="utf-8-sig")
    regional_long.to_csv(regional_out, index=False, encoding="utf-8-sig")

    logger.info("Saved RF series: %s", national_out)
    logger.info("Saved regional dataset: %s", regional_out)

    print_success(f"Saved RF series: {national_out}")
    print_success(f"Saved regional dataset: {regional_out}")
    print_info(f"RF rows: {len(national_df)}")
    print_info(f"Regional rows: {len(regional_long)}")