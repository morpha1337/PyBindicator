from time import struct_time, localtime, mktime
import microcontroller


def string_to_struct_time(value: str) -> struct_time:
    if value is None:
        return None

    str_arr = value.split("/")
    int_array = [int(numeric_string) for numeric_string in str_arr]
    return struct_time(int_array)


def struct_time_to_string(value: struct_time) -> str:
    if value is None:
        return None

    return "{}/{}/{}/{}/{}/{}/{}/{}/{}".format(
        value.tm_year,
        value.tm_mon,
        value.tm_mday,
        value.tm_hour,
        value.tm_min,
        value.tm_sec,
        value.tm_wday,
        value.tm_yday,
        value.tm_isdst)


def convert_start_time_to_seconds(value: str) -> int:
    raw_time = value.split(":")
    return ((24 - int(raw_time[0])) * 60 * 60) + (int(raw_time[1]) * 60)


def convert_end_time_to_seconds(value: str) -> int:
    raw_time = value.split(":")
    return (int(raw_time[0]) * 60 * 60) + (int(raw_time[1]) * 60)


def was_woken_normally(next_wake_up_time: struct_time, current_time: struct_time) -> bool:
    # if the next wake time hasnt passed yet then the device was woken by either
    # the button being pressed or a power fluctuation.
    valid_reasons = [
        "microcontroller.ResetReason.DEEP_SLEEP_ALARM",
        "microcontroller.ResetReason.RESET_PIN",
    ]

    # todo: test wether this correctly returns when woken from a button.
    print("Reset Caused By: ", microcontroller.cpu.reset_reason)
    reason = microcontroller.cpu.reset_reason
    return reason in valid_reasons


def get_today_as_epoch() -> int:
    today_as_struct = localtime()
    modified_date = struct_time([
        today_as_struct.tm_year,
        today_as_struct.tm_mon,
        today_as_struct.tm_mday,
        0,
        0,
        0,
        today_as_struct.tm_wday,
        today_as_struct.tm_yday,
        today_as_struct.tm_isdst,
    ])
    return mktime(modified_date)


def get_days_to_seconds(days: int) -> int:
    return days * 24 * 60 * 60
