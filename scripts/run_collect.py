from src.collect.rosstat import collect_rosstat_real
from src.collect.cbr import collect_cbr_stub
from src.collect.emiss import collect_emiss_stub
from src.utils.logging import print_step, print_success, print_warning


if __name__ == "__main__":
    print_step("DATA COLLECTION")
    rosstat_result = collect_rosstat_real()
    if rosstat_result is None:
        print_warning("Rosstat collection did not produce a parsed CSV.")
    collect_cbr_stub()
    collect_emiss_stub()
    print_success("Data collection stage completed.")