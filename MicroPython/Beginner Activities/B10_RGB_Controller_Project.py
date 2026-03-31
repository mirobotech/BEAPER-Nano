"""
================================================================================
Project: RGB Controller [B10_RGB_Controller_Project.py]
March 31, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPER_Nano.py board module file.

Before starting this project, re-read GE1 and GE2
from Activity 10: Analog Output.

The Arduino Nano ESP32 module includes a built-in RGB LED driven
by three independent PWM channels - one each for red, green, and
blue. Mixing these three channels at different intensities produces
a wide range of colours.

The board module provides three functions for setting each channel:
  beaper.nano_rgb_red(brightness)    # 0-65535, 0=off, 65535=full
  beaper.nano_rgb_green(brightness)  # 0-65535, 0=off, 65535=full
  beaper.nano_rgb_blue(brightness)   # 0-65535, 0=off, 65535=full

Note: the RGB LED elements are active-LOW in hardware - a lower
duty cycle produces more light. The board module's functions handle
this inversion automatically, so 0 always means off and 65535
always means full brightness, matching the LED2-LED5 convention.

Colour mixing reference:
  Red   only          = Red
  Green only          = Green
  Blue  only          = Blue
  Red + Green         = Yellow
  Red + Blue          = Magenta
  Green + Blue        = Cyan
  Red + Green + Blue  = White (or near-white)

Controls:
  RV1 - red channel brightness (if pots installed)
  RV2 - green channel brightness (if pots installed)
  SW2/SW3 - step red channel down/up (if no pots)
  SW4/SW5 - step green channel down/up (if no pots)

Note: This project applies to BEAPER Nano only. BEAPER Pico and
ARPS-2 do not have on-board RGB LEDs. For those platforms, RGB
output can be achieved using a NeoPixel LED strip - see the
future NeoPixel activity.
================================================================================
"""
# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32
import BEAPER_Nano as beaper

import time

# --- Program Configuration ------------
POTS_INSTALLED = False                # Set True if RV1 and RV2 are installed

# --- Program Constants ----------------
STEP_DELAY    = 20                    # Main loop delay (ms)
COLOUR_STEP   = 2000                  # Brightness change per button press

# --- Program Variables ----------------
red_brightness   = 0                  # Current red channel (0-65535)
green_brightness = 0                  # Current green channel (0-65535)
blue_brightness  = 0                  # Current blue channel (0-65535)


# --- Program Functions ----------------

def set_rgb(red, green, blue):
  # Set the RGB LED to the given red, green, and blue brightness values.
  # Clamps each value to 0-65535 before applying.
  red   = max(0, min(65535, red))
  green = max(0, min(65535, green))
  blue  = max(0, min(65535, blue))
  beaper.nano_rgb_red(red)
  beaper.nano_rgb_green(green)
  beaper.nano_rgb_blue(blue)

def rgb_off():
  # Turn off the RGB LED.
  set_rgb(0, 0, 0)


# --- Main Program ---------------------

beaper.nano_led_on()
rgb_off()
print("RGB Controller")

if POTS_INSTALLED:
  print("RV1: red   RV2: green")
else:
  print("SW2/SW5: red down/up   SW3/SW4: green down/up")
print("Blue channel is set to 0 - see Extension Activity 1")

while True:
  SW2_pressed = beaper.SW2.value() == 0
  SW3_pressed = beaper.SW3.value() == 0
  SW4_pressed = beaper.SW4.value() == 0
  SW5_pressed = beaper.SW5.value() == 0
  
  if POTS_INSTALLED:
    red_brightness   = beaper.RV1_level()
    green_brightness = beaper.RV2_level()
  else:
    if SW2_pressed:
      red_brightness -= COLOUR_STEP
    elif SW5_pressed:
      red_brightness += COLOUR_STEP
    if SW3_pressed:
      green_brightness -= COLOUR_STEP
    elif SW4_pressed:
      green_brightness += COLOUR_STEP

  set_rgb(red_brightness, green_brightness, blue_brightness)
  print("R:", red_brightness >> 8,    # >> 8 converts 16-bit (0-65535) to 8-bit (0-255) for display
        "G:", green_brightness >> 8,
        "B:", blue_brightness >> 8, end="\r")

  time.sleep_ms(STEP_DELAY)


"""
Extension Activities

1.  Add blue channel control. Using two potentiometers to control
    red and green, adding buttons to control blue is easy. With
    only four buttons controlling red and green, you will need
    to decide how to handle blue. Some options:

    a) Derive blue automatically from red and green, for example:
       blue_brightness = 65535 - red_brightness - green_brightness
       (clamped to 0). How does this feel to use?

    b) Add a mode toggle: pressing SW2 and SW5 together switches
       between (red + green) mode and (blue + brightness) mode.

    c) Use one button each for red, green, and blue, making each
       button increase or decrease its colour value while it's 
       being held. Toggle the direction on every press and after
       a colour value reaches its maximum or minimum.

    Choose one approach and implement it, then observe which
    colours are easy or hard to produce.

2.  Write a 'fade_to(target_r, target_g, target_b, steps)'
    function that smoothly transitions from the current colour
    to a target colour over a given number of steps. Use it to
    create a colour sequence that cycles through a list of preset
    colours with smooth transitions between each:

  colours = (
    (65535,     0,     0),   # Red
    (65535, 32767,     0),   # Orange
    (65535, 65535,     0),   # Yellow
    (    0, 65535,     0),   # Green
    (    0,     0, 65535),   # Blue
    (65535,     0, 65535),   # Violet
  )

    The following code reads the sequence to extract each
    target colour:

  for colour in colour:
    target_r = colour[0]   # Next red colour target
    target_g = colour[1]   # Next green colour target
    target_b = colour[2]   # Next blue colour target
    fade_to(target_r, target_g, target_b, steps)

3.  NeoPixel preview: NeoPixels (WS2812B addressable LEDs) use
    the same RGB colour model as this project, but each LED in
    a strip is individually addressable over a single data wire
    using the 'neopixel' module. NeoPixels use 8-bit values
    (0-255) rather than 16-bit. To convert from this project's
    16-bit values to NeoPixel 8-bit values, shift right by 8:

      neopixel_value = rgb_value >> 8

    The HSV conversion and colour mixing concepts introduced in EA4,
    below, also apply directly to NeoPixel strips - the same
    'hsv_to_rgb()' function works, just with the output scaled
    to 0-255 using '>> 8' before passing to the NeoPixel library.

4.  HSV (Hue-Saturation-Value) colour mixing is more intuitive than
    direct RGB for many applications. Hue is expressed in degrees
    around the colour wheel (0=red, 120=green, 240=blue, 360=red
    again). Saturation controls vividness as a percentage (100=full
    colour, 0=white). Value controls overall brightness as a
    percentage (0=off, 100=full brightness).

    The following function converts HSV values to RGB duty cycles.
    Add it to your program and use RV1 to sweep hue and RV2 to
    control brightness (with saturation fixed at 100). Alternatively,
    use two buttons to control hue, and two to control brightness:

def hsv_to_rgb(h, s, v):
  # Convert HSV to RGB duty cycle values (0-65535).
  # h: hue in degrees (0-360)
  # s: saturation as a percentage (0-100)
  # v: brightness as a percentage (0-100)
  s = s / 100.0
  v = v / 100.0
  if s == 0.0:
    val = int(v * 65535)
    return val, val, val
  i = int(h / 60) % 6
  f = (h / 60) - int(h / 60)
  p = int(v * (1 - s) * 65535)
  q = int(v * (1 - s * f) * 65535)
  t = int(v * (1 - s * (1 - f)) * 65535)
  v = int(v * 65535)
  if i == 0: return v, t, p
  if i == 1: return q, v, p
  if i == 2: return p, v, t
  if i == 3: return p, q, v
  if i == 4: return t, p, v
  if i == 5: return v, p, q
  
    Call it in your main loop:

  hue        = beaper.RV1_level() / 65535
  brightness = beaper.RV2_level() / 65535
  r, g, b    = hsv_to_rgb(hue, 1.0, brightness)
  set_rgb(r, g, b)

    Trace through hsv_to_rgb() with h=0, h=120, and h=240 (all with
    s=100, v=100) and verify that the expected primary colours — red,
    green, and blue — appear on the LED.

"""