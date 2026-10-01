#!/usr/bin/env python3
"""Print the next X wake times from app.production.get_next_wake_time.

Runs on desktop Python (not CircuitPython). Uses secrets['bins'] and the real
production scheduler, with a fake clock advanced to each wake in turn.

Usage (from repo root):
    py -3 scripts/next_wake_times.py 5
"""

from __future__ import annotations

import argparse
import sys
import time as time_mod
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock


ROOT = Path(__file__).resolve().parents[1]


def _stub_circuitpython_modules() -> None:
    """Install enough fake modules so app.production imports on CPython."""
    names = [
        "alarm",
        "alarm.time",
        "alarm.pin",
        "microcontroller",
        "microcontroller.pin",
        "board",
        "digitalio",
        "neopixel",
        "wifi",
        "socketpool",
        "ssl",
        "rtc",
        "foamyguy_nvm_helper",
        "adafruit_requests",
        "adafruit_ntp",
        "adafruit_connection_manager",
        "glowbit",
        "rainbowio",
        "supervisor",
        "analogio",
        "pwmio",
    ]
    for name in names:
        if name not in sys.modules:
            sys.modules[name] = MagicMock()

    # helpers imports `import alarm` then uses alarm.time.TimeAlarm / alarm.pin.PinAlarm
    alarm_mod = ModuleType("alarm")
    alarm_mod.wake_alarm = None
    alarm_mod.time = MagicMock()
    alarm_mod.pin = MagicMock()
    sys.modules["alarm"] = alarm_mod
    sys.modules["alarm.time"] = alarm_mod.time
    sys.modules["alarm.pin"] = alarm_mod.pin


class FakeClock:
    """Patch time.time / localtime (and model.bin.time) to a controllable epoch."""

    def __init__(self, now: float) -> None:
        self.now = float(now)
        self._real_time = time_mod.time
        self._real_localtime = time_mod.localtime

    def time(self) -> float:
        return self.now

    def localtime(self, secs: float | None = None) -> time_mod.struct_time:
        if secs is None:
            secs = self.now
        return self._real_localtime(secs)

    def install(self) -> None:
        import model.bin as bin_mod

        # production uses `import time` / time.time(); Bin uses `from time import time`
        time_mod.time = self.time  # type: ignore[assignment]
        time_mod.localtime = self.localtime  # type: ignore[assignment]
        bin_mod.time = self.time
        bin_mod.localtime = self.localtime

        import helpers as helpers_mod

        helpers_mod.localtime = self.localtime

    def restore(self) -> None:
        import model.bin as bin_mod
        import helpers as helpers_mod

        time_mod.time = self._real_time  # type: ignore[assignment]
        time_mod.localtime = self._real_localtime  # type: ignore[assignment]
        bin_mod.time = self._real_time
        bin_mod.localtime = self._real_localtime
        helpers_mod.localtime = self._real_localtime


def _format(st: time_mod.struct_time) -> str:
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d} (isdst={})".format(
        st.tm_year,
        st.tm_mon,
        st.tm_mday,
        st.tm_hour,
        st.tm_min,
        st.tm_sec,
        st.tm_isdst,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print the next X wake times from get_next_wake_time()."
    )
    parser.add_argument(
        "x",
        type=int,
        help="How many successive next-wake times to compute",
    )
    args = parser.parse_args()
    if args.x < 1:
        print("X must be >= 1", file=sys.stderr)
        return 2

    sys.path.insert(0, str(ROOT))
    _stub_circuitpython_modules()

    from secrets import secrets
    from model.bin import convert_json_to_bin
    from app.production import get_active_notifications, get_next_wake_time
    from helpers import format_struct_time

    clock = FakeClock(time_mod.time())
    clock.install()
    try:
        notifications = convert_json_to_bin(secrets["bins"])

        print("Fake now (start):", _format(clock.localtime()))
        print("Seeded bins:")
        for bin_inst in notifications:
            print("  ", bin_inst)
        print()

        for i in range(1, args.x + 1):
            # Mirror TIME-wake production order: advance dates, then schedule.
            for bin_inst in notifications:
                bin_inst.set_next_collection_date()

            active = get_active_notifications(notifications)
            next_wake = get_next_wake_time(notifications, active)
            reason = "end_date (lights off)" if active else "start_date (lights on)"

            print("---- wake #{:d} ----".format(i))
            print("  now:            ", _format(clock.localtime()))
            print(
                "  active:         ",
                [b.label for b in active] if active else "(none)",
            )
            print("  next_wake_time: ", format_struct_time(next_wake), "<-", reason)
            print("  next_wake detail:", _format(next_wake))

            # Advance clock to just after this wake so the next iteration moves forward.
            clock.now = time_mod.mktime(next_wake) + 1

        print()
        print("Final bin dates:")
        for bin_inst in notifications:
            print("  ", bin_inst)
    finally:
        clock.restore()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
