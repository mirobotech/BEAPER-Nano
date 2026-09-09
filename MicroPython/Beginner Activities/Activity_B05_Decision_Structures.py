# ================================================================================
# Beginner Activity 5: Decision Structures [Activity_B05_Decision_Structures.py]
# Version: 1.2
# Updated: September 8, 2026
#
# Platform: mirobo.tech BEAPER Nano circuit (any configuration)
# Requires: BEAPER_Nano.py board module file
# ================================================================================

# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32.
import BEAPER_Nano as beaper  # Set up BEAPER Nano I/O

import time

# --- Program Constants ----------------
MAX_COUNT = const(50)

# --- Program Variables ----------------
SW3_pressed = False
SW4_pressed = False
SW5_pressed = False
SW3_presses = 0
SW4_presses = 0
SW3_last = False
SW4_last = False

beaper.nano_led_on()  # Status LED on

while True:
  # Read pushbuttons
  SW3_pressed = (beaper.SW3.value() == 0)
  SW4_pressed = (beaper.SW4.value() == 0)
  SW5_pressed = (beaper.SW5.value() == 0)

  if SW3_pressed:
    beaper.LED2.value(1)
  else:
    beaper.LED2.value(0)

  time.sleep_ms(20)  # Short delay for button debouncing


# ================================================================================
# Guided Exploration
# ================================================================================
#
# Real programs rarely make simple yes/no decisions. Most interesting
# behaviour comes from choosing between multiple possibilities based
# on changing input conditions or values, and from comparing them with
# what has happened before.
#
# This activity introduces the if/elif chain - a way of expressing
# multi-way decisions - along with comparison operators, counting
# variables, and edge detection. Combined with the named variables and
# Boolean logic from Activity 4, these features make it possible to
# create programs with memory and multi-way judgment.
#
# --------------------------------------------------------------------------------
# GE 1 - Combining conditions with 'and'
# --------------------------------------------------------------------------------
#
# This program's button variables (SW3_pressed, SW4_pressed, etc.)
# hold True or False Boolean values, which means they can easily be
# combined using the Boolean logical operators 'and', 'or', and 'not'.
# For example, changing the if condition in the program to:
#
# Example code:
#
# if SW3_pressed and SW4_pressed:
#
# ...will light LED2 only when both SW3 and SW4 are pressed at the
# same time. Modify the if condition in your program to match this
# example and verify that it works as expected.
#
# --------------------------------------------------------------------------------
# GE 2 - The 'or' operator
# --------------------------------------------------------------------------------
#
# Replace the 'and' operator in the if condition with 'or' and run the
# program again. Does it work the way you would expect it to?
#
# --------------------------------------------------------------------------------
# GE 3 - The 'not' operator
# --------------------------------------------------------------------------------
#
# It's just as easy to invert an input to its opposite state using the
# logical 'not' operator. Predict how you think this conditional
# expression will behave:
#
# Example code:
#
# if SW3_pressed and not SW4_pressed:
#
# Try the condition in your program to verify your prediction.
#
# --------------------------------------------------------------------------------
# GE 4 - Counting button presses
# --------------------------------------------------------------------------------
#
# Let's make this program count the number of times SW3 is pressed.
# Start by reverting the if condition back to reading only the state
# of SW3.
#
# Next, add the 'SW3_presses += 1' compound operation inside
# the if block to accumulate SW3 presses. This is shorthand for
# 'SW3_presses = SW3_presses + 1' - it adds 1 to the current value and
# stores the result back into the same variable:
#
# Example code:
#
# if SW3_pressed:
#   beaper.LED2.value(1)
#   SW3_presses += 1
# else:
#   beaper.LED2.value(0)
#
# Add a print statement inside the if block to display the count in
# the console each time SW3 is pressed:
#
# Example code:
#
# if SW3_pressed:
#   beaper.LED2.value(1)
#   SW3_presses += 1
#   print("SW3_presses:", SW3_presses)
#
# Run the program, open the console, and press SW3 a few times. How
# quickly does the count increase? Does the count go up once per
# press, or faster? What do you think is happening?
#
# --------------------------------------------------------------------------------
# GE 5 - Comparison operators and if/elif chains
# --------------------------------------------------------------------------------
#
# Previous programs have used the '==' (equal to) conditional operator
# to check if two values are the same. MicroPython supports six
# comparison operators that can be used in if conditions:
#
# ==  equal to
# !=  not equal to
# <   less than
# >   greater than
# <=  less than or equal to
# >=  greater than or equal to
#
# Now add this set of if/elif conditions below the SW3 if block to
# display the count using the LEDs:
#
# Example code:
#
# # Light LEDs for different numbers of presses
# if SW3_presses >= 1:
#   beaper.LED3.value(1)
# elif SW3_presses >= 10:
#   beaper.LED4.value(1)
# elif SW3_presses >= MAX_COUNT:
#   beaper.LED5.value(1)
#
# The if/elif structure is a chain of conditional decisions. Starting
# with the first if, each condition is evaluated in turn until the
# first true condition is found. Once a true condition is found, its
# code runs and the rest of the chain is skipped entirely.
#
# Run the program and press SW3. LED3 should light after the first
# press - does it? Does LED4 light after ten presses? Using what you
# now know about how the chain works, can you explain why?
#
# Re-arrange the conditions so that the chain evaluates from the
# largest value down to the smallest, and add a reset block for SW5:
#
# Example code:
#
# # Light LEDs for different numbers of presses
# if SW3_presses >= MAX_COUNT:
#   beaper.LED5.value(1)
# elif SW3_presses >= 10:
#   beaper.LED4.value(1)
# elif SW3_presses >= 1:
#   beaper.LED3.value(1)
#
# # Reset the count
# if SW5_pressed:
#   SW3_presses = 0
#   beaper.LED3.value(0)
#   beaper.LED4.value(0)
#   beaper.LED5.value(0)
#
# Test the updated program. Does the LED behaviour now match what you
# would expect? Press SW5 to reset the count and confirm that all
# three LEDs turn off.
#
# Watch closely as the count climbs past 1 and past 10 - does the LED
# from an earlier range ever turn back off once a later range lights
# up, or do you end up with more than one LED lit at a time? If you
# wanted only the current range's LED to be lit at any moment, what
# would an elif branch need to do about the other LEDs, and how might
# an else at the end of the chain help?
#
# --------------------------------------------------------------------------------
# GE 6 - Edge detection
# --------------------------------------------------------------------------------
#
# You may have noticed that the counter increases very quickly - much
# faster than you are actually pressing the button. This is because
# the button state is read every loop cycle, so holding SW3 for even
# a fraction of a second registers dozens of counts.
#
# The solution is edge detection - counting a press only when the
# button transitions from not pressed to pressed. The program already
# declares SW3_last for exactly this purpose:
#
# Example code:
#
# # Detect a new SW3 press (not pressed to pressed transition)
# if SW3_pressed and not SW3_last:
#   SW3_presses += 1
#   beaper.LED2.value(1)
# else:
#   beaper.LED2.value(0)
#
# SW3_last must be updated at the end of each loop cycle, after all
# the button logic has run, so it correctly holds the previous loop's
# button state:
#
# Example code:
#
# # Save button states for next loop
# SW3_last = SW3_pressed
#
# Add both of these changes to your program. The print statement from
# GE 4 will now show exactly one count per press in the console,
# regardless of how long the button is held. This is a good example
# of using print() to verify that a fix is working correctly - once
# you are satisfied, the print statement can be removed or commented
# out.
#
# The SW4_last variable is also already declared for the same
# purpose. Can you add edge detection for SW4 as well?
#
# --------------------------------------------------------------------------------
# GE 7 - Comparing to Activity 4
# --------------------------------------------------------------------------------
#
# Remove the print statement from your program and run it to confirm
# everything still works correctly. Now think back to Activity 4,
# where pressing SW2 during the light pattern had no effect until the
# pattern finished. How is the approach in this activity different,
# and what makes edge detection better suited to counting presses
# accurately?


# ================================================================================
# Extension Activities
# ================================================================================
#
# The activities below build directly on the counting and edge
# detection techniques from the Guided Exploration. Use named
# variables and constants throughout, and use print() to help develop
# and debug your programs - removing or commenting out debugging
# output once you are satisfied that everything works correctly.
#
# --------------------------------------------------------------------------------
# EA 1 - Up/down counter with clamping
# --------------------------------------------------------------------------------
#
# Modify the press-counting program from the Guided Exploration so
# that pressing SW4 increases the count and pressing SW3 decreases it.
# Clamp the count so that it can never go below zero or above
# MAX_COUNT. Use the LEDs to display four ranges of the count value
# (off, low, medium, and high).
#
# --------------------------------------------------------------------------------
# EA 2 - Scrolling patterns
# --------------------------------------------------------------------------------
#
# Create a program that uses SW3 and SW4 as 'back' and 'forward'
# buttons to scroll through four different LED patterns, one per
# button press. Pressing SW4 should advance to the next pattern, and
# pressing SW3 should go back to the previous one. The sequence should
# wrap around - going past the last pattern returns to the first, and
# going before the first returns to the last.
#
# --------------------------------------------------------------------------------
# Project: Rapid-Clicker Game
# --------------------------------------------------------------------------------
#
# Looking for a bigger challenge that pulls these ideas together?
# B05_Rapid_Clicker_Project.py is a separate, open-ended project file
# that asks you to build a two-player clicking race, using
# edge-detected counters, an if/elif chain, and a Boolean game-state
# variable from this activity's own toolkit. It's provided as a
# skeleton with TODOs rather than a finished program - a good next
# step if you'd like to develop your skills more independently.