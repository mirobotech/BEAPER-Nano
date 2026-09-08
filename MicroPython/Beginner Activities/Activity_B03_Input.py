# ================================================================================
# Beginner Activity 3: Digital Input [Activity_B03_Input.py]
# Version: 1.2
# Updated: September 7, 2026
#
# Platform: mirobo.tech BEAPER Nano circuit (any configuration)
# Requires: BEAPER_Nano.py board module file
# ================================================================================

# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32.
import BEAPER_Nano as beaper  # Set up BEAPER Nano I/O

import time

beaper.nano_led_on()  # Use Arduino Nano ESP32's LED as a status indicator

while True:
  # Momentary button SW2
  if beaper.SW2.value() == 0:
    beaper.LED2.value(1)
  else:
    beaper.LED2.value(0)

  # Start a pattern
  if beaper.SW5.value() == 0:
    beaper.LED2.value(1)
    time.sleep(0.2)
    beaper.LED3.value(1)
    time.sleep(0.2)
    beaper.LED4.value(1)
    time.sleep(0.2)
    beaper.LED5.value(1)
    time.sleep(0.2)
    beaper.LED2.value(0)
    time.sleep(0.2)
    beaper.LED3.value(0)
    time.sleep(0.2)
    beaper.LED4.value(0)
    time.sleep(0.2)
    beaper.LED5.value(0)
    time.sleep(0.2)

  time.sleep_ms(20)  # Short delay for button debouncing


# ================================================================================
# Guided Exploration
# ================================================================================
#
# From this activity onward, the main loop continuously checks the
# state of inputs and responds to them. This technique is known as
# polling: the program repeatedly checks if each button is pressed
# on every pass through the loop. Understanding polling, and its
# limitations, is fundamental to writing responsive microcontroller
# programs.
#
# This activity introduces if-conditions as a common program decision
# structure. An if statement or an if-else conditional structure is
# often used to react to a single input. The program also introduces
# a way of combining multiple inputs using logical operators.
#
# --------------------------------------------------------------------------------
# GE 1 - Pull-up inputs and if-else
# --------------------------------------------------------------------------------
#
# The pushbuttons in the BEAPER Nano circuit are connected in what is
# known as a pull-up configuration, meaning one side of each pushbutton
# switch is wired in series with a resistor that is connected, or
# 'pulled up', to the power supply voltage. The other terminal of the
# pushbutton is connected to ground, and the microcontroller input pin
# sits in between the pull-up resistor and the switch, reading the
# voltage across the switch.
#
# The inactive voltage (when the pushbutton is not pressed) will be
# high due to the pull-up resistor's connection to the power supply,
# and the active voltage (when the pushbutton is pressed) will be 0V
# because the switch connects the pin directly to ground. This is
# what makes it an active-low input — the pin reads 0 when active.
#
# Notice that BEAPER_Nano.py already configured each pushbutton pin
# using Pin.PULL_UP when the board module was set up in Activity 1 —
# this enables the microcontroller's internal pull-up resistors, so
# no external resistors are needed on the circuit board.
#
# MicroPython's value() method can be used without an argument to
# read the value of an I/O pin, like this:
#
# Example code:
#
# if beaper.SW2.value() == 0:
#
# Note that two equals signs '==' are used to compare values, while a
# single equals sign '=' is used to assign a value. Mixing these up
# is one of the most common beginner mistakes in programming —
# 'if beaper.SW2.value() = 0' would cause an error, while
# 'if beaper.SW2.value() == 0' checks whether SW2 is reading 0.
#
# What value do you expect beaper.SW2.value() to return when SW2 is
# not pressed? What about when SW2 is pressed?
#
# An 'if' structure operates similarly to the 'while' loop: program
# statements indented below it execute 'if' the condition is true.
# This if condition also has a complementary 'else:' clause, which
# runs when the initial if condition is false — so one of the two
# branches always executes.
#
# Looking at SW2's if-else condition, explain the program flow when
# SW2 is not pressed and also when SW2 is pressed. Which LED2 value()
# call executes in each case?
#
# Notice how the comments '# Momentary button SW2' and '# Start a
# pattern' mark the start of each new section of code, while the
# comment on 'beaper.nano_led_on()' explains what that single
# statement does and why it's there. Getting into the habit of
# writing clear comments like these will make your own programs much
# easier to read, understand, and debug later.
#
# --------------------------------------------------------------------------------
# GE 2 - Blocking delays and button response
# --------------------------------------------------------------------------------
#
# Press SW5 to start the light pattern. While the pattern is running,
# does pressing and holding SW2 turn LED2 on? Explain why or why not,
# and what you think is happening in the program.
#
# Think back to Activity 2's discussion of blocking delays —
# time.sleep() pauses the microcontroller completely while it runs,
# so nothing else in the program can happen until the delay finishes.
# How does that relate to what you're observing here? Can you think
# of a way to test and verify your explanation?
#
# --------------------------------------------------------------------------------
# GE 3 - Playing a tone while a button is held
# --------------------------------------------------------------------------------
#
# Activity 2's Guided Exploration (GE 6) demonstrated how to use
# tone() with both a frequency and a duration argument. Passing
# tone() only a frequency argument causes it to start playing until
# either another tone() call changes the frequency, or noTone() is
# called to stop it.
#
# An if-else condition is an ideal way to play a tone while a button
# is held and stop it when the button is released. Add this code to
# your program to try it out:
#
# Example code:
#
# if beaper.SW3.value() == 0:
#   beaper.tone(440)
# else:
#   beaper.noTone()
#
# What is the advantage of using an if-else structure here instead of
# two separate if conditions — one to start the tone and one to stop
# it?
#
# --------------------------------------------------------------------------------
# GE 4 - Nested if-else conditions
# --------------------------------------------------------------------------------
#
# Let's try using a combination of two pushbuttons to turn on one
# LED. One way to accomplish this is by nesting one if-else condition
# inside another, like this:
#
# Example code:
#
# if beaper.SW3.value() == 0:
#   if beaper.SW4.value() == 0:
#     beaper.LED3.value(1)
#   else:
#     beaper.LED3.value(0)
# else:
#   beaper.LED3.value(0)
#
# The nested if-else logic enables SW4 to turn the LED on only if
# both SW3 and SW4 are pressed. Try the code in your program to
# verify that it works as expected.
#
# --------------------------------------------------------------------------------
# GE 5 - The logical 'and' operator
# --------------------------------------------------------------------------------
#
# A better way to turn one LED on using two pushbuttons is with a logical
# 'and' operator in the if condition, like this:
#
# Example code:
#
# if beaper.SW3.value() == 0 and beaper.SW4.value() == 0:
#   beaper.LED3.value(1)
# else:
#   beaper.LED3.value(0)
#
# Try this code in your program to verify that it works. In what
# ways is this solution better than using nested if-else conditions?
#
# --------------------------------------------------------------------------------
# GE 6 - The logical 'or' operator
# --------------------------------------------------------------------------------
#
# The logical 'or' operator can also be used in conditional expressions.
# Predict when the LED would be lit if the 'and' operator in GE 5 were
# replaced with 'or'. Try it in your program to verify your prediction.


# ================================================================================
# Extension Activities
# ================================================================================
#
# Writing programs that respond to inputs is where microcontroller
# programming starts to feel alive. As you write your own programs,
# get into the habit of adding comments like the ones you saw in the
# starter program — a comment that explains *why* code is written a
# certain way is often more valuable than one that just describes
# *what* it does. Future you will thank present you!
#
# --------------------------------------------------------------------------------
# EA 1 - Start/Stop buttons
# --------------------------------------------------------------------------------
#
# Create a program that simulates the separate 'Start' and 'Stop'
# buttons found on large industrial machines. The machine (simulated
# by an LED) should turn on when the 'Start' button is pressed, and
# remain on until the 'Stop' button is pressed.
#
# What happens if both buttons are held at the same time? Is the
# machine (LED) on or off? Describe what the program is doing in
# this case.
#
# Using what you learned about the logical 'and' operator in GE 5,
# modify your program so that the 'Start' button only turns the
# machine on when the 'Stop' button is not being held at the same
# time.
#
# --------------------------------------------------------------------------------
# EA 2 - Hold-to-activate timing
# --------------------------------------------------------------------------------
#
# Modify the program from EA 1 to light the LED only after the
# 'Start' button has been held for longer than one second.
#
# --------------------------------------------------------------------------------
# EA 3 - Per-button patterns and tones
# --------------------------------------------------------------------------------
#
# Create a program that uses each pushbutton to display its own
# unique lighting pattern using any combination of LEDs, or to play a
# different tone or short tune for each button that is pressed.
#
# --------------------------------------------------------------------------------
# EA 4 - Bicycle turn signal
# --------------------------------------------------------------------------------
#
# Imagine that you're creating a turn signal circuit for a bicycle. The
# circuit has four LEDs in a row, just like your circuit, controlled by two
# pushbuttons mounted on the bicycle's handlebars. Write a program to activate
# a turn signal using one or more of BEAPER Nano's LEDs to indicate a left or
# right turn while the corresponding button is held.
#
# For an extra challenge, add brake functionality or a bell/horn feature. Can
# you make the brake or horn operate while the turn signal is active? What
# makes doing this so difficult?