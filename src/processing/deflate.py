import pandas as pd


def deflate_series(
    df: pd.DataFrame,
    nominal_col: str,
    cpi_col: str,
    real_col: str,
) -> pd.DataFrame:
    """
    Deflate a nominal monetary series by CPI.

    Formula:
        real = nominal / (CPI / 100)
    """
    result = df.copy()
    result[real_col] = result[nominal_col] / (result[cpi_col] / 100.0)
    return result