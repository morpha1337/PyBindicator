# SPDX-FileCopyrightText: 2021 Kattni Rembor for Adafruit Industries
# SPDX-License-Identifier: MIT

"""Filesystem mode at boot: CircuitPython writable by default; hold Boot for USB deploy."""

import time
import alarm
import board
import digitalio
import storage
import neopixel

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
button = digitalio.DigitalInOut(board.BUTTON)
button.switch_to_input(pull=digitalio.Pull.UP)

# Deep-sleep wakes re-run boot.py — skip the deploy window and stay CP-writable.
if alarm.wake_alarm is None:
    # White NeoPixel = hold Boot now to leave CIRCUITPY writable by the computer.
    pixel.fill((255, 255, 255))
    time.sleep(3)
    pixel.fill((0, 0, 0))

    # Pressed (False) → host writable (CP read-only). Released → CP writable.
    storage.remount("/", readonly=not button.value)
else:
    storage.remount("/", False)
``