# ================================================================================
# Capstone Project: Morse Code Trainer [Morse_Code_Trainer.py]
# Version: 1.0
# Updated: July 25, 2026
#
# Platform: mirobo.tech BEAPER Nano circuit (any configuration)
# Requires: BEAPER_Nano.py board module file
#
# Practice sending and receiving Morse code using a single button.
# Hold SW2 briefly for a dot, longer for a dash - the same tap/hold
# timing idea from Activity 11, applied to classify each press rather
# than just detecting a hold.
#
# Two modes, selected with SW3/SW4 at the menu:
#
#   TRANSMIT - Free practice. Tap out letters at your own pace; each
#              completed letter is decoded and printed as soon as you
#              pause. No pressure, no scoring - just practice forming
#              correct dot/dash patterns.
#
#   RECEIVE  - The program picks a random letter and sends it back to
#              you (LED2 flashes, LS1 beeps - a dot is a short flash,
#              a dash is three times as long). You then tap the same
#              letter back using the identical tap interface, and the
#              program checks whether it matches.
#
# Both modes rely on the exact same underlying mechanism - reading
# taps, classifying each as a dot or dash, and detecting when a
# letter is complete from the pause that follows it. That shared
# logic lives in one function, read_tap(), that both modes call.
#
# Hardware used:
#   SW2          - Tap button (hold briefly for a dot, longer for a dash)
#   SW3 / SW4    - Cycle mode (only while at the menu)
#   SW5          - Start / return to menu
#   LED2         - Lights while SW2 is held, and during RECEIVE's playback
#   LS1          - Piezo speaker (tap tone, playback tone)
#
# Compatible with all BEAPER Nano configurations. No additional
# hardware or jumper changes required.
#
# --------------------------------------------------------------------------------
# Timing (see Development Guide Step 1 for calibration):
#   DOT_MAX_MS    - a press shorter than this is a dot; longer is a dash
#   LETTER_GAP_MS - a pause longer than this after a release, with no
#                   new press, means the letter is complete
#
# Real Morse timing uses fixed ratios: a dash is three dot-durations
# long, the gap between letters is three dot-durations, and the gap
# between words is seven. This trainer uses similar proportions but
# with more forgiving absolute values, since tapping accurately by
# hand is harder than a machine sending at a fixed rate.
#
# --------------------------------------------------------------------------------
# Trainer behaviour:
#   MENU           - Select mode with SW3/SW4. Press SW5 to begin.
#   TRANSMIT       - Continuous free-form tapping and decoding.
#                    Press SW5 to return to the menu.
#   RECEIVE_SEND   - The program sends a random letter.
#   RECEIVE_LISTEN - Your turn - tap back the same letter.
#   RECEIVE_RESULT - Shows whether you matched it, then starts
#                    another round automatically.
#
# Before you begin - complete your capstone plan using the Capstone
# Preparation Guide: a plain-English description of each mode, a
# state diagram, your constants and variables, and your testing plan.
# ================================================================================

# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32.
import BEAPER_Nano as beaper  # Set up BEAPER Nano I/O

import time
import random

# --- State Constants -------------------
STATE_MENU           = const(0)      # Selecting a mode
STATE_TRANSMIT       = const(1)      # Free-form tapping and decoding
STATE_RECEIVE_SEND   = const(2)      # Program is sending the target letter
STATE_RECEIVE_LISTEN = const(3)      # Player taps the letter back
STATE_RECEIVE_RESULT = const(4)      # Showing whether it matched

STATE_NAMES = {
  STATE_MENU:           "MENU",
  STATE_TRANSMIT:       "TRANSMIT",
  STATE_RECEIVE_SEND:   "RECEIVE_SEND",
  STATE_RECEIVE_LISTEN: "RECEIVE_LISTEN",
  STATE_RECEIVE_RESULT: "RECEIVE_RESULT",
}

# --- Mode Constants ---------------------
MODE_TRANSMIT = const(0)
MODE_RECEIVE  = const(1)
NUM_MODES     = const(2)

MODE_NAMES = {
  MODE_TRANSMIT: "TRANSMIT",
  MODE_RECEIVE:  "RECEIVE",
}

# --- Morse Code Lookup Table -------------
# Two parallel lists, indexed together - the same pattern used
# throughout this curriculum's capstones, here holding the full
# alphabet. MORSE_LETTERS[i] and MORSE_CODES[i] together describe
# one letter: MORSE_LETTERS[0] is "A", MORSE_CODES[0] is its
# dot/dash pattern ".-", and so on.
MORSE_LETTERS = ['A','B','C','D','E','F','G','H','I','J','K','L','M',
                  'N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
MORSE_CODES   = ['.-','-...','-.-.','-..','.','..-.','--.','....','..',
                  '.---','-.-','.-..','--','-.','---','.--.','--.-',
                  '.-.','...','-','..-','...-','.--','-..-','-.--','--..']
NUM_LETTERS   = const(26)

# --- Tap Timing Configuration -------------
DOT_MAX_MS    = const(300)           # Press shorter than this = dot; longer = dash
LETTER_GAP_MS = const(700)           # Pause this long after a release = letter complete

# --- Receive Mode Playback Configuration --
SYMBOL_GAP_MS     = const(200)       # Silent gap between symbols within one letter
DASH_MULTIPLIER   = const(3)         # A dash is played this many times as long as a dot
RESULT_DISPLAY_MS = const(2000)      # How long the RECEIVE result is shown

# --- Program Variables -------------------
state        = STATE_MENU
state_start  = 0

current_mode = MODE_TRANSMIT

# --- Shared tap-reading state (used by read_tap(), see below) ---
sw2_was_pressed  = False
press_start      = 0
current_sequence = ""                # Dots/dashes accumulated for the letter in progress
last_release_time = 0
letter_pending    = False            # True when at least one symbol is waiting on a gap

# --- SW3/SW4 edge detection (menu mode cycling) ---
sw3_last = 1
sw4_last = 1

# --- Receive mode variables ---
target_letter = ""
target_code   = ""
symbol_index  = 0                    # Which symbol of target_code is being sent/was just sent
sending_on    = False                # True while LED2/LS1 are active for the current symbol
symbol_start  = 0
received_correct = False


# --- Program Functions ------------------

def enter_state(new_state, current_time, reason=""):
  global state, state_start
  state       = new_state
  state_start = current_time
  print("-->", STATE_NAMES[new_state], end="")
  if reason:
    print(" (", reason, ")", sep="")
  else:
    print()

def decode_letter(sequence):
  # Look up the letter matching a completed dot/dash sequence.
  # Returns '?' if the sequence does not match any known letter -
  # this happens naturally from mistimed taps and is not an error.
  for i in range(NUM_LETTERS):
    if MORSE_CODES[i] == sequence:
      return MORSE_LETTERS[i]
  return '?'

def encode_letter(letter):
  # Look up the dot/dash sequence for a given letter.
  for i in range(NUM_LETTERS):
    if MORSE_LETTERS[i] == letter:
      return MORSE_CODES[i]
  return ""

def read_tap(current_time):
  # Read SW2, classify each press as a dot or dash by its duration,
  # and accumulate symbols into current_sequence. Call this every
  # loop iteration while tap input should be accepted (both TRANSMIT
  # and RECEIVE_LISTEN do this).
  #
  # Returns the completed sequence (a string of '.' and '-') once a
  # LETTER_GAP_MS pause follows the most recent release with no new
  # press - this is the signal that the player has finished a letter
  # and moved on. Returns None on every call where nothing new has
  # completed yet.
  #
  # TODO: implement this function using the following steps:
  #
  # 1. Read SW2's current state. Compare it against sw2_was_pressed
  #    (tracking the PREVIOUS reading) to detect edges - the same
  #    pattern used for SW3/SW4 in STATE_MENU below.
  #
  # 2. On a press edge (was not pressed, now is): record
  #    press_start = current_time. Update sw2_was_pressed.
  #
  # 3. On a release edge (was pressed, now is not): calculate how
  #    long the press lasted (current_time - press_start). If shorter
  #    than DOT_MAX_MS, append '.' to current_sequence; otherwise
  #    append '-'. Record last_release_time = current_time and set
  #    letter_pending = True. Update sw2_was_pressed.
  #
  # 4. Regardless of the above, check: if letter_pending is True AND
  #    SW2 is not currently pressed AND the time since
  #    last_release_time is at least LETTER_GAP_MS, the letter is
  #    complete. Save current_sequence into a local variable, reset
  #    current_sequence = "" and letter_pending = False, and return
  #    the saved sequence.
  #
  # 5. If none of the above produced a completed sequence, return
  #    None.
  #
  # Think carefully about step 4's ordering relative to steps 2-3 -
  # should the gap check happen before or after processing a
  # press/release edge that occurs on the very same call?
  pass


# --- Main Program ---------------------

beaper.LED2.value(0)
print("Morse Code Trainer")
print("SW3/SW4: change mode   SW5: start / menu   SW2: tap")
print()

state_start = time.ticks_ms()
enter_state(STATE_MENU, state_start, "startup")
print("Mode:", MODE_NAMES[current_mode])

while True:
  current_time = time.ticks_ms()
  elapsed      = time.ticks_diff(current_time, state_start)

  # --- State: Menu ---
  if state == STATE_MENU:
    sw3_current = beaper.SW3.value()
    sw4_current = beaper.SW4.value()
    if (sw3_current == 0 and sw3_last == 1) or (sw4_current == 0 and sw4_last == 1):
      current_mode = (current_mode + 1) % NUM_MODES
      print("Mode:", MODE_NAMES[current_mode])
    sw3_last = sw3_current
    sw4_last = sw4_current

    if beaper.SW5.value() == 0:
      if current_mode == MODE_TRANSMIT:
        print("Tap away - pause to complete a letter. SW5 to return to menu.")
        enter_state(STATE_TRANSMIT, current_time, "start")
      else:
        target_letter = MORSE_LETTERS[random.randint(0, NUM_LETTERS - 1)]
        target_code   = encode_letter(target_letter)
        symbol_index  = 0
        sending_on    = True
        symbol_start  = current_time
        beaper.LED2.value(1)
        beaper.tone(440)
        enter_state(STATE_RECEIVE_SEND, current_time, "start")

  # --- State: Transmit ---
  elif state == STATE_TRANSMIT:
    if beaper.SW5.value() == 0:
      enter_state(STATE_MENU, current_time, "SW5 pressed")
    else:
      # TODO: call read_tap(current_time). If it returns a completed
      #       sequence (not None), decode it with decode_letter() and
      #       print both the sequence and the decoded letter, e.g.:
      #       "-.-.  ->  C"
      pass

  # --- State: Receive - Send (fully worked - see Development Guide Step 3) ---
  elif state == STATE_RECEIVE_SEND:
    symbol_duration = DOT_MAX_MS if target_code[symbol_index] == '.' else DOT_MAX_MS * DASH_MULTIPLIER
    symbol_elapsed  = time.ticks_diff(current_time, symbol_start)

    if sending_on and symbol_elapsed >= symbol_duration:
      beaper.LED2.value(0)
      beaper.noTone()
      sending_on = False
      symbol_start = current_time
    elif not sending_on and symbol_elapsed >= SYMBOL_GAP_MS:
      symbol_index += 1
      if symbol_index >= len(target_code):
        print("Your turn - tap back:", target_letter)
        enter_state(STATE_RECEIVE_LISTEN, current_time, "sent")
      else:
        beaper.LED2.value(1)
        beaper.tone(440)
        sending_on = True
        symbol_start = current_time

  # --- State: Receive - Listen ---
  elif state == STATE_RECEIVE_LISTEN:
    # TODO: call read_tap(current_time). If it returns a completed
    #       sequence, compare it against target_code:
    #       - set received_correct = (sequence == target_code)
    #       - print what the player sent and whether it was correct
    #       - play a distinct confirmation or "incorrect" tone
    #       - enter_state(STATE_RECEIVE_RESULT, current_time)
    pass

  # --- State: Receive - Result ---
  elif state == STATE_RECEIVE_RESULT:
    if elapsed >= RESULT_DISPLAY_MS:
      if beaper.SW5.value() == 0:
        enter_state(STATE_MENU, current_time, "SW5 pressed")
      else:
        # Start another round automatically
        target_letter = MORSE_LETTERS[random.randint(0, NUM_LETTERS - 1)]
        target_code   = encode_letter(target_letter)
        symbol_index  = 0
        sending_on    = True
        symbol_start  = current_time
        beaper.LED2.value(1)
        beaper.tone(440)
        enter_state(STATE_RECEIVE_SEND, current_time, "next round")

  time.sleep_ms(1)


# ================================================================================
# Development Guide
# ================================================================================
#
# Work through these steps in order.
#
# --------------------------------------------------------------------------------
# Step 1 - Calibrate the timing constants
# --------------------------------------------------------------------------------
#
# Before implementing anything, get a feel for DOT_MAX_MS and
# LETTER_GAP_MS by tapping naturally on SW2 while printing raw press
# durations. Temporarily add this loop after beaper.LED2.value(0)
# near the top of the program:
#
# Example code:
#
# while True:
#   if beaper.SW2.value() == 0:
#     press_start = time.ticks_ms()
#     while beaper.SW2.value() == 0:
#       pass
#     duration = time.ticks_diff(time.ticks_ms(), press_start)
#     print("press duration:", duration, "ms")
#
# Tap several short presses and several deliberately longer ones.
# Choose a DOT_MAX_MS value comfortably between your typical short
# and long presses - not guessed, measured. Remove the test loop
# once you have a value that feels right.
#
# --------------------------------------------------------------------------------
# Step 2 - Implement read_tap()
# --------------------------------------------------------------------------------
#
# This is the core mechanism the whole trainer depends on - both
# modes call it. Implement it following the TODO steps in its
# definition. Test it in isolation before moving on: temporarily call
# it every loop iteration from STATE_MENU and print whatever it
# returns, then tap out a few letters by hand and confirm the raw
# sequences look right (dots and dashes in the order and count you
# expect) before worrying about whether they decode to the correct
# letter.
#
# --------------------------------------------------------------------------------
# Step 3 - Understand RECEIVE_SEND
# --------------------------------------------------------------------------------
#
# STATE_RECEIVE_SEND is already complete - read through it before
# implementing RECEIVE_LISTEN. It uses the same flash-then-gap
# sub-phase pattern as Rock-Paper-Scissors's countdown: sending_on
# tracks whether LED2/LS1 are currently active for the symbol at
# symbol_index, and symbol_duration is calculated per-symbol (a dash
# takes DASH_MULTIPLIER times as long as a dot to send) rather than
# being a single fixed value.
#
# Run the program, select RECEIVE, and press SW5. Confirm a random
# letter is sent - watch and listen for a pattern of short and long
# flashes with gaps between them, and check the Serial Monitor for
# which letter was chosen so you can verify what you saw matches.
#
# --------------------------------------------------------------------------------
# Step 4 - Transmit mode
# --------------------------------------------------------------------------------
#
# Implement the TODO in STATE_TRANSMIT. Test by selecting TRANSMIT
# and tapping out several different letters, confirming each is
# decoded correctly after you pause. Deliberately tap an invalid
# sequence (five dots in a row, for example) and confirm it prints
# '?' rather than crashing or hanging.
#
# --------------------------------------------------------------------------------
# Step 5 - Receive listening and comparison
# --------------------------------------------------------------------------------
#
# Implement the TODO in STATE_RECEIVE_LISTEN. Test by selecting
# RECEIVE and correctly tapping back several letters the program
# sends, then deliberately tapping the wrong letter back at least
# once, confirming both outcomes are detected and reported correctly.
#
# --------------------------------------------------------------------------------
# Step 6 - Full session
# --------------------------------------------------------------------------------
#
# Play several RECEIVE rounds in a row and confirm each automatically
# starts the next after RESULT_DISPLAY_MS, and that pressing SW5
# during RECEIVE_RESULT returns to the menu instead. Switch between
# TRANSMIT and RECEIVE at the menu and confirm both still work
# correctly after switching back and forth.


# ================================================================================
# Extension Activities
# ================================================================================
#
# --------------------------------------------------------------------------------
# EA 1 - External Morse key
# --------------------------------------------------------------------------------
#
# A real Morse key (a straight key, specifically - the classic
# spring-loaded lever switch) is far more tactile and authentic to
# practice on than a small tactile button. Wire one to H1 as a
# second momentary switch input, using the same pull-up pattern as
# Combination Safe's door sensor (H1 also carries I2C/QWIIC SDA on
# BEAPER Nano - not a conflict for this capstone, which does not use
# I2C, but worth knowing if you extend the project further):
#
# Example code:
#
# from machine import Pin
# key_switch = Pin(beaper.H1_PIN, Pin.IN, Pin.PULL_UP)
#
# Rather than choosing between SW2 or the external key, let both work
# at once - replace every beaper.SW2.value() == 0 check inside
# read_tap() with a call to a small helper function:
#
# Example code:
#
# def tap_pressed():
#   return beaper.SW2.value() == 0 or key_switch.value() == 0
#
# This sidesteps needing any kind of input-source setting entirely.
# With no external key wired up, key_switch simply reads "released"
# permanently via its own pull-up, so nothing breaks or needs
# toggling - SW2 keeps working exactly as before. With a key
# connected, either one taps out dots and dashes interchangeably,
# even switching between them mid-session.
#
# --------------------------------------------------------------------------------
# EA 2 - Full words and phrases
# --------------------------------------------------------------------------------
#
# Add a third mode where RECEIVE sends a whole word instead of a
# single letter - each letter of the word sent in turn, with a
# WORD_GAP_MS-length pause (rather than SYMBOL_GAP_MS) marking the
# boundary between letters within the word so the player can tell
# where one letter ends and the next begins. Build your own word
# list (a simple list of short, all-uppercase strings works well -
# add your own words to it) and pick one at random the same way
# target_letter is currently chosen from MORSE_LETTERS. The player
# must tap back the entire word, letter by letter, matching
# read_tap()'s per-letter completion against the word's letters in
# order.
#
# --------------------------------------------------------------------------------
# EA 3 - Numbers and punctuation
# --------------------------------------------------------------------------------
#
# Extend MORSE_LETTERS and MORSE_CODES with entries for 0-9 (and
# punctuation, if you like) rather than building a separate lookup
# mechanism - the existing decode_letter()/encode_letter() functions
# work unchanged with a longer table, since they already search the
# whole list rather than assuming exactly 26 entries. Remember to
# update NUM_LETTERS to match the new table length.
#
# --------------------------------------------------------------------------------
# EA 4 - Adjustable speed (WPM)
# --------------------------------------------------------------------------------
#
# Morse speed is conventionally measured in words per minute (WPM),
# based on a standard word length. Add a speed setting (adjustable
# with SW3/SW4 at the menu, similar to how mode is currently
# selected) that scales DOT_MAX_MS, LETTER_GAP_MS, SYMBOL_GAP_MS, and
# RECEIVE_SEND's dot duration all together from one WPM value, rather
# than as independent constants. What relationship between WPM and
# dot duration would you use? (Hint: research the standard "PARIS"
# timing method real operators use to define WPM precisely.)
#
# --------------------------------------------------------------------------------
# EA 5 - SOS recognition
# --------------------------------------------------------------------------------
#
# Real operators send SOS as a single continuous prosign - three
# dots, three dashes, three dots, with no letter-gap pauses between
# the S, O, and S - rather than as three separately-decoded letters.
# In read_tap()'s terms, this means the full sequence "...---..."
# arrives as ONE completed sequence, not three. Add a check (in
# either TRANSMIT or RECEIVE, or both) for this exact sequence, and
# trigger a distinct, attention-grabbing alarm response when
# detected - reusing Alarm System's aesthetic seems fitting for
# something that is, after all, the universal distress signal.
#
# --------------------------------------------------------------------------------
# EA 6 - Audio-only or visual-only practice
# --------------------------------------------------------------------------------
#
# Real Morse operators work by sound alone - add a setting (cycled
# at the menu alongside mode) that makes RECEIVE_SEND use only LS1,
# only LED2, or both together, letting a player practice pure audio
# reception once they no longer need the visual flash as a crutch.