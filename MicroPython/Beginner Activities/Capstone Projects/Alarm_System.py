# ================================================================================
# Capstone Project: Alarm System [Alarm_System.py]
# Version: 1.0
# Updated: July 25, 2026
#
# Platform: mirobo.tech BEAPER Nano circuit (any configuration)
# Requires: BEAPER_Nano.py board module file
#
# A five-state intrusion alarm. Arm and disarm with the same
# four-button code, entered the same way as the Activity 12 capstone
# combination lock and safe: any button may be pressed at each step,
# and correctness is only checked once all four digits are in, so a
# wrong attempt reveals nothing about which digit was incorrect.
#
# Hardware used:
#   SW2-SW5    - Arm/disarm code entry buttons (all four used as code digits)
#   LED2-LED5  - Alarm system state indicators
#   LS1        - Piezo speaker (entry beeps, countdown, alarm tone)
#
# Sensor options (choose one, or combine - see EA3):
#   Option A - Optical proximity sensor (contactless):
#     Two sub-choices, depending on which jumper position you use -
#     these share jumpers with other sensors, so only one is
#     available at a time:
#       - Q4 (ambient light sensor, JP1 set to Enviro.): an object or
#         hand passing in front of the sensor changes the light
#         reading. Mount the circuit inside the protected space so
#         the sensor faces the opening.
#       - Q1, Q2, or Q3 (break-away floor/line sensors, matching
#         jumper set to Robot): detects a trip by reflectivity, the
#         same way these sensors detect a floor or line on the robot
#         platforms. More consistent regardless of room lighting.
#     Either way, set SENSOR_MODE = "optical" and calibrate
#     SENSOR_THRESHOLD for your setup - see take_sensor_baseline()
#     and Step 1 in the Development Guide below. Change
#     'beaper.light_level()' to 'beaper.Q1_level()' (or Q2/Q3) in
#     both functions if you use a floor/line sensor instead of Q4.
#
#   Option B - Contact switch on an expansion header:
#     A magnetic contact switch (reed switch) or a simple mechanical
#     switch (lever, roller, or pushbutton-style) both work here -
#     wire a normally-closed (NC) switch to a spare header and GND.
#     Set SENSOR_MODE = "contact". A mechanical switch is more likely
#     to be available in a school's parts bin than a reed switch, but
#     its contacts can bounce - see Activity 11 EA1's debounce
#     pattern if 'check_sensors()' behaves inconsistently right at
#     the moment of a trip.
#
# --------------------------------------------------------------------------------
# Alarm system behaviour:
#   DISARMED  - Safe. Enter the arm code to begin arming. If alarms
#               occurred since the last disarm, the count is displayed.
#   ARMING    - Exit delay: sensors ignored while you leave. LEDs
#               count down. Do NOT enter the code during this phase.
#   ARMED     - Sensors active. Circuit goes dark. Do not touch buttons.
#   TRIPPED   - Entry delay: sensor tripped, enter the disarm code now
#               or the alarm will sound. LEDs flash urgently.
#   ALARM     - Alarm sounding. Enter the code to disarm. The alarm
#               records itself. Stops after ALARM_DURATION, then re-arms.
#
# Before you begin - complete your capstone plan using the Capstone
# Preparation Guide: project description, state diagram, state
# details table, constants and variables, and testing plan.
# ================================================================================

# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32.
import BEAPER_Nano as beaper  # Set up BEAPER Nano I/O

import time
from machine import Pin

# --- State Constants -------------------
STATE_DISARMED = const(0)            # Safe - waiting for arm code
STATE_ARMING   = const(1)            # Exit delay - sensors ignored
STATE_ARMED    = const(2)            # Sensors active - circuit dark
STATE_TRIPPED  = const(3)            # Entry delay - enter code or alarm sounds
STATE_ALARM    = const(4)            # Alarm sounding - enter code to disarm

STATE_NAMES = {
  STATE_DISARMED: "DISARMED",
  STATE_ARMING:   "ARMING",
  STATE_ARMED:    "ARMED",
  STATE_TRIPPED:  "TRIPPED",
  STATE_ALARM:    "ALARM",
}

# --- Code Entry Result Constants -------
CODE_INCOMPLETE = const(0)           # Still entering - no result yet
CODE_CORRECT    = const(1)           # Correct code entered
CODE_WRONG      = const(2)           # Wrong code entered - entry reset

# --- The Arm/Disarm Code ---------------
# 2, 3, 4, and 5 represent SW2, SW3, SW4, and SW5. Change these to
# choose your own code. Default: SW2, SW4, SW3, SW5.
CORRECT_1 = const(2)
CORRECT_2 = const(4)
CORRECT_3 = const(3)
CORRECT_4 = const(5)

# --- Sensor Configuration --------------
SENSOR_MODE      = "optical"         # "optical" or "contact"
SENSOR_THRESHOLD = 3000              # Optical: light change that indicates a trip

# Only used if SENSOR_MODE == "contact" - construct your own Pin
# object, since H1-H4 are general-purpose headers the board module
# does not pre-configure. Change H1_PIN to whichever header you
# wired the switch to.
sensor_switch = Pin(beaper.H1_PIN, Pin.IN, Pin.PULL_UP)

# --- Timing Constants -------------------
EXIT_DELAY     = const(15000)        # Time to leave before arming (ms)
ENTRY_DELAY    = const(10000)        # Time to enter code before alarm sounds (ms)
ALARM_DURATION = const(60000)        # Alarm sounds for this long before re-arming (ms)
BEEP_INTERVAL  = const(1000)         # Entry-delay countdown beep interval (ms)
FLASH_INTERVAL = const(250)          # Urgent flash interval in TRIPPED/ALARM (ms)
BEEP_SHORT     = const(80)           # Short neutral beep for key feedback (ms)
LOOP_DELAY     = const(10)           # Main loop delay (ms)

# --- Tone Constants ---------------------
TONE_KEY   = 880                     # Neutral key-press beep (Hz)
TONE_ALARM = 2000                    # Alarm tone frequency (Hz)

# --- Program Variables ------------------
state           = STATE_DISARMED
state_start     = 0

alarm_count     = 0                  # Number of alarms since last disarm
showing_count   = False              # True while displaying alarm count on entry to DISARMED
last_beep_time  = 0                  # Last entry-delay or countdown beep
last_flash_time = 0                  # Last urgent flash toggle
flash_on        = False              # Current urgent flash state

sensor_baseline = 0                  # Sensor reading at the moment of arming

# Code entry, reused across DISARMED (arming) and TRIPPED/ALARM (disarming)
entry_step      = 0                  # Presses received so far in the current attempt (0-4)
entered_1       = 0                  # Digits recorded during the current attempt
entered_2       = 0
entered_3       = 0
entered_4       = 0


# --- Program Functions ------------------

def all_leds_off():
  beaper.LED2.value(0)
  beaper.LED3.value(0)
  beaper.LED4.value(0)
  beaper.LED5.value(0)

def enter_state(new_state, current_time, reason=""):
  global state, state_start, flash_on, entry_step
  all_leds_off()
  beaper.noTone()
  state       = new_state
  state_start = current_time
  flash_on    = False
  entry_step  = 0                    # Always start code entry fresh on a state change
  print("-->", STATE_NAMES[new_state], end="")
  if reason:
    print(" (", reason, ")", sep="")
  else:
    print()

def read_button():
  # Return 2, 3, 4, or 5 if that button is currently pressed, or 0 if
  # none of the four code buttons are pressed. Reused from Activity
  # 12's capstone combination lock.
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
  # immediately after a press is detected.
  while (beaper.SW2.value() == 0 or beaper.SW3.value() == 0 or
         beaper.SW4.value() == 0 or beaper.SW5.value() == 0):
    pass

def check_code_entry():
  # Check for a button press and record it as part of the current
  # four-button code entry. Returns CODE_CORRECT once all four
  # digits have been entered and match the stored code, CODE_WRONG
  # once all four have been entered and do not match, or
  # CODE_INCOMPLETE while entry is still in progress.
  #
  # Like the Activity 12 capstone combination lock, correctness is
  # only checked once all four presses have been recorded - not
  # press by press - so a wrong attempt reveals nothing about which
  # digit was incorrect. This same function is used for both arming
  # (called from DISARMED) and disarming (called from TRIPPED or
  # ALARM), since the same code serves both purposes.
  global entry_step, entered_1, entered_2, entered_3, entered_4
  pressed = read_button()
  if pressed == 0:
    return CODE_INCOMPLETE

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

  if entry_step < 4:
    return CODE_INCOMPLETE

  entry_step = 0
  if (entered_1 == CORRECT_1 and entered_2 == CORRECT_2 and
      entered_3 == CORRECT_3 and entered_4 == CORRECT_4):
    return CODE_CORRECT
  else:
    print("    wrong code - entry reset")
    return CODE_WRONG

def check_sensors():
  # Return True if the sensor detects a trip (door opened, proximity
  # detected). Adjust this function to match your sensor configuration.
  if SENSOR_MODE == "optical":
    # TODO: compare beaper.light_level() to sensor_baseline. Both a
    #       drop in light (an object blocking the sensor) and a rise
    #       (a reflective object approaching the sensor) can indicate
    #       a trip, so compare the absolute difference:
    #       abs(current - sensor_baseline) > SENSOR_THRESHOLD.
    #       Return True or False based on this comparison. If you
    #       are using Q1, Q2, or Q3 instead of Q4 (see the header
    #       comment), call that function here instead.
    return False
  elif SENSOR_MODE == "contact":
    # A normally-closed (NC) switch reads LOW when closed (door
    # shut) and HIGH when open (door opened), with the pin
    # configured INPUT_PULLUP.
    return sensor_switch.value() == 1
  return False

def take_sensor_baseline():
  # Read the current sensor level and store it as the armed
  # baseline. Called at the moment of arming so the baseline
  # reflects the closed/undisturbed state of the protected space.
  global sensor_baseline
  sensor_baseline = beaper.light_level()
  print("    sensor baseline:", sensor_baseline)

def display_alarm_count(count):
  # Show the number of alarms that occurred since last disarm.
  # Called on entry to DISARMED if count > 0.
  # TODO: implement a clear visual display of your choice - for
  #       example, flash LED2-LED5 together 'count' times with a
  #       pause between flashes, similar to Combination Safe's
  #       flash_attempts().
  print("*** ALARM COUNT:", count, "alarm(s) since last disarm ***")


# --- Main Program ---------------------

all_leds_off()
beaper.nano_led_on()  # Turn on Arduino Nano ESP32's built-in LED as a status indicator

print("Alarm System")
print("Code: SW", CORRECT_1, "SW", CORRECT_2, "SW", CORRECT_3, "SW", CORRECT_4)
print()

state_start     = time.ticks_ms()
last_flash_time = state_start
last_beep_time  = state_start

enter_state(STATE_DISARMED, state_start, "startup")
beaper.LED2.value(1)                 # LED2 on = disarmed indicator

while True:
  current_time = time.ticks_ms()
  elapsed      = time.ticks_diff(current_time, state_start)

  if state == STATE_DISARMED:
    # Display the alarm count once on entry, if any alarms occurred
    if alarm_count > 0 and not showing_count:
      showing_count = True
      display_alarm_count(alarm_count)

    result = check_code_entry()
    if result == CODE_CORRECT:
      # TODO: enter_state(STATE_ARMING, current_time, "armed"), call
      #       take_sensor_baseline() just before leaving this state
      #       so the baseline reflects the current (safe) reading,
      #       and reset alarm_count and showing_count to 0/False.
      pass

  elif state == STATE_ARMING:
    # Sensors are ignored during the exit delay - the user is leaving.
    # TODO: implement a countdown display using 'elapsed' and
    #       EXIT_DELAY. A simple approach: divide EXIT_DELAY into
    #       four equal segments. In the first quarter all four LEDs
    #       are on; by the last quarter only LED2 is on.
    # TODO: once elapsed >= EXIT_DELAY, confirm arming with a short
    #       beep, turn off all LEDs (circuit goes dark while armed),
    #       and enter_state(STATE_ARMED, current_time).
    pass

  elif state == STATE_ARMED:
    # Circuit is dark. Check sensors every loop iteration. Buttons
    # are not read here - a press while armed has no effect (code
    # entry only happens in DISARMED, TRIPPED, and ALARM).
    if check_sensors():
      enter_state(STATE_TRIPPED, current_time, "sensor tripped")

  elif state == STATE_TRIPPED:
    # TODO: flash LED2-LED5 together at FLASH_INTERVAL using
    #       last_flash_time, the same repeating-timer pattern from
    #       Activity 12's alarm state.
    # TODO: beep briefly every BEEP_INTERVAL using last_beep_time,
    #       as a second independent timer running alongside the flash.

    result = check_code_entry()
    if result == CODE_CORRECT:
      # TODO: disarm silently - no alarm recorded, since the user
      #       responded before the entry delay expired.
      #       enter_state(STATE_DISARMED, current_time, "disarmed")
      #       and turn LED2 on for the disarmed indicator.
      pass

    # TODO: if elapsed >= ENTRY_DELAY without a correct code,
    #       increment alarm_count and
    #       enter_state(STATE_ALARM, current_time, "entry delay expired").
    pass

  elif state == STATE_ALARM:
    # TODO: flash LED2-LED5 at FLASH_INTERVAL using last_flash_time.
    # TODO: sound a continuous alarm tone on LS1. Consider
    #       alternating between two frequencies using a second
    #       independent timer for an attention-getting pattern - the
    #       same two-timers-in-one-state technique used for the
    #       flash and beep in Activity 12's alarm state, applied
    #       here to two different tones instead of a flash and a beep.

    result = check_code_entry()
    if result == CODE_CORRECT:
      # TODO: enter_state(STATE_DISARMED, current_time, "disarmed")
      #       and turn LED2 on. Do not increment alarm_count again -
      #       it was already recorded when the alarm was triggered.
      pass

    # TODO: if elapsed >= ALARM_DURATION without a correct code,
    #       enter_state(STATE_ARMED, current_time, "alarm timeout")
    #       to re-arm - the intruder has not disarmed the system.
    pass

  time.sleep_ms(LOOP_DELAY)


# ================================================================================
# Development Guide
# ================================================================================
#
# Work through these steps in order. Test each step thoroughly
# before continuing - a working partial system is always better
# than a broken complete one.
#
# --------------------------------------------------------------------------------
# Step 1 - Sensor configuration and baseline
# --------------------------------------------------------------------------------
#
# Choose your sensor mode and implement 'check_sensors()'.
#
# For optical mode: mount the sensor facing the door or opening. Run
# the program, open the door slowly, and print the sensor reading
# every loop iteration to find the typical range of values when
# undisturbed vs. disturbed. Set SENSOR_THRESHOLD to a value
# comfortably between the two.
#
# For contact mode: wire your NC switch to H1 (or another header -
# update sensor_switch if so) and GND. Verify that 'check_sensors()'
# returns True when the door is open and False when closed. If using
# a mechanical switch, watch for bounce right at the moment of the
# transition - see the header comment's note on Option B.
#
# --------------------------------------------------------------------------------
# Step 2 - Disarmed state and code entry
# --------------------------------------------------------------------------------
#
# Implement the arm transition from STATE_DISARMED. Code entry
# itself is already handled by 'check_code_entry()' - you only need
# to act on the CODE_CORRECT result. Test carefully:
# - Correct sequence transitions to ARMING
# - Wrong sequence resets silently (stays in DISARMED, no feedback
#   beyond the neutral key beeps already heard during entry)
# - A partial sequence followed by the correct remaining digits works
#
# --------------------------------------------------------------------------------
# Step 3 - Arming (exit delay)
# --------------------------------------------------------------------------------
#
# Implement the countdown in STATE_ARMING. Test that sensors are
# genuinely ignored during the exit delay by triggering them while
# the countdown runs. Verify the circuit goes dark when ARMED.
#
# --------------------------------------------------------------------------------
# Step 4 - Armed and tripped
# --------------------------------------------------------------------------------
#
# Implement the entry delay in STATE_TRIPPED. Test the full
# arm -> trip -> disarm sequence:
# - Arm the system
# - Trigger the sensor
# - Enter the code within ENTRY_DELAY
# - Verify STATE_DISARMED is reached with no alarm recorded
#
# --------------------------------------------------------------------------------
# Step 5 - Alarm and re-arm
# --------------------------------------------------------------------------------
#
# Implement STATE_ALARM. Test the full arm -> trip -> timeout ->
# alarm -> re-arm sequence. Verify alarm_count increments correctly
# and is displayed on the next successful disarm.
#
# --------------------------------------------------------------------------------
# Step 6 - Alarm count display
# --------------------------------------------------------------------------------
#
# Implement 'display_alarm_count()' with a visible LED display, not
# just the console message already provided. Verify the count is
# accurate and clears after being shown.


# ================================================================================
# Extension Activities
# ================================================================================
#
# --------------------------------------------------------------------------------
# EA 1 - Acknowledge and clear the alarm count
# --------------------------------------------------------------------------------
#
# After the alarm count is displayed on entry to DISARMED, require a
# button press to acknowledge it before accepting a new arm code.
# What happens currently if the user starts entering a new code
# while the count is still displaying?
#
# --------------------------------------------------------------------------------
# EA 2 - Tamper protection
# --------------------------------------------------------------------------------
#
# If SENSOR_MODE is "contact" and the sensor trips while in
# STATE_ARMED, add a check that the sensor is still tripped a short
# time later before transitioning to STATE_TRIPPED - a very brief
# trip could indicate a tamper attempt rather than genuine entry.
# Log tamper attempts separately from alarm_count.
#
# --------------------------------------------------------------------------------
# EA 3 - Multiple sensors
# --------------------------------------------------------------------------------
#
# Extend 'check_sensors()' to read both an optical sensor and a
# contact switch, returning True if either is triggered. Print which
# sensor tripped to the console for debugging.
#
# --------------------------------------------------------------------------------
# EA 4 - Changeable code
# --------------------------------------------------------------------------------
#
# Add a mode (triggered by a special button sequence from DISARMED)
# that lets the user change the arm/disarm code. CORRECT_1-4 are
# currently declared with 'const()', which MicroPython treats as
# fixed at compile time - not reassignable while the program runs.
# The first step is removing 'const()' from each, the same way
# Combination Safe separates DEFAULT_CODE_1-4 (fixed starting point)
# from code_1-4 (the current, changeable code). Once they are plain
# variables, how will the new code persist if the board loses power?
# A fully persistent version would write the new code to a file,
# which is covered in the intermediate activities.
#
# --------------------------------------------------------------------------------
# EA 5 - Panic button
# --------------------------------------------------------------------------------
#
# SW5 held for 3 seconds in any state immediately transitions to
# STATE_ALARM and increments alarm_count, simulating a manual
# panic/duress feature found in real alarm systems. You will need
# the 'button_is_down' / 'button_down_time' hold-detection pattern
# from Activity 11, checked independently of 'check_code_entry()'
# since SW5 is also one of the four code digits. What changes does
# this require to avoid a held SW5 being misread as a code digit at
# the same time?