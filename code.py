"""CircuitPython entry point; selects PRODUCTION, DEBUG, or SHOW mode."""

from __future__ import annotations

from app.production import start_program
from app.debug import debug
from app.demo import demo


class RunMode:
    """Runtime mode constants (CircuitPython 9.2.x has no stdlib enum module)."""

    PRODUCTION = 1
    DEBUG = 2
    SHOW = 3


def start_bindicator(mode: int) -> None:
    """Dispatch to the selected runtime mode."""
    if mode == RunMode.PRODUCTION:
        print("Starting the Bindicator in Production Mode!")
        start_program(True)
    elif mode == RunMode.DEBUG:
        print("Starting the Bindicator in Debug Mode!")
        debug()
    elif mode == RunMode.SHOW:
        print("Starting the Bindicator in SHOW Mode!")
        demo()


start_bindicator(RunMode.PRODUCTION)
