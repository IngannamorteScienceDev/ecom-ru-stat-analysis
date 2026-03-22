from src.collect.rosstat import collect_rosstat_stub
from src.processing.clean import clean_main_dataset
from src.processing.merge import build_master_dataset
from src.analysis.metrics import add_basic_metrics
from src.modeling.forecast import run_forecast_stub


def run_full_pipeline() -> None:
    """
    Run the high-level project pipeline.
    """
    collect_rosstat_stub()
    clean_main_dataset()
    build_master_dataset()
    add_basic_metrics()
    run_forecast_stub()


if __name__ == "__main__":
    run_full_pipeline()