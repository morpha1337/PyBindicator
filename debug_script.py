import glow_bit_controller
import time_controller
import button_controller
import wifi_controller
import memory_controller
from secrets import secrets
from config import config
from bin import Bin

import time
import monash


def debug():
    button = button_controller.ButtonController(config["button"])
    gbit = glow_bit_controller.GlowBitController(config["glowbit"])
    wifi = wifi_controller.WifiController(secrets, config["wifi"])
    t_cont = time_controller.TimeController(config["time"])
    memory = memory_controller.MemoryController()

    gbit.top(glow_bit_controller.WHITE)
    gbit.bottom(glow_bit_controller.WHITE)

    # WARNING: this is an execution blocking infinite loop.
    button.test_button()

    wifi.connect()
    current_time = wifi.set_date_time(config["timezone_offset"])
    wifi.test_wifi()

    print("Last Boot Time Was: ", memory.last_wake_time)
    memory.last_wake_time = current_time

    bins = monash.get_bin_data(secrets["bin_data"], wifi)
    active_bins = list(
        filter(lambda x: x.is_active(t_cont.alert_begin, t_cont.alert_end), bins)
    )
    memory.notifications = active_bins
    gbit.show_notifications(memory.notifications)

    memory.clear_notifications()
    memory.add_notification(
        Bin("test3", time.localtime(time.time()), glow_bit_controller.YELLOW, 0)
    )
    memory.save_to_mem()

    pin_alarm = button.build_pin_alarm()
    t_cont.light_sleep(5, pin_alarm)
