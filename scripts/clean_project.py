from pathlib import Path
import shutil
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


TARGET_DIRS = [
    PROJECT_ROOT / "data" / "interim",
    PROJECT_ROOT / "data" / "processed",
    PROJECT_ROOT / "outputs" / "figures",
    PROJECT_ROOT / "outputs" / "tables",
    PROJECT_ROOT / "outputs" / "models",
    PROJECT_ROOT / "outputs" / "logs",
]


def clean_directory_contents(directory: Path) -> None:
    """
    Remove all files and subdirectories inside a target directory,
    but keep the directory itself.
    """
    if not directory.exists():
        return

    for item in directory.iterdir():
        if item.name == ".gitkeep":
            continue
        if item.is_dir():
            shutil.rmtree(item, ignore_errors=True)
        else:
            item.unlink(missing_ok=True)


def clean_python_cache(root: Path) -> None:
    """
    Remove __pycache__ folders and .pyc files recursively.
    """
    for pycache_dir in root.rglob("__pycache__"):
        shutil.rmtree(pycache_dir, ignore_errors=True)

    for pyc_file in root.rglob("*.pyc"):
        pyc_file.unlink(missing_ok=True)


if __name__ == "__main__":
    for target_dir in TARGET_DIRS:
        clean_directory_contents(target_dir)

    clean_python_cache(PROJECT_ROOT)

    print("Project artifacts, cache folders, and .pyc files were removed.")