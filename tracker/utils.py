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


def log(msg: str) -> None:
    """
    Print a timestamped log message to the console.

    Args:
        msg (str): The message to display.
    """
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


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