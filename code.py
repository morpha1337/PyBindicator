"""CircuitPython entry point; selects PRODUCTION, DEBUG, or SHOW mode."""

from __future__ import annotations

from enum import IntEnum, auto

from app.bindicator import start_program
from app.debug import debug
from app.demo import demo


class RunMode(IntEnum):
    PRODUCTION = auto()
    DEBUG = auto()
    SHOW = auto()


def start_bindicator(mode: RunMode) -> None:
    """Dispatch to the selected runtime mode."""
    match mode:
        case RunMode.PRODUCTION:
            print("Starting the Bindicator in Production Mode!")
            start_program(False)
        case RunMode.DEBUG:
            print("Starting the Bindicator in Debug Mode!")
            debug()
        case RunMode.SHOW:
            print("Starting the Bindicator in SHOW Mode!")
            demo()


start_bindicator(RunMode.PRODUCTION)
