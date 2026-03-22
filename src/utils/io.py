from pathlib import Path
from typing import Iterable

import pandas as pd


def read_csv_safe(path: Path) -> pd.DataFrame:
    """
    Read CSV using UTF-8 SIG encoding.
    """
    return pd.read_csv(path, encoding="utf-8-sig")


def save_csv_safe(df: pd.DataFrame, path: Path) -> None:
    """
    Save CSV using UTF-8 SIG encoding.
    """
    df.to_csv(path, index=False, encoding="utf-8-sig")


def find_first_existing_file(paths: Iterable[Path]) -> Path | None:
    """
    Return the first existing file from the iterable or None.
    """
    for path in paths:
        if path.exists():
            return path
    return None