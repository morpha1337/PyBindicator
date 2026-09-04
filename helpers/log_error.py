"""Write production exceptions to a file when no serial monitor is attached."""

from __future__ import annotations

import traceback


def log_error(exc: BaseException, path: str = "error.txt") -> None:
    """Overwrite path with exception traceback for post-mortem without a serial monitor."""
    traceback.print_exception(exc)
    try:
        with open(path, "w") as f:
            traceback.print_exception(exc, file=f)
    except OSError as err:
        print("Could not write", path, err)
