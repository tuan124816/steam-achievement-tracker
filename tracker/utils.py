"""
utils.py
---------
Utility functions for logging and displaying progress.

Provides:
- Timestamped logging output for clean console messages.
- Simple tqdm-based progress bar wrapper for iteration display.
"""

from tqdm import tqdm
from datetime import datetime
from typing import Iterable, Iterator, Any
from pathlib import Path


# Color codes
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"


DEBUG_DIR = Path("debug")


def log(msg: str, color: str = Colors.GREEN) -> None:
    """
    Print a timestamped log message to the console.

    Args:
        msg (str): Text to print.
        color (str): ANSI color code.
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{color}[{timestamp}] {msg}{Colors.RESET}")


def warn(msg: str) -> None:
    """Yellow warning log."""
    log(msg, Colors.YELLOW)


def error(msg: str) -> None:
    """Red error log."""
    log(msg, Colors.RED)


def debug_save_html(filename: str, html: str) -> None:
    """
    Save an HTML file into /debug/ only if debug mode is enabled.
    """
    DEBUG_DIR.mkdir(exist_ok=True)
    out = DEBUG_DIR / filename
    out.write_text(html, encoding="utf-8")
    log(f"Debug HTML saved → {out}", Colors.YELLOW)


def progress_bar(iterable: Iterable[Any], desc: str = "Processing") -> Iterator[Any]:
    """
    Wrap an iterable with a tqdm progress bar.

    Args:
        iterable (Iterable): The object to iterate over.
        desc (str): Short label displayed beside the progress bar.

    Returns:
        tqdm.tqdm: A tqdm-wrapped iterator for progress visualization.
    """
    return tqdm(iterable, desc=desc, ncols=80)