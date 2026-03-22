import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from src.utils.paths import get_path, load_config
from src.utils.logging import print_info, print_success, print_warning


def run_forecast_stub() -> None:
    """
    Fit a simple RF forecast model for the target series.
    """
    input_file = get_path("processed_data") / "master_rf_dataset_with_metrics.csv"
    output_dir = get_path("models")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "forecast_rf_values.csv"

    print_info("Starting RF forecast model estimation.")

    if not input_file.exists():
        print_warning(f"RF dataset for forecasting not found: {input_file}")
        return

    df = pd.read_csv(input_file).sort_values("year").reset_index(drop=True)

    if len(df) < 4:
        print_warning("Not enough RF observations for forecasting.")
        return

    config = load_config()
    horizon = int(config["modeling"]["forecast_horizon"])

    y = df["share_online"]
    model = ExponentialSmoothing(y, trend="add", seasonal=None)
    fitted = model.fit()
    forecast = fitted.forecast(horizon)

    future_years = list(range(int(df["year"].iloc[-1]) + 1, int(df["year"].iloc[-1]) + horizon + 1))
    result = pd.DataFrame(
        {
            "year": future_years,
            "forecast_share_online": forecast.values,
        }
    )

    result.to_csv(output_file, index=False, encoding="utf-8-sig")
    print_success(f"Saved RF forecast output: {output_file}")