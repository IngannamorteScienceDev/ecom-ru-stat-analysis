from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.modeling.forecast import run_forecast_stub
from src.utils.logging import print_step, print_success


if __name__ == "__main__":
    print_step("MODELING AND FORECASTING")
    run_forecast_stub()
    print_success("Modeling stage completed.")