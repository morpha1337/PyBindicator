"""GlowBit 1x8 NeoPixel strip on A1; pixels 0-3 top, 4-7 bottom."""

from __future__ import annotations

import neopixel
from rainbowio import colorwheel
import board
import random
import time
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
        """Light top/bottom segments for one or two active bins (strip has two halves)."""
        if not bins:
            return
        # Hardware is two segments only; ignore any further active bins.
        bins = bins[:2]
        if len(bins) == 1:
            self.top(bins[0].color)
            self.bottom(bins[0].color)
            return
        if random.randint(0, 1) == 0:
            self.top(bins[0].color)
            self.bottom(bins[1].color)
        else:
            self.top(bins[1].color)
            self.bottom(bins[0].color)

    def show_loading(self, percent: int) -> None:
        """Light a progress bar; color shifts red → yellow → green by percent."""

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

        self.pixels.fill(color)
        self.pixels.show()

    def bootup_anim(self) -> None:
        print("Boot Up Animation Begun")
        red = 0
        blue = 0
        green = 0
        while red < 255:
            time.sleep(0.001)
            self.pixels.fill((red, blue, green))
            red += 1
        while blue < 255:
            time.sleep(0.001)
            self.pixels.fill((red, blue, green))
            blue += 1
        while red > 0:
            time.sleep(0.001)
            self.pixels.fill((red, blue, green))
            red -= 1
        while green < 255:
            time.sleep(0.001)
            self.pixels.fill((red, blue, green))
            green += 1
        while blue > 0:
            time.sleep(0.001)
            self.pixels.fill((red, blue, green))
            blue -= 1
        while red < 255:
            time.sleep(0.001)
            self.pixels.fill((red, blue, green))
            red += 1
        while blue < 255:
            time.sleep(0.001)
            self.pixels.fill((red, blue, green))
            blue += 1
        time.sleep(1)
        self.pixels.fill((0, 0, 0))

    def shutdown_anim(self) -> None:
        print("Shutdown Animation Begun")
        self.pixels.fill((0, 0, 0))
        for i in range(255):
            j = 255 - i
            self.pixels.fill((j,j,j))
            time.sleep(0.001)
        self.turn_off()

    def init_glowbit_anim(self) -> None:
        print("Init Glowbit Animation Begun")
        for j in range(255):
            for i in range(self.num_pixels):
                rc_index = (i * 256 // self.num_pixels) + j
                self.pixels[i] = colorwheel(rc_index & 255)
            self.pixels.show()
            time.sleep(0.1)