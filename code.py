"""CircuitPython entry point; selects PRODUCTION, DEBUG, or SHOW mode."""

from __future__ import annotations

from app.bindicator import start_program
from app.debug import debug
from app.demo import demo

PRODUCTION_MODE = "PRODUCTION"
DEBUG_MODE = "DEBUG"
SHOW_MODE = "SHOW"


def start_bindicator(mode: str) -> None:
    """Dispatch to the selected runtime mode."""
    if mode == PRODUCTION_MODE:
        print("Starting the Bindicator in Production Mode!")
        start_program(False)
    elif mode == DEBUG_MODE:
        print("Starting the Bindicator in Debug Mode!")
        debug()
    elif mode == SHOW_MODE:
        print("Starting the Bindicator in SHOW Mode!")
        demo()


start_bindicator(PRODUCTION_MODE)
