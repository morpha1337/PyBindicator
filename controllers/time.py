"""Deep/light sleep and alert-window time conversion."""

from __future__ import annotations

import alarm
import time
from helpers import (
    convert_start_time_to_seconds,
    convert_end_time_to_seconds,
    format_struct_time,
)

try:
    from typing import Optional
except ImportError:
    pass


class TimeController:
    """Schedule sleep alarms and expose alert window as seconds before/after collection."""

    sleep_time: float
    use_external_wake_up: bool
    alert_begin: int
    alert_end: int

    def __init__(self, config: dict) -> None:
        self.sleep_time = float(config["sleep_time"])
        self.use_external_wake_up = bool(config["use_external_wake_up"])
        # alert_begin/end are seconds before/after midnight on collection day
        self.alert_begin = convert_start_time_to_seconds(str(config["alert_begin"]))
        self.alert_end = convert_end_time_to_seconds(str(config["alert_end"]))

    def sleep(self, next_wake_time: Optional[float] = None) -> None:
        if next_wake_time is None:
            next_wake_time = time.monotonic() + self.sleep_time

        time.sleep(next_wake_time)

    def _monotonic_wake_from_epoch(self, epoch_wake_time: Optional[float]) -> float:
        """Convert a wall-clock wake (epoch seconds) to a TimeAlarm monotonic_time."""
        if epoch_wake_time is None:
            return time.monotonic() + self.sleep_time

        # TimeAlarm(monotonic_time=...) needs duration from now, not epoch.
        duration = epoch_wake_time - time.time()
        # Past/immediate targets must not become a near-zero sleep (boot loop).
        if duration <= 0:
            print(
                "Wake time already past; sleeping 1h to avoid reboot loop. "
                "Caller should schedule a future epoch."
            )
            duration = 3600
        return time.monotonic() + duration

    def light_sleep(
        self,
        next_wake_time: Optional[float] = None,
        pin_alarm: Optional[alarm.pin.PinAlarm] = None,
    ) -> None:
        """Light sleep until time alarm (and optional button alarm).

        next_wake_time is wall-clock epoch seconds (time.time() / mktime).
        """
        print("going into LIGHT sleep...")
        if next_wake_time is not None:
            print("next wake time: ", format_struct_time(time.localtime(next_wake_time)))
        if pin_alarm is not None:
            print("Pin Alarm is active.")
        print("================")

        time_alarm = alarm.time.TimeAlarm(
            monotonic_time=self._monotonic_wake_from_epoch(next_wake_time)
        )

        if self.use_external_wake_up and pin_alarm:
            alarm.light_sleep_until_alarms(time_alarm, pin_alarm)
        else:
            alarm.light_sleep_until_alarms(time_alarm)

    def deep_sleep(
        self,
        next_wake_time: Optional[float] = None,
        pin_alarm: Optional[alarm.pin.PinAlarm] = None,
    ) -> None:
        """Deep sleep; restarts the interpreter on wake.

        next_wake_time is wall-clock epoch seconds (time.time() / mktime).
        """
        print("going into DEEP sleep now...")
        if next_wake_time is not None:
            print("next wake time: ", format_struct_time(time.localtime(next_wake_time)))
        if pin_alarm is not None:
            print("Pin Alarm is active.")
        print("================")

        time_alarm = alarm.time.TimeAlarm(
            monotonic_time=self._monotonic_wake_from_epoch(next_wake_time)
        )

        if self.use_external_wake_up and pin_alarm:
            alarm.exit_and_deep_sleep_until_alarms(time_alarm, pin_alarm)
        else:
            alarm.exit_and_deep_sleep_until_alarms(time_alarm)
