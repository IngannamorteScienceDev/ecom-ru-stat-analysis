from src.modeling.forecast import run_forecast_stub
from src.utils.logging import print_step, print_success


if __name__ == "__main__":
    print_step("MODELING AND FORECASTING")
    run_forecast_stub()
    print_success("Modeling stage completed.")