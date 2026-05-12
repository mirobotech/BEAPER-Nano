"""
================================================================================
Capstone Project: Alarm System [BEAPER_Nano-Capstone_Alarm_System.py]
May 11, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPER_Nano.py board module file.

Hardware used:
  SW2-SW5    - Arm/disarm code entry buttons
  LED2-LED5  - Alarm system state indicators
  LS1        - Piezo speaker (entry countdown beeps, alarm tone)

Sensor options (choose one or combine):
  Option A - Optical proximity sensor (contactless, no wiring needed):
    Set JP1 to Enviro. to use Q4 (ambient light sensor) as a proximity
    sensor. An object or hand passing in front of the sensor changes
    the light reading. Mount the circuit inside the locker or room so
    the sensor faces the opening. Set SENSOR_MODE = "optical".

  Option B - Hard-wired contact switch on expansion header:
    Wire a normally-closed (NC) magnetic door/drawer contact switch
    between H1 (or H2, H3, H4) and GND. When the door opens the
    circuit breaks, pulling H1 HIGH. Set SENSOR_MODE = "contact" and
    set SENSOR_PIN to match your header choice.

  You can combine both: check_sensors() can read both and return True
  if either is triggered. See check_sensors() below.

Compatible with all BEAPER Nano configurations.
Optical sensor: set JP1 to Enviro. (selects ambient light sensor Q4).
Contact sensor: no jumper changes required, wire to H1-H4.

--------------------------------------------------------------------------------
Alarm system behaviour:
  DISARMED  - Safe. Enter the arm code to begin arming.
              If alarms occurred since last disarm, count is displayed.
  ARMING    - Exit delay: sensors ignored while you leave. LEDs count
              down. Do NOT enter the code during this phase.
  ARMED     - Sensors active. Circuit goes dark. Do not touch buttons.
  TRIPPED   - Entry delay: sensors tripped, enter disarm code now or
              alarm will sound. LEDs flash urgently.
  ALARM     - Alarm sounding. Enter code to disarm. Alarm records
              itself. Stops after ALARM_DURATION, then re-arms.
--------------------------------------------------------------------------------
Before you begin - complete your capstone plan:
  1. Write a plain-English description from the user's perspective.
  2. List all states and draw your state diagram with transitions.
  3. Complete the state details table (outputs, transitions, next states).
  4. List all constants and variables you will need.
  5. Write your testing plan before writing any code.
================================================================================
"""
# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32
import BEAPER_Nano as beaper

import time

# --- State Constants ------------------
STATE_DISARMED = const(0)  # Safe - waiting for arm code
STATE_ARMING   = const(1)  # Exit delay - sensors ignored
STATE_ARMED    = const(2)  # Sensors active - circuit dark
STATE_TRIPPED  = const(3)  # Entry delay - enter code or alarm sounds
STATE_ALARM    = const(4)  # Alarm sounding - enter code to disarm

STATE_NAMES = {
  STATE_DISARMED: "DISARMED",
  STATE_ARMING:   "ARMING",
  STATE_ARMED:    "ARMED",
  STATE_TRIPPED:  "TRIPPED",
  STATE_ALARM:    "ALARM",
}

# --- Code Entry Result Constants ------
CODE_INCOMPLETE = const(0)   # Still entering - no result yet
CODE_CORRECT    = const(1)   # Correct code entered
CODE_WRONG      = const(2)   # Wrong button pressed - entry reset

# --- Sensor Configuration -------------
SENSOR_MODE     = "optical"  # "optical" or "contact" - see header above
SENSOR_PIN      = beaper.H1  # Header pin for contact switch (Option B only)

# --- Timing Constants -----------------
EXIT_DELAY      = const(15000)  # Time to leave before arming (ms)
ENTRY_DELAY     = const(10000)  # Time to enter code before alarm sounds (ms)
ALARM_DURATION  = const(60000)  # Alarm sounds for this long before re-arming (ms)
BEEP_INTERVAL   = const(1000)   # Entry countdown beep interval (ms)
FLASH_INTERVAL  = const(250)    # Urgent flash interval in TRIPPED/ALARM (ms)
ARM_FLASH_TIME  = const(100)    # Brief armed-confirmation flash duration (ms)

# --- Code Constants -------------------
# The arm/disarm code as a tuple of button indices (0=SW2, 1=SW3, 2=SW4, 3=SW5).
# Change this to set your code. Default: SW2, SW4, SW3, SW5.
ARM_CODE        = (0, 2, 1, 3)

# --- Loop Constant --------------------
LOOP_DELAY      = const(10)     # Main loop delay (ms)

# --- Hardware Maps --------------------
BUTTONS = (beaper.SW2,  beaper.SW3,  beaper.SW4,  beaper.SW5)
LEDS    = (beaper.LED2, beaper.LED3, beaper.LED4, beaper.LED5)

# --- Program Variables ----------------
state            = STATE_DISARMED
state_start      = 0

alarm_count      = 0      # Number of alarms since last disarm
showing_count    = False  # True while displaying alarm count on entry to DISARMED
last_beep_time   = 0      # Last entry-delay beep or countdown flash
last_flash_time  = 0      # Last urgent flash toggle
flash_on         = False  # Current urgent flash state

# Sensor baseline (set during ARMING for optical mode)
sensor_baseline  = 0      # Light level reading at time of arming

# Code entry state
code_step        = 0      # Index into ARM_CODE - how many correct presses so far
last_button      = -1     # Last button state (for edge detection, -1 = none)


# --- Program Functions ----------------

def all_leds_off():
  for led in LEDS:
    led.value(0)

def enter_state(new_state, current_time, reason=""):
  global state, state_start, flash_on, code_step, last_button
  all_leds_off()
  beaper.noTone()
  state       = new_state
  state_start = current_time
  flash_on    = False
  code_step   = 0         # Reset code entry on every state change
  last_button = -1
  print("-->", STATE_NAMES[new_state], end="")
  if reason:
    print(" (", reason, ")", sep="")
  else:
    print()

def read_button_press():
  # Return the index (0-3) of a button that has JUST been pressed
  # (transition from not-pressed to pressed), or -1 if no new press.
  # Uses last_button for edge detection.
  global last_button
  for i, btn in enumerate(BUTTONS):
    if btn.value() == 0:
      if last_button != i:
        last_button = i
        return i
      return -1          # Already held - not a new press
  last_button = -1
  return -1

def check_code_entry(current_time):
  # Check for a button press and match it against the next step in ARM_CODE.
  # Returns CODE_CORRECT, CODE_WRONG, or CODE_INCOMPLETE.
  # Resets code_step internally on a wrong press.
  global code_step
  pressed = read_button_press()
  if pressed == -1:
    return CODE_INCOMPLETE
  if pressed == ARM_CODE[code_step]:
    code_step += 1
    beaper.tone(800 + code_step * 100, 80)  # Rising confirmation tone
    if code_step == len(ARM_CODE):
      code_step = 0
      return CODE_CORRECT
    return CODE_INCOMPLETE
  else:
    code_step = 0
    beaper.tone(200, 150)                   # Low rejection tone
    print("    wrong button - code reset")
    return CODE_WRONG

def check_sensors():
  # Return True if any sensor detects a trip (door opened, proximity detected).
  # Adjust this function to match your sensor configuration.
  if SENSOR_MODE == "optical":
    # Optical proximity: trip if light level changes significantly from baseline.
    # A drop in light (object blocking sensor) OR rise (reflective object near
    # sensor) can both indicate a trip - use absolute difference.
    current_light = beaper.light_level()
    # TODO: define SENSOR_THRESHOLD and compare to sensor_baseline.
    #       Return True if abs(current_light - sensor_baseline) > SENSOR_THRESHOLD.
    #       Start with SENSOR_THRESHOLD = 3000 and adjust for your environment.
    return False  # Replace with threshold comparison

  elif SENSOR_MODE == "contact":
    # Contact switch (NC): trip if header pin reads HIGH (circuit broken).
    # A normally-closed switch reads LOW when closed (door shut) and
    # HIGH when open (door opened).
    return beaper.H1.value() == 1  # Adjust pin if using H2, H3, or H4

  return False  # Fallback - no sensor configured

def take_sensor_baseline():
  # Read the current light level and store it as the armed baseline.
  # Called at the moment of arming so the baseline reflects the
  # closed/undisturbed state of the protected space.
  global sensor_baseline
  sensor_baseline = beaper.light_level()
  print("    sensor baseline:", sensor_baseline)

def display_alarm_count(count):
  # Show the number of alarms that occurred since last disarm.
  # Called on entry to DISARMED if count > 0.
  # TODO: implement a clear visual display of your choice.
  # Ideas: flash LED2-LED5 together 'count' times with a pause between
  #        flashes, or print to the serial console, or both.
  print("*** ALARM COUNT:", count, "alarm(s) since last disarm ***")


# --- Main Program ---------------------

all_leds_off()
beaper.nano_led_on()
print("Alarm System")
print("Code: SW", [s + 2 for s in ARM_CODE])
print()

state_start     = time.ticks_ms()
last_flash_time = time.ticks_ms()
last_beep_time  = time.ticks_ms()

# Enter initial state - show disarmed indicator
enter_state(STATE_DISARMED, state_start, "startup")
LEDS[0].value(1)                # LED2 on = disarmed indicator

while True:
  current_time = time.ticks_ms()
  elapsed      = time.ticks_diff(current_time, state_start)

  # ---- State: Disarmed ----
  if state == STATE_DISARMED:
    # Display alarm count on entry if alarms occurred
    if alarm_count > 0 and not showing_count:
      showing_count = True
      display_alarm_count(alarm_count)

    # Check for arm code entry
    result = check_code_entry(current_time)
    if result == CODE_CORRECT:
      # TODO: transition to STATE_ARMING and set the sensor baseline.
      #       Call take_sensor_baseline() just before leaving this state
      #       so the baseline reflects the current (safe) light level.
      #       Reset alarm_count and showing_count here.
      pass

  # ---- State: Arming (exit delay) ----
  elif state == STATE_ARMING:
    # Sensors are ignored during exit delay - the user is leaving.
    # Provide a visual and/or audio countdown so the user knows how
    # long they have.
    # TODO: implement a countdown display using elapsed and EXIT_DELAY.
    #       A simple approach: LEDs step off one by one as time passes.
    #       Divide EXIT_DELAY into four equal segments. In the first
    #       quarter all four LEDs are on; by the last quarter only LED2
    #       is on; when EXIT_DELAY elapses, transition to STATE_ARMED.
    # TODO: when EXIT_DELAY elapses, confirm arming with a short beep
    #       pattern and transition to STATE_ARMED. Turn off all LEDs
    #       (circuit goes dark while armed).
    pass

  # ---- State: Armed ----
  elif state == STATE_ARMED:
    # Circuit is dark. Check sensors every loop iteration.
    # Do not read buttons here - any button press while armed should
    # not affect the system (it will be handled in TRIPPED).
    if check_sensors():
      enter_state(STATE_TRIPPED, current_time, "sensor tripped")
      # TODO: start urgent LED flashing and beeping to warn the user
      #       they must enter the code before ENTRY_DELAY elapses.

  # ---- State: Tripped (entry delay) ----
  elif state == STATE_TRIPPED:
    # Flash all LEDs urgently and beep every BEEP_INTERVAL to tell the
    # user to enter their code.
    # TODO: flash LED2-LED5 together at FLASH_INTERVAL using last_flash_time.
    # TODO: beep briefly every BEEP_INTERVAL using last_beep_time.

    # Check for disarm code entry
    result = check_code_entry(current_time)
    if result == CODE_CORRECT:
      # TODO: disarm silently (no alarm recorded). Transition to
      #       STATE_DISARMED and restore the disarmed LED indicator.
      pass

    # TODO: if ENTRY_DELAY elapses without correct code, increment
    #       alarm_count and transition to STATE_ALARM.
    pass

  # ---- State: Alarm ----
  elif state == STATE_ALARM:
    # Alarm is sounding. Flash all LEDs and sound the piezo continuously.
    # TODO: flash LED2-LED5 at FLASH_INTERVAL using last_flash_time.
    # TODO: sound a continuous alarm tone on LS1. Consider alternating
    #       between two frequencies for an attention-getting pattern.

    # Check for disarm code entry (disarms even while alarm is sounding)
    result = check_code_entry(current_time)
    if result == CODE_CORRECT:
      # TODO: transition to STATE_DISARMED. Alarm count was already
      #       recorded when alarm was triggered, so do not increment it
      #       again here.
      pass

    # TODO: if ALARM_DURATION elapses without code entry, transition
    #       back to STATE_ARMED (re-arm - the intruder has not disarmed).
    pass

  time.sleep_ms(LOOP_DELAY)


"""
Capstone Development Guide

Work through these steps in order. Test each step thoroughly before
continuing - a working partial system is always better than a broken
complete one.

Step 1 - Sensor configuration and baseline
  Choose your sensor mode ("optical" or "contact") and configure
  check_sensors() to return True when the sensor is triggered.

  For optical mode: set JP1 to Enviro. Mount the circuit with Q4
  facing the door or opening. Run the program, open the door slowly,
  and print the light level every loop iteration to find the typical
  range of values when undisturbed vs disturbed. Set SENSOR_THRESHOLD
  to a value comfortably between the two ranges.

  For contact mode: wire your NC switch between H1 and GND. Verify
  that check_sensors() returns True when the door is open and False
  when closed before implementing any state logic.

Step 2 - Disarmed state and code entry
  Implement the arm code transition from STATE_DISARMED. The code
  entry is handled by check_code_entry() - you only need to act on
  the CODE_CORRECT result. Test the code entry carefully:
  - Correct sequence transitions to ARMING
  - Wrong button resets silently (stays in DISARMED)
  - Partial sequence followed by correct completion works

Step 3 - Arming (exit delay)
  Implement the countdown in STATE_ARMING. Test that sensors are
  genuinely ignored during the exit delay by triggering them while
  the countdown runs. Verify the circuit goes dark when ARMED.

Step 4 - Armed and tripped
  Implement sensor checking in STATE_ARMED and the entry delay in
  STATE_TRIPPED. Test the full arm → trip → disarm sequence:
  - Arm the system
  - Trigger the sensor
  - Enter the code within ENTRY_DELAY
  - Verify STATE_DISARMED is reached with no alarm recorded

Step 5 - Alarm and re-arm
  Implement STATE_ALARM. Test the full arm → trip → timeout → alarm
  → re-arm sequence. Verify alarm_count increments correctly and
  is displayed on the next successful disarm.

Step 6 - Refinements and extensions

  a) Display improvements: implement display_alarm_count() to show
     the count visually (LED flashes) as well as via serial output.
     Add a button press in DISARMED to acknowledge and clear the
     count after it has been displayed.

  b) Tamper protection: if SENSOR_MODE is "contact" and the sensor
     trips while in STATE_ARMED, add a check that the sensor is still
     tripped when transitioning to STATE_TRIPPED (a very brief trip
     could indicate a tamper attempt rather than entry). Log it.

  c) Multiple sensors: extend check_sensors() to read both an optical
     sensor and a contact switch. Return True if either is triggered.
     Print which sensor tripped to the serial console for debugging.

  d) Code change: add a mode (triggered by a special button sequence
     from DISARMED) that allows the user to change the arm/disarm code.
     How will you store the new code so it persists between sessions?
     Consider using a list instead of a tuple for ARM_CODE if you want
     it to be mutable.

  e) Panic button: SW5 held for 3 seconds in any state immediately
     transitions to STATE_ALARM and increments alarm_count. This
     simulates a manual panic/duress feature found in real alarm systems.
     What changes to the state machine does this require?

"""
