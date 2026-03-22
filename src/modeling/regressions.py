import pandas as pd
import statsmodels.api as sm


def run_ols_regression(df: pd.DataFrame, target: str, features: list[str]):
    """
    Run OLS regression for selected target and feature columns.
    """
    data = df.dropna(subset=[target] + features).copy()
    x = data[features]
    x = sm.add_constant(x)
    y = data[target]
    model = sm.OLS(y, x).fit()
    return model