# ================================================================================
# Beginner Activity 4 Project: LED Level Indicator
# [B04_Level_Indicator_Project.py]
# Version: 1.2
# Updated: September 7, 2026
#
# Platform: mirobo.tech BEAPER Nano circuit (any configuration)
# Requires: BEAPER_Nano.py board module file
# ================================================================================

# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32.
import BEAPER_Nano as beaper  # Set up BEAPER Nano I/O

import time

# ================================================================================
# LED Level Indicator
# ================================================================================
#
# Many real devices - volume controls, brightness dials, battery
# gauges - show a level using a row of lights instead of a number.
# This project lets you build one, using BEAPER Nano's four LEDs
# as a simple bar graph.
#
# Your level indicator should:
#
#  - Use SW4 to increase and SW3 to decrease a 'level' variable
#    ranging from 0 to 4.
#  - Use edge-detection - the same _pressed/_last pattern from this
#    activity's EA 2 - so holding a button changes the level once per
#    press, not repeatedly while it's held.
#  - Keep the level from going below 0 or above 4.
#  - Light LEDs cumulatively to show the current level as a bar graph:
#    level 1 lights LED2 only, level 2 lights LED2 and LED3, and so on
#    up to level 4, which lights all four LEDs. Level 0 lights none.
#
# Stretch goals:
#
#  - Add a SCALE value to represent an alternate range - a volume
#    level from 0 to 20 in steps of 5, or a battery percentage from
#    0 to 100 in steps of 25, for example - without changing anything
#    else in your program. (See the hints in the TODOs.)
#  - Play a short tone each time the level changes, using a different
#    frequency for each level.
#  - Briefly blink the top or bottom LED when a button press would
#    push the level past its minimum or maximum, to signal the limit
#    was reached.
#  - For an extra challenge, explore the RGB LED functions in
#    BEAPER_Nano.py (introduced in Activity B01) and use them to
#    shift the RGB LED's colour as the level changes - green at low
#    levels, red at high levels, for example.

# --- Program Constants ----------------
LEVEL_MIN = const(0)
LEVEL_MAX = const(4)
# TODO: Define a named SCALE constant for converting level into a
# displayed value.

# --- Program Variables ----------------
level = 0
up_pressed = False
up_last = False
down_pressed = False
down_last = False

beaper.nano_led_on()  # Use Arduino Nano ESP32's LED as a status indicator

while True:
  up_pressed = (beaper.SW4.value() == 0)
  down_pressed = (beaper.SW3.value() == 0)

  # TODO: Increase level by 1 when up_pressed is True and up_last was
  # False - but only if level is below LEVEL_MAX. Update up_last, and
  # print() the new displayed value (level * SCALE).

  # TODO: Decrease level by 1 when down_pressed is True and down_last
  # was False - but only if level is above LEVEL_MIN. Update
  # down_last, and print() the new displayed value (level * SCALE).

  # TODO: Light LED2 through LED5 based on the current level, using
  # four independent if conditions (not elif) so each LED lights when
  # level is at least as high as its position in the bar graph.

  time.sleep_ms(20)  # Short delay for button debouncing