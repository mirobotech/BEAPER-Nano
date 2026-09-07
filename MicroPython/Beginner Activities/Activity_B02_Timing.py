# ================================================================================
# Beginner Activity 2: Timing (Blocking) [Activity_B02_Timing.py]
# Version: 1.2
# Updated: September 7, 2026
#
# Platform: mirobo.tech BEAPER Nano circuit (any configuration)
# Requires: BEAPER_Nano.py board module file
# ================================================================================

# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32.
import BEAPER_Nano as beaper  # Set up BEAPER Nano I/O

import time  # Import time functions

beaper.nano_led_on()  # Use Arduino Nano ESP32's LED as a status indicator

# Main loop - code indented below while True: repeats forever
while True:
  beaper.LED2.value(1)
  beaper.LED5.value(0)
  time.sleep(0.5)        # wait 0.5 seconds

  beaper.LED2.value(0)
  beaper.LED5.value(1)
  time.sleep(0.5)        # wait 0.5 seconds


# ================================================================================
# Guided Exploration
# ================================================================================
#
# Timing is fundamental to microcontroller programs, and one way to control
# timing is by adding delay instructions to a program. Without delays,
# microcontrollers execute instructions in microseconds - far too fast for
# people to perceive.
#
# This activity introduces blocking delays, time delays in which no other
# processing occurs (future activities will introduce non-blocking delays).
# Blinking LEDs, making musical tones, and creating responsive controls are
# all made possible by using delays as part of the program.
#
# --------------------------------------------------------------------------------
# GE 1 - Importing the time module
# --------------------------------------------------------------------------------
#
# Activity B01 imported the BEAPER_Nano.py board module to make the I/O
# devices defined in the board module file available to its starter program.
#
# Example code:
#
# import BEAPER_Nano as beaper  # Set up BEAPER Nano I/O
#
# The import statement essentially incorporates the contents of the board module
# into the current program. The code in the board module won't appear in your
# program, but all of it will be available to your program exactly as if you
# had typed it into your program. (You can open the board module in the editor
# to see and edit all of the code that it contains.)
#
# The import time statement below it works in a similar way. It imports the
# functions built into MicroPython's time module into this program. Unlike
# the board module, it's not possible to open the time module to view its
# source code and read its functions. Instead, the description of each function
# in native MicroPython modules are found in the MicroPython documentation.
# We'll look up the time functions in GE 2, below.
#
# It's useful to recognize that a dot '.' appearing between two names in a
# MicroPython statement means the program is using some code defined inside
# a different module or object. (This is different from a decimal point in
# a number, like the '0.5' in time.sleep(0.5), below.) For now, notice that:
#
# Example code:
#
# beaper.LED2.value(1)  - sets the value of LED2 in the beaper module
#
# time.sleep(0.5)       - calls the sleep function in the time module
#
# - the value() method is called on the LED2 object defined in the beaper
#   module, and
# - the sleep() function is being invoked from the time module.
#
# Most MicroPython programs are composed of many instructions combined in this
# way, and we will explore modules, objects, and methods in more detail in later
# activities.
#
# What do you think will happen if a program tries to use sleep() without
# importing the time module first? Comment out the import time statement
# and try to run the program. What happens? Restore the statement before
# moving on.
#
# --------------------------------------------------------------------------------
# GE 2 - MicroPython documentation
# --------------------------------------------------------------------------------
#
# Open the MicroPython documentation in a browser using this URL:
#
# https://docs.micropython.org/en/latest/library/time.html#module-time
#
# Look up the time.sleep() function. Read its description. What does the
# parameter passed to sleep() represent? What units does it use?
#
# Glancing through the page, you'll also see the other time functions available
# in MicroPython, including sleep_ms() and sleep_us(), both of which will be
# used shortly. Getting comfortable finding and reading documentation like this
# is an important skill, and the micropython.org web site is the definitive
# guide to all MicroPython instructions and functions.
#
# --------------------------------------------------------------------------------
# GE 3 - Millisecond delays
# --------------------------------------------------------------------------------
#
# Run the starter program if you haven't done so already. The LEDs should
# alternate on and off with a short delay between each change. How long
# does each LED stay on? Does it match the delay value in the code?
#
# There is another way to accomplish the same result using the time.sleep_ms()
# (sleep milliseconds) function. Replace both time.sleep(0.5) calls in your
# program with the following time.sleep_ms() calls:
#
# Example code:
#
# time.sleep_ms(500)
#
# Run the program again. The result should be exactly the same. Is it?
# Expressing the time delay as an integer number of milliseconds rather than
# a decimal number of seconds is an easier and less error-prone way to
# define very short time delays. Which function might be a better choice
# if you needed a sub-millisecond delay?
#
# --------------------------------------------------------------------------------
# GE 4 - Stopping the program
# --------------------------------------------------------------------------------
#
# Stop the program from running. When the program stops, do all of the
# LEDs turn off, including the Arduino Nano ESP32's built-in LED?
#
# Some outputs may stay in their last state when a program stops. When
# stopping future programs that control different kinds of output devices,
# what do you need to be careful of?
#
# --------------------------------------------------------------------------------
# GE 5 - Generating a tone
# --------------------------------------------------------------------------------
#
# sleep_us() delays for the number of microseconds provided. While
# microsecond delays are much too short to see, they can be used to
# generate signals at audible frequencies - including sound waves! Some
# piezo speakers contain their own driver circuit and make a sound when
# powered on, but the speaker on BEAPER Nano has to be switched on and off
# rapidly to create sound. Let's try it.
#
# First, add these two lines between the import statements and the main
# while True: loop in the program. The first line imports the Pin functions
# from MicroPython's machine module, and the second line configures the
# microcontroller's LS1 pin as an output named 'speaker':
#
# Example code:
#
# from machine import Pin
# speaker = Pin(beaper.LS1_PIN, Pin.OUT)
#
# Next, add this new 'while True:' loop above the existing one:
#
# Example code:
#
# while True:
#   speaker.value(1)
#   time.sleep_us(1136)
#   speaker.value(0)
#   time.sleep_us(1136)
#
# Reminder: easily remove pound symbol '#' comments from multiple lines of code
# by highlighting the lines and pressing CMD-/ on macOS, or CTRL-/ on Windows.
#
# Run the program. It should produce a 440 Hz tone. Each half-cycle of
# the sound wave lasts 1136 microseconds, so the full period will be
# 1136 + 1136 = 2272 microseconds. Since frequency = 1 / period, that
# gives 1,000,000 / 2272 ≈ 440 Hz, equal to the musical note A4.
#
# Are the LEDs still flashing while the sound is playing? Stop the
# program to stop the tone, then think about what the program is actually
# doing. Explain what is happening and why the LEDs are no longer blinking.
#
# --------------------------------------------------------------------------------
# GE 6 - The tone() and noTone() functions
# --------------------------------------------------------------------------------
#
# There is an easier and more flexible way to produce tones using the
# BEAPER_Nano.py board module's tone() and noTone() functions.
#
# Remove the 'from machine import Pin' statement, the speaker definition,
# and the entire while True: loop added in GE 5. Then replace the sleep()
# calls in the original loop as shown:
#
# Example code:
#
# while True:
#   beaper.LED2.value(1)
#   beaper.LED5.value(0)
#   beaper.tone(440, 500)
#
#   beaper.LED2.value(0)
#   beaper.LED5.value(1)
#   beaper.tone(523, 500)
#
# The first parameter in tone() is the frequency in Hz, and the second is
# the duration in milliseconds. So, beaper.tone(440, 500) plays a 440 Hz
# tone for 500 ms. Notice that tone() also acts as a delay: the program
# waits for the tone to finish before moving to the next statement, just
# as sleep() did before.
#
# You can also call beaper.noTone() at any point to stop a tone
# immediately. When you stop the program, the tone may continue playing
# because it runs on a hardware timer that keeps going independently of
# the program loop. Press the reset button, or call noTone(), to silence
# it.


# ================================================================================
# Extension Activities
# ================================================================================
#
# Notice that the starter program has two distinct sections: statements
# that run once when the program starts, followed by statements inside
# the while True: loop that repeat forever. This setup-then-loop pattern
# appears in virtually every microcontroller program you will write. Use
# the setup section for anything that should happen only once at startup,
# and the loop for everything that should keep running.
#
# --------------------------------------------------------------------------------
# EA 1 - Simulate a start-up sequence
# --------------------------------------------------------------------------------
#
# Simulate a machine's start-up and operation by lighting one LED for two
# seconds after the program starts. After the two-second delay, have the
# program blink a second LED once per second.
#
# --------------------------------------------------------------------------------
# EA 2 - Create an LED pattern
# --------------------------------------------------------------------------------
#
# Create an animated light pattern using the four on-board LEDs. It could
# light and extinguish the four LEDs in sequence, chase a lit LED across
# the four positions or back and forth, or make a more unique or artistic
# pattern. It's up to you!
#
# --------------------------------------------------------------------------------
# EA 3 - Binary counting
# --------------------------------------------------------------------------------
#
# Really old computers used lights to show binary values. Try to simulate
# a binary counting sequence using BEAPER Nano's LEDs.
#
# --------------------------------------------------------------------------------
# EA 4 - Compose a tune
# --------------------------------------------------------------------------------
#
# Create a musical sequence of tones or a short song that repeats after a
# short pause.
