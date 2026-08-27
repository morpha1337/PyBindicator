import bindicator
import demo_script
import debug_script

PRODUCTION_MODE = "PRODUCTION"
DEBUG_MODE = "DEBUG"
SHOW_MODE = "SHOW"


def start_bindicator(mode: str):
    if mode == PRODUCTION_MODE:
        print("Starting the Bindicator in Production Mode!")
        bindicator.start_program(False)
    elif mode == DEBUG_MODE:
        print("Starting the Bindicator in Debug Mode!")
        debug_script.debug()
    elif mode == SHOW_MODE:
        print("Starting the Bindicator in SHOW Mode!")
        demo_script.demo()


start_bindicator(PRODUCTION_MODE)
