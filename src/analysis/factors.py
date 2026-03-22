import pandas as pd


def correlation_matrix(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """
    Return correlation matrix for selected columns.
    """
    return df[columns].corr(method="pearson")