import board
import digitalio
import time
import alarm


class ButtonController:
    button_led_pin = board.A2
    button_pin = board.A3
    led = digitalio.DigitalInOut(button_led_pin)
    led.direction = digitalio.Direction.OUTPUT

    def __init__(self, config):
        self.debounce = config["debounce"]
        self.led.value = False

    def __del__(self):
        self.release_pins()

    def release_pins(self):
        print("Releasing Button bindings...")
        try:
            self.button.deinit()
            self.led.deinit()
        except AttributeError:
            print("Button Pins were not initialised. Continuing...")

    def build_pin_alarm(self):
        self.release_pins()
        # pin must be released .deinit() before the alarm can be placed.
        # https://docs.circuitpython.org/en/latest/shared-bindings/alarm/pin/index.html#alarm.pin.PinAlarm
        return alarm.pin.PinAlarm(pin=self.button_pin, value=False, pull=False)

    def enable_button(self):
        print("enabled button")
        self.led.value = True
        self.button = digitalio.DigitalInOut(self.button_pin)
        self.button.direction = digitalio.Direction.INPUT

    def disable_button(self):
        print("disabled button")
        self.led.value = False
        self.button.deinit()

    def read_button_state(self):
        # todo add debounce code here
        return self.button.value

    def await_reset(self) -> None:
        self.enable_button()
        while True:
            time.sleep(0.25)
            if self.button.value is True:
                return

    def blink(self):
        while True:
            self.led.value = True
            time.sleep(0.5)
            self.led.value = False
            time.sleep(0.5)

    def test_button(self):
        self.enable_button()
        while True:
            time.sleep(0.25)
            # strangely the default for the button is True (if not pressed) and False if pressed.
            if self.button.value is True:
                self.led.value = False
                print("Pressed")
            else:
                print("Unpressed")
                self.led.value = True
