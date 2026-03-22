from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from src.utils.paths import get_path, load_config
from src.utils.logging import print_info, print_success, print_warning


def _mae(y_true, y_pred) -> float:
    return float(np.mean(np.abs(np.array(y_true) - np.array(y_pred))))


def _rmse(y_true, y_pred) -> float:
    return float(np.sqrt(np.mean((np.array(y_true) - np.array(y_pred)) ** 2)))


def _mape(y_true, y_pred) -> float:
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    mask = y_true != 0
    if mask.sum() == 0:
        return np.nan
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)


def _forecast_naive(train: pd.DataFrame, horizon: int) -> np.ndarray:
    last_value = train["share_online"].iloc[-1]
    return np.repeat(last_value, horizon)


def _forecast_linear_trend(train: pd.DataFrame, future_years: np.ndarray) -> np.ndarray:
    model = LinearRegression()
    X_train = train[["year"]].values
    y_train = train["share_online"].values
    model.fit(X_train, y_train)
    return model.predict(future_years.reshape(-1, 1))


def _forecast_holt(train: pd.DataFrame, horizon: int) -> np.ndarray:
    model = ExponentialSmoothing(train["share_online"], trend="add", seasonal=None)
    fitted = model.fit()
    return fitted.forecast(horizon).values


def run_forecast_stub() -> None:
    """
    Compare simple forecast models, choose the best on holdout years,
    and build final forecast with approximate prediction interval.
    """
    input_file = get_path("processed_data") / "master_rf_dataset_with_metrics.csv"
    output_dir = get_path("models")
    output_dir.mkdir(parents=True, exist_ok=True)

    forecast_output = output_dir / "forecast_rf_values.csv"
    comparison_output = output_dir / "forecast_model_comparison.csv"

    print_info("Starting advanced RF forecast estimation.")

    if not input_file.exists():
        print_warning(f"RF dataset for forecasting not found: {input_file}")
        return

    df = pd.read_csv(input_file).sort_values("year").reset_index(drop=True)

    if len(df) < 6:
        print_warning("Not enough RF observations for advanced forecasting.")
        return

    config = load_config()
    horizon = int(config["modeling"]["forecast_horizon"])
    holdout_years = int(config["modeling"]["holdout_years"])

    train = df.iloc[:-holdout_years].copy()
    test = df.iloc[-holdout_years:].copy()

    future_test_years = test["year"].values

    model_results = []

    naive_pred = _forecast_naive(train, holdout_years)
    model_results.append(
        {
            "model": "naive_last_value",
            "mae": _mae(test["share_online"], naive_pred),
            "rmse": _rmse(test["share_online"], naive_pred),
            "mape": _mape(test["share_online"], naive_pred),
        }
    )

    linear_pred = _forecast_linear_trend(train, future_test_years)
    model_results.append(
        {
            "model": "linear_trend",
            "mae": _mae(test["share_online"], linear_pred),
            "rmse": _rmse(test["share_online"], linear_pred),
            "mape": _mape(test["share_online"], linear_pred),
        }
    )

    holt_pred = _forecast_holt(train, holdout_years)
    model_results.append(
        {
            "model": "holt_linear",
            "mae": _mae(test["share_online"], holt_pred),
            "rmse": _rmse(test["share_online"], holt_pred),
            "mape": _mape(test["share_online"], holt_pred),
        }
    )

    comparison_df = pd.DataFrame(model_results).sort_values("rmse").reset_index(drop=True)
    comparison_df.to_csv(comparison_output, index=False, encoding="utf-8-sig")
    print_success(f"Saved forecast model comparison: {comparison_output}")

    best_model = comparison_df.iloc[0]["model"]

    future_years = np.arange(df["year"].iloc[-1] + 1, df["year"].iloc[-1] + horizon + 1)

    if best_model == "naive_last_value":
        final_forecast = _forecast_naive(df, horizon)
        fitted_values = np.repeat(df["share_online"].shift(1).dropna().mean(), len(df))
        residual_std = float(df["share_online"].diff().dropna().std())
    elif best_model == "linear_trend":
        final_forecast = _forecast_linear_trend(df, future_years)
        lr = LinearRegression()
        lr.fit(df[["year"]].values, df["share_online"].values)
        fitted_values = lr.predict(df[["year"]].values)
        residual_std = float(np.std(df["share_online"].values - fitted_values, ddof=1))
    else:
        model = ExponentialSmoothing(df["share_online"], trend="add", seasonal=None)
        fitted = model.fit()
        final_forecast = fitted.forecast(horizon).values
        fitted_values = fitted.fittedvalues
        residual_std = float(np.std(df["share_online"].values - fitted_values, ddof=1))

    result = pd.DataFrame(
        {
            "year": future_years,
            "forecast_share_online": final_forecast,
            "lower_95": final_forecast - 1.96 * residual_std,
            "upper_95": final_forecast + 1.96 * residual_std,
            "best_model": best_model,
        }
    )

    result.to_csv(forecast_output, index=False, encoding="utf-8-sig")
    print_success(f"Saved RF forecast output: {forecast_output}")