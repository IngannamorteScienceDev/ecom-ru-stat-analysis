from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd
import requests
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

from src.utils.paths import get_path, load_config
from src.utils.logging import (
    get_logger,
    print_info,
    print_success,
    print_warning,
)

logger = get_logger(__name__)


EXPECTED_YEARS = list(range(2014, 2026))


def _download_file(url: str, destination: Path) -> bool:
    """
    Download a file from URL to destination.
    Returns True on success, False otherwise.
    """
    try:
        with requests.get(url, stream=True, timeout=60) as response:
            response.raise_for_status()
            total = int(response.headers.get("content-length", 0))

            with Progress(
                SpinnerColumn(),
                TextColumn("[bold cyan]{task.description}"),
                BarColumn(),
                TextColumn("{task.completed}/{task.total} bytes"),
                TimeElapsedColumn(),
            ) as progress:
                task = progress.add_task("Downloading Rosstat file", total=total if total > 0 else 1)

                with open(destination, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            progress.update(task, advance=len(chunk))
        return True
    except Exception as exc:
        logger.exception("Failed to download file: %s", exc)
        return False


def ensure_rosstat_file() -> Path | None:
    """
    Ensure Rosstat source file exists locally.

    Priority:
    1. Existing local file in data/raw/
    2. Download from config URL if provided
    """
    config = load_config()
    raw_dir = get_path("raw_data")
    raw_dir.mkdir(parents=True, exist_ok=True)

    local_filename = config["sources"]["rosstat"].get("local_filename", "rosstat_share_online.xlsx")
    download_url = config["sources"]["rosstat"].get("download_url", "").strip()
    fallback_page = config["sources"]["rosstat"].get("fallback_page", "")

    local_path = raw_dir / local_filename

    if local_path.exists():
        print_success(f"Rosstat source file found: {local_path}")
        logger.info("Rosstat source file found: %s", local_path)
        return local_path

    # search for any plausible manual file
    candidates = sorted(list(raw_dir.glob("*.xlsx")) + list(raw_dir.glob("*.xls")))
    if candidates:
        print_success(f"Found manual Rosstat-like source file: {candidates[0]}")
        logger.info("Using manual source file: %s", candidates[0])
        return candidates[0]

    if download_url:
        print_info("No local Rosstat file found. Attempting download from config URL.")
        success = _download_file(download_url, local_path)
        if success and local_path.exists():
            print_success(f"Downloaded Rosstat file: {local_path}")
            logger.info("Downloaded Rosstat file: %s", local_path)
            return local_path

    print_warning("Rosstat source file is missing.")
    if fallback_page:
        print_warning(f"Download the XLS/XLSX manually from: {fallback_page}")
    logger.warning("Rosstat source file is missing.")
    return None


def _clean_year_label(value) -> int | None:
    """
    Convert a cell value into an integer year if possible.
    """
    if pd.isna(value):
        return None

    text = str(value).strip()
    digits = "".join(ch for ch in text if ch.isdigit())

    if len(digits) == 4:
        year = int(digits)
        if 1990 <= year <= 2100:
            return year

    return None


def _normalize_value(value) -> float | None:
    """
    Convert a Rosstat numeric cell into float.
    """
    if pd.isna(value):
        return None

    text = str(value).strip().replace(",", ".").replace("%", "")
    text = text.replace("\xa0", "").replace(" ", "")

    try:
        return float(text)
    except ValueError:
        return None


def _extract_series_from_wide_sheet(df: pd.DataFrame) -> pd.DataFrame | None:
    """
    Try to extract a single time series from a wide Rosstat-style sheet.
    Heuristic:
    - find years in rows,
    - find first numeric value column next to them.
    """
    for col_idx in range(df.shape[1]):
        years = df.iloc[:, col_idx].apply(_clean_year_label)
        valid_year_mask = years.notna()

        if valid_year_mask.sum() >= 5:
            for val_idx in range(col_idx + 1, min(col_idx + 4, df.shape[1])):
                values = df.iloc[:, val_idx].apply(_normalize_value)
                valid_values = values[valid_year_mask].notna()

                if valid_values.sum() >= 5:
                    result = pd.DataFrame(
                        {
                            "year": years[valid_year_mask].astype(int),
                            "share_online": values[valid_year_mask].astype(float),
                        }
                    )
                    result = result.dropna().sort_values("year").drop_duplicates(subset=["year"])
                    return result

    return None


def _extract_series_from_long_sheet(df: pd.DataFrame) -> pd.DataFrame | None:
    """
    Try to detect explicit year/value columns in a long-format sheet.
    """
    lowered_columns = [str(col).strip().lower() for col in df.columns]
    year_candidates = [i for i, col in enumerate(lowered_columns) if "год" in col or "year" in col]
    value_candidates = [
        i
        for i, col in enumerate(lowered_columns)
        if "интернет" in col or "доля" in col or "share" in col or "%" in col
    ]

    if not year_candidates:
        return None

    year_col = df.columns[year_candidates[0]]
    value_col = df.columns[value_candidates[0]] if value_candidates else df.columns[min(year_candidates[0] + 1, len(df.columns) - 1)]

    result = pd.DataFrame(
        {
            "year": df[year_col].apply(_clean_year_label),
            "share_online": df[value_col].apply(_normalize_value),
        }
    )
    result = result.dropna().sort_values("year").drop_duplicates(subset=["year"])
    if len(result) >= 5:
        result["year"] = result["year"].astype(int)
        result["share_online"] = result["share_online"].astype(float)
        return result

    return None


def parse_rosstat_share_online(file_path: Path) -> pd.DataFrame:
    """
    Parse Rosstat XLS/XLSX file and extract year/share_online series.
    """
    print_info(f"Parsing Rosstat file: {file_path.name}")

    excel_file = pd.ExcelFile(file_path)
    logger.info("Detected sheets: %s", excel_file.sheet_names)

    for sheet_name in excel_file.sheet_names:
        logger.info("Trying sheet: %s", sheet_name)

        # first attempt: preserve headers as raw rows
        raw_df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
        parsed = _extract_series_from_wide_sheet(raw_df)
        if parsed is not None and not parsed.empty:
            print_success(f"Parsed Rosstat data from sheet: {sheet_name}")
            return parsed

        # second attempt: regular header mode
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        parsed = _extract_series_from_long_sheet(df)
        if parsed is not None and not parsed.empty:
            print_success(f"Parsed Rosstat data from sheet: {sheet_name}")
            return parsed

    raise ValueError(
        "Could not parse Rosstat file automatically. "
        "Check the file structure or rename columns manually."
    )


def collect_rosstat_real() -> Path | None:
    """
    Collect and parse the real Rosstat source file into raw CSV.
    """
    source_file = ensure_rosstat_file()
    if source_file is None:
        return None

    raw_dir = get_path("raw_data")
    output_file = raw_dir / "rosstat_share_online_raw.csv"

    try:
        df = parse_rosstat_share_online(source_file)
    except Exception as exc:
        logger.exception("Failed to parse Rosstat file: %s", exc)
        print_warning(f"Failed to parse Rosstat file automatically: {exc}")
        return None

    df = df[(df["year"] >= 2014) & (df["year"] <= 2100)].copy()
    df = df.sort_values("year").reset_index(drop=True)
    df.to_csv(output_file, index=False, encoding="utf-8-sig")

    logger.info("Saved parsed Rosstat raw CSV: %s", output_file)
    print_success(f"Saved parsed Rosstat raw CSV: {output_file}")
    print_info(f"Rows parsed: {len(df)} | Years: {df['year'].min()}–{df['year'].max()}")

    return output_file