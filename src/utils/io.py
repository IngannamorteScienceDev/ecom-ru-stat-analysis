from pathlib import Path
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