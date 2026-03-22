from pathlib import Path

import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from src.utils.paths import get_path
from src.utils.logging import get_logger

logger = get_logger(__name__)


def run_forecast_stub() -> None:
    """
    Fit a simple forecasting model for the target series.
    """
    input_file = get_path("processed_data") / "master_dataset_with_metrics.csv"
    output_dir = get_path("models")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "forecast_values.csv"

    if not input_file.exists():
        logger.warning("Dataset for forecasting not found: %s", input_file)
        return

    df = pd.read_csv(input_file).sort_values("year").reset_index(drop=True)

    if len(df) < 4:
        logger.warning("Not enough observations for forecasting.")
        return

    y = df["share_online"]
    model = ExponentialSmoothing(y, trend="add", seasonal=None)
    fitted = model.fit()

    horizon = 3
    forecast = fitted.forecast(horizon)

    future_years = list(range(int(df["year"].iloc[-1]) + 1, int(df["year"].iloc[-1]) + horizon + 1))
    result = pd.DataFrame({"year": future_years, "forecast_share_online": forecast.values})
    result.to_csv(output_file, index=False, encoding="utf-8-sig")
    logger.info("Saved forecast output: %s", output_file)