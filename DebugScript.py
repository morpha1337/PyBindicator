import GlowBitController
import TimeController
import ButtonController
import WifiController
import MemoryController
from secrets import secrets
from config import config
from Bin import convertJsonToBin

import time
import Monash
import random
import rtc


def Debug():
    # instantiate the controllers.
    button = ButtonController.ButtonController(config["button"])
    gbit = GlowBitController.GlowBitController(config["glowbit"])
    wifi = WifiController.WifiController(secrets, config["wifi"])
    tCont = TimeController.TimeController(config["time"])
    memory = MemoryController.MemoryController()

    # test the glowbit.
    gbit.top(GlowBitController.WHITE)
    gbit.bottom(GlowBitController.WHITE)

    # test the button
    button.testButton()  # WARNING: this is an execution blocking infinite loop.

    # test Wifi and set DateTime
    wifi.connect()
    currentTime = wifi.setDateTime(config['timezone_offset'])
    wifi.testWifi()

    print("Last Boot Time Was: ", memory.LastWakeTime)
    memory.LastWakeTime = currentTime

    bins = Monash.getBinData(secrets['bin_data'], wifi)
    activeBins = list(filter(lambda x: (x.isActive(tCont.alertBegin, tCont.alertEnd) is True), bins))
    memory.Notifications = activeBins
    gbit.showNotifications(memory.Notifications)

    # Test the MemoryController
    memory.clearNotifications()
    memory.addNotification("test3", time.localtime(time.time()), GlowBitController.YELLOW)
    memory.saveToMem()

    # test the sleepmode.
    pinAlarm = button.buildPinAlarm()
    time.lightsleep(5, pinAlarm)  # restarts the bindicator program when it wakes ##pass None and get the default SleepTime from config# Write your code here :-)
