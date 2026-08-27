from time import struct_time, localtime, mktime
import microcontroller

def stringToStruct_Time(input: str) -> struct_time:
    if(input is None):
        return None

    str_arr = input.split("/")

    int_array = [int(numeric_string) for numeric_string in str_arr]

    return struct_time(int_array)

def struct_TimeToString(input: struct_time) -> str:
    if(input is None):
        return None

    return "{}/{}/{}/{}/{}/{}/{}/{}/{}".format(
        input.tm_year,
        input.tm_mon,
        input.tm_mday,
        input.tm_hour,
        input.tm_min,
        input.tm_sec,
        input.tm_wday,
        input.tm_yday,
        input.tm_isdst)

def convertStartTimeToSeconds(input: str) -> int:
    rawTime = input.split(":")
    return ((24-int(rawTime[0])) * 60 * 60) + (int(rawTime[1]) * 60)

def convertEndTimeToSeconds(input: str) -> int:
    rawTime = input.split(":")
    return ((int(rawTime[0])) * 60 * 60) + (int(rawTime[1]) * 60)

def wasWokenNormaly(nextWakeUpTime: struct_time, currentTime: struct_time) -> bool:
    # if the next wake time hasnt passed yet then the device was woken by either
    # the button being pressed or a power fluctuation.
    validReasons = ["microcontroller.ResetReason.DEEP_SLEEP_ALARM"
                    , "microcontroller.ResetReason.RESET_PIN"]

    # todo: test wether this correctly returns when woken from a button. Would fix the issue im having with wasButtonPressed
    print("Reset Caused By: ", microcontroller.cpu.reset_reason)
    reason = microcontroller.cpu.reset_reason
    return (reason in validReasons)

def getTodayAsEpoch() -> int:
    todayAsStruct = localtime()
    modifiedDate = struct_time([todayAsStruct.tm_year, todayAsStruct.tm_mon, todayAsStruct.tm_mday, 0, 0, 0 ,todayAsStruct.tm_wday, todayAsStruct.tm_yday, todayAsStruct.tm_isdst])
    return mktime(modifiedDate)

def getDaysToSeconds(days: int) -> int:
    return days * 24 * 60 * 60
