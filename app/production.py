"""Production wake loop: Wi-Fi, schedule, GlowBit display, deep sleep."""

from __future__ import annotations

from secrets import secrets
from config import config
from model.bin import Bin, convert_json_to_bin
from helpers import (
    get_wake_source,
    needs_clock_sync,
    WakeSource,
    log_error,
    format_struct_time,
)
from controllers.button import ButtonController
from controllers.glow_bit import GlowBitController, WHITE, RED
from controllers.wifi import WifiController
from controllers.time import TimeController
from controllers.memory import MemoryController

import time
from time import struct_time
from microcontroller import reset


def start_program(catch_errors: bool) -> None:
    """Run one production cycle, then deep-sleep until the next alarm or button press."""
    button = ButtonController()
    gbit = GlowBitController(config["glowbit"])
    wifi = WifiController(secrets, config["wifi"])
    t_cont = TimeController(config["time"])
    memory = MemoryController()

    gbit.bootup_anim()
    # gbit.bottom(WHITE)

    try:
        wake_source = get_wake_source()

        print("==========")
        print("Wake source: ", wake_source)
        print("Last Boot Time Was: ", format_struct_time(memory.last_wake_time))
        print("Last Clock Sync Was: ", format_struct_time(memory.last_clock_sync))
        print("==========")

        if needs_clock_sync(
            wake_source,
            memory.last_clock_sync,
            config["time"]["clock_sync_interval_days"],
        ):
            wifi.connect()
            current_time = wifi.set_date_time(config["timezone_offset"])
            memory.last_clock_sync = current_time
        else:
            current_time = time.localtime()
            print("Skipping Wi-Fi; using RTC time: ", format_struct_time(current_time))

        if wake_source == WakeSource.TIME:
            # Time alarm — update notification state based on current time.
            memory.update_notifications()
        elif wake_source == WakeSource.BUTTON:
            # Button press — discard stale notification state.
            memory.clear_notifications()

        if not memory.notifications:
            bins = convert_json_to_bin(secrets["bins"])
            memory.add_notifications(bins)
            print(len(bins), " bins added into memory from secrets:")
            for bin_inst in bins:
                print("\t", bin_inst)

        active_notifs = get_active_notifications(
            memory.notifications, t_cont.alert_begin, t_cont.alert_end
        )

        if active_notifs:
            gbit.show_notifications(active_notifs)
        else:
            gbit.turn_off()

        next_wake_time = get_next_wake_time(memory.notifications)

        memory.last_wake_time = current_time
        memory.next_wake_time = next_wake_time
        memory.save_to_mem()

        pin_alarm = button.build_pin_alarm()
        t_cont.deep_sleep(time.mktime(next_wake_time), pin_alarm)

    except Exception as e:
        log_error(e)
        gbit.top(RED)
        gbit.bottom(RED)

        if catch_errors:
            button.await_reset()
            gbit.turn_off()
            reset()
        else:
            raise


def get_active_notifications(
    bins: list[Bin], start_time: int, end_time: int
) -> list[Bin]:
    """Return bins whose collection date falls within the configured alert window."""
    return list(filter(lambda x: x.is_active(start_time, end_time), bins))


def get_next_wake_time(notifications: list[Bin]) -> struct_time:
    """Return the struct_time of the earliest upcoming collection."""
    if not notifications:
        raise ValueError("cannot schedule wake with no notifications")

    def collection_epoch(entry: Bin) -> float:
        return time.mktime(entry.next_collection_date)

    notifications.sort(key=collection_epoch)
    return notifications[0].next_collection_date
