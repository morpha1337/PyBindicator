# SPDX-FileCopyrightText: 2017 Limor Fried for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Remount CIRCUITPY read/write when A0 is grounded (dev workflow)."""

import board
import digitalio
import storage

switch = digitalio.DigitalInOut(board.A0)
switch.direction = digitalio.Direction.INPUT
switch.pull = digitalio.Pull.UP

# If A0 is connected to ground, the host can write files while code is running.
storage.remount("/", switch.value)
