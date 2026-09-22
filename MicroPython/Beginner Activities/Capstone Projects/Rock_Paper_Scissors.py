# ================================================================================
# Capstone Project: Rock-Paper-Scissors [RockPaperScissors.py]
# Version: 1.0
# Updated: July 25, 2026
#
# Platform: mirobo.tech BEAPER Nano circuit (any configuration)
# Requires: BEAPER_Nano.py board module file
#
# A single-player Rock-Paper-Scissors game against the computer.
# Press SW5 to begin a round: a 3-2-1 countdown flashes and beeps,
# speeding up as it counts down, then a short window opens for you
# to make your choice. Miss the window and it counts as too slow -
# no result is compared.
#
# Hardware used:
#   SW2 - Rock
#   SW3 - Paper
#   SW4 - Scissors
#   SW5 - Start a round
#   LS1 - Piezo speaker (countdown beeps, "go" tone, outcome tones)
#
# Compatible with all BEAPER Nano configurations. No additional
# hardware or jumper changes required.
#
# --------------------------------------------------------------------------------
# Game behaviour:
#   IDLE      - Waiting. Press SW5 to begin.
#   COUNTDOWN - 3-2-1, LED2-LED4 flash together with a beep on each
#               count. The gap between counts shrinks as it
#               progresses - see COUNTDOWN_INTERVALS below.
#   CHOOSING  - A short window opens (CHOOSE_WINDOW_MS). Press SW2,
#               SW3, or SW4 for your choice. No press before the
#               window closes counts as too slow.
#   REVEAL    - The computer's choice is generated, compared against
#               yours, and the result (win/lose/tie/too slow) is
#               announced with a distinct tone pattern and printed to
#               the Serial Monitor. Session totals (wins/losses/ties)
#               are tracked throughout.
#
# Before you begin - complete your capstone plan using the Capstone
# Preparation Guide: a plain-English description from the player's
# perspective, a state diagram, your constants and variables, and
# your testing plan.
# ================================================================================

# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32.
import BEAPER_Nano as beaper  # Set up BEAPER Nano I/O

import time
import random

# --- State Constants -------------------
STATE_IDLE      = const(0)           # Waiting - press SW5 to start
STATE_COUNTDOWN = const(1)           # 3-2-1 countdown, LEDs flashing
STATE_CHOOSING  = const(2)           # Choice window open - press SW2/SW3/SW4
STATE_REVEAL    = const(3)           # Showing the result of the round

STATE_NAMES = {
  STATE_IDLE:      "IDLE",
  STATE_COUNTDOWN: "COUNTDOWN",
  STATE_CHOOSING:  "CHOOSING",
  STATE_REVEAL:    "REVEAL",
}

# --- Choice Constants -------------------
CHOICE_ROCK     = const(0)
CHOICE_PAPER    = const(1)
CHOICE_SCISSORS = const(2)
CHOICE_NONE     = const(-1)          # Sentinel: no choice made (too slow)

CHOICE_NAMES = {
  CHOICE_ROCK:     "Rock",
  CHOICE_PAPER:    "Paper",
  CHOICE_SCISSORS: "Scissors",
}

CHOICE_LEDS = (beaper.LED2, beaper.LED3, beaper.LED4)   # Indexed by CHOICE_ROCK/PAPER/SCISSORS

# --- Countdown Configuration -------------
# Three parallel lists, indexed together - the same pattern used for
# Simon Game's BUTTONS/LEDS/TONES. COUNTDOWN_INTERVALS[i] is the
# total time (ms) count i occupies; COUNTDOWN_TONES[i] is the pitch
# played at the start of count i. Intervals shrink and pitch rises
# as the countdown progresses, building tension toward "go."
COUNTDOWN_INTERVALS = [800, 600, 400]      # ms per count - gets faster
COUNTDOWN_TONES     = [330, 415, 523]      # Hz per count - gets higher (E4, G#4, C5)
GO_TONE             = 660                  # Distinct tone marking the choice window opening
FLASH_TIME          = const(150)           # ms the LEDs stay lit within each count

# --- Choosing/Reveal Configuration -------
CHOOSE_WINDOW_MS   = const(3000)     # How long the player has to choose
RESULT_DISPLAY_MS  = const(2500)     # How long the result is shown before returning to IDLE

# --- Program Variables -------------------
state       = STATE_IDLE
state_start = 0

# --- Countdown sub-phase tracking ---
countdown_index = 0                  # Which count we're on (0, 1, 2)
phase_start     = 0                  # Time the CURRENT count began
flashing        = False              # True while LEDs are lit within the current count

# --- Round variables ---
player_choice   = CHOICE_NONE
computer_choice = CHOICE_NONE

# --- Session totals ---
win_count  = 0
loss_count = 0
tie_count  = 0


# --- Program Functions ------------------

def all_choice_leds_on():
  for led in CHOICE_LEDS:
    led.value(1)

def all_choice_leds_off():
  for led in CHOICE_LEDS:
    led.value(0)

def enter_state(new_state, current_time, reason=""):
  global state, state_start
  state       = new_state
  state_start = current_time
  print("-->", STATE_NAMES[new_state], end="")
  if reason:
    print(" (", reason, ")", sep="")
  else:
    print()

def start_round(current_time):
  # Begin a new round: reset countdown tracking, start the first
  # count immediately, and enter STATE_COUNTDOWN.
  global countdown_index, phase_start, flashing, player_choice, computer_choice
  countdown_index = 0
  phase_start     = current_time
  flashing        = True
  player_choice   = CHOICE_NONE
  computer_choice = CHOICE_NONE
  all_choice_leds_on()
  beaper.tone(COUNTDOWN_TONES[0])
  enter_state(STATE_COUNTDOWN, current_time, "round start")


# --- Main Program ---------------------

all_choice_leds_off()
print("Rock-Paper-Scissors")
print("SW2: Rock   SW3: Paper   SW4: Scissors   SW5: start round")
print()

state_start = time.ticks_ms()
enter_state(STATE_IDLE, state_start, "startup")

while True:
  current_time = time.ticks_ms()
  elapsed      = time.ticks_diff(current_time, state_start)

  # --- State: Idle ---
  if state == STATE_IDLE:
    if beaper.SW5.value() == 0:
      start_round(current_time)

  # --- State: Countdown (fully worked - see Development Guide Step 1) ---
  elif state == STATE_COUNTDOWN:
    count_elapsed = time.ticks_diff(current_time, phase_start)

    if flashing and count_elapsed >= FLASH_TIME:
      all_choice_leds_off()
      beaper.noTone()
      flashing = False

    if count_elapsed >= COUNTDOWN_INTERVALS[countdown_index]:
      countdown_index += 1
      phase_start = current_time
      if countdown_index >= 3:
        beaper.tone(GO_TONE, 200)
        enter_state(STATE_CHOOSING, current_time, "go!")
      else:
        all_choice_leds_on()
        beaper.tone(COUNTDOWN_TONES[countdown_index])
        flashing = True

  # --- State: Choosing ---
  elif state == STATE_CHOOSING:
    # TODO: if SW2/SW3/SW4 is pressed, set player_choice to the
    #       matching CHOICE_ROCK/PAPER/SCISSORS constant and
    #       enter_state(STATE_REVEAL, current_time, "chose").
    #
    # TODO: if elapsed >= CHOOSE_WINDOW_MS with no press, the player
    #       was too slow - player_choice stays CHOICE_NONE (its
    #       default). enter_state(STATE_REVEAL, current_time,
    #       "too slow").
    pass

  # --- State: Reveal ---
  elif state == STATE_REVEAL:
    # TODO: on the first iteration of this state (hint: elapsed will
    #       be 0 or very small on the very first pass), determine and
    #       announce the result:
    #
    #       if player_choice == CHOICE_NONE:
    #           print("Too slow!")
    #       else:
    #           computer_choice = random.randint(0, 2)
    #           print("You chose:", CHOICE_NAMES[player_choice])
    #           print("Computer chose:", CHOICE_NAMES[computer_choice])
    #           if player_choice == computer_choice:
    #               tie_count += 1
    #               print("Tie!")
    #           elif (player_choice == CHOICE_ROCK and computer_choice == CHOICE_SCISSORS) or \
    #                (player_choice == CHOICE_PAPER and computer_choice == CHOICE_ROCK) or \
    #                (player_choice == CHOICE_SCISSORS and computer_choice == CHOICE_PAPER):
    #               win_count += 1
    #               print("You win!")
    #           else:
    #               loss_count += 1
    #               print("You lose!")
    #           print("Score - wins:", win_count, " losses:", loss_count, " ties:", tie_count)
    #
    #       Play a distinct tone pattern for each outcome - for
    #       example an ascending two-note beep for a win, a single
    #       low buzz for a loss, and a single mid tone for a tie.
    #       Light CHOICE_LEDS[player_choice] to show what you picked
    #       (skip this if player_choice is CHOICE_NONE).
    #
    # TODO: once elapsed >= RESULT_DISPLAY_MS, turn off all
    #       CHOICE_LEDS and enter_state(STATE_IDLE, current_time).
    pass

  time.sleep_ms(1)


# ================================================================================
# Development Guide
# ================================================================================
#
# Work through these steps in order.
#
# --------------------------------------------------------------------------------
# Step 1 - Understand the countdown
# --------------------------------------------------------------------------------
#
# STATE_COUNTDOWN is already complete and working - read through it
# before starting on the TODOs elsewhere. It uses two nested timers:
# an outer one (count_elapsed vs COUNTDOWN_INTERVALS[countdown_index])
# tracking how long the CURRENT count has been running in total, and
# an inner one (the same count_elapsed vs FLASH_TIME) tracking only
# how long the LEDs should stay lit within that count. This is the
# same non-blocking repeating-timer pattern from Activity 11, applied
# twice at once - once for the overall count duration, once for the
# shorter flash within it.
#
# Run the program and press SW5. Confirm the countdown flashes three
# times, getting visibly faster and higher-pitched each time, then
# plays a distinct "go" tone and transitions to CHOOSING (check the
# Serial Monitor for the state transition, since nothing is
# implemented in CHOOSING yet).
#
# --------------------------------------------------------------------------------
# Step 2 - Reading the player's choice
# --------------------------------------------------------------------------------
#
# Implement the button-reading TODO in STATE_CHOOSING. Test that
# pressing SW2, SW3, or SW4 during the choosing window correctly
# records player_choice and transitions to STATE_REVEAL - check the
# Serial Monitor's state transition message for each.
#
# --------------------------------------------------------------------------------
# Step 3 - Timeout handling
# --------------------------------------------------------------------------------
#
# Implement the timeout TODO in STATE_CHOOSING. Test by starting a
# round and simply waiting without pressing anything - confirm it
# transitions to STATE_REVEAL after CHOOSE_WINDOW_MS with
# player_choice still CHOICE_NONE.
#
# --------------------------------------------------------------------------------
# Step 4 - Determining the winner
# --------------------------------------------------------------------------------
#
# Implement the TODO in STATE_REVEAL. Test all nine possible
# combinations of player choice vs. computer choice deliberately -
# this is easiest by temporarily hardcoding computer_choice to a
# fixed value instead of using random.randint() while you test each
# of your three choices against it, then restoring the random version
# once you have confirmed the win/lose/tie logic is correct for every
# combination.
#
# --------------------------------------------------------------------------------
# Step 5 - Outcome feedback and return to idle
# --------------------------------------------------------------------------------
#
# Add the tone patterns and LED feedback described in the TODO, and
# implement the return-to-idle timing. Confirm a full round - start,
# countdown, choose, reveal, and return to idle - works correctly
# several times in a row, and that win_count/loss_count/tie_count
# accumulate correctly across multiple rounds without resetting.


# ================================================================================
# Extension Activities
# ================================================================================
#
# --------------------------------------------------------------------------------
# EA 1 - Best-of-N match
# --------------------------------------------------------------------------------
#
# Layer a "match" concept on top of individual rounds: track a match
# score separately from the session totals, and end the match (with
# a distinct fanfare) once either the player or the computer reaches
# a set number of wins (best of 5, for example). What should happen
# to the match score when SW5 starts a new round after a match has
# already ended?
#
# --------------------------------------------------------------------------------
# EA 2 - Elegant win-determination refactor
# --------------------------------------------------------------------------------
#
# The if/elif chain in STATE_REVEAL checks three specific winning
# combinations explicitly. There is a more compact way to determine
# the same result using modular arithmetic: with choices numbered
# 0, 1, 2 (Rock, Paper, Scissors), the player wins whenever
# (player_choice - computer_choice) % 3 == 1, and loses whenever it
# equals 2 (0 means a tie). Verify this produces identical results
# to your existing if/elif chain for all nine combinations before
# replacing it - why does this formula work? (Hint: consider what
# each choice "beats" as you move one step forward through the cycle
# Rock -> Paper -> Scissors -> Rock.)
#
# --------------------------------------------------------------------------------
# EA 3 - Adaptive computer opponent
# --------------------------------------------------------------------------------
#
# Instead of choosing randomly every time, track how many times the
# player has chosen each of Rock/Paper/Scissors across the session
# (three counters, similar to win_count/loss_count/tie_count) and
# bias the computer's choice toward whichever counters the player's
# most frequent pick. This is a simple introduction to
# pattern-based prediction rather than pure randomness - does it
# actually make the computer harder to beat once you have played
# enough rounds for a pattern to emerge? How would a player adapt
# their own strategy once they suspect the computer is doing this?
#
# --------------------------------------------------------------------------------
# EA 4 - Escalating time pressure
# --------------------------------------------------------------------------------
#
# Reuse Simon Game's "difficulty increases with progress" idea:
# shrink CHOOSE_WINDOW_MS by a fixed amount after each round within
# a session (with a reasonable minimum so it never becomes
# impossible), so the game gets tenser to play the longer a session
# continues. Should the window reset to its original length after a
# "too slow" round, or keep shrinking regardless of outcome?