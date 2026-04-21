"""
================================================================================
Capstone Project: Simon Memory Game [BEAPER_Nano-Capstone_Simon_Game.py]
April 21, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPER_Nano.py board module file.

Hardware used:
  SW2 / LED2 - Button and LED 1 (e.g. green)
  SW3 / LED3 - Button and LED 2 (e.g. red)
  SW4 / LED4 - Button and LED 3 (e.g. yellow)
  SW5 / LED5 - Button and LED 4 (e.g. blue)
  LS1        - Piezo speaker (one distinct tone per button)

Compatible with all BEAPER Nano configurations. No additional
hardware or jumper changes required.

--------------------------------------------------------------------------------
Game rules:
  The game plays back a growing sequence of flashing LEDs with tones.
  The player repeats the sequence by pressing the matching buttons.
  Each correct round adds one more step to the sequence.
  A wrong button press or timeout ends the game.
  Press any button during the idle animation to start a new game.
--------------------------------------------------------------------------------
Before you begin - complete your capstone plan:
  1. Write a plain-English description of the game from the player's
     perspective (what they see, hear, and do).
  2. List all states and draw your state diagram.
  3. Complete the state details table (outputs, transitions, next states).
  4. List all constants and variables you will need.
  5. Write your testing plan before writing any code.
================================================================================
"""
# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32
import BEAPER_Nano as beaper

import time
import random

# --- State Constants ------------------
STATE_IDLE      = const(0)  # Attract animation, waiting for player to start
STATE_PLAYBACK  = const(1)  # Showing current sequence step (LED + tone)
STATE_GAP       = const(2)  # Silent pause between playback steps
STATE_WAITING   = const(3)  # Player's turn - waiting for button press
STATE_CORRECT   = const(4)  # Brief correct-press feedback before next step
STATE_GAME_OVER = const(5)  # Wrong press or timeout - show score then idle

STATE_NAMES = {
  STATE_IDLE:      "IDLE",
  STATE_PLAYBACK:  "PLAYBACK",
  STATE_GAP:       "GAP",
  STATE_WAITING:   "WAITING",
  STATE_CORRECT:   "CORRECT",
  STATE_GAME_OVER: "GAME_OVER",
}

# --- Hardware Maps --------------------
# Parallel arrays: index 0-3 maps to button/LED/tone for each Simon colour.
BUTTONS = (beaper.SW2,  beaper.SW3,  beaper.SW4,  beaper.SW5)
LEDS    = (beaper.LED2, beaper.LED3, beaper.LED4, beaper.LED5)
TONES   = (659,         554,         440,         330)         # Hz, one per button

# --- Game Constants -------------------
MAX_LENGTH    = const(16)   # Maximum sequence length (traditional Simon = 16)
SHOW_TIME     = const(400)  # How long each sequence step is shown (ms)
GAP_TIME      = const(150)  # Silent gap between playback steps (ms)
PRESS_TIME    = const(300)  # How long a correct press lights the LED (ms)
TIMEOUT_MS    = const(5000) # Player must press within this time (ms)
IDLE_INTERVAL = const(300)  # Attract animation step interval (ms)

# --- Game Variables -------------------
state        = STATE_IDLE
state_start  = 0             # Time current state began

sequence     = [0] * MAX_LENGTH   # The generated sequence (button indices 0-3)
seq_length   = 0             # Current length of the active sequence
play_index   = 0             # Which step is currently being played back
input_index  = 0             # Which step the player is currently entering
score        = 0             # Highest sequence length completed this session

idle_step    = 0             # Current step in attract animation
last_idle    = 0             # Last time idle animation advanced


# --- Program Functions ----------------

def all_leds_off():
  for led in LEDS:
    led.value(0)
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
  LEDS[sequence[index]].value(1)
  beaper.tone(TONES[sequence[index]])

def read_button():
  # Return the index (0-3) of any currently pressed button, or -1 if none.
  for i, btn in enumerate(BUTTONS):
    if btn.value() == 0:
      return i
  return -1

def add_step():
  # Append a new random step to the sequence.
  sequence[seq_length] = random.randint(0, 3)

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
      seq_length += 1
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
    #         correctly: update score if needed, add a new step, reset
    #         play_index and input_index, and begin PLAYBACK of the new
    #         longer sequence
    #       - otherwise, remain in WAITING for the next button press
    pass

  # ---- State: Game over ----
  elif state == STATE_GAME_OVER:
    # TODO: play a distinctive failure sound and flash all LEDs briefly.
    #       After the feedback duration, call display_score() and enter IDLE.
    #       Hint: use elapsed to time the failure animation, then transition.
    pass

  time.sleep_ms(1)


"""
Capstone Development Guide

Work through these steps in order. Complete each step and test it
before moving on to the next.

Step 1 - Idle animation
  Implement the attract animation in STATE_IDLE. The pattern should
  cycle through the four LEDs using idle_step and the IDLE_INTERVAL
  timer. Test that pressing any button transitions to the first
  playback state and stops the animation.

Step 2 - Single step playback
  Implement STATE_PLAYBACK and STATE_GAP for a sequence of length 1.
  Verify that pressing the correct button produces a correct-press
  flash, and that pressing the wrong button transitions to GAME_OVER.
  Check the serial output to confirm state transitions are printing
  correctly.

Step 3 - Full playback sequence
  Extend the playback logic to handle sequences longer than 1. Use
  play_index to advance through the sequence. After all steps are
  shown, transition to STATE_WAITING with input_index = 0.

Step 4 - Player input and correct sequence
  Implement STATE_WAITING and STATE_CORRECT. After each correct press
  advance input_index. When input_index reaches seq_length, the round
  is complete - add a new step and begin playback of the longer sequence.

Step 5 - Game over and score
  Implement STATE_GAME_OVER with a clear failure sound/animation that
  is distinct from the correct-press feedback. Implement display_score()
  in a way that makes the score clear. Return to STATE_IDLE afterward.

Step 6 - Difficulty and polish (extensions)
  Consider these improvements once the core game works:

  a) Adjustable speed: decrease SHOW_TIME and GAP_TIME as the sequence
     grows longer, making later rounds harder. How will you calculate
     the speed from the current sequence length?

  b) High score: track the best score across multiple games in a
     variable that persists between STATE_GAME_OVER and STATE_IDLE.
     Display it at the start of each game.

  c) Strict mode: add a penalty for pressing a button at the wrong
     time (during playback). How does this affect your state machine?
     Which states need to check for unexpected button presses?

  d) Sound design: are the four tones clearly distinguishable on your
     hardware? Try adjusting TONES to find four pitches that sound
     natural together. The traditional Simon tones are E4, C#5, A3, 
     and E3, but these have been moved up an octave to E5, C#5, A4,
     and E4 (659 Hz, 554 Hz, 440 Hz, 330 Hz) so they sound better
     when played on the circuit's small piezo speaker.

"""
