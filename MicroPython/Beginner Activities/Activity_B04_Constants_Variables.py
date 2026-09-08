# ================================================================================
# Beginner Activity 4: Constants and Variables [Activity_B04_Constants_Variables.py]
# Version: 1.2
# Updated: September 7, 2026
#
# Platform: mirobo.tech BEAPER Nano circuit (any configuration)
# Requires: BEAPER_Nano.py board module file
# ================================================================================

# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32.
import BEAPER_Nano as beaper  # Set up BEAPER Nano I/O

import time

# --- Program Constants ----------------
BLINK_DELAY = const(200)

# --- Program Variables ----------------
SW2_pressed = False
display_pattern = False

beaper.nano_led_on()  # Use Arduino Nano ESP32's LED as a status indicator

while True:
  SW2_pressed = (beaper.SW2.value() == 0)

  # Start pattern with SW2 press
  if SW2_pressed:
    display_pattern = True

  # Show pattern on LEDs
  if display_pattern:
    beaper.LED2.value(1)
    time.sleep_ms(BLINK_DELAY)
    beaper.LED3.value(1)
    time.sleep_ms(BLINK_DELAY)
    beaper.LED4.value(1)
    time.sleep_ms(BLINK_DELAY)
    beaper.LED5.value(1)
    time.sleep_ms(BLINK_DELAY)
    beaper.LED2.value(0)
    time.sleep_ms(BLINK_DELAY)
    beaper.LED3.value(0)
    time.sleep_ms(BLINK_DELAY)
    beaper.LED4.value(0)
    time.sleep_ms(BLINK_DELAY)
    beaper.LED5.value(0)
    time.sleep_ms(BLINK_DELAY)
    display_pattern = False

  time.sleep_ms(20)  # Short delay for button debouncing


# ================================================================================
# Guided Exploration
# ================================================================================
#
# Good programs are written for two audiences: the computer that runs
# them and the people who read them. Constants, variables, and
# meaningful names are how programmers communicate intent to others -
# not just about what the code does, but why it does it. The concepts
# introduced in this activity will make your programs easier to read,
# easier to change, and easier to debug.
#
# This activity introduces two new ideas: named constants, which hold
# a value that never changes while the program runs, and variables,
# whose values do change - including Boolean variables, which store a
# simple True/False state. You'll also see how print() can reveal what
# a variable's value is at a specific moment, one of the most useful
# tools for understanding and debugging your own programs.
#
# --------------------------------------------------------------------------------
# GE 1 - Program constants
# --------------------------------------------------------------------------------
#
# There are several new concepts in this program, so let's start with
# the simplest one - program constants:
#
# Example code:
#
# # --- Program Constants ----------------
# BLINK_DELAY = const(200)
#
# A program constant is a named, unchanging value used in place of a
# number in a program. Here, 'BLINK_DELAY' is defined as a constant
# with a value of 200. This value will not change while the program
# runs. (The names of constants are written in ALL_CAPS by convention,
# to distinguish them from variables.)
#
# Using a named constant instead of a bare number provides two
# important benefits. First, the name 'BLINK_DELAY' is descriptive -
# it tells anyone reading the program what 200 actually means. Second,
# every part of the program that uses BLINK_DELAY can be updated
# simply by changing one value at the top of the program.
#
# Run the program and observe the blink rate. Then change BLINK_DELAY
# to 100 and run it again, then try 50. Think about how much longer
# it would have taken to update every sleep_ms() call individually.
#
# BLINK_DELAY holds an integer value - a whole number, positive or
# negative. The SW2_pressed variable (introduced below) will hold a
# Boolean value - either True or False. A third common type, float,
# is used for numbers with decimal parts (for example, 3.14159).
# MicroPython infers the type of a constant or variable from the
# value assigned to it, while many other languages require the type
# to be declared explicitly.
#
# --------------------------------------------------------------------------------
# GE 2 - Boolean variables
# --------------------------------------------------------------------------------
#
# The second concept introduced here is the use of Boolean variables.
# Variables are named like constants, but their values are expected
# to change as the program runs. This program defines two variables:
#
# Example code:
#
# # --- Program Variables ----------------
# SW2_pressed = False
# display_pattern = False
#
# Both variables start as False, but will switch between True and False
# while the program runs. Since the result of an if condition is either
# True or False, Boolean variables can be a useful shortcut in if
# conditions. Instead of writing:
#
# Example code:
#
# if display_pattern == True:
#
# the program uses:
#
# Example code:
#
# if display_pattern:
#
# Both mean the same thing - the second simply uses the variable's
# own True or False state directly, without needing the separate
# comparison to True or False. The Boolean variable is already True
# or False.
#
# Explain which part of the program sets display_pattern to True, and
# which part resets it to False.
#
# --------------------------------------------------------------------------------
# GE 3 - Debugging with print()
# --------------------------------------------------------------------------------
#
# Sometimes you need to see what your program is doing to understand if it's
# working properly. Printing the current value of a variable to the terminal
# at a specific moment in time is one way to do that. MicroPython's built-in
# print() function sends text to the console in your editor, making it one of
# the most useful tools for understanding and debugging programs.
#
# Add this line inside the 'if SW2_pressed:' block to print the value
# of display_pattern each time SW2 is pressed:
#
# Example code:
#
# if SW2_pressed:
#   display_pattern = True
#   print("display_pattern:", display_pattern)
#
# Run the program, open the console in your editor, and press SW2. Do
# you see the output you expected?
#
# Now add a second print statement inside the 'if display_pattern:'
# block, just before 'display_pattern = False', to show the moment it
# resets:
#
# Example code:
#
# print("display_pattern reset to:", False)
#
# You'll see print() used again in the next activity. Revealing variable
# state at key moments is one of the most practical debugging techniques
# you can use.
#
# --------------------------------------------------------------------------------
# GE 4 - The SW2_pressed variable
# --------------------------------------------------------------------------------
#
# The SW2_pressed variable is assigned using this statement:
#
# Example code:
#
# SW2_pressed = (beaper.SW2.value() == 0)
#
# SW2 is read and compared with 0 because it is wired as an
# active-low input. If SW2 reads 0, the expression evaluates to True
# and SW2_pressed becomes True - which, in turn, enables it to be used
# directly in any if condition.
#
# The name SW2_pressed carries meaning: it will be True only when SW2
# is actually being pressed. This makes the if condition that follows
# the switch input clear and unambiguous:
#
# Example code:
#
# if SW2_pressed:
#
# A programmer reading this code doesn't need to know whether the
# switch is active-high or active-low - that detail is handled once,
# at the top of the loop, and hidden behind a meaningful variable name.
#
# Could the program use a similar approach to detect a button being
# released? Write an appropriate variable name and expression that
# would be True only when SW2 is not being pressed.
#
# --------------------------------------------------------------------------------
# GE 5 - Looking ahead to Exploration
# --------------------------------------------------------------------------------
#
# The program so far uses a single constant and two Boolean
# variables. The next file, B04_Constants_Variables_Exploration.py,
# extends these ideas with multiple constants, multiple named button
# variables, and a variable delay that changes at runtime.
#
# Before loading and running that program, read through its code and
# try to predict what each button will do and how the program works.
# Which parts of the code made your prediction easier?


# ================================================================================
# Extension Activities
# ================================================================================
#
# The programs you write from here on should use named constants and
# variables from the start - choose names that describe what a value
# represents, not just what type it is. A name like 'SW2_pressed'
# tells a reader far more than 'button' or 'b2'. Treat naming as part
# of program design, not as an afterthought.
#
# --------------------------------------------------------------------------------
# EA 1 - Start/Stop buttons
# --------------------------------------------------------------------------------
#
# Re-create the Start-Stop pushbutton program from Activity 3 using
# named button variables and a logical variable for the machine
# state. (Activity 3's Start-Stop problem is re-printed, below.)
#
# Create a program that simulates the 'Start' and 'Stop' buttons
# found on large industrial machines. The machine (simulated by an
# LED) should turn on when the 'Start' button is pressed and remain
# on until the 'Stop' button is pressed. Ensure that the machine
# cannot be turned on while the Stop button is being pressed.
#
# --------------------------------------------------------------------------------
# EA 2 - Toggle button
# --------------------------------------------------------------------------------
#
# Create the code for a toggle button - a type of switch behaviour
# that uses a single button to alternately turn a device on and off.
# The output should only change when the button transitions from not
# pressed to pressed, so holding the button should not cause repeated
# toggling.
#
# You will need three variables: one for the current LED state, one
# for the current button state, and one for the previous button
# state. Start a new program with something like:
#
# Example code:
#
# LED2_on = False
# toggle_pressed = False
# toggle_last = False
#
# At the end of each loop, save the current value of toggle_pressed into
# toggle_last before reading the new button state. A toggle should only
# happen when toggle_pressed is True and toggle_last was False - meaning
# a new press has just occurred.
#
# --------------------------------------------------------------------------------
# EA 3 - Per-button toggles
# --------------------------------------------------------------------------------
#
# Extend the toggle button program from EA 2 so that each pushbutton
# toggles its corresponding LED, allowing any combination of LEDs to
# be set simply by pressing each of BEAPER Nano's individual buttons.
#
# --------------------------------------------------------------------------------
# EA 4 - Bicycle turn signal
# --------------------------------------------------------------------------------
#
# Re-create the bicycle turn signal circuit from Activity 3 using
# named button variables and logical variables for the turn signal
# state.
#
# The circuit uses four LEDs in a row, just like your circuit, controlled
# by two pushbuttons on the bicycle's handlebars. Write a program to simulate
# the turn signal using one or more of BEAPER Nano's LEDs to indicate a left
# or right turn while the corresponding button is held.
#
# For an extra challenge, add brake functionality or a bell/horn feature.
# Can you make the brake or horn operate while the turn signal is active?
# What makes doing this so difficult?
#
# --------------------------------------------------------------------------------
# Project: LED Level Indicator
# --------------------------------------------------------------------------------
#
# Are you looking for a bigger challenge that pulls all of these ideas
# together? B04_Level_Indicator_Project.py is a separate, open-ended
# project file that asks you to build a four-LED bar graph controlled by
# two buttons, using named constants and the edge-detection pattern from
# EA 2 (toggle). It's provided as a skeleton with TODOs rather than as a
# finished program, and is a good next step if you'd like to complete a
# program on your own instead of following guided steps.