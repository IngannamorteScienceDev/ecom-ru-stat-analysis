from src.collect.rosstat import collect_rosstat_real
from src.collect.cbr import collect_cbr_stub
from src.collect.emiss import collect_emiss_stub
from src.utils.logging import print_step, print_success


if __name__ == "__main__":
    print_step("DATA COLLECTION")
    collect_rosstat_real()
    collect_cbr_stub()
    collect_emiss_stub()
    print_success("Data collection stage completed.")