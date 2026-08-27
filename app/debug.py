"""Hardware and network test harness (not used in production)."""

from __future__ import annotations

from secrets import secrets
from config import config
from model.bin import Bin
from controllers.button import ButtonController
from controllers.glow_bit import GlowBitController, WHITE, YELLOW
from controllers.wifi import WifiController
from controllers.time import TimeController
from controllers.memory import MemoryController
from councils import monash

import time


def debug() -> None:
    """Run hardware and network checks as a sequential checklist."""
    print("=== Bindicator debug checklist ===")

    print("[1/8] Init controllers...")
    button = ButtonController(config["button"])
    gbit = GlowBitController(config["glowbit"])
    wifi = WifiController(secrets, config["wifi"])
    t_cont = TimeController(config["time"])
    memory = MemoryController()

    print("[2/8] GlowBit startup (white)...")
    gbit.top(WHITE)
    gbit.bottom(WHITE)

    print("[3/8] Wi-Fi connect...")
    wifi.connect()

    print("[4/8] NTP sync...")
    current_time = wifi.set_date_time(config["timezone_offset"])

    print("[5/8] Wi-Fi HTTP test...")
    wifi.test_wifi()

    print("[6/8] NVM last wake time...")
    print("Last Boot Time Was: ", memory.last_wake_time)
    memory.last_wake_time = current_time

    print("[7/8] Monash schedule + active bins on GlowBit...")
    bins = monash.get_bin_data(secrets["bin_data"], wifi)
    active_bins = list(
        filter(lambda x: x.is_active(t_cont.alert_begin, t_cont.alert_end), bins)
    )
    memory.notifications = active_bins
    gbit.show_notifications(memory.notifications)

    memory.clear_notifications()
    memory.add_notification(
        Bin("test3", time.localtime(time.time()), YELLOW, 0)
    )
    memory.save_to_mem()

    print("[8/8] Button press test...")
    button.test_button(10)

    print("=== Checklist complete — light sleep 5s (button wake enabled) ===")
    pin_alarm = button.build_pin_alarm()
    t_cont.light_sleep(5, pin_alarm)
