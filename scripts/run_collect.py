from src.collect.rosstat import collect_rosstat_stub
from src.collect.cbr import collect_cbr_stub
from src.collect.emiss import collect_emiss_stub


if __name__ == "__main__":
    collect_rosstat_stub()
    collect_cbr_stub()
    collect_emiss_stub()