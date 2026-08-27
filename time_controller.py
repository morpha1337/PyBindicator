import alarm
import time
from helpers import convert_start_time_to_seconds, convert_end_time_to_seconds


class TimeController:
    def __init__(self, config):
        self.sleep_time = float(config["sleep_time"])
        self.use_external_wake_up = bool(config["use_external_wake_up"])
        self.alert_begin = convert_start_time_to_seconds(str(config["alert_begin"]))
        self.alert_end = convert_end_time_to_seconds(str(config["alert_end"]))

    def sleep(self, next_wake_time: float = None):
        if next_wake_time is None:
            next_wake_time = time.monotonic() + self.sleep_time

        time.sleep(next_wake_time)

    def light_sleep(self, next_wake_time: float = None, pin_alarm=None):
        if next_wake_time is None:
            next_wake_time = time.monotonic() + self.sleep_time

        print("going into LIGHT sleep...")
        if next_wake_time is not None:
            print("next wake time: ", time.localtime(next_wake_time))
        if pin_alarm is not None:
            print("Pin Alarm is active.")
        print("================")

        time_alarm = alarm.time.TimeAlarm(monotonic_time=next_wake_time)

        if self.use_external_wake_up is True and pin_alarm is not None:
            alarm.light_sleep_until_alarms(time_alarm, pin_alarm)
        else:
            alarm.light_sleep_until_alarms(time_alarm)

    def deep_sleep(self, next_wake_time: float = None, pin_alarm=None):
        if next_wake_time is None:
            next_wake_time = time.monotonic() + self.sleep_time

        print("going into DEEP sleep now...")
        if next_wake_time is not None:
            print("next wake time: ", time.localtime(next_wake_time))
        if pin_alarm is not None:
            print("Pin Alarm is active.")
        print("================")

        time_alarm = alarm.time.TimeAlarm(monotonic_time=next_wake_time)

        if self.use_external_wake_up is True and pin_alarm is not None:
            alarm.exit_and_deep_sleep_until_alarms(time_alarm, pin_alarm)
        else:
            alarm.exit_and_deep_sleep_until_alarms(time_alarm)
