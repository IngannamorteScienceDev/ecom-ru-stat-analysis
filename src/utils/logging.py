import logging
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler

from src.utils.paths import get_path

console = Console()


def get_logger(name: str) -> logging.Logger:
    """
    Create and configure a project logger with rich console output
    and file logging.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    logger.propagate = False

    log_dir = get_path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "project.log"

    rich_handler = RichHandler(
        console=console,
        rich_tracebacks=True,
        markup=True,
        show_time=True,
        show_level=True,
        show_path=False,
    )
    rich_handler.setLevel(logging.INFO)
    rich_handler.setFormatter(logging.Formatter("%(message)s"))

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    )

    logger.addHandler(rich_handler)
    logger.addHandler(file_handler)

    return logger


def print_step(title: str) -> None:
    """
    Print a prominent pipeline step title.
    """
    console.rule(f"[bold cyan]{title}[/bold cyan]")


def print_success(message: str) -> None:
    """
    Print success message.
    """
    console.print(f"[bold green]✔[/bold green] {message}")


def print_warning(message: str) -> None:
    """
    Print warning message.
    """
    console.print(f"[bold yellow]⚠[/bold yellow] {message}")


def print_info(message: str) -> None:
    """
    Print informational message.
    """
    console.print(f"[bold blue]ℹ[/bold blue] {message}")