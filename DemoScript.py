import GlowBitController
import TimeController
import ButtonController
import random
import time
from config import config

def Demo():
    button = ButtonController.ButtonController(config["button"])
    gbit = GlowBitController.GlowBitController(config["glowbit"])
    tCont = TimeController.TimeController(config["time"])

    while True:
        # this mode will just show random colors on the top and bottom segments whenever the button is pressed.
        print("="*10)

        start = random.randint(1, 3)

        if(start == 1):
            print("showing 1 random colors.")
            color = gbit.getRandomColor()
            gbit.top(color)
            gbit.bottom(color)
        elif(start >= 2):
            print("showing 2 random colors.")
            gbit.top(gbit.getRandomColor())
            gbit.bottom(gbit.getRandomColor())

        # needs a healty WAIT time to prevent button double tapping.
        time.sleep(1)

        # now go back to sleep.
        pinAlarm = button.buildPinAlarm()
        nextWakeTime = 10
        tCont.lightsleep(nextWakeTime, pinAlarm)
