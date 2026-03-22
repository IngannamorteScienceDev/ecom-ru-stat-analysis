from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.processing.clean import clean_main_dataset
from src.processing.merge import build_master_dataset
from src.utils.logging import print_step, print_success


if __name__ == "__main__":
    print_step("DATA PREPARATION")
    clean_main_dataset()
    build_master_dataset()
    print_success("Data preparation stage completed.")