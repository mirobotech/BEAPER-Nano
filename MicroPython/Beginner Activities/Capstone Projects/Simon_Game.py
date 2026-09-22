# ================================================================================
# Capstone Project: Simon Memory Game [Simon_Game.py]
# Version: 1.0
# Updated: July 25, 2026
#
# Platform: mirobo.tech BEAPER Nano circuit (any configuration)
# Requires: BEAPER_Nano.py board module file
#
# Hardware used:
#   SW2 / LED2 - Button and LED 1 (e.g. green)
#   SW3 / LED3 - Button and LED 2 (e.g. red)
#   SW4 / LED4 - Button and LED 3 (e.g. yellow)
#   SW5 / LED5 - Button and LED 4 (e.g. blue)
#   LS1        - Piezo speaker (one distinct tone per button)
#
# Compatible with all BEAPER Nano configurations. No additional
# hardware or jumper changes required.
#
# --------------------------------------------------------------------------------
# Game rules:
#   The game plays back a growing sequence of flashing LEDs with tones.
#   The player repeats the sequence by pressing the matching buttons.
#   Each correct round adds one more step to the sequence.
#   A wrong button press or timeout ends the game.
#   Completing the maximum sequence length (MAX_LENGTH) wins the game.
#   Press any button during the idle animation to start a new game.
#
# --------------------------------------------------------------------------------
# This capstone introduces two new data structures: tuples and lists.
# Both hold multiple related values under one name, indexed by position
# (starting at 0) - but they behave differently once created. Read the
# Development Guide's Step 1 before starting, since every other step
# depends on understanding this distinction.
#
# Before you begin - complete your capstone plan using the Capstone
# Preparation Guide: project description, state diagram, state
# details table, constants and variables, and testing plan.
# ================================================================================

# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32.
import BEAPER_Nano as beaper  # Set up BEAPER Nano I/O

import time
import random

# --- State Constants ------------------
STATE_IDLE      = const(0)   # Attract animation, waiting for player to start
STATE_PLAYBACK  = const(1)   # Showing current sequence step (LED + tone)
STATE_GAP       = const(2)   # Silent pause between playback steps
STATE_WAITING   = const(3)   # Player's turn - waiting for button press
STATE_CORRECT   = const(4)   # Brief correct-press feedback before next step
STATE_GAME_OVER = const(5)   # Wrong press, timeout, or MAX_LENGTH reached

STATE_NAMES = {
  STATE_IDLE:      "IDLE",
  STATE_PLAYBACK:  "PLAYBACK",
  STATE_GAP:       "GAP",
  STATE_WAITING:   "WAITING",
  STATE_CORRECT:   "CORRECT",
  STATE_GAME_OVER: "GAME_OVER",
}

# --- Hardware Maps --------------------
# Tuples: fixed-size, ordered collections that cannot change size or be
# reassigned by index after creation. Good for grouping a fixed set of
# related values - here, one entry per Simon colour, indexed 0-3.
# See Development Guide Step 1 before relying on these.
BUTTONS = (beaper.SW2,  beaper.SW3,  beaper.SW4,  beaper.SW5)
LEDS    = (beaper.LED2, beaper.LED3, beaper.LED4, beaper.LED5)
TONES   = (659,         554,         440,         330)         # Hz, one per button

# --- Game Constants -------------------
MAX_LENGTH    = const(16)    # Maximum sequence length (traditional Simon = 16)
SHOW_TIME     = const(400)   # How long each sequence step is shown (ms)
GAP_TIME      = const(150)   # Silent gap between playback steps (ms)
PRESS_TIME    = const(300)   # How long a correct press lights the LED (ms)
TIMEOUT_MS    = const(5000)  # Player must press within this time (ms)
IDLE_INTERVAL = const(300)   # Attract animation step interval (ms)

# --- Game Variables -------------------
state        = STATE_IDLE
state_start  = 0             # Time current state began

# List: like a tuple, but individual elements CAN be changed after
# creation - see Development Guide Step 1. sequence[0] * MAX_LENGTH
# creates a list of 16 zeros as a starting point; add_step() below
# replaces one zero at a time with a random step as the game grows.
sequence     = [0] * MAX_LENGTH   # The generated sequence (button indices 0-3)
seq_length   = 0             # Current length of the active sequence
play_index   = 0             # Which step is currently being played back
input_index  = 0             # Which step the player is currently entering
score        = 0             # Highest sequence length completed this session

idle_step    = 0             # Current step in attract animation
last_idle    = 0             # Last time idle animation advanced


# --- Program Functions ----------------

def all_leds_off():
  for i in range(4):
    LEDS[i].value(0)
  beaper.nano_led_off()

def enter_state(new_state, current_time, reason=""):
  global state, state_start
  all_leds_off()
  beaper.noTone()
  state       = new_state
  state_start = current_time
  print("-->", STATE_NAMES[new_state], end="")
  if reason:
    print(" (", reason, ")", sep="")
  else:
    print()

def show_step(index):
  # Light the LED and play the tone for sequence step at 'index'.
  button_index = sequence[index]
  LEDS[button_index].value(1)
  beaper.tone(TONES[button_index])

def read_button():
  # Return the index (0-3) of any currently pressed button, or -1 if none.
  for i in range(4):
    if BUTTONS[i].value() == 0:
      return i
  return -1

def add_step():
  # Append a new random step to the sequence, if there is room.
  # Returns True if a step was added, False if the sequence is
  # already at MAX_LENGTH (the player has won).
  global seq_length
  if seq_length >= MAX_LENGTH:
    return False
  sequence[seq_length] = random.randint(0, 3)
  seq_length += 1
  return True

def display_score(final_score):
  # Flash LEDs to indicate the score - one flash per level completed.
  # TODO: implement a visual or serial score display of your choice.
  # Ideas: flash LED2-LED5 as a bar (1-4 flashes = 1-4 LEDs lit),
  #        print the score to the serial console, or blink the
  #        on-board LED 'score' times with a pause between groups.
  print("Score:", final_score, "steps completed")


# --- Main Program ---------------------

all_leds_off()
beaper.nano_led_on()
print("Simon Memory Game")
print("Press any button to start")
print()

state_start = time.ticks_ms()
last_idle   = time.ticks_ms()

while True:
  current_time = time.ticks_ms()
  elapsed      = time.ticks_diff(current_time, state_start)
  pressed      = read_button()

  # ---- State: Idle (attract animation) ----
  if state == STATE_IDLE:
    # TODO: cycle a simple animation across LED2-LED5 using idle_step and
    #       last_idle with IDLE_INTERVAL timing (pattern from Activity 11).
    #       Hint: light LEDS[idle_step % 4] and advance idle_step each interval.

    # Start a new game when any button is pressed
    if pressed != -1:
      seq_length  = 0
      input_index = 0
      play_index  = 0
      add_step()
      enter_state(STATE_PLAYBACK, current_time, "game start")
      show_step(0)

  # ---- State: Playback (showing one sequence step) ----
  elif state == STATE_PLAYBACK:
    # TODO: when SHOW_TIME elapses, turn off the LED and tone then
    #       transition to STATE_GAP. After the gap, either show the
    #       next step (transition back to PLAYBACK) or, if all steps
    #       have been shown, transition to STATE_WAITING.
    #       Use play_index to track which step is currently showing.
    pass

  # ---- State: Gap (silent pause between steps) ----
  elif state == STATE_GAP:
    # TODO: when GAP_TIME elapses, check if there are more steps to show.
    #       If play_index < seq_length, show the next step and enter PLAYBACK.
    #       If all steps have been shown, enter WAITING (player's turn).
    pass

  # ---- State: Waiting (player's turn) ----
  elif state == STATE_WAITING:
    # TODO: if TIMEOUT_MS elapses with no button press, enter GAME_OVER.
    # TODO: if a button is pressed:
    #       - if it matches sequence[input_index], enter CORRECT
    #         (light the pressed LED and play its tone for PRESS_TIME)
    #       - if it does not match, enter GAME_OVER
    pass

  # ---- State: Correct press feedback ----
  elif state == STATE_CORRECT:
    # TODO: when PRESS_TIME elapses, turn off LED and tone, then:
    #       - increment input_index
    #       - if input_index == seq_length, the full sequence was entered
    #         correctly:
    #           - update score if seq_length > score
    #           - call add_step(). If it returns False, the sequence has
    #             reached MAX_LENGTH - the player has won! Enter
    #             STATE_GAME_OVER with reason "you win!" (consider a
    #             distinct victory tone in that state, different from
    #             the failure tone).
    #           - otherwise, reset play_index and input_index to 0 and
    #             begin STATE_PLAYBACK of the new, longer sequence
    #       - if input_index < seq_length, remain in WAITING for the
    #         next button press
    pass

  # ---- State: Game over ----
  elif state == STATE_GAME_OVER:
    # TODO: play a distinctive failure sound and flash all LEDs briefly.
    #       (Check state_start's reason was not saved - if you want a
    #       different sound for winning MAX_LENGTH vs. losing, store
    #       a separate 'won' flag when entering this state instead of
    #       trying to inspect the reason string later.)
    #       After the feedback duration, call display_score() and enter IDLE.
    #       Hint: use elapsed to time the failure animation, then transition.
    pass

  time.sleep_ms(1)


# ================================================================================
# Development Guide
# ================================================================================
#
# Work through these steps in order. Complete each step and test it
# before moving on to the next.
#
# --------------------------------------------------------------------------------
# Step 1 - Understanding lists and tuples
# --------------------------------------------------------------------------------
#
# Every activity up to this point stored related values in separate
# named variables - Activity 12's combination lock used entered_1,
# entered_2, entered_3, entered_4 for a four-digit code. That works
# well for a small, fixed number of values, but Simon's sequence can
# grow up to MAX_LENGTH (16) steps. Writing entered_1 through
# entered_16, with a 16-way if/elif chain to read the right one,
# would be unwieldy - and would need rewriting entirely if MAX_LENGTH
# ever changed. This capstone uses two new constructs instead.
#
# A TUPLE is an ordered collection of values, indexed starting at 0,
# written with parentheses:
#
# Example code:
#
# BUTTONS = (beaper.SW2, beaper.SW3, beaper.SW4, beaper.SW5)
#
# BUTTONS[0] is beaper.SW2, BUTTONS[1] is beaper.SW3, and so on.
# Once created, a tuple's size is fixed, and you cannot assign a new
# value to one of its positions - BUTTONS[0] = beaper.SW3 would raise
# an error. This program uses three tuples - BUTTONS, LEDS, and
# TONES - as parallel lookups: button index 2 (SW4) always
# corresponds to LEDS[2] (LED4) and TONES[2] (440 Hz). This is a
# natural fit for a tuple, because the mapping between buttons, LEDs,
# and tones never changes while the program runs.
#
# A LIST looks similar but is written with square brackets, and -
# unlike a tuple - its elements CAN be changed after creation:
#
# Example code:
#
# sequence = [0] * MAX_LENGTH
#
# This creates a list of 16 zeros: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
# 0, 0, 0, 0, 0]. Unlike the tuples above, individual elements of
# 'sequence' change throughout the game:
#
# Example code:
#
# sequence[seq_length] = random.randint(0, 3)
#
# This is the core reason Simon's sequence needs a list rather than a
# tuple: each round, a new random step is written into the next
# available position. A tuple could not do this - you would need to
# build an entirely new tuple every time a step is added, which is
# both awkward and wasteful. Use a tuple when a fixed collection of
# values will not change; use a list when individual elements need
# to be updated after creation.
#
# Both are read the same way - square brackets with an index:
# BUTTONS[i], LEDS[i], sequence[i]. Trace through 'add_step()' and
# 'show_step()' and confirm you can predict what each line does
# before continuing.
#
# --------------------------------------------------------------------------------
# Step 2 - Idle animation
# --------------------------------------------------------------------------------
#
# Implement the attract animation in STATE_IDLE. The pattern should
# cycle through the four LEDs using idle_step and the IDLE_INTERVAL
# timer. Test that pressing any button transitions to the first
# playback state and stops the animation.
#
# --------------------------------------------------------------------------------
# Step 3 - Single step playback
# --------------------------------------------------------------------------------
#
# Implement STATE_PLAYBACK and STATE_GAP for a sequence of length 1.
# Verify that pressing the correct button produces a correct-press
# flash, and that pressing the wrong button transitions to GAME_OVER.
# Check the Serial output to confirm state transitions are printing
# correctly.
#
# --------------------------------------------------------------------------------
# Step 4 - Full playback sequence
# --------------------------------------------------------------------------------
#
# Extend the playback logic to handle sequences longer than 1. Use
# play_index to advance through the sequence. After all steps are
# shown, transition to STATE_WAITING with input_index = 0.
#
# --------------------------------------------------------------------------------
# Step 5 - Player input and correct sequence
# --------------------------------------------------------------------------------
#
# Implement STATE_WAITING and STATE_CORRECT. After each correct press
# advance input_index. When input_index reaches seq_length, the round
# is complete - call add_step() and begin playback of the longer
# sequence, unless add_step() returns False (MAX_LENGTH reached).
#
# --------------------------------------------------------------------------------
# Step 6 - Winning and losing
# --------------------------------------------------------------------------------
#
# Implement STATE_GAME_OVER with a clear failure sound/animation that
# is distinct from the correct-press feedback - and a distinct sound
# for winning (reaching MAX_LENGTH) versus losing (wrong press or
# timeout). Test both endings deliberately: losing is easy to test by
# pressing a wrong button, but reaching MAX_LENGTH requires either
# genuine skill or temporarily lowering MAX_LENGTH for testing.
# Implement display_score() in a way that makes the score clear.
# Return to STATE_IDLE afterward.
#
# --------------------------------------------------------------------------------
# Step 7 - Difficulty and polish
# --------------------------------------------------------------------------------
#
# Once the core game works end to end, move on to the Extension
# Activities below for ideas on making the game more challenging or
# more polished.


# ================================================================================
# Extension Activities
# ================================================================================
#
# --------------------------------------------------------------------------------
# EA 1 - Adjustable speed
# --------------------------------------------------------------------------------
#
# Decrease SHOW_TIME and GAP_TIME as the sequence grows longer,
# making later rounds harder. How will you calculate the speed from
# the current sequence length?
#
# --------------------------------------------------------------------------------
# EA 2 - High score
# --------------------------------------------------------------------------------
#
# Track the best score across multiple games in a variable that
# persists between STATE_GAME_OVER and STATE_IDLE. Display it at the
# start of each game.
#
# --------------------------------------------------------------------------------
# EA 3 - Strict mode
# --------------------------------------------------------------------------------
#
# Add a penalty for pressing a button at the wrong time (during
# playback). How does this affect your state machine? Which states
# need to check for unexpected button presses?
#
# --------------------------------------------------------------------------------
# EA 4 - Sound design
# --------------------------------------------------------------------------------
#
# Are the four tones clearly distinguishable on your hardware? Try
# adjusting TONES to find four pitches that sound natural together.
# The traditional Simon tones are E4, C#5, A3, and E3, but these have
# been moved up an octave to E5, C#5, A4, and E4 (659 Hz, 554 Hz,
# 440 Hz, 330 Hz) so they sound better when played on the circuit's
# small piezo speaker.