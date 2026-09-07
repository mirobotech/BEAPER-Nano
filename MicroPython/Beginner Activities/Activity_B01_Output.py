# ================================================================================
# Beginner Activity 1: Digital Output [Activity_B01_Output.py]
# Version: 1.2
# Updated: September 7, 2026
#
# Platform: mirobo.tech BEAPER Nano circuit (any configuration)
# Requires: BEAPER_Nano.py board module file.
# ================================================================================

# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32.
import BEAPER_Nano as beaper  # Set up BEAPER Nano I/O

# Turn on one LED
beaper.LED2.value(1)

# Main loop - code indented below while True: repeats forever
while True:
  # Nothing here for now
  pass


# ================================================================================
# Guided Exploration
# ================================================================================
#
# Guided exploration (GE) activities and questions highlight the key ideas
# introduced in the program. In a classroom, instructors can use them to
# guide discussion, demonstration, prediction, and troubleshooting.
# Independent learners can use the guided exploration activities as
# checkpoints to test their understanding before moving on.
#
# This first beginner activity introduces the basic structure of
# MicroPython programs.
#
# --------------------------------------------------------------------------------
# GE 1 - Comments and program statements
# --------------------------------------------------------------------------------
#
# Most computer programs contain both text comments (which help anyone
# reading the program code to understand it) and the actual program
# statements that the microcontroller will run, or execute.
#
# Comments in MicroPython follow a pound sign '#', meaning anything that
# follows the pound sign in a line of text will be ignored.
#
# In the starter program, most of the text is comments. How does the
# MicroPython editor you're using treat the comments differently from the
# actual program code?
#
# In later GE and EA sections you'll be asked to modify or replace the code
# in your program. When copying activity code into your program you'll need
# to strip out the pound characters in order for the code to run. It's easy
# to toggle code comments on or off by selecting one of more lines of text
# and then pressing CMD-/ on macOS, or CTRL-/ on Windows.
#
# --------------------------------------------------------------------------------
# GE 2 - Importing the board module
# --------------------------------------------------------------------------------
#
# The first real program statement encountered in this program imports a
# board module file for your BEAPER Nano circuit.
#
# Example code:
#
# import BEAPER_Nano as beaper
#
# The 'BEAPER_Nano.py' board module file must be copied into the filesystem
# memory of the microcontroller before this program runs. If the file is not
# present when the import statement runs, an error will be generated, and an
# error message will be printed in the terminal below.
#
# The BEAPER_Nano.py board module file contains ordinary MicroPython
# program code that defines and configures BEAPER Nano's I/O devices and
# microcontroller pins for you, helping you to start writing programs more
# quickly. You can open the board module file in the code editor to explore
# all of the code it contains.
#
# The board module file includes the names and pin numbers of all I/O
# devices on the circuit, including LED2. This lets program statements,
# like the one below, use the name LED2 to control its operation instead
# of us needing to know the pin number LED2 is connected to.
#
# Example code:
#
# beaper.LED2.value(1)
#
# Let's break this statement down: the BEAPER_Nano board module has been
# given the shorter name 'beaper' by the import statement, and 'LED2' is one
# of the objects defined in the BEAPER_Nano board module file. MicroPython's
# 'value' method is used to read or set pin values, so the end result of the
# microcontroller running this statement is that the value of the LED2 pin
# gets set to 1, meaning the output voltage of the pin connected to LED2
# is set to around 3.3V, which will turn LED2 on.
#
# All of BEAPER Nano's other LEDs (LED2 - LED5) can be controlled in
# exactly the same way. Let's try it.
#
# Add a second LED output statement to light LED3 below the existing
# statement that lights LED2. Run the updated program to verify that it
# works as expected.
#
# --------------------------------------------------------------------------------
# GE 3 - Sequential execution
# --------------------------------------------------------------------------------
#
# MicroPython runs every program by reading, interpreting, and executing
# each program statement, in order, from the top of the program code to the
# bottom.
#
# So, after adding the statement 'beaper.LED3.value(1)' below the existing
# 'beaper.LED2.value(1)' statement in GE 2, the microcontroller will turn
# LED2 on first, followed by LED3. Though these two actions take place
# sequentially, they happen so fast that, to us at least, it looks like both
# LEDs turn on simultaneously.
#
# --------------------------------------------------------------------------------
# GE 4 - The main program loop
# --------------------------------------------------------------------------------
#
# If all that we wanted the program to do was to turn two LEDs on, it could
# end after these two statements have run. In reality, microcontroller
# programs usually don't end. Instead, they continue running the task they
# were designed to do over and over again in what is called a main program
# loop.
#
# In MicroPython programs, the 'while True:' structure is the most common
# method used to create a main program loop. Any statements indented by the
# same amount below the 'while True:' line will be repeated forever.
#
# Indentation is very important in MicroPython, and program editors will
# try to help you indent your program code in a consistent way - let them!
# If two or more program statements that are meant to be in the same code
# structure use different amounts of space characters to indent their code,
# the MicroPython interpreter will generate an error due to the mismatch.
# You will often run into this problem when copying and pasting code
# examples from different sources.
#
# Would it make sense to put the 'beaper.LED2.value(1)' output statement
# inside the 'while True:' loop? Why or why not? What would the program be
# trying to do if the statement used to turn on an LEDs was moved into
# the 'while True:' loop?
#
# --------------------------------------------------------------------------------
# GE 5 - The pass statement
# --------------------------------------------------------------------------------
#
# The 'pass' statement in the main 'while True:' loop prevents MicroPython
# from generating an error due to the otherwise empty loop. Comment out the
# pass statement by placing a pound sign in front of the pass keyword.
# Then, try to run the program.
#
# Example code:
#
# # pass
#
# Since MicroPython interpreters ignore the rest of any line of text
# following a pound sign, the pass statement will now be ignored.
# What do you think the word pass actually does? How might pass
# be helpful to us later?
#
# --------------------------------------------------------------------------------
# GE 6 - Fast output changes
# --------------------------------------------------------------------------------
#
# Let's try to blink LED3 on and off. Replace the contents of the main
# 'while True:' loop with two statements: one to turn the LED on, followed
# by a second one to turn the LED off.
#
# Example code:
#
# while True:
#   beaper.LED3.value(1)  # LED3 on
#   beaper.LED3.value(0)  # LED3 off
#
# Reminder: easily remove comment pound signs '#' from multiple lines of
# code by highlighting the lines and pressing CMD-/ on macOS, or CTRL-/ on
# Windows.
#
# Since these two statements are now inside the main loop, 'pass' is no
# longer needed. The loop will run each statement once, first turning LED3
# on, and then turning LED3 off. After that, the loop will repeat from the
# top, turning LED3 on again, and then off again... forever.
#
# Run the program and observe LED3. Is LED3 on, off, or flashing? What
# should be happening? Is it? How could you test your prediction?


# ================================================================================
# Extension Activities
# ================================================================================
#
# Extension activities give learners a chance to apply the concepts and
# ideas presented in the guided exploration activities in new contexts,
# or as new challenges. Instructors may assign selected extensions for
# practice, enrichment, or assessment. Independent learners can use them
# to help solidify understanding and to apply their skills.
#
# --------------------------------------------------------------------------------
# EA 1 - Turn LED2 on and off
# --------------------------------------------------------------------------------
#
# The statement used to turn LED2 on in the starter program runs before
# the main while: loop. What do you think will happen if this statement
# is immediately followed by a second statement to turn LED2 off?
#
# Try it! Do you see LED2 turning on and then off? Explain what is happening
# and why you think this happens.
#
# --------------------------------------------------------------------------------
# EA 2 - Reverse the statement order
# --------------------------------------------------------------------------------
#
# Predict what will happen if the order of the two LED2 statements in EA 1
# is reversed so that LED2 is turned off first, and then turned on.
#
# Try it! Does the state of LED2 match your prediction?
#
# --------------------------------------------------------------------------------
# EA 3 - Create an LED pattern
# --------------------------------------------------------------------------------
#
# Create a program that lights a pattern by illuminating at least two of the
# on-board LEDs. Run your program to verify that it works as expected.
#
# --------------------------------------------------------------------------------
# EA 4 - Use the microcontroller module LED
# --------------------------------------------------------------------------------
#
# The BEAPER_Nano.py board module file includes functions to control the
# Arduino Nano ESP32 module's on-board LED, as well as many other pin
# definitions and pre-made functions for the BEAPER Nano circuit. (Feel
# free to open the file to explore all of the code that it contains.)
#
# One of the functions in the BEAPER Nano board module is used to turn on
# the Arduino Nano ESP32 microcontroller's on-board LED:
#
# Example code:
#
# beaper.nano_led_on()
#
# Add this function call at the very beginning of your program so that the
# Arduino Nano ESP32's LED can act as a status indicator to show that your
# program is running even if none of the BEAPER Nano's on-board LEDs are
# lit. Run the program to verify that it works.
#
# --------------------------------------------------------------------------------
# EA 5 - Try the RGB LEDs
# --------------------------------------------------------------------------------
#
# Explore the BEAPER_Nano.py board module file to find the RGB LED
# functions. These work differently than the normal board LEDs. Instead of
# being turned on or off with a 1 or 0, each LED element (R - red, G -
# green, B - blue) is controlled using its own brightness value, expressed
# as a percentage. Try this:
#
# Example code:
#
# beaper.nano_rgb_green(50)
#
# The brightness value of each LED element can range from 0 (off) to 100
# (full brightness). Mixing two or three brightnesses together can generate
# unique colours.
#
# Can you make white light? How about Yellow? Orange? Aqua?
#
# The board module also includes a combined function that sets all three RGB
# LED elements in a single statement. This can make mixing colours quicker:
#
# Example code:
#
# beaper.nano_rgb(50, 0, 50)  # A dim purple (R=50, G=0, B=50)
#
# Use the beaper.nano_rgb() statement to make a new colour.
