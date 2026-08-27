import GlowBitController
import TimeController
import ButtonController
import WifiController
import MemoryController
from secrets import secrets
from config import config
from Bin import convertJsonToBin
from Helpers import wasWokenNormaly

import time
import Monash
import random
import rtc
from microcontroller import reset

def startProgram(catchErrors: bool):
    # instantiate the controllers.
    button = ButtonController.ButtonController(config["button"])
    gbit = GlowBitController.GlowBitController(config["glowbit"])
    wifi = WifiController.WifiController(secrets, config["wifi"])
    tCont = TimeController.TimeController(config["time"])
    memory = MemoryController.MemoryController()

    # Note: Currently we dont want to play any animations during the bootup sequence
    # Sleep() is code blocking and we want it to connect to wifi Whilst the animation plays.
    gbit.top(GlowBitController.WHITE)
    gbit.bottom(GlowBitController.WHITE)

    try:
        # Connect to wifi and set Date Time
        wifi.connect()
        currentTime = wifi.setDateTime(config['timezone_offset'])
        print("Last Boot Time Was: ", memory.LastWakeTime)

        # was button hit?
        wokenUp = wasWokenNormaly(memory.LastWakeTime, currentTime)
        if(wokenUp):
            memory.updateNotifications()
        else:
            # check and remove expired notifications
            memory.clearNotifications()

        # if there are no Bins in memory
        if(len(memory.Notifications) is 0):
            bins = convertJsonToBin(secrets['bins'])
            memory.addNotifications(bins)
            print(len(bins), " bins added into memory from secrets:")
            [print("\t", bininst.__str__()) for bininst in bins]

        # get Active Notifications
        activeNotifs = getActiveNotifications(memory.Notifications, tCont.alertBegin, tCont.alertEnd)
        if(len(activeNotifs) > 0):
            gbit.showNotifications(activeNotifs)
        else:
            gbit.turnOff()

        # Determine Next Wake Time.
        nextWakeTime = getNextWakeTime(memory.Notifications)

        # Finaly, save the new memory state
        memory.LastWakeTime = currentTime
        memory.NextWakeTime = nextWakeTime
        memory.saveToMem()

        # now go back to sleep.
        pinAlarm = button.buildPinAlarm()
        tCont.deepsleep(time.mktime(nextWakeTime), pinAlarm)

        # end program untill next wake.

    except Exception as e:
        gbit.top(GlowBitController.RED)
        gbit.bottom(GlowBitController.RED)

        if(catchErrors):
            print(e)
            button.awaitReset()
            gbit.turnOff()
            reset()
        else:
            raise e


def getActiveNotifications(bins: [Bin], startTime: int, endTime: int) -> [Bin]:
    return list(filter(lambda x: (x.isActive(startTime, endTime)), bins))

def getNextWakeTime(notifications: [Bin]) -> struct_time:
    def getNextCollectionDate(e: Bin):
        return time.mktime(e.NextCollectionDate)

    notifications.sort(key=getNextCollectionDate)

    index = 0
    while index < len(notifications):
        index+=1

    return notifications[index].NextCollectionDate
