"""Show/demo mode: random GlowBit colours on each button wake."""

from __future__ import annotations

import random
import time
from config import config
from controllers.button import ButtonController
from controllers.glow_bit import GlowBitController
from controllers.time import TimeController


def demo() -> None:
    """Light random top/bottom colours, then light-sleep until button press."""
    button = ButtonController(config["button"])
    gbit = GlowBitController(config["glowbit"])
    t_cont = TimeController(config["time"])

    while True:
        print("=" * 10)

        start = random.randint(1, 3)

        if start == 1:
            print("showing 1 random color.")
            color = gbit.get_random_color()
            gbit.top(color)
            gbit.bottom(color)
        else:
            print("showing 2 random colors.")
            gbit.top(gbit.get_random_color())
            gbit.bottom(gbit.get_random_color())

        time.sleep(1)

        pin_alarm = button.build_pin_alarm()
        next_wake_time = 10
        t_cont.light_sleep(next_wake_time, pin_alarm)
