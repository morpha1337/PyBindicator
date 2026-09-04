"""Write production exceptions to a file when no serial monitor is attached."""

from __future__ import annotations

import sys


def log_error(exc: BaseException, path: str = "error.txt") -> None:
    """Overwrite path with exception traceback for post-mortem without a serial monitor."""
    try:
        with open(path, "w") as f:
            sys.print_exception(exc, f)
    except OSError as err:
        print("Could not write", path, err)
