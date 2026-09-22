# ================================================================================
# Capstone Project: Reaction Time Game [Reaction_Game.py]
# Version: 1.0
# Updated: July 25, 2026
#
# Platform: mirobo.tech BEAPER Nano circuit (any configuration)
# Requires: BEAPER_Nano.py board module file
#
# Two reaction-testing games in one, selected with SW3/SW4:
#
#   SIMPLE   - React as fast as possible to an unpredictable stimulus.
#              LED2 lights up after a random delay - press SW2 the
#              instant it does. Pressing too early ends the trial
#              immediately as a false start, the same way real
#              reaction-time testing works.
#
#   TIMING   - React at the RIGHT MOMENT to a predictable, repeating
#              pattern instead. LED2-LED5 chase continuously in a
#              loop; press SW2 exactly when the chase reaches the
#              target LED (LED4). Unlike SIMPLE, the pattern's timing
#              is known in advance - this tests anticipation and
#              rhythm judgement rather than raw speed.
#
# Both modes measure the same underlying thing - how close your
# press was to a reference moment in time - but the character of
# that reference moment (unpredictable vs. predictable) is what
# makes them test genuinely different skills.
#
# Hardware used:
#   SW2          - Start a round / react during a round
#   SW3 / SW4    - Cycle game mode (only while at the menu)
#   SW5          - Cancel the current round, return to the menu
#   LS1          - Piezo speaker (stimulus/target beep, result tones)
#   On-board LED - On during an active round
#
# Compatible with all BEAPER Nano configurations. No additional
# hardware or jumper changes required.
#
# --------------------------------------------------------------------------------
# Before you begin - complete your capstone plan using the Capstone
# Preparation Guide: a plain-English description of each mode from
# the player's perspective, a state diagram for each, your constants
# and variables, and your testing plan.
# ================================================================================

# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32.
import BEAPER_Nano as beaper  # Set up BEAPER Nano I/O

import time
import random

# --- State Constants -------------------
STATE_MENU    = const(0)             # Selecting a mode, waiting to start
STATE_WAITING = const(1)             # SIMPLE only: waiting out the random delay
STATE_REACT   = const(2)             # SIMPLE only: stimulus is showing, timing the press
STATE_CHASING = const(3)             # TIMING only: chase pattern running
STATE_RESULT  = const(4)             # Showing the result of the last round

STATE_NAMES = {
  STATE_MENU:    "MENU",
  STATE_WAITING: "WAITING",
  STATE_REACT:   "REACT",
  STATE_CHASING: "CHASING",
  STATE_RESULT:  "RESULT",
}

# --- Mode Constants ---------------------
MODE_SIMPLE = const(0)               # Simple reaction time
MODE_TIMING = const(1)               # Timing / anticipation
NUM_MODES   = const(2)

MODE_NAMES = {
  MODE_SIMPLE: "SIMPLE",
  MODE_TIMING: "TIMING",
}

# --- Simple Reaction Time Configuration -
REACT_LED     = beaper.LED2          # The single stimulus LED for SIMPLE mode
MIN_WAIT_MS   = const(1500)          # Shortest possible random delay before the stimulus
MAX_WAIT_MS   = const(4000)          # Longest possible random delay before the stimulus

# --- Timing/Anticipation Configuration --
CHASE_LEDS        = (beaper.LED2, beaper.LED3, beaper.LED4, beaper.LED5)
CHASE_INTERVAL_MS = const(300)       # Time the chase spends on each LED
TARGET_POSITION   = const(2)         # Index into CHASE_LEDS - 2 = LED4

# --- Timing Constants --------------------
RESULT_DISPLAY_MS = const(2000)      # How long a result is shown before returning to MENU
LOOP_DELAY        = const(1)         # Main loop delay (ms) - kept short for timing precision

# --- Program Variables -------------------
state        = STATE_MENU
state_start  = 0

current_mode = MODE_SIMPLE

# --- SIMPLE mode variables ---
wait_duration       = 0              # This round's random delay (ms)
stimulus_time       = 0              # When the stimulus actually lit
reaction_time       = 0              # Most recent trial's reaction time (ms)
best_reaction_time  = 999999         # Best (lowest) reaction time this session
false_start         = False          # True if the most recent trial was a false start

# --- TIMING mode variables ---
chase_position       = 0             # Which of the 4 CHASE_LEDS is currently lit
last_chase_step      = 0             # Time the chase last advanced
last_target_lit_time = 0             # Time the chase most recently lit the target LED
timing_error         = 0             # Most recent trial's timing error (ms)
best_timing_error    = 999999        # Best (lowest) timing error this session

# --- SW3/SW4 edge detection (menu mode cycling) ---
sw3_last = 1
sw4_last = 1


# --- Program Functions ------------------

def all_leds_off():
  for led in CHASE_LEDS:   # CHASE_LEDS includes REACT_LED (LED2) as its first entry
    led.value(0)
  beaper.nano_led_off()

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
  # Begin a new round in the currently selected mode.
  global wait_duration, false_start
  beaper.nano_led_on()
  all_leds_off()
  if current_mode == MODE_SIMPLE:
    wait_duration = random.randint(MIN_WAIT_MS, MAX_WAIT_MS)
    false_start   = False
    enter_state(STATE_WAITING, current_time, "round start")
  elif current_mode == MODE_TIMING:
    global chase_position, last_chase_step, last_target_lit_time
    chase_position   = 0
    last_chase_step  = current_time
    CHASE_LEDS[0].value(1)
    if TARGET_POSITION == 0:
      last_target_lit_time = current_time
    enter_state(STATE_CHASING, current_time, "round start")


# --- Main Program ---------------------

all_leds_off()
print("Reaction Time Game")
print("SW3/SW4: change mode   SW2: start / react   SW5: cancel")
print()

state_start = time.ticks_ms()
enter_state(STATE_MENU, state_start, "startup")
print("Mode:", MODE_NAMES[current_mode])

while True:
  current_time = time.ticks_ms()
  elapsed      = time.ticks_diff(current_time, state_start)

  # --- Cancel (SW5) - checked before all state logic, except at the menu ---
  if beaper.SW5.value() == 0 and state != STATE_MENU and state != STATE_RESULT:
    all_leds_off()
    enter_state(STATE_MENU, current_time, "cancelled")

  # --- State: Menu ---
  elif state == STATE_MENU:
    sw3_current = beaper.SW3.value()
    sw4_current = beaper.SW4.value()
    if (sw3_current == 0 and sw3_last == 1) or (sw4_current == 0 and sw4_last == 1):
      current_mode = (current_mode + 1) % NUM_MODES
      print("Mode:", MODE_NAMES[current_mode])
    sw3_last = sw3_current
    sw4_last = sw4_current

    if beaper.SW2.value() == 0:
      start_round(current_time)

  # --- State: Waiting (SIMPLE mode - random delay before stimulus) ---
  elif state == STATE_WAITING:
    # TODO: if SW2 is pressed here, it is a false start - the player
    #       reacted before the stimulus appeared. Set false_start =
    #       True and enter_state(STATE_RESULT, current_time,
    #       "false start").
    #
    # TODO: once elapsed >= wait_duration, light REACT_LED, sound a
    #       short beep, record stimulus_time = current_time, and
    #       enter_state(STATE_REACT, current_time).
    pass

  # --- State: React (SIMPLE mode - stimulus is showing) ---
  elif state == STATE_REACT:
    # TODO: if SW2 is pressed, compute reaction_time =
    #       time.ticks_diff(current_time, stimulus_time). Update
    #       best_reaction_time if this is an improvement. Turn off
    #       REACT_LED and enter_state(STATE_RESULT, current_time).
    pass

  # --- State: Chasing (TIMING mode) ---
  elif state == STATE_CHASING:
    # TODO: non-blocking chase animation - if elapsed since
    #       last_chase_step >= CHASE_INTERVAL_MS: turn off the
    #       current CHASE_LEDS[chase_position], advance chase_position
    #       by 1 (wrapping with % 4), turn on the new
    #       CHASE_LEDS[chase_position], and reset last_chase_step =
    #       current_time. If the new chase_position == TARGET_POSITION,
    #       also record last_target_lit_time = current_time and sound
    #       a short beep - this is the moment a well-timed press
    #       should land on.
    #
    # TODO: if SW2 is pressed, compute timing_error =
    #       abs(time.ticks_diff(current_time, last_target_lit_time)).
    #       Note this only measures distance from the MOST RECENT
    #       time the target lit, not the nearest occurrence in either
    #       direction - see Development Guide Step 5 for the
    #       limitation this creates and how to improve it. Update
    #       best_timing_error if this is an improvement. Turn off all
    #       CHASE_LEDS and enter_state(STATE_RESULT, current_time).
    pass

  # --- State: Result ---
  elif state == STATE_RESULT:
    # TODO: on entry to this state (elapsed == 0, or track a
    #       'result_shown' flag to only do this once), print the
    #       result:
    #       - SIMPLE, false start: print "Too soon!"
    #       - SIMPLE, normal: print reaction_time and whether it is
    #         a new best
    #       - TIMING: print timing_error and whether it is a new best
    #       Consider a distinct confirmation tone for a new best.
    #
    # TODO: once elapsed >= RESULT_DISPLAY_MS, enter_state(STATE_MENU,
    #       current_time) to return to mode selection.
    pass

  time.sleep_ms(LOOP_DELAY)


# ================================================================================
# Development Guide
# ================================================================================
#
# Work through these steps in order. Test SIMPLE mode completely
# before starting TIMING mode - they share very little code, but the
# overall program structure (state transitions, result display) is
# easiest to get right once with one working mode as a reference.
#
# --------------------------------------------------------------------------------
# Step 1 - Menu and mode selection
# --------------------------------------------------------------------------------
#
# The menu and mode-cycling logic (SW3/SW4 in STATE_MENU) is already
# complete. Run the program and confirm pressing SW3 or SW4 toggles
# between SIMPLE and TIMING, printing the mode name each time.
# Confirm SW2 calls start_round() and transitions to the correct
# first state for whichever mode is selected (STATE_WAITING for
# SIMPLE, STATE_CHASING for TIMING).
#
# --------------------------------------------------------------------------------
# Step 2 - False start detection
# --------------------------------------------------------------------------------
#
# Implement the false-start TODO in STATE_WAITING. Test by starting a
# SIMPLE round and immediately pressing SW2 before the LED lights.
# Confirm this transitions straight to STATE_RESULT without ever
# lighting REACT_LED.
#
# --------------------------------------------------------------------------------
# Step 3 - Stimulus and reaction timing
# --------------------------------------------------------------------------------
#
# Implement the remaining TODO in STATE_WAITING (lighting the
# stimulus) and the TODO in STATE_REACT (measuring the press).
# Test several rounds and confirm reaction_time values look
# reasonable (human simple reaction time is typically 150-300ms) and
# that best_reaction_time only updates when a round is genuinely
# faster than the previous best.
#
# --------------------------------------------------------------------------------
# Step 4 - Chase animation
# --------------------------------------------------------------------------------
#
# Implement the chase animation portion of the TODO in STATE_CHASING,
# without the press-handling yet. Confirm the four LEDs light in
# sequence, looping continuously, at the rate set by
# CHASE_INTERVAL_MS, and that a beep sounds each time the chase
# passes over the target LED (LED4).
#
# --------------------------------------------------------------------------------
# Step 5 - Timing measurement and its limitation
# --------------------------------------------------------------------------------
#
# Implement the press-handling portion of the TODO in STATE_CHASING.
# Test by pressing SW2 at different points in the chase cycle and
# confirming timing_error is small when you press near the target
# LED and large otherwise.
#
# This measurement has a known limitation worth understanding: it is
# calculated only against the MOST RECENT time the target lit, not
# whichever occurrence (past or upcoming) is actually closer. Press
# SW2 just before the chase is about to reach the target again - you
# should genuinely be very close in time, but timing_error will
# report a value close to a full chase cycle instead of close to
# zero, because it is measuring backward to the previous lit moment
# rather than forward to the upcoming one. Confirm you can observe
# this for yourself before moving on - EA 'improved timing
# measurement' below addresses it properly.
#
# --------------------------------------------------------------------------------
# Step 6 - Result display
# --------------------------------------------------------------------------------
#
# Implement STATE_RESULT. Test that each of the three result types
# (SIMPLE false start, SIMPLE normal, TIMING) prints a clear,
# distinguishable message, and that the program correctly returns to
# STATE_MENU after RESULT_DISPLAY_MS with the previously selected
# mode still active.


# ================================================================================
# Extension Activities
# ================================================================================
#
# --------------------------------------------------------------------------------
# EA 1 - Improved timing measurement
# --------------------------------------------------------------------------------
#
# Fix the limitation identified in Development Guide Step 5: rather
# than measuring only backward to the most recent time the target
# lit, compute the shortest distance to either the most recent OR
# the next upcoming occurrence, whichever is closer. This is the
# same "shortest distance around a repeating cycle" problem Stepper
# Controller's EA1 (bidirectional movement) solves for a rotating
# position - the chase's position within its 4-step cycle is directly
# analogous to the stepper's position within a full revolution.
#
# --------------------------------------------------------------------------------
# EA 2 - Running average
# --------------------------------------------------------------------------------
#
# Beyond tracking only the single best result, keep a running sum
# and count of every trial's result (in either mode) and display the
# average alongside the best. How does the average compare to the
# best across many trials - does it reveal anything the best score
# alone does not?
#
# --------------------------------------------------------------------------------
# EA 3 - Choice reaction time
# --------------------------------------------------------------------------------
#
# Add a third mode where, instead of always lighting REACT_LED, the
# stimulus randomly lights ONE of LED2-LED5 (reusing the read_button()
# style pattern from Simon Game or Combination Safe), and the player
# must press the MATCHING button (SW2-SW5) as quickly as possible.
# This tests both reaction speed and discrimination together - a
# real, named distinction in human factors research called "choice
# reaction time," typically measurably slower than simple reaction
# time even though it uses the same LEDs and buttons.
#
# --------------------------------------------------------------------------------
# EA 4 - Rhythm matching
# --------------------------------------------------------------------------------
#
# Add a fourth mode with a steady metronome beep and flash at a
# fixed tempo (reuse Activity 11's repeating-timer pattern
# directly). The player tries to press SW2 in sync with each beat,
# and each press is scored by how close it lands to the nearest
# beat - similar in spirit to TIMING mode, but matching a continuous
# rhythm rather than a single target point in a longer cycle. Track
# and display a running average timing error across several beats
# rather than just one round's result.
#
# --------------------------------------------------------------------------------
# EA 5 - Head-to-head
# --------------------------------------------------------------------------------
#
# Add a two-player mode: both players' buttons (for example SW2 and
# SW5, freeing SW5 from its cancel role while this mode is active)
# watch the same SIMPLE-style unpredictable stimulus, and whichever
# player presses first wins the round. This reuses SIMPLE mode's
# false-start and stimulus-timing logic almost entirely - the main
# difference is in STATE_REACT, which now needs to check two buttons
# and determine which was pressed first, rather than measuring one
# button's absolute reaction time.