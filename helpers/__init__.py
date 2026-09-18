"""Time conversion and wake-reason helpers."""

from __future__ import annotations

from time import struct_time, localtime, mktime
import alarm

from helpers.log_error import log_error

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


def format_struct_time(value: Optional[struct_time]) -> str:
    """Human-readable timestamp for serial logs (YYYY-MM-DD HH:MM:SS)."""
    if value is None:
        return "None"
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        value.tm_year,
        value.tm_mon,
        value.tm_mday,
        value.tm_hour,
        value.tm_min,
        value.tm_sec,
    )


def get_wake_source() -> str:
    """Return WakeSource for this boot from alarm.wake_alarm (not reset_reason)."""
    wake = alarm.wake_alarm
    if isinstance(wake, alarm.time.TimeAlarm):
        return WakeSource.TIME
    if isinstance(wake, alarm.pin.PinAlarm):
        return WakeSource.BUTTON
    return WakeSource.POWER


def needs_clock_sync(
    wake_source: str,
    last_clock_sync: Optional[struct_time],
    interval_days: int,
) -> bool:
    """True if Wi-Fi/NTP is required: cold boot, never synced, or interval elapsed."""
    if wake_source == WakeSource.POWER:
        return True
    if last_clock_sync is None:
        return True
    age_seconds = mktime(localtime()) - mktime(last_clock_sync)
    return age_seconds >= get_days_to_seconds(interval_days)


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
