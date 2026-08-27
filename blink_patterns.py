"""Legacy GlowBit patterns — migrate into glow_bit_controller then delete."""

import neopixel
import board
import time
from rainbowio import colorwheel


def bootup():
    print("Booted Up")
    pixel = neopixel.NeoPixel(pixel_pin, 1)
    red = 0
    blue = 0
    green = 0
    while red < 255:
        pixel.fill((red, blue, green))
        red += 1
    while blue < 255:
        pixel.fill((red, blue, green))
        blue += 1
    while red > 0:
        pixel.fill((red, blue, green))
        red -= 1
    while green < 255:
        pixel.fill((red, blue, green))
        green += 1
    while blue > 0:
        pixel.fill((red, blue, green))
        blue -= 1
    while red < 255:
        pixel.fill((red, blue, green))
        red += 1
    while blue < 255:
        pixel.fill((red, blue, green))
        blue += 1
    time.sleep(0.5)
    pixel.fill((0, 0, 0))
    time.sleep(0.2)
    pixel.fill((red, blue, green))
    time.sleep(0.2)
    pixel.fill((0, 0, 0))
    time.sleep(0.2)
    pixel.fill((red, blue, green))
    time.sleep(0.2)
    pixel.fill((0, 0, 0))
    time.sleep(0.2)
    pixel.fill((red, blue, green))
    time.sleep(0.2)
    pixel.fill((0, 0, 0))


def init_glowbit():
    pixels = neopixel.NeoPixel(
        pixel_pin, num_pixels, brightness=pixel_brightness, auto_write=False
    )
    for j in range(255):
        for i in range(num_pixels):
            rc_index = (i * 256 // num_pixels) + j
            pixels[i] = colorwheel(rc_index & 255)
        pixels.show()
        time.sleep(0.1)


def blank_pixels():
    pixels = neopixel.NeoPixel(
        pixel_pin, num_pixels, brightness=pixel_brightness, auto_write=False
    )
    pixels.fill(0, 0, 0, 0)
    pixels.show()


def write_bins(bin_list):
    binno = 1
    write_bin(binno)


def write_bin(bin_data):
    pixels = neopixel.NeoPixel(
        pixel_pin, num_pixels, brightness=pixel_brightness, auto_write=False
    )
    bin_colour = bin_data[0]
    del bin_data[0]
    if bin_colour == "RED":
        for i in bin_data:
            pixels[i] = RED
    elif bin_colour == "BLUE":
        for i in bin_data:
            pixels[i] = RED


def generic_error():
    pixels = neopixel.NeoPixel(
        pixel_pin, num_pixels, brightness=pixel_brightness, auto_write=False
    )
    pixels[0] = OFF
    pixels[1] = OFF
    pixels[2] = OFF
    pixels[3] = RED
    pixels[4] = RED
    pixels[5] = OFF
    pixels[6] = OFF
    pixels[7] = OFF


def no_wifi_error():
    pixels = neopixel.NeoPixel(
        pixel_pin, num_pixels, brightness=pixel_brightness, auto_write=False
    )
    pixels[0] = OFF
    pixels[1] = RED
    pixels[2] = OFF
    pixels[3] = OFF
    pixels[4] = OFF
    pixels[5] = OFF
    pixels[6] = RED
    pixels[7] = OFF


def no_date_found_error():
    pixels = neopixel.NeoPixel(
        pixel_pin, num_pixels, brightness=pixel_brightness, auto_write=False
    )
    pixels[0] = RED
    pixels[1] = BLUE
    pixels[2] = GREEN
    pixels[3] = VIOLET
    pixels[4] = PINK
    pixels[5] = OFF
    pixels[6] = WHITE
    pixels[7] = RED
