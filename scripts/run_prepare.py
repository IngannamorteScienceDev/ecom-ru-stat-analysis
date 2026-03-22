from src.processing.clean import clean_main_dataset
from src.processing.merge import build_master_dataset


if __name__ == "__main__":
    clean_main_dataset()
    build_master_dataset()