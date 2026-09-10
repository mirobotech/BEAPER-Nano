# ================================================================================
# Beginner Activity 7 Project: Morse Code [B07_Morse_Code_Project.py]
# Version: 1.2
# Updated: September 10, 2026
#
# Platform: mirobo.tech BEAPER Nano circuit (any configuration)
# Requires: BEAPER_Nano.py board module file
# ================================================================================

# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32.
import BEAPER_Nano as beaper  # Set up BEAPER Nano I/O

import time

# ================================================================================
# Morse Code
# ================================================================================
#
# Morse code represents letters as sequences of short and long
# signals - dots and dashes. This project asks you to encode a
# message of your own choosing, using a for loop to step through a
# sequence of symbols, the same way GE 4 previewed iterating directly
# over a string.
#
# Your Morse code project should:
#
#  - Represent at least one word or short phrase as Morse code,
#    encoding each letter as a sequence of dots and dashes.
#  - Play a short tone and flash an LED for each dot, and a longer
#    tone and flash for each dash.
#  - Leave a gap between symbols within a letter, a longer gap between
#    letters, and a longer gap still between words. (By convention,
#    real Morse code uses a dash three times as long as a dot, a
#    gap between letters three times the dot duration, and a gap
#    between words seven times the dot duration - but you can choose
#    your own timing if you prefer.)
#  - Use a for loop to iterate over each letter's dot/dash pattern,
#    rather than writing out each tone individually.
#
# You don't need to encode the entire alphabet - just the letters in
# your chosen message. Look up the Morse code patterns for the
# letters you need before you start.
#
# This project is built in two parts. Part 1 sends a single, fixed
# pattern - SOS - using one for loop. Part 2 expands this into a full
# message of your choice, adding a second, outer loop and a way to
# look up each letter's pattern - reusing Part 1's loop unchanged
# inside it.
#
# Stretch goals:
#
#  - Encode the full alphabet using a dictionary that maps each
#    letter to its dot/dash pattern, so any short message could be
#    converted automatically.
#  - Add a 'receive' mode: use a pushbutton to let the user tap out
#    Morse code themselves, measuring how long the button is held to
#    distinguish dots from dashes.
#  - Display the message being sent on the console, one letter at a
#    time, in sync with the LED and tone output.
#  - Experiment with different frequencies or rhythms to make the
#    output easier (or harder!) to distinguish by ear.

# --- Program Constants ----------------
# Part 1 TODO: Define constants for your dot duration, dash duration,
# and the gap between symbols.

# Part 2 TODO: Once Part 1 is working, add constants for the gap
# between letters and the gap between words.

# --- Program Variables ----------------
# Part 1 TODO: Define a variable named 'pattern' holding the SOS code
# as a string of '.' and '-' characters: "...---...". Notice this is
# sent as one unbroken sequence rather than as three separate
# letters - that's how SOS is actually sent in real Morse code.

beaper.nano_led_on()  # Status indicator

# ================================================================================
# Part 1: Send SOS
# ================================================================================
#
# TODO: Use a for loop to iterate over each character in 'pattern'.
# For each symbol:
#   - Light an LED and play a tone - short for a dot, long for a
#     dash.
#   - Pause for the symbol gap before moving to the next symbol.
#
# Get this working, and confirm you can see and hear a correct SOS
# pattern, before moving on to Part 2.


# ================================================================================
# Part 2: Send a full message
# ================================================================================
#
# TODO: Define your own short message as a string (for example,
# MESSAGE = "SOS", or a word of your choice).
#
# TODO: Wrap your Part 1 code in an outer for loop that iterates over
# each letter in MESSAGE. At the start of each iteration, before your
# existing Part 1 loop runs, set 'pattern' using an if/elif chain that
# compares the current letter against each pattern you need - you
# only need the letters that appear in your own message, not the
# whole alphabet. Look up the Morse code patterns for those letters
# before you start.
#
# Your Part 1 loop - iterating over 'pattern' to send each symbol -
# doesn't need to change at all. It now just runs once per letter
# instead of once total, using whichever pattern the if/elif chain
# just looked up.
#
# TODO: Pause for the letter gap after each letter's pattern
# finishes, before moving to the next letter. Between words, if your
# message contains more than one, pause for the (longer) word gap
# instead.