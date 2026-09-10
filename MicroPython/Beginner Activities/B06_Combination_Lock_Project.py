# ================================================================================
# Beginner Activity 6 Project: Combination Lock [B06_Combination_Lock_Project.py]
# Version: 1.2
# Updated: September 9, 2026
#
# Platform: mirobo.tech BEAPER Nano circuit (any configuration)
# Requires: BEAPER_Nano.py board module file
# ================================================================================

# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32.
import BEAPER_Nano as beaper  # Set up BEAPER Nano I/O

import time

# ================================================================================
# Combination Lock
# ================================================================================
#
# Real combination locks require a specific sequence of inputs before
# they open. This project asks you to build one, using a step counter
# and conditional loops from this activity's examples.
#
# Your combination lock should:
#
#  - Use a sequence of at least four button presses as the
#    combination (buttons can repeat - for example SW2, SW3, SW2, SW5
#    is a valid four-step combination).
#  - Track progress through the sequence using a step counter variable.
#  - Give confirmation feedback for a correct press, and a clearly
#    different error signal for a wrong press, resetting the step
#    counter back to 0 so the whole sequence must be re-entered from
#    the start.
#  - Celebrate somehow when the full sequence is entered correctly,
#    and stop accepting input until the program is reset (or restarted).
#
# The exact combination, the confirmation and error signals, and the
# celebratory correct code signal are up to you - there's no single
# correct design. Use print() while developing your program to check
# that your step counter is behaving as you expect it to, and then
# remove or comment out the print statements when you're satisfied that
# the program is working properly.
#
# Stretch goals:
#
#  - Add a lockout: after a number of incorrect attempts, ignore all
#    input for several seconds before allowing the user to try again.
#  - Add a timed entry window: each step must be pressed within a few
#    seconds of the last one, or the sequence resets automatically.
#  - Track and display the longest correct partial sequence entered
#    so far, even on attempts that were never completed.

# --- Program Constants ----------------
# TODO: Set the code length.

# --- Program Variables ----------------
# TODO: Define a step counter variable, starting at 0.

# TODO: Define a variable to track whether the most recent button
# press matched the expected button for the current step - you'll
# update this on every press, not just once at the end.

beaper.nano_led_on()  # Status LED

while True:
  # TODO: Wrap everything below in a counted while loop that runs
  # while the step counter is less than your code length. This forms
  # the digit-entry loop, and it exits once the full sequence has
  # been entered correctly. Inside the loop:

  # TODO: Read all four pushbuttons.

  # TODO: If any button is pressed:
  #   - Compare it against the button expected for the current step
  #     using an if/elif chain keyed on the step counter's value (see
  #     Activity 5's GE 5 for a similar pattern, comparing a variable
  #     against several possibilities in turn).
  #   - If it matches: advance the step counter, and give confirmation
  #     feedback.
  #   - If it doesn't match: give error feedback, and reset the step
  #     counter back to 0.
  #   - Wait in a second, indefinite while loop until the button is
  #     released, before continuing - this prevents a single press
  #     from being counted more than once.

  # TODO: The digit-entry loop exits on its own once the full
  # combination has been entered correctly. Celebrate, and stop
  # responding to further button presses until reset.

  time.sleep_ms(20)  # Short delay for button debouncing
  
