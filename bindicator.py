import glow_bit_controller
import time_controller
import button_controller
import wifi_controller
import memory_controller
from secrets import secrets
from config import config
from bin import convert_json_to_bin
from helpers import was_woken_normally

import time
from microcontroller import reset


def start_program(catch_errors: bool):
    button = button_controller.ButtonController(config["button"])
    gbit = glow_bit_controller.GlowBitController(config["glowbit"])
    wifi = wifi_controller.WifiController(secrets, config["wifi"])
    t_cont = time_controller.TimeController(config["time"])
    memory = memory_controller.MemoryController()

    gbit.top(glow_bit_controller.WHITE)
    gbit.bottom(glow_bit_controller.WHITE)

    try:
        wifi.connect()
        current_time = wifi.set_date_time(config["timezone_offset"])
        print("Last Boot Time Was: ", memory.last_wake_time)

        woken_up = was_woken_normally(memory.last_wake_time, current_time)
        if woken_up:
            memory.update_notifications()
        else:
            memory.clear_notifications()

        if len(memory.notifications) == 0:
            bins = convert_json_to_bin(secrets["bins"])
            memory.add_notifications(bins)
            print(len(bins), " bins added into memory from secrets:")
            for bin_inst in bins:
                print("\t", bin_inst)

        active_notifs = get_active_notifications(
            memory.notifications, t_cont.alert_begin, t_cont.alert_end
        )
        if len(active_notifs) > 0:
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
        gbit.top(glow_bit_controller.RED)
        gbit.bottom(glow_bit_controller.RED)

        if catch_errors:
            print(e)
            button.await_reset()
            gbit.turn_off()
            reset()
        else:
            raise


def get_active_notifications(bins: list, start_time: int, end_time: int) -> list:
    return list(filter(lambda x: x.is_active(start_time, end_time), bins))


def get_next_wake_time(notifications: list):
    def get_next_collection_date(entry):
        return time.mktime(entry.next_collection_date)

    notifications.sort(key=get_next_collection_date)

    index = 0
    while index < len(notifications):
        index += 1

    return notifications[index].next_collection_date
