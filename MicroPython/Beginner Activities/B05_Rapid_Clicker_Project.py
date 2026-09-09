# ================================================================================
# Beginner Activity 5 Project: Rapid-Clicker Game
# [B05_Rapid_Clicker_Project.py]
# Version: 1.2
# Updated: September 8, 2026
#
# Platform: mirobo.tech BEAPER Nano circuit (any configuration)
# Requires: BEAPER_Nano.py board module file
# ================================================================================

# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32.
import BEAPER_Nano as beaper  # Set up BEAPER Nano I/O

import time

# ================================================================================
# Rapid-Clicker Game
# ================================================================================
#
# Two players race to be the first to reach a target number of clicks.
# This project asks you to build the game using the same techniques
# from this activity's Guided Exploration: edge-detected counting,
# an if/elif chain, and a Boolean variable that tracks whether the
# game is still being played.
#
# Suggested button assignment (feel free to change it):
#   SW3 - Player 1      SW4 - Player 2      SW5 - Reset
#
# Your rapid-clicker game should:
#
#  - Give each player their own button and their own edge-detected
#    counter, so holding a button down doesn't rack up extra clicks.
#  - Declare the first player to reach a target count (for example,
#    MAX_COUNT) the winner.
#  - Give each player some visual feedback for their own clicks, and
#    a clearly different signal for whoever wins.
#  - Stop counting clicks from either player once the game has been
#    won, until it's reset.
#  - Use a third button to reset both counters and start a new round.
#
# How you show clicks, whose turn it is, or who won is up to you -
# there's no single correct LED layout. Use print() while you're
# developing to check that both counters are behaving as you expect,
# then remove or comment out the print statement once you're
# satisfied it's working.
#
# Stretch goals:
#
#  - Add a short tone() on each click, and a distinct victory tune
#    for whichever player wins.
#  - Add a countdown (using the LEDs, a tone, or both) before the
#    round starts, during which clicks don't count.
#  - Best-of-three: track wins per player across multiple rounds,
#    and declare an overall champion.
#  - Add a false-start penalty: if a player clicks before the
#    countdown finishes, they automatically lose the round.

# --- Program Constants ----------------
MAX_COUNT = const(50)

# --- Program Variables ----------------
# TODO: Define edge-detection variables for each player's button
# (current-pressed and last-pressed, following GE 6's pattern).

# TODO: Define a counter variable for each player, starting at 0.

# TODO: Define a Boolean variable to track whether the game is still
# active, starting as True.

beaper.nano_led_on()  # Status LED on

while True:
  # TODO: Read each player's button.

  # TODO: Wrap the rest of this section in an 'if game_active:' block.
  #
  # Inside that block:
  #   - Use edge detection to count a new click for each player who
  #     just pressed their button (not pressed to pressed, as in GE 6).
  #   - Give each click some visual feedback.
  #   - Check whether either player has just reached MAX_COUNT. If
  #     so, light that player's win signal and set game_active to
  #     False so further clicks are ignored.
  #   - Save each player's button state for next loop's edge
  #     detection (SW3_last = SW3_pressed, and the same for SW4).

  # TODO: Outside the 'if game_active:' block, check the reset button.
  # Resetting should work regardless of whether the game is currently
  # active, so it needs to be checked unconditionally every loop:
  #   - Reset both counters to 0.
  #   - Turn off all LEDs.
  #   - Set game_active back to True.

  time.sleep_ms(20)  # Short delay for button debouncing