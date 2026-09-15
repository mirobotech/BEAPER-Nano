# ================================================================================
# Project: RGB Controller [B10_RGB_Controller_Project.py]
# Version: 1.2
# Updated: September 14, 2026
#
# Platform: mirobo.tech BEAPER Nano circuit (any configuration)
# Requires: BEAPER_Nano.py board module file
#
# Before starting this project, re-read GE 1 from Activity 10:
# Analog Output, and GE 2 (map_range()) from Activity 9: Analog Input.
#
# The Arduino Nano ESP32 module includes a built-in RGB LED driven
# by three independent PWM channels - one each for red, green, and
# blue. Mixing these three channels at different intensities produces
# a wide range of colours.
#
# The board module provides three functions for setting each channel:
#   beaper.nano_rgb_red(brightness)    # 0-100, 0=off, 100=full
#   beaper.nano_rgb_green(brightness)  # 0-100, 0=off, 100=full
#   beaper.nano_rgb_blue(brightness)   # 0-100, 0=off, 100=full
#
# Note: the RGB LED elements are active-LOW in hardware - a lower
# duty cycle produces more light. The board module's functions handle
# this inversion automatically, so 0 always means off and 100 always
# means full brightness.
#
# Colour mixing reference:
#   Red   only          = Red
#   Green only          = Green
#   Blue  only          = Blue
#   Red + Green         = Yellow
#   Red + Blue          = Magenta
#   Green + Blue        = Cyan
#   Red + Green + Blue  = White (or near-white)
#
# Controls:
#   RV1 - red channel brightness (if pots installed)
#   RV2 - green channel brightness (if pots installed)
#   SW2/SW3 - step red channel down/up (if no pots)
#   SW4/SW5 - step green channel down/up (if no pots)
#
# ================================================================================

# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32.
import BEAPER_Nano as beaper  # Set up BEAPER Nano I/O

import time

# --- Program Configuration ------------
POTS_INSTALLED = False                # Set True if RV1 and RV2 are installed

# --- Program Constants ----------------
STEP_DELAY    = 20                    # Main loop delay (ms)
COLOUR_STEP   = 4                     # Brightness change per button press

# --- Program Variables ----------------
red_brightness   = 0                  # Current red channel (0-100)
green_brightness = 0                  # Current green channel (0-100)
blue_brightness  = 0                  # Current blue channel (0-100)


# --- Program Functions ----------------

def map_range(value, in_min, in_max, out_min, out_max):
  # Map a value from one range to another, returning a float result.
  # Use int(map_range(...)) when an integer result is required.
  # See Activity 9, GE 2 for a full explanation of this function.
  return out_min + (value - in_min) * (out_max - out_min) / (in_max - in_min)

def set_rgb(red, green, blue):
  # Set the RGB LED to the given red, green, and blue brightness values.
  # Clamps each value to 0-100 before applying.
  red   = max(0, min(100, red))
  # TODO: Clamp green, blue values to 0-100 range
  beaper.nano_rgb_red(red)
  # TODO: Set green, blue RGB LED intensity

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

while True:
  SW2_pressed = beaper.SW2.value() == 0
  SW3_pressed = beaper.SW3.value() == 0
  SW4_pressed = beaper.SW4.value() == 0
  SW5_pressed = beaper.SW5.value() == 0

  if POTS_INSTALLED:
    red_brightness   = int(map_range(beaper.RV1_level(), 0, 65535, 0, 100))
    # TODO: set green_brightness or blue_brightness from RV2
  else:
    if SW2_pressed:
      red_brightness -= COLOUR_STEP
    elif SW5_pressed:
      red_brightness += COLOUR_STEP
    # TODO: set green_brightness or blue_brightness using SW3/SW4

  # Clamp here, not just inside set_rgb(), so held buttons can't push
  # the stored brightness values past 0-100 while the LED itself
  # appears maxed out - otherwise many presses would be needed to
  # bring an overshot value back into range before the LED responds.
  red_brightness   = max(0, min(100, red_brightness))
  # TODO: clamp green_brightness, blue_brightness to 0-100 range

  set_rgb(red_brightness, green_brightness, blue_brightness)
  print("R:", red_brightness, "G:", green_brightness, "B:", blue_brightness, end="\r")

  time.sleep_ms(STEP_DELAY)


# ================================================================================
# Extension Activities
# ================================================================================
#
# --------------------------------------------------------------------------------
# EA 1 - Complete the skeleton
# --------------------------------------------------------------------------------
#
# Complete the set_rgb function to clamp and set the green and
# blue LED intensities. This program controls two of the three red,
# green, and blue LED elements using either two potentiometers, or
# two sets of up/down pushbuttons (EA 2, below, lets you configure
# a method to control all three). Complete the missing sections of
# the main while loop to control the green channel, as described in
# Controls above.
#
# --------------------------------------------------------------------------------
# EA 2 - Add blue channel control
# --------------------------------------------------------------------------------
#
# Add blue channel control. Using two potentiometers to control
# red and green, adding buttons to control blue is easy. With
# only four buttons controlling red and green, you will need
# to decide how to handle blue. Some options:
#
# a) Derive blue automatically from red and green, for example:
#    blue_brightness = 100 - red_brightness - green_brightness
#    (clamped to 0). How does this feel to use?
#
# b) Add a mode toggle: pressing SW2 and SW5 together switches
#    between (red + green) mode and (blue + brightness) mode.
#
# c) Use one button each for red, green, and blue, making each
#    button increase or decrease its colour value while it's
#    being held. Toggle the direction on every press and after
#    a colour value reaches its maximum or minimum.
#
# Choose one approach and implement it, then observe which
# colours are easy or hard to produce.
#
# --------------------------------------------------------------------------------
# EA 3 - fade_to() and a colour sequence
# --------------------------------------------------------------------------------
#
# Write a 'fade_to(target_r, target_g, target_b, steps)'
# function that smoothly transitions from the current colour
# to a target colour over a given number of steps. Use it to
# create a colour sequence that cycles through a list of preset
# colours with smooth transitions between each:
#
# Example code:
#
# colours = (
#   (100,   0,   0),   # Red
#   (100,  50,   0),   # Orange
#   (100, 100,   0),   # Yellow
#   (  0, 100,   0),   # Green
#   (  0,   0, 100),   # Blue
#   (100,   0, 100),   # Violet
# )
#
# The following code reads the sequence to extract each
# target colour:
#
# Example code:
#
# for colour in colours:
#   target_r = colour[0]   # Next red colour target
#   target_g = colour[1]   # Next green colour target
#   target_b = colour[2]   # Next blue colour target
#   fade_to(target_r, target_g, target_b, steps)
#
# --------------------------------------------------------------------------------
# EA 4 - NeoPixel preview
# --------------------------------------------------------------------------------
#
# NeoPixels (WS2812B addressable LEDs) use the same RGB colour
# model as this project, but each LED in a strip is individually
# addressable over a single data wire using the 'neopixel' module.
# NeoPixels use 8-bit values (0-255) rather than this project's
# 0-100 range. To convert a 0-100 brightness value to a NeoPixel
# 0-255 value, scale it with multiplication and division:
#
# Example code:
#
# neopixel_value = value * 255 // 100
#
# The HSV conversion and colour mixing concepts introduced in EA 5,
# below, also apply directly to NeoPixel strips - colour.py's
# 'hsv_to_rgb()' function already returns values in the 0-255 range
# NeoPixels expect, with no conversion needed at all.
#
# --------------------------------------------------------------------------------
# EA 5 - HSV colour mixing
# --------------------------------------------------------------------------------
#
# HSV (Hue-Saturation-Value) colour mixing is more intuitive than
# direct RGB for many applications. Hue is expressed in degrees
# around the colour wheel (0=red, 120=green, 240=blue, 360=red
# again). Saturation controls vividness as a percentage (100=full
# colour, 0=white). Value controls overall brightness as a
# percentage (0=off, 100=full brightness).
#
# Rather than writing this conversion yourself, this project uses
# the 'hsv_to_rgb()' function from colour.py - a standalone module
# also used by the NeoPixel capstone project. Copy colour.py
# alongside this program, then import it and open it in your editor
# to read through 'hsv_to_rgb()' while you work through this section:
#
# Example code:
#
# import colour
#
# Add this near the top of your program, with the other imports.
#
# colour.py's 'hsv_to_rgb()' takes the same h, s, and v arguments
# described above, but - unlike this project's RGB LED, which uses
# 0-100 - it returns red, green, and blue values in the 0-255 range,
# matching the convention most colour hardware (including NeoPixels)
# actually uses. Before calling set_rgb(), each value needs to be
# scaled down from 0-255 to 0-100:
#
# Example code:
#
# hue        = int(map_range(beaper.RV1_level(), 0, 65535, 0, 360))
# brightness = int(map_range(beaper.RV2_level(), 0, 65535, 0, 100))
# r, g, b    = colour.hsv_to_rgb(hue, 100, brightness)
# set_rgb(r * 100 // 255, g * 100 // 255, b * 100 // 255)
#
# Add this to your main loop (with saturation fixed at 100), using
# RV1 to sweep hue and RV2 to control brightness. Alternatively, use
# two buttons to control hue, and two to control brightness.
#
# Notice that 'hue' and 'brightness' are both wrapped in 'int()'
# before being used - map_range() always returns a float (Activity 9,
# GE 2), but 'hsv_to_rgb()' expects integer arguments, and dividing
# with '/' inside it would produce further float values that its
# '//' operations aren't designed to handle. Try removing one of the
# 'int()' calls and observe what happens - does the LED still respond
# correctly?
#
# Open colour.py and trace through 'hsv_to_rgb()' with h=0, h=120,
# and h=240 (all with s=100, v=100) and verify that the expected
# primary colours - red, green, and blue - appear on the LED after
# the 0-255-to-0-100 conversion above.
#
# colour.py also provides 'hsv_to_rgbw()' and 'rgb_to_rgb565()' for
# working with RGBW NeoPixel strips and colour LCD displays. Since
# NeoPixels expect 0-255 values directly (see EA 3), a future NeoPixel
# project can call colour.py's functions and use their output
# unscaled - the 0-255-to-0-100 conversion shown here is needed only
# because this project's RGB LED happens to use a 0-100 range.
