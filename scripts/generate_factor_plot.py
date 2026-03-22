from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.viz.plots import plot_factor_coefficients
from src.utils.logging import print_step, print_success


if __name__ == "__main__":
    print_step("FACTOR COEFFICIENT PLOT")
    plot_factor_coefficients()
    print_success("Factor coefficient plot generation completed.")