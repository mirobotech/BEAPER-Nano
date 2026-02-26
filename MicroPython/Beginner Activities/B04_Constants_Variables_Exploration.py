"""
================================================================================
Beginner Activity 4 Exploration: Constants and Variables
[B04_Constants_Variables_Exploration.py]
February 26, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPER_Nano.py board module file.
================================================================================
"""
# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32
import BEAPER_Nano as beaper

import time

# --- Program Constants ----------------
SLOW_DELAY = const(200)
MEDIUM_DELAY = const(100)
FAST_DELAY = const(50)
LUDICROUS_DELAY = const(25)

# --- Program Variables ----------------
SW2_pressed = False
display_pattern = False
blink_delay_ms = 200

beaper.nano_led_on()

while True:
  # Check pushbuttons
  slow_button = (beaper.SW2.value() == 0)
  medium_button = (beaper.SW3.value() == 0)
  fast_button = (beaper.SW4.value() == 0)
  ludicrous_button = (beaper.SW5.value() == 0)

  if slow_button:
    blink_delay_ms = SLOW_DELAY
    display_pattern = True

  if medium_button:
    blink_delay_ms = MEDIUM_DELAY
    display_pattern = True

  if fast_button:
    blink_delay_ms = FAST_DELAY
    display_pattern = True

  if ludicrous_button:
    blink_delay_ms = LUDICROUS_DELAY
    display_pattern = True

  # Show the pattern
  if display_pattern:
    beaper.LED2.value(1)
    time.sleep_ms(blink_delay_ms)
    beaper.LED3.value(1)
    time.sleep_ms(blink_delay_ms)
    beaper.LED4.value(1)
    time.sleep_ms(blink_delay_ms)
    beaper.LED5.value(1)
    time.sleep_ms(blink_delay_ms)
    beaper.LED2.value(0)
    time.sleep_ms(blink_delay_ms)
    beaper.LED3.value(0)
    time.sleep_ms(blink_delay_ms)
    beaper.LED4.value(0)
    time.sleep_ms(blink_delay_ms)
    beaper.LED5.value(0)
    time.sleep_ms(blink_delay_ms)
    display_pattern = False


"""
Guided Exploration

This program extends the concepts from Activity_B04_Constants_Variables.py
— multiple constants, multiple named button variables, and a variable
delay that changes at runtime. If you haven't already read through
the code above and made a prediction about what each button does,
do that before running the program.

1.  Run the program and press each button. Does the behaviour match
    your prediction? Which characteristics of the code made the
    program's behaviour easiest to predict before running it?

    Add print statements to display the values of blink_delay_ms and
    display_pattern at key points in the loop — for example, each
    time a button is pressed and each time the pattern starts and
    finishes. Open the console in your editor and observe the output
    as you press different buttons.

    Can you see display_pattern cycling between True and False as
    the pattern runs? Which button sets which delay value?

2.  blink_delay_ms is defined by assigning it a value directly,
    without const(). How does MicroPython know that SLOW_DELAY and
    the other similarly defined names are constants, while
    blink_delay_ms is a variable? What does const() actually tell
    MicroPython, and what would happen if you tried to assign a new
    value to SLOW_DELAY while the program was running?

3.  Predict what will happen if two buttons are pressed at the same
    time. Try it! Was your prediction correct? Trace through the
    program code to explain why this happens.

    When you are done exploring this program, return to
    Activity_B04_Constants_Variables.py for the Extension Activities.

"""