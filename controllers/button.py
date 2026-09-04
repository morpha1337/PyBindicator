"""Tactile button on A2 (LED) and A3 (input); supports wake-on-press via PinAlarm."""

from __future__ import annotations

import board
import digitalio
import time
import alarm

try:
    from typing import Optional
except ImportError:
    pass


class ButtonController:
    """Drive the button LED and read press state; pins must be released before sleep.

    Hardware is active-high: pressed = True, released = False.
    """

    button_led_pin = board.A2
    button_pin = board.A3

    led: digitalio.DigitalInOut
    button: Optional[digitalio.DigitalInOut]

    def __init__(self) -> None:
        self.led = digitalio.DigitalInOut(self.button_led_pin)
        self.led.direction = digitalio.Direction.OUTPUT
        self.led.value = False
        self.button = None

    def __del__(self) -> None:
        self.release_pins()

    def release_pins(self) -> None:
        """Deinit GPIO so PinAlarm can bind the button pin."""
        print("Releasing Button bindings...")
        if self.button is not None:
            self.button.deinit()
            self.button = None
        self.led.deinit()

    def build_pin_alarm(self) -> alarm.pin.PinAlarm:
        """Release pins and return a PinAlarm for wake-on-press (active-high)."""
        self.release_pins()
        # PinAlarm requires the pin be deinit'd first on ESP32-S2.
        return alarm.pin.PinAlarm(pin=self.button_pin, value=True, pull=False)

    def enable_button(self) -> None:
        print("enabled button")
        self.led.value = True
        self.button = digitalio.DigitalInOut(self.button_pin)
        self.button.direction = digitalio.Direction.INPUT

    def disable_button(self) -> None:
        print("disabled button")
        self.led.value = False
        if self.button is not None:
            self.button.deinit()
            self.button = None

    def read_button_state(self) -> bool:
        """Return True when pressed, False when released (active-high)."""
        return self.button.value

    def await_reset(self) -> None:
        """Block until the user presses the button (error recovery)."""
        self.enable_button()
        while True:
            time.sleep(0.25)
            if self.button.value:
                return

    def blink(self) -> None:
        while True:
            self.led.value = True
            time.sleep(0.5)
            self.led.value = False
            time.sleep(0.5)

    def test_button(self, duration_seconds: float = 10) -> None:
        """Debug helper: print press state for a fixed duration."""
        self.enable_button()
        end_time = time.monotonic() + duration_seconds
        print("Button test for %s seconds (active-high: True=Pressed)..." % duration_seconds)
        while time.monotonic() < end_time:
            time.sleep(0.25)
            # Active-high: True = pressed, False = released.
            if self.button.value:
                self.led.value = True
                print("Pressed")
            else:
                self.led.value = False
                print("Released")
        self.disable_button()
