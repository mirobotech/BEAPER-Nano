# ================================================================================
# Capstone Project: Combination Safe [Combination_Safe.py]
# Version: 1.0
# Updated: July 25, 2026
#
# Platform: mirobo.tech BEAPER Nano circuit (any configuration)
# Requires: BEAPER_Nano.py board module file
#
# A four-digit digital safe. SW2, SW3, SW4, and SW5 are the code
# buttons - any of the four can appear at any position in the code,
# and digits may repeat. Enter the correct four-button sequence to
# unlock; a wrong sequence resets silently with no visible feedback,
# so a would-be intruder learns nothing about which digit was wrong.
# The number of wrong attempts since the last successful unlock is
# logged silently and shown briefly the next time the safe opens.
#
# Hardware used:
#   SW2-SW5    - Code entry buttons (all four used as code digits)
#   LED2       - Code-setting mode indicator (on while setting a new code)
#   LED5       - Attempt counter indicator (flashes after unlock if
#                any wrong attempts were logged)
#   LS1        - Piezo speaker (key feedback, code-set, unlock, wrong-code tones)
#   Servo on H5 (SERVO1 by default) - Locking mechanism
#
# IMPORTANT - Header pin sharing: H5-H8 are electrically the same
# pins as H1-H4 (H5=H1, H6=H4, H7=H2, H8=H3 - see BEAPER_Nano.py).
# If you choose the door-sensor Option B (contact switch) below, wire
# it to a header that is NOT aliased to whichever servo header you
# use, or the two will conflict. With the default SERVO1 (H5), use
# H2, H3, or H4 for the contact switch, not H1.
#
# Door sensor options (choose one):
#   Option A - Optical proximity sensor (contactless):
#     Two sub-choices, depending on which jumper position you use -
#     these share jumpers with other sensors, so only one is
#     available at a time:
#       - Q4 (ambient light sensor, JP1 set to Enviro.): detects the
#         door by the change in ambient room light as it swings shut.
#         Simple to mount, but the threshold depends on your room's
#         lighting and may need recalibrating if that changes.
#       - Q1, Q2, or Q3 (break-away floor/line sensors, matching
#         jumper set to Robot): detects the door by reflectivity as
#         a surface on the door approaches the sensor, the same way
#         these sensors detect a floor or line on the robot
#         platforms. More consistent regardless of room lighting,
#         but needs the sensor mounted close enough to the door to
#         pick up a clear reflectivity change as it closes.
#     Either way, set SENSOR_MODE = "optical" and calibrate
#     SENSOR_THRESHOLD for your setup - see take_sensor_baseline()
#     and Step 3 in the Development Guide below. Change
#     'beaper.light_level()' to 'beaper.Q1_level()' (or Q2/Q3) in
#     both functions if you use a floor/line sensor instead of Q4.
#
#   Option B - Contact switch on an expansion header:
#     A magnetic contact switch (reed switch) or a simple mechanical
#     switch (lever, roller, or pushbutton-style) both work here -
#     wire it to a spare header (see the pin-sharing note above) and
#     GND. Set SENSOR_MODE = "contact" and SENSOR_CLOSED_VALUE to
#     match your switch type (0 for NC, 1 for NO).
#
#     Mechanical switches are more likely to be available in a
#     school's parts bins than magnetic reed switches, but their
#     contacts can bounce - producing several rapid open/close
#     readings over a few milliseconds as the contact settles, rather
#     than one clean transition. Reed switches usually bounce less,
#     but are not guaranteed to be bounce-free either. If
#     'door_is_closed()' behaves inconsistently right at the moment
#     the door closes, this is the likely cause - Activity 11 EA1's
#     debounce pattern is the tool for this, applied to
#     'door_switch.value()' instead of a pushbutton.
#
# Safe behaviour:
#   UNLOCKED  - Servo open. Hold SW2 for HOLD_TIME to enter
#               code-setting mode. If a code has been set, the door
#               sensor closing locks the safe automatically.
#
#   SETTING   - LED2 on. Any four button presses set the new code -
#               correctness does not apply while setting a code, only
#               while verifying one. Each press beeps for
#               confirmation. After the fourth press the new code is
#               saved and the safe returns to UNLOCKED, still open.
#
#   ENTRY_1-4 - Door is locked. Each press beeps neutrally with no
#               indication of correctness. After the fourth press:
#               correct code -> unlock tone, servo opens, any logged
#               attempts flash on LED5, attempt count resets to 0.
#               wrong code   -> silence, attempt count increments,
#               entry silently restarts at ENTRY_1.
#
# Before you begin - complete your capstone plan using the Capstone
# Preparation Guide: project description, state diagram, state
# details table, constants and variables, and testing plan.
# ================================================================================

# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32.
import BEAPER_Nano as beaper  # Set up BEAPER Nano I/O

import time
from machine import Pin, PWM

# --- State Constants -------------------
STATE_UNLOCKED = const(0)            # Servo open - safe accessible
STATE_SETTING  = const(1)            # Recording a new code (stays unlocked)
STATE_ENTRY_1  = const(2)            # Locked, awaiting the first digit
STATE_ENTRY_2  = const(3)            # Locked, awaiting the second digit
STATE_ENTRY_3  = const(4)            # Locked, awaiting the third digit
STATE_ENTRY_4  = const(5)            # Locked, awaiting the fourth digit

STATE_NAMES = {
  STATE_UNLOCKED: "UNLOCKED",
  STATE_SETTING:  "SETTING",
  STATE_ENTRY_1:  "ENTRY_1",
  STATE_ENTRY_2:  "ENTRY_2",
  STATE_ENTRY_3:  "ENTRY_3",
  STATE_ENTRY_4:  "ENTRY_4",
}

# --- Sensor Configuration --------------
SENSOR_MODE         = "optical"      # "optical" or "contact"
SENSOR_THRESHOLD    = 3000           # Optical: light drop that indicates door closed
SENSOR_CLOSED_VALUE = 0              # Contact: pin value when door is CLOSED (0=NC, 1=NO)

# Only used if SENSOR_MODE == "contact" - construct your own Pin object,
# since H1-H4 are general-purpose headers the board module does not
# pre-configure. Change H2_PIN to whichever header you wired the
# switch to (see the pin-sharing note above).
door_switch = Pin(beaper.H2_PIN, Pin.IN, Pin.PULL_UP)

# --- Servo Configuration ---------------
# Adjust these angles to match your servo mounting and locking mechanism.
# Test with the servo disconnected from the locking bar first - see
# Step 1 in the Development Guide below.
LOCKED_ANGLE   = 0                   # Servo angle (degrees) when locked
UNLOCKED_ANGLE = 90                  # Servo angle (degrees) when unlocked

# The board module's SERVO1-SERVO4 constants are commented out in
# BEAPER_Nano.py, since H5-H8 share pins with H1-H4 and I2C - only
# uncomment the one you are using. This project uses SERVO1 (H5) by
# default; change to SERVO2/H6, SERVO3/H7, or SERVO4/H8 if you need
# H5 free for something else.
SERVO1 = PWM(Pin(beaper.H5_PIN), freq=50, duty_u16=4915)

# --- Code Constants ---------------------
# The starting code, used until a new one is set via STATE_SETTING.
# 2, 3, 4, and 5 represent SW2, SW3, SW4, and SW5 - change these to
# choose your own starting combination. Digits may repeat.
DEFAULT_CODE_1 = const(2)
DEFAULT_CODE_2 = const(3)
DEFAULT_CODE_3 = const(4)
DEFAULT_CODE_4 = const(5)

# --- Timing Constants -------------------
HOLD_TIME      = const(2000)         # SW2 hold duration to enter code-setting mode (ms)
BEEP_SHORT     = const(80)           # Short neutral beep duration for key feedback (ms)
LOOP_DELAY     = const(10)           # Main loop delay (ms)

# --- Tone Constants ---------------------
TONE_KEY       = 880                 # Neutral key-press beep (Hz)
TONE_SETTING   = 1200                # Code-setting mode entry/confirmation tone (Hz)
TONE_UNLOCK    = 1047                # Correct code / unlock tone (Hz) - C6
TONE_WRONG     = 220                 # Wrong code tone (Hz) - brief, then silence

# --- Program Variables ------------------
state           = STATE_UNLOCKED
state_start     = 0

# The currently stored code. Starts at the DEFAULT_CODE values above,
# and is overwritten when a new code is set in STATE_SETTING.
code_1          = DEFAULT_CODE_1
code_2          = DEFAULT_CODE_2
code_3          = DEFAULT_CODE_3
code_4          = DEFAULT_CODE_4
code_set        = False              # True once a code has been set at least once

entered_1       = 0                  # Digits recorded during the current attempt
entered_2       = 0
entered_3       = 0
entered_4       = 0

entry_step      = 0                  # Presses received so far in STATE_SETTING (0-4)
attempt_count   = 0                  # Wrong attempts since the last unlock

# SW2 hold detection (active only in STATE_UNLOCKED) - the same
# three-variable pattern used for tap/hold detection in Activity 11.
sw2_down        = False
sw2_down_time   = 0

sensor_baseline = 0                  # Optical mode: light level with the door open


# --- Program Functions ------------------

def all_leds_off():
  beaper.LED2.value(0)
  beaper.LED5.value(0)

def enter_state(new_state, current_time, reason=""):
  global state, state_start
  state = new_state
  state_start = current_time
  print("-->", STATE_NAMES[new_state], end="")
  if reason:
    print(" (", reason, ")", sep="")
  else:
    print()

def read_button():
  # Return 2, 3, 4, or 5 if that button is currently pressed, or 0 if
  # none of the four code buttons are pressed.
  if beaper.SW2.value() == 0:
    return 2
  elif beaper.SW3.value() == 0:
    return 3
  elif beaper.SW4.value() == 0:
    return 4
  elif beaper.SW5.value() == 0:
    return 5
  else:
    return 0

def wait_for_release():
  # Block until SW2, SW3, SW4, and SW5 are all released. Called
  # immediately after a press is detected - see Activity 12, GE4.
  while (beaper.SW2.value() == 0 or beaper.SW3.value() == 0 or
         beaper.SW4.value() == 0 or beaper.SW5.value() == 0):
    pass

def take_sensor_baseline():
  # Records the optical sensor's reading with the door open, as a
  # reference point for door_is_closed()'s threshold comparison.
  # Change beaper.light_level() to beaper.Q1_level() (or Q2/Q3) here
  # too if you are using a floor/line sensor instead of Q4.
  global sensor_baseline
  sensor_baseline = beaper.light_level()
  print("    sensor baseline:", sensor_baseline)

def door_is_closed():
  # Return True if the door sensor indicates the door is closed.
  if SENSOR_MODE == "optical":
    # TODO: compare beaper.light_level() to sensor_baseline. A drop
    #       in light large enough to exceed SENSOR_THRESHOLD means
    #       the door has closed and is now blocking the sensor.
    #       Return True or False based on this comparison. If you
    #       are using Q1, Q2, or Q3 instead of Q4 (see the header
    #       comment), call that function here instead - the rest of
    #       the comparison works the same way.
    return False
  elif SENSOR_MODE == "contact":
    return door_switch.value() == SENSOR_CLOSED_VALUE
  return False

def flash_attempts(count):
  # Flash LED5 'count' times to show logged wrong attempts, then
  # clear it. Called immediately after a successful unlock.
  # TODO: implement the flash sequence - for example, LED5 on for
  #       200ms, off for 200ms, repeated 'count' times, then off.
  print("    attempts since last unlock:", count)


# --- Main Program ---------------------

all_leds_off()
beaper.nano_led_on()  # Turn on Arduino Nano ESP32's built-in LED as a status indicator
beaper.set_servo(SERVO1, UNLOCKED_ANGLE)   # Start unlocked - see Development Guide Step 1
take_sensor_baseline()

print("Combination Safe")
print("Hold SW2 for", HOLD_TIME, "ms to set a new code")
if not code_set:
  print("No code set yet - safe will not lock until a code is set")
print()

state_start = time.ticks_ms()
enter_state(STATE_UNLOCKED, state_start, "startup")

while True:
  current_time = time.ticks_ms()

  if state == STATE_UNLOCKED:
    # SW2 hold detection - reused from Activity 11's tap/hold pattern
    sw2_current = beaper.SW2.value()
    if sw2_current == 0 and not sw2_down:
      sw2_down = True
      sw2_down_time = current_time
    elif sw2_current == 1:
      sw2_down = False

    if sw2_down and time.ticks_diff(current_time, sw2_down_time) >= HOLD_TIME:
      sw2_down = False
      entry_step = 0
      beaper.tone(TONE_SETTING, 300)
      enter_state(STATE_SETTING, current_time, "SW2 held")
      beaper.LED2.value(1)

    # TODO: if the program is still in STATE_UNLOCKED at this point
    #       (the hold above may have just changed it - check state
    #       again) and code_set is True, call door_is_closed(). If it
    #       returns True, call beaper.set_servo(SERVO1, LOCKED_ANGLE)
    #       and enter_state(STATE_ENTRY_1, current_time, "door closed").

  elif state == STATE_SETTING:
    pressed = read_button()
    if pressed != 0:
      entry_step += 1
      if entry_step == 1:
        entered_1 = pressed
      elif entry_step == 2:
        entered_2 = pressed
      elif entry_step == 3:
        entered_3 = pressed
      elif entry_step == 4:
        entered_4 = pressed
      beaper.tone(TONE_KEY, BEEP_SHORT)
      wait_for_release()

      # TODO: once entry_step reaches 4, copy entered_1-4 into
      #       code_1-4, set code_set = True, sound TONE_SETTING
      #       briefly to confirm the new code, turn LED2 off, and
      #       enter_state(STATE_UNLOCKED, current_time, "code set").

  elif state == STATE_ENTRY_1:
    # This state is fully implemented as a model. ENTRY_2 and
    # ENTRY_3 below follow exactly the same pattern - write those
    # yourself before attempting ENTRY_4, which is different.
    pressed = read_button()
    if pressed != 0:
      entered_1 = pressed
      beaper.tone(TONE_KEY, BEEP_SHORT)
      wait_for_release()
      enter_state(STATE_ENTRY_2, current_time)

  elif state == STATE_ENTRY_2:
    # TODO: follow the same pattern as STATE_ENTRY_1 above - read a
    #       button, record it as entered_2, beep, wait for release,
    #       then enter_state(STATE_ENTRY_3, current_time).
    pass

  elif state == STATE_ENTRY_3:
    # TODO: follow the same pattern again - record entered_3, beep,
    #       wait for release, then enter_state(STATE_ENTRY_4, current_time).
    pass

  elif state == STATE_ENTRY_4:
    # TODO: read a button and record it as entered_4, beep, and wait
    #       for release, following the same pattern as the states
    #       above. Then compare entered_1, entered_2, entered_3, and
    #       entered_4 against code_1, code_2, code_3, and code_4:
    #
    #       If all four match:
    #         - sound TONE_UNLOCK
    #         - call beaper.set_servo(SERVO1, UNLOCKED_ANGLE)
    #         - enter_state(STATE_UNLOCKED, current_time, "unlocked")
    #         - if attempt_count > 0, call flash_attempts(attempt_count)
    #         - reset attempt_count to 0
    #
    #       If any digit does not match:
    #         - increment attempt_count
    #         - sound TONE_WRONG briefly - no LEDs, no other feedback
    #         - enter_state(STATE_ENTRY_1, current_time, "wrong code")
    pass

  time.sleep_ms(LOOP_DELAY)


# ================================================================================
# Development Guide
# ================================================================================
#
# Work through these steps in order. Fully test each step before
# moving to the next - a capstone this size is much easier to debug
# in small pieces than all at once at the end.
#
# --------------------------------------------------------------------------------
# Step 1 - Servo setup and angles
# --------------------------------------------------------------------------------
#
# Before any state logic, verify your servo moves correctly. The
# program already moves the servo to UNLOCKED_ANGLE at startup, using
# the board module's 'set_servo(servo, angle)' function from
# Activity 10 - the same function works here, just passed SERVO1
# instead of SERVO1/SERVO2. Temporarily add these lines right after
# that, and run the program:
#
# Example code:
#
# time.sleep_ms(2000)
# beaper.set_servo(SERVO1, LOCKED_ANGLE)
# time.sleep_ms(2000)
# beaper.set_servo(SERVO1, UNLOCKED_ANGLE)
#
# Adjust LOCKED_ANGLE and UNLOCKED_ANGLE until the servo moves your
# locking bar or bolt to the correct positions. Remove the test lines
# above once you are satisfied, and use 'beaper.set_servo(SERVO1,
# angle)' everywhere the TODOs mention moving the servo.
#
# --------------------------------------------------------------------------------
# Step 2 - Button reading
# --------------------------------------------------------------------------------
#
# Verify that 'read_button()' returns the correct number (2-5) for
# each of SW2-SW5, and 0 when nothing is pressed. Add a temporary
# print statement after the STATE_ENTRY_1 block's 'pressed =
# read_button()' line to confirm this before relying on it elsewhere.
#
# --------------------------------------------------------------------------------
# Step 3 - Door sensor calibration
# --------------------------------------------------------------------------------
#
# Choose your sensor mode and implement 'door_is_closed()'. For
# optical mode, print 'beaper.light_level()' (or Q1/Q2/Q3, whichever
# you chose) while opening and closing the door to find a
# SENSOR_THRESHOLD that reliably distinguishes the two. For contact
# mode, test that 'door_switch.value()' returns the expected reading
# for both open and closed. Verify 'door_is_closed()' returns True
# only when the door is actually closed, in both directions of
# travel.
#
# If you are using a mechanical contact switch, watch closely for
# bounce right at the moment the door closes - print
# 'door_switch.value()' on every loop iteration for a second or two
# around the transition and look for rapid flickering rather than one
# clean change. See the header comment's note on Option B for what
# to do if you find it.
#
# --------------------------------------------------------------------------------
# Step 4 - Code setting
# --------------------------------------------------------------------------------
#
# Implement the code-commit TODO in STATE_SETTING. Test:
# - LED2 lights when SW2 is held for HOLD_TIME, and turns off after
#   the fourth press
# - Each of the four presses produces a short beep
# - A different code can be set by repeating the hold process
# - The safe remains physically unlocked throughout code-setting
#
# --------------------------------------------------------------------------------
# Step 5 - Entry states and locking
# --------------------------------------------------------------------------------
#
# Complete STATE_ENTRY_2 and STATE_ENTRY_3 by following
# STATE_ENTRY_1's pattern. With a code set, close the door (or
# simulate the sensor) and verify the servo moves to LOCKED_ANGLE and
# the state transitions to ENTRY_1. Print the sensor reading and the
# result of 'door_is_closed()' during this test if the threshold
# needs adjusting.
#
# --------------------------------------------------------------------------------
# Step 6 - Code entry and unlock
# --------------------------------------------------------------------------------
#
# Implement the correct and wrong-code branches in STATE_ENTRY_4.
# Test the complete lock/unlock cycle:
# - Set a code from UNLOCKED
# - Close the door (auto-locks)
# - Enter the correct code - servo should open
# - Enter a wrong code - silence, no visible feedback, entry restarts
# - Enter the correct code again after one or more wrong attempts -
#   verify flash_attempts() fires and attempt_count resets to 0
#
# --------------------------------------------------------------------------------
# Step 7 - Attempt display
# --------------------------------------------------------------------------------
#
# Implement 'flash_attempts()'. The flash should be noticeable but
# not alarming - a few slow flashes of LED5, for example. Verify the
# count is accurate and LED5 clears after the display finishes.


# ================================================================================
# Extension Activities
# ================================================================================
#
# --------------------------------------------------------------------------------
# EA 1 - Auto-relock after timeout
# --------------------------------------------------------------------------------
#
# After unlocking, if the door sensor shows the door has been open
# for RELOCK_TIMEOUT milliseconds, sound a warning beep and re-lock
# automatically. This prevents leaving the safe open accidentally.
#
# --------------------------------------------------------------------------------
# EA 2 - Lockout after repeated failures
# --------------------------------------------------------------------------------
#
# After LOCKOUT_ATTEMPTS wrong codes in a row, freeze the keypad for
# LOCKOUT_TIME milliseconds. Flash LED5 continuously during lockout.
# No button presses accepted. This slows brute-force attempts
# significantly. Add a STATE_LOCKOUT and update your state diagram.
#
# --------------------------------------------------------------------------------
# EA 3 - Progress indicator during entry
# --------------------------------------------------------------------------------
#
# LED3 and LED4 are not used anywhere in the base program. Light one
# additional LED per digit entered during ENTRY_1-4, the same
# cumulative bar-graph pattern used in Activity 12's combination
# lock, so someone entering the code can see their progress without
# counting beeps. Should this progress indicator also appear during
# STATE_SETTING? Consider whether showing progress while setting a
# new code makes the safe easier to use, or easier to observe by
# someone who should not see the new code being set.
#
# --------------------------------------------------------------------------------
# EA 4 - Code change confirmation
# --------------------------------------------------------------------------------
#
# Require the existing code to be entered correctly before a new one
# can be set. Add a STATE_VERIFY between the SW2 hold and
# STATE_SETTING - only proceed to SETTING if the current code is
# entered correctly first. This prevents someone from changing the
# code without knowing the original, even while the safe is unlocked.
#
# --------------------------------------------------------------------------------
# EA 5 - Variable code length
# --------------------------------------------------------------------------------
#
# Extend the code to five or six digits, following the same pattern
# used to go from Activity 12's three-digit lock to this capstone's
# four digits: one more STATE_ENTRY_n, one more entered_n variable,
# and one more code_n variable per additional digit. At what code
# length does adding states and variables one at a time start to
# feel unwieldy? This is the same tradeoff Activity 12 EA3 raised -
# a fully flexible length would use a list and a loop with an index
# variable, which you will meet in the intermediate activities.