import pandas as pd


def calculate_share(df: pd.DataFrame, value_col: str, group_total_col: str, output_col: str) -> pd.DataFrame:
    """
    Calculate share as a percentage.
    """
    result = df.copy()
    result[output_col] = result[value_col] / result[group_total_col] * 100
    return result


def calculate_structural_shift(df: pd.DataFrame, share_col: str, output_col: str) -> pd.DataFrame:
    """
    Calculate structural shift for a share indicator.
    """
    result = df.copy()
    result[output_col] = result[share_col].diff()
    return result