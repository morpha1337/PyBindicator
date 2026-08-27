"""Tactile button on A2 (LED) and A3 (input); supports wake-on-press via PinAlarm."""

import board
import digitalio
import time
import alarm


class ButtonController:
    """Drive the button LED and read press state; pins must be released before sleep."""

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
        """Deinit GPIO so PinAlarm can bind the button pin."""
        print("Releasing Button bindings...")
        try:
            self.button.deinit()
            self.led.deinit()
        except AttributeError:
            print("Button pins were not initialized. Continuing...")

    def build_pin_alarm(self):
        """Release pins and return a PinAlarm for wake-on-button."""
        self.release_pins()
        # PinAlarm requires the pin be deinit'd first on ESP32-S2.
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
        # todo: add debounce (see adafruit_debouncer)
        return self.button.value

    def await_reset(self) -> None:
        """Block until the user presses the button (error recovery)."""
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
        """Debug helper: infinite loop printing press state."""
        self.enable_button()
        while True:
            time.sleep(0.25)
            # Pull-up wiring: True = released, False = pressed.
            if self.button.value is True:
                self.led.value = False
                print("Released")
            else:
                print("Pressed")
                self.led.value = True
