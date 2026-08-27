import alarm
import time
from Helpers import convertStartTimeToSeconds, convertEndTimeToSeconds

class TimeController:
    sleepTime: float
    usExternalWakeUp: bool
    alertBegin: int  # in seconds
    alertEnd: int  # in seconds

    def __init__(self, config):
        self.sleepTime = float(config["sleep_time"])
        self.useExternalWakeUp = bool(config["use_external_wake_up"])
        # convert the time to seconds for easy math.
        self.alertBegin = convertStartTimeToSeconds(str(config["alert_begin"]))
        self.alertEnd = convertEndTimeToSeconds(str(config["alert_end"]))

    def sleep(self, nextWakeTime: float = None):
        if nextWakeTime is None:
            nextWakeTime = time.monotonic() + self.sleepTime

        time.sleep(nextWakeTime)

    def lightsleep(self, nextWakeTime: float = None, pin_alarm=None):
        if nextWakeTime is None:
            nextWakeTime = time.monotonic() + self.sleepTime

        print("going into LIGHT sleep...")
        if nextWakeTime is not None:
            print("next wake time: ", time.localtime(nextWakeTime))
        if pin_alarm is not None:
            print("Pin Alarm is active.")
        print("================")

        time_alarm = alarm.time.TimeAlarm(monotonic_time=nextWakeTime)

        if self.useExternalWakeUp is True and pin_alarm is not None:
            alarm.light_sleep_until_alarms(time_alarm, pin_alarm)
        else:
            alarm.light_sleep_until_alarms(time_alarm)

    def deepsleep(self, nextWakeTime: float = None, pin_alarm=None):
        # Deepsleep restarts the board when it wakes... but you CAN preserve pin states whilst in sleep.
        if nextWakeTime is None:
            nextWakeTime = time.monotonic() + self.sleepTime

        print("going into DEEP sleep now...")
        if nextWakeTime is not None:
            print("next wake time: ", time.localtime(nextWakeTime))
        if pin_alarm is not None:
            print("Pin Alarm is active.")
        print("================")

        time_alarm = alarm.time.TimeAlarm(monotonic_time=nextWakeTime)

        if self.useExternalWakeUp is True and pin_alarm is not None:
            alarm.exit_and_deep_sleep_until_alarms(time_alarm, pin_alarm)
        else:
            alarm.exit_and_deep_sleep_until_alarms(time_alarm)
