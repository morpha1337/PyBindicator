import Bindicator
import DemoScript
import DebugScript

Production_Mode = "PRODUCTION"
Debug_Mode = "DEBUG"
Show_Mode = "SHOW"

def StartBindicator(mode: str):
    if(mode is Production_Mode):
        print("Starting the Bindicator in Production Mode!")
        Bindicator.startProgram(False)
    elif (mode is Debug_Mode):
        print("Starting the Bindicator in Debug Mode!")
        DebugScript.Debug()
    elif (mode is Show_Mode):
        print("Starting the Bindicator in SHOW Mode!")
        DemoScript.Demo()


StartBindicator(Production_Mode)
