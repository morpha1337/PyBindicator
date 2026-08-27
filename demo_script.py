import glow_bit_controller
import time_controller
import button_controller
import random
import time
from config import config


def demo():
    button = button_controller.ButtonController(config["button"])
    gbit = glow_bit_controller.GlowBitController(config["glowbit"])
    t_cont = time_controller.TimeController(config["time"])

    while True:
        print("=" * 10)

        start = random.randint(1, 3)

        if start == 1:
            print("showing 1 random colors.")
            color = gbit.get_random_color()
            gbit.top(color)
            gbit.bottom(color)
        elif start >= 2:
            print("showing 2 random colors.")
            gbit.top(gbit.get_random_color())
            gbit.bottom(gbit.get_random_color())

        time.sleep(1)

        pin_alarm = button.build_pin_alarm()
        next_wake_time = 10
        t_cont.light_sleep(next_wake_time, pin_alarm)
