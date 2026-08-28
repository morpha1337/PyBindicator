"""GlowBit 1x8 NeoPixel strip on A1; pixels 0-3 top, 4-7 bottom."""

from __future__ import annotations

import neopixel
import board
import random
from math import ceil, floor
from model.bin import Bin

RED = (255, 0, 0)
ORANGE = (255, 34, 0)
YELLOW = (255, 170, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
VIOLET = (153, 0, 255)
MAGENTA = (255, 0, 51)
PINK = (255, 51, 119)
AQUA = (85, 125, 255)
WHITE = (255, 255, 255)
OFF = (0, 0, 0)

Color = tuple


class GlowBitController:
    """Control the 8-pixel strip split into top and bottom bin indicators."""

    pixel_pin = board.A1
    num_pixels = 8

    pixel_brightness: float
    pixels: neopixel.NeoPixel

    def __init__(self, config: dict) -> None:
        self.pixel_brightness = config["brightness"]
        self.pixels = neopixel.NeoPixel(
            self.pixel_pin, self.num_pixels, brightness=self.pixel_brightness
        )

    def top(self, color: Color) -> None:
        """Set pixels 0-3 to color."""
        self.pixels[0] = color
        self.pixels[1] = color
        self.pixels[2] = color
        self.pixels[3] = color
        self.pixels.show()

    def bottom(self, color: Color) -> None:
        """Set pixels 4-7 to color."""
        self.pixels[4] = color
        self.pixels[5] = color
        self.pixels[6] = color
        self.pixels[7] = color
        self.pixels.show()

    def turn_off(self) -> None:
        self.pixels.fill(OFF)

    def apply(self, pixel_num: int, color: Color) -> None:
        self.pixels[pixel_num] = color
        self.pixels.show()

    def get_random_color(self) -> Color:
        return random.choice([RED, GREEN, YELLOW, MAGENTA, CYAN])

    def show_notifications(self, bins: list[Bin]) -> None:
        """Light top/bottom segments for one or two active bins."""
        if not bins:
            return
        if len(bins) == 1:
            self.top(bins[0].color)
            self.bottom(bins[0].color)
            return
        if len(bins) == 2:
            if random.randint(0, 1) == 0:
                self.top(bins[0].color)
                self.bottom(bins[1].color)
            else:
                self.top(bins[1].color)
                self.bottom(bins[0].color)
            return
        raise Exception("Three bins are not supported yet")

    def show_loading(self, percent: int) -> None:
        """Light a progress bar; color shifts red → yellow → green by percent."""
        number_lit = (percent * self.num_pixels) / 100

        # CircuitPython has no round(); manual ceil/floor instead.
        if number_lit % 1 >= 0.5:
            number_lit = ceil(number_lit)
        else:
            number_lit = floor(number_lit)

        # Calculate color based on percent; red → yellow → green gradient.
        if percent <= 0:
            color = RED
        elif percent >= 100:
            color = GREEN
        elif percent <= 50:
            blend = percent / 50
            color = (255, int(170 * blend), 0)
        else:
            blend = (percent - 50) / 50
            color = (int(255 * (1 - blend)), int(170 + 85 * blend), 0)

        for index in range(self.num_pixels):
            if index < number_lit:
                self.pixels[index] = color
            else:
                self.pixels[index] = OFF
        self.pixels.show()
