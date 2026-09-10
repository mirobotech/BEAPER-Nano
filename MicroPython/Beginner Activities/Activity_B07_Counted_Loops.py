# ================================================================================
# Beginner Activity 7: Counted Loops [Activity_B07_Counted_Loops.py]
# Version: 1.2
# Updated: September 10, 2026
#
# Platform: mirobo.tech BEAPER Nano circuit (any configuration)
# Requires: BEAPER_Nano.py board module file
# ================================================================================

# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32.
import BEAPER_Nano as beaper  # Set up BEAPER Nano I/O

import time

# --- Program Constants ----------------
FLASH_DELAY = const(100)
STEP_DELAY = const(300)

# --- Program Variables ----------------
SW5_pressed = False

beaper.nano_led_on()  # Status LED

# Wait for SW5 to begin
print("Press SW5 to begin...")
while not SW5_pressed:
  beaper.nano_led_toggle()
  time.sleep_ms(FLASH_DELAY)
  SW5_pressed = (beaper.SW5.value() == 0)

beaper.nano_led_on()
print("Starting!")

# Part 1: Repeat a done signal three times using a for loop
print("Part 1: for loop repeat")
for i in range(3):
  beaper.LED2.value(1)
  beaper.tone(4000, FLASH_DELAY)
  beaper.LED2.value(0)
  time.sleep_ms(FLASH_DELAY)

time.sleep_ms(STEP_DELAY)

# Part 2: Count up through LEDs using the loop variable
print("Part 2: count up")
for i in range(2, 6):
  print("  i =", i)
  beaper.LED2.value(1 if i >= 2 else 0)
  beaper.LED3.value(1 if i >= 3 else 0)
  beaper.LED4.value(1 if i >= 4 else 0)
  beaper.LED5.value(1 if i >= 5 else 0)
  time.sleep_ms(STEP_DELAY)

time.sleep_ms(STEP_DELAY)

# Part 3: Count down through LEDs using a negative step
print("Part 3: count down")
for i in range(5, 1, -1):
  print("  i =", i)
  beaper.LED2.value(1 if i >= 2 else 0)
  beaper.LED3.value(1 if i >= 3 else 0)
  beaper.LED4.value(1 if i >= 4 else 0)
  beaper.LED5.value(1 if i >= 5 else 0)
  time.sleep_ms(STEP_DELAY)

# All LEDs off
beaper.LED2.value(0)
beaper.LED3.value(0)
beaper.LED4.value(0)
beaper.LED5.value(0)
print("Done!")


# ================================================================================
# Guided Exploration
# ================================================================================
#
# In Activity 6, Extension Activity 1 asked you to replace three
# manual repetitions with a while loop. The while loop required
# you to manage a loop control variable yourself - initialize it,
# check it in the condition, and update it inside the loop body.
#
# The for loop structure is designed specifically for situations
# where the number of iterations is known in advance. It handles
# the initialize, check, and update steps automatically, leaving you
# to focus on what the loop body should do. This activity explores
# three forms of the for loop - range(n), range(start, stop), and
# range(start, stop, step) - and when to use each one.
#
# --------------------------------------------------------------------------------
# GE 1 - range(3) and the for loop
# --------------------------------------------------------------------------------
#
# Look at Part 1 of this program:
#
# Example code:
#
# for i in range(3):
#   beaper.LED2.value(1)
#   beaper.tone(4000, FLASH_DELAY)
#   beaper.LED2.value(0)
#   time.sleep_ms(FLASH_DELAY)
#
# The 'for i in range(3):' line tells MicroPython to run the loop
# body three times, automatically managing a loop index variable
# named 'i'. The range(3) function produces the sequence of values
# that always starts at 0, and in this case counts 0, 1, 2 - one
# for each iteration.
#
# You can verify the sequence by adding a print statement inside the
# loop to print the value of i on each iteration, like this:
#
# Example code:
#
# for i in range(3):
#   print("i =", i)
#   beaper.LED2.value(1)
#   ...
#
# Run the program and observe the console output. Does i have the
# values you expected? Compare this for loop with the while loop
# solution you wrote in Activity 6 Extension Activity 1. What does
# the for loop handle automatically that your while loop required
# you to do manually?
#
# --------------------------------------------------------------------------------
# GE 2 - range(start, stop) and conditional expressions
# --------------------------------------------------------------------------------
#
# GE 1 shows how the loop's index variable always starts at zero,
# which doesn't matter since its value isn't used by any other part
# of the program code - it's only used internally to count loop
# iterations.
#
# Part 2 of the program uses a two-argument form of range() that
# enables the index variable to be more useful outside of the loop:
#
# Example code:
#
# for i in range(2, 6):
#
# This tells MicroPython to start at 2 and stop before 6, producing
# the values 2, 3, 4, 5. This lets the loop index values match the LED
# numbers on the circuit board - a nice usability benefit!
#
# Look at how i is used inside the Part 2 loop body:
#
# Example code:
#
# beaper.LED2.value(1 if i >= 2 else 0)
# beaper.LED3.value(1 if i >= 3 else 0)
# beaper.LED4.value(1 if i >= 4 else 0)
# beaper.LED5.value(1 if i >= 5 else 0)
#
# Here, i is not just being counted - it is being used as meaningful
# data. Each line uses a conditional expression that reads 'A if
# condition, else B', and evaluates to A when the condition is True,
# and B when it's False. This is a compact way to choose between two
# values based on a comparison, and you'll see it used again in later
# activities.
#
# When i is 2, only LED2 is lit. For what other values is LED2 lit?
# Trace through all four values of i (2, 3, 4, 5) and describe which
# LEDs you expect to be lit for each value.
#
# Run the program to verify your prediction. Was it correct?
#
# --------------------------------------------------------------------------------
# GE 3 - range(start, stop, step)
# --------------------------------------------------------------------------------
#
# Part 3 uses a three-argument form of range():
#
# Example code:
#
# for i in range(5, 1, -1):
#
# The third argument is the step - the amount added to i after each
# iteration. A step of -1 counts downward. This produces the values
# 5, 4, 3, 2 - stopping before reaching 1.
#
# Why does the sequence stop at 2 and not at 1? What would you change
# to make it include 1 as well?
#
# Try replacing the step with -2 in Part 3:
#
# Example code:
#
# for i in range(5, 0, -2):
#
# What values does i take? What do the LEDs show? Add a print
# statement to verify your prediction.
#
# --------------------------------------------------------------------------------
# GE 4 - Naming the loop variable
# --------------------------------------------------------------------------------
#
# The loop variable in a for loop doesn't have to be named 'i'. That
# name is just a common convention, but any name works and a descriptive
# name is often preferable. In fact, if you don't need to use the loop
# variable at all (as in Part 1, where only the number of repetitions
# matters), Python convention is to use an underscore '_' as the
# variable name to signal that the value is intentionally ignored:
#
# Example code:
#
# for _ in range(3):
#   beaper.LED2.value(1)
#   beaper.tone(4000, FLASH_DELAY)
#   beaper.LED2.value(0)
#   time.sleep_ms(FLASH_DELAY)
#
# Replace 'i' with '_' in the Part 1 loop and verify that the program
# still works identically. When should you choose to use a meaningful
# name like 'i' or 'count' instead of '_'?
#
# As a preview of something you'll explore in the intermediate
# activities: MicroPython's for loop can iterate over any sequence,
# not just a range of numbers. The BEAPER_Nano.py board module
# defines a list of LED objects called LEDS, so you can write:
#
# Example code:
#
# for led in beaper.LEDS:
#   led.value(1)
#   time.sleep_ms(STEP_DELAY)
#
# ...and the loop will visit each LED in turn without needing a range
# or an index variable at all, or even knowing how many there are!
#
# A string is a sequence too, and you can iterate over each character
# in a string the same way each led in LEDS was, above:
#
# Example code:
#
# for char in "abc":
#   print(char)
#
# Try it. How many times does the loop run? What does each iteration
# print? You'll use this exact pattern - iterating directly over a
# string of symbols - in this activity's project.
#
# Lists (like beaper.LEDS above) are introduced in the intermediate
# activities, but string iteration is fair game any time you need it.
#
# --------------------------------------------------------------------------------
# GE 5 - for vs. while
# --------------------------------------------------------------------------------
#
# A for loop and a while loop can often solve the same problem. Here
# is the Part 1 for loop rewritten as a while loop:
#
# Example code:
#
# count = 0
# while count < 3:
#   beaper.LED2.value(1)
#   beaper.tone(4000, FLASH_DELAY)
#   beaper.LED2.value(0)
#   time.sleep_ms(FLASH_DELAY)
#   count += 1
#
# And here is a while loop equivalent for the Part 2 for loop:
#
# Example code:
#
# i = 2
# while i < 6:
#   beaper.LED2.value(1 if i >= 2 else 0)
#   beaper.LED3.value(1 if i >= 3 else 0)
#   beaper.LED4.value(1 if i >= 4 else 0)
#   beaper.LED5.value(1 if i >= 5 else 0)
#   time.sleep_ms(STEP_DELAY)
#   i += 1
#
# Both approaches produce identical results. When would you choose a
# for loop over a while loop, and when would a while loop be the
# better choice? Think about what each one communicates to someone
# reading your code.
#
# --------------------------------------------------------------------------------
# GE 6 - Nested for loops
# --------------------------------------------------------------------------------
#
# A for loop can be placed inside another for loop - this is called
# nesting. Here is a simple example to try:
#
# Example code:
#
# for led in range(2, 6):
#   for flash in range(led - 1):
#     beaper.LED2.value(1 if led >= 2 else 0)
#     beaper.LED3.value(1 if led >= 3 else 0)
#     beaper.LED4.value(1 if led >= 4 else 0)
#     beaper.LED5.value(1 if led >= 5 else 0)
#     time.sleep_ms(FLASH_DELAY)
#     beaper.LED2.value(0)
#     beaper.LED3.value(0)
#     beaper.LED4.value(0)
#     beaper.LED5.value(0)
#     time.sleep_ms(FLASH_DELAY)
#   time.sleep_ms(STEP_DELAY)
#
# Before running it, trace through the loop values and predict what
# you will see. For each value of 'led', how many times does the
# inner loop run? What does the pattern look like?
#
# Run the program to check your prediction. Print both loop variables
# to the console to help verify your understanding of what is
# happening at each step.


# ================================================================================
# Extension Activities
# ================================================================================
#
# For loops are the right tool when the number of iterations is known
# in advance. Before starting each program below, think about which
# loop type fits each part of the problem - a for loop where the
# count is fixed, and a while loop where the program needs to wait
# for something to happen or respond to changing conditions.
#
# --------------------------------------------------------------------------------
# EA 1 - Rewrite Activity 6 with counted loops
# --------------------------------------------------------------------------------
#
# Rewrite the Activity 6 starter program, replacing only the parts
# that are naturally expressed as counted loops. The wait-for-SW5
# loop should remain a while loop - explain in a comment why it
# cannot be replaced with a for loop. The countdown should become a
# for loop using range() with a negative step, and the done signal
# should become a for loop using range(3).
#
# How much shorter is the rewritten version compared to the
# Activity 6 original? Which version do you find easier to read?
#
# --------------------------------------------------------------------------------
# EA 2 - Animated bar graph
# --------------------------------------------------------------------------------
#
# Create an LED bar graph that fills from left to right and then
# empties from right to left, repeating continuously. Use two for
# loops - one to fill and one to empty - and adjust the step delay to
# find a speed that looks smooth.
#
# Extend the program so that SW4 speeds up the animation and SW3
# slows it down, using a variable delay that changes with each button
# press. What minimum and maximum values make sense?
#
# --------------------------------------------------------------------------------
# EA 3 - Structured LED display
# --------------------------------------------------------------------------------
#
# Use nested for loops to create a structured LED display. The outer
# loop should select each LED in sequence (LED2 through LED5), and
# the inner loop should flash that LED a number of times equal to its
# position in the sequence (LED2 flashes once, LED3 flashes twice,
# LED4 three times, LED5 four times). Add a short pause between each
# LED's flashes and a longer pause between LEDs.
#
# Once this works, add a second pass in reverse order using a second
# pair of nested loops, so the full sequence goes 1-2-3-4 flashes and
# then 4-3-2-1 flashes before repeating.
#
# --------------------------------------------------------------------------------
# EA 4 - Binary counter
# --------------------------------------------------------------------------------
#
# Create a binary counter that uses the four LEDs to display the
# binary representation of numbers from 0 to 15. Use a for loop to
# count from 0 to 15, and for each value light the LEDs to show its
# binary representation:
#
#  - LED2 represents the 1s place (bit 0)
#  - LED3 represents the 2s place (bit 1)
#  - LED4 represents the 4s place (bit 2)
#  - LED5 represents the 8s place (bit 3)
#
# Hint: MicroPython's bitwise AND operator '&' and right-shift
# operator '>>' can help extract individual bits from a number:
#
# Example code:
#
# for i in range(16):
#   beaper.LED2.value((i >> 0) & 1)  # bit 0
#   beaper.LED3.value((i >> 1) & 1)  # bit 1
#   beaper.LED4.value((i >> 2) & 1)  # bit 2
#   beaper.LED5.value((i >> 3) & 1)  # bit 3
#   time.sleep_ms(STEP_DELAY)
#
# Use print to display each number's decimal value and its binary
# representation in the console alongside the LED display. What is
# the highest number the four LEDs can represent?
#
# --------------------------------------------------------------------------------
# Project: Morse Code
# --------------------------------------------------------------------------------
#
# Looking for a bigger challenge that pulls these ideas together?
# B07_Morse_Code_Project.py is a separate, open-ended project file
# that asks you to encode a message of your choice as Morse code
# using LED flashes and tones, iterating over a sequence with a for
# loop. It's provided as a skeleton with TODOs rather than a finished
# program - a good next step if you'd like to build your skills and
# design your own program.