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

    try:
        gbit.bootup_anim() # play bootup animation on GlowBit

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
            # Button press — dismiss notifications.
            memory.notification_expiry_time = current_time
        else:
            # Cold boot — clear notifications and seed from secrets.
            memory.clear_notifications()
            
            
        # If no notifications are present, seed from secrets.
        if not memory.notifications:
            bins = convert_json_to_bin(secrets["bins"])
            memory.add_notifications(bins)
            print(len(bins), " bins added into memory from secrets:")
            for bin_inst in bins:
                print("\t", bin_inst)

        active_notifs = get_active_notifications(
            memory.notifications, t_cont.alert_begin, t_cont.alert_end, memory.notification_expiry_time
        )
        print("=============")
        print("[", len(active_notifs), "] active notifications.")

        if active_notifs:
            gbit.show_notifications(active_notifs)
        else:
            gbit.turn_off()

        next_wake_time = get_next_wake_time(memory.notifications)

        memory.last_wake_time = current_time
        memory.next_wake_time = next_wake_time
        memory.save_to_mem()

        gbit.shutdown_anim() # play shutdown animation on GlowBit

        print("==============")
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
    bins: list[Bin], start_time: int, end_time: int, dismiss_time: struct_time = None
) -> list[Bin]:
    """Return bins in the alert window, excluding any dismissed for the current alert."""
    active_notifs = list(filter(lambda x: x.is_active(start_time, end_time), bins))

    if dismiss_time is not None:
        # Keep only bins whose alert window had not started yet at dismiss time.
        dismiss_epoch = time.mktime(dismiss_time)
        active_notifs = list(
            filter(
                lambda x: time.mktime(x.next_collection_date) - start_time > dismiss_epoch,
                active_notifs,
            )
        )

    return active_notifs


def get_next_wake_time(notifications: list[Bin]) -> struct_time:
    """Return the struct_time of the earliest upcoming collection."""
    if not notifications:
        raise ValueError("cannot schedule wake with no notifications")

    def collection_epoch(entry: Bin) -> float:
        return time.mktime(entry.next_collection_date)

    notifications.sort(key=collection_epoch)
    return notifications[0].next_collection_date
