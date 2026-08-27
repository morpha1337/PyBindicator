"""GlowBit 1x8 NeoPixel strip on A1; pixels 0-3 top, 4-7 bottom."""

import neopixel
import board
import random
from math import ceil, floor

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


class GlowBitController:
    """Control the 8-pixel strip split into top and bottom bin indicators."""

    pixel_pin = board.A1
    num_pixels = 8

    def __init__(self, config):
        self.pixel_brightness = config["brightness"]
        self.pixels = neopixel.NeoPixel(
            self.pixel_pin, self.num_pixels, brightness=self.pixel_brightness
        )

    def top(self, color) -> None:
        """Set pixels 0-3 to color."""
        self.pixels[0] = color
        self.pixels[1] = color
        self.pixels[2] = color
        self.pixels[3] = color
        self.pixels.show()

    def bottom(self, color) -> None:
        """Set pixels 4-7 to color."""
        self.pixels[4] = color
        self.pixels[5] = color
        self.pixels[6] = color
        self.pixels[7] = color
        self.pixels.show()

    def turn_off(self) -> None:
        self.pixels.fill(OFF)

    def apply(self, pixel_num: int, color: tuple) -> None:
        self.pixels[pixel_num] = color
        self.pixels.show()

    def get_random_color(self) -> tuple:
        index = random.randint(0, 4)
        if index == 0:
            return RED
        elif index == 1:
            return GREEN
        elif index == 2:
            return YELLOW
        elif index == 3:
            return MAGENTA
        elif index == 4:
            return CYAN

    def show_notifications(self, colors: list) -> None:
        """Light top/bottom segments for one or two active bin colours."""
        if len(colors) == 0:
            return
        elif len(colors) == 1:
            self.top(colors[0])
            self.bottom(colors[0])
            return
        elif len(colors) == 2:
            start = random.randint(0, 1)
            if start == 0:
                self.top(colors[0])
                self.bottom(colors[1])
            else:
                self.top(colors[1])
                self.bottom(colors[0])
        elif len(colors) == 3:
            raise Exception("Three bins are not supported yet")

    def show_loading(self, percent: int) -> None:
        number_lit = (percent * self.num_pixels) / 100

        # CircuitPython has no round(); manual ceil/floor instead.
        if number_lit % 1 >= 0.5:
            number_lit = ceil(number_lit)
        else:
            number_lit = floor(number_lit)

        index = 0
        while index < number_lit:
            self.apply(index, YELLOW)
            index += 1
