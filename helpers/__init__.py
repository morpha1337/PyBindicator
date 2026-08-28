"""Time conversion, alert-window math, and wake-reason helpers."""

from __future__ import annotations

from time import struct_time, localtime, mktime
import alarm

try:
    from typing import Optional
except ImportError:
    pass


class WakeSource:
    """How the board woke into this interpreter restart (deep sleep or power-on)."""

    TIME = "time"
    BUTTON = "button"
    POWER = "power"


def string_to_struct_time(value: Optional[str]) -> Optional[struct_time]:
    """Parse Y/M/D/H/M/S/wday/yday/isdst string used in NVM and secrets."""
    if value is None:
        return None

    str_arr = value.split("/")
    int_array = [int(numeric_string) for numeric_string in str_arr]
    return struct_time(int_array)


def struct_time_to_string(value: Optional[struct_time]) -> Optional[str]:
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
        value.tm_isdst,
    )


def convert_start_time_to_seconds(value: str) -> int:
    """Convert HH:MM alert_begin to seconds before midnight on collection day."""
    raw_time = value.split(":")
    return (24 - int(raw_time[0])) * 60 * 60 + int(raw_time[1]) * 60


def convert_end_time_to_seconds(value: str) -> int:
    """Convert HH:MM alert_end to seconds after midnight on collection day."""
    raw_time = value.split(":")
    return int(raw_time[0]) * 60 * 60 + int(raw_time[1]) * 60


def get_wake_source() -> str:
    """Return WakeSource for this boot from alarm.wake_alarm (not reset_reason)."""
    wake = alarm.wake_alarm
    if isinstance(wake, alarm.time.TimeAlarm):
        return WakeSource.TIME
    if isinstance(wake, alarm.pin.PinAlarm):
        return WakeSource.BUTTON
    return WakeSource.POWER


def get_today_as_epoch() -> int:
    """Midnight today as seconds since epoch."""
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
