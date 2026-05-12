"""
================================================================================
Capstone Project: Combination Safe [BEAPER_Nano-Capstone_Combination_Safe.py]
May 11, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPER_Nano.py board module file.

Hardware used:
  SW2-SW5    - Code entry buttons (all four used as code digits)
  LED2       - Code-setting mode indicator (on while setting code)
  LED5       - Attempt counter indicator (flashes on unlock if attempts > 0)
  LS1        - Piezo speaker (key feedback, code set, unlock, wrong code tones)
  Servo on H9 or H10 - Locking mechanism (LOCKED_ANGLE / UNLOCKED_ANGLE)

Door sensor options (choose one):
  Option A - Optical proximity sensor (contactless):
    Set JP1 to Enviro. to use Q4 (ambient light sensor). Mount so the
    sensor detects the door closing (light level changes). Set
    SENSOR_MODE = "optical". Calibrate SENSOR_THRESHOLD for your setup.

  Option B - Hard-wired contact switch on expansion header:
    Wire a normally-closed (NC) or normally-open (NO) magnetic contact
    to H1 (or H2, H3, H4) and GND. Set SENSOR_MODE = "contact" and
    SENSOR_CLOSED_VALUE to match your switch type (0 for NC, 1 for NO).

Compatible with all BEAPER Nano configurations.
--------------------------------------------------------------------------------
Safe behaviour:
  UNLOCKED  - Servo open. Any number of failed unlock attempts are logged
              silently. Hold SW2 for 2 seconds to enter code-setting mode.
              Door closing (sensor) automatically locks if a code is set.

  SETTING   - LED2 on. Enter any four button presses to set the new code.
              Each press beeps for confirmation. After four presses the code
              is saved, LED2 turns off, and the safe returns to UNLOCKED.
              The safe remains physically unlocked throughout.

  LOCKED    - Each button press beeps neutrally. After four presses:
              correct code -> unlock tone, servo opens, attempt flash if any.
              wrong code   -> silence, counter increments, entry resets.
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
from machine import PWM

# --- State Constants ------------------
STATE_UNLOCKED = const(0)  # Servo open - safe accessible
STATE_SETTING  = const(1)  # Memorizing new 4-digit code (stays unlocked)
STATE_LOCKED   = const(2)  # Servo closed - awaiting correct code

STATE_NAMES = {
  STATE_UNLOCKED: "UNLOCKED",
  STATE_SETTING:  "SETTING",
  STATE_LOCKED:   "LOCKED",
}

# --- Sensor Configuration -------------
SENSOR_MODE         = "optical"  # "optical" or "contact"
SENSOR_PIN          = beaper.H1  # Header pin for contact switch (Option B)
SENSOR_THRESHOLD    = 3000       # Optical: light change that indicates door closed
SENSOR_CLOSED_VALUE = 0          # Contact: pin value when door is CLOSED (0=NC, 1=NO)

# --- Servo Configuration --------------
# Adjust these angles to match your servo mounting and locking mechanism.
# Test with the servo disconnected from the locking bar first.
LOCKED_ANGLE   = 0    # Servo angle (degrees) when locked
UNLOCKED_ANGLE = 90   # Servo angle (degrees) when unlocked

# --- Code Constants -------------------
CODE_LENGTH    = const(4)    # Fixed code length (number of button presses)

# --- Timing Constants -----------------
HOLD_TIME      = const(2000) # SW2 hold duration to enter code-setting mode (ms)
BEEP_SHORT     = const(80)   # Short neutral beep duration for key feedback (ms)
LOOP_DELAY     = const(10)   # Main loop delay (ms)

# --- Tone Constants -------------------
TONE_KEY       = 880         # Neutral key-press beep (Hz)
TONE_SETTING   = 1200        # Code-setting mode entry confirmation (Hz)
TONE_UNLOCK    = 1047        # Correct code / unlock tone (Hz) - C6
TONE_WRONG     = 220         # Wrong code tone (Hz) - plays briefly then silence

# --- Hardware Setup -------------------
servo = PWM(beaper.H9, freq=50)   # Change to beaper.H10 if using that header

def servo_angle(degrees):
  # Set servo to the given angle (0-180 degrees).
  # Maps degrees to the standard servo PWM pulse range (1000-2000 us at 50 Hz).
  min_duty = 1000 * 65535 // 20000   # 1 ms pulse = 0 degrees
  max_duty = 2000 * 65535 // 20000   # 2 ms pulse = 180 degrees
  duty = min_duty + (max_duty - min_duty) * degrees // 180
  servo.duty_u16(duty)

# --- Program Variables ----------------
state          = STATE_UNLOCKED
state_start    = 0

code           = [0] * CODE_LENGTH  # Current stored code (button indices 0-3)
code_set       = False              # True once a code has been set at least once
entry          = [0] * CODE_LENGTH  # Current button presses being entered
entry_index    = 0                  # How many presses received in current entry
attempt_count  = 0                  # Wrong attempts since last unlock

# SW2 hold detection (for code-setting entry)
sw2_down       = False
sw2_down_time  = 0
hold_fired     = False

# Last button state for edge detection across all buttons
last_buttons   = [1, 1, 1, 1]      # 1 = not pressed (INPUT_PULLUP logic)

# Sensor baseline for optical mode
sensor_baseline = 0


# --- Program Functions ----------------

def all_leds_off():
  beaper.LED2.value(0)
  beaper.LED5.value(0)

def enter_state(new_state, current_time, reason=""):
  global state, state_start, entry_index, hold_fired
  state       = new_state
  state_start = current_time
  entry_index = 0
  hold_fired  = False
  print("-->", STATE_NAMES[new_state], end="")
  if reason:
    print(" (", reason, ")", sep="")
  else:
    print()

BUTTONS = (beaper.SW2, beaper.SW3, beaper.SW4, beaper.SW5)

def read_any_press():
  # Return index (0-3) of a button that just transitioned to pressed,
  # or -1 if no new press. Updates last_buttons for edge detection.
  global last_buttons
  for i in range(4):
    current = BUTTONS[i].value()
    if current == 0 and last_buttons[i] == 1:
      last_buttons[i] = 0
      return i
    if current == 1:
      last_buttons[i] = 1
  return -1

def door_is_closed():
  # Return True if the door sensor indicates the door is closed.
  if SENSOR_MODE == "optical":
    # TODO: compare current light level to sensor_baseline.
    #       Return True if the difference exceeds SENSOR_THRESHOLD.
    #       A drop in light (door blocking sensor) indicates closed.
    return False  # Replace with threshold comparison
  elif SENSOR_MODE == "contact":
    return beaper.H1.value() == SENSOR_CLOSED_VALUE
  return False

def take_sensor_baseline():
  global sensor_baseline
  sensor_baseline = beaper.light_level()
  print("    sensor baseline:", sensor_baseline)

def flash_attempts(count):
  # Flash LED5 'count' times to indicate logged wrong attempts, then clear.
  # Called immediately after unlocking.
  # TODO: implement the flash sequence.
  # Each flash: LED5 on for 200ms, off for 200ms.
  # After all flashes, a longer pause, then LED5 off.
  print("    attempts since last unlock:", count)

def code_matches(entered):
  # Return True if the entered sequence matches the stored code.
  for i in range(CODE_LENGTH):
    if entered[i] != code[i]:
      return False
  return True


# --- Main Program ---------------------

all_leds_off()
beaper.nano_led_on()
servo_angle(UNLOCKED_ANGLE)         # Start unlocked
take_sensor_baseline()

print("Combination Safe")
print("Hold SW2 for 2 s to set code")
print("No code set - door will not lock until code is set")
print()

state_start = time.ticks_ms()
enter_state(STATE_UNLOCKED, state_start, "startup")

while True:
  current_time = time.ticks_ms()
  elapsed      = time.ticks_diff(current_time, state_start)
  pressed      = read_any_press()

  # ---- SW2 hold detection (active in UNLOCKED only) ----
  # Detect a 2-second hold on SW2 to enter code-setting mode.
  # Uses the three-variable pattern from Activity 11.
  if state == STATE_UNLOCKED:
    sw2_current = beaper.SW2.value()
    if sw2_current == 0 and not sw2_down:
      sw2_down      = True
      sw2_down_time = current_time
      hold_fired    = False
    elif sw2_current == 1:
      sw2_down   = False
      hold_fired = False
    if (sw2_down and not hold_fired and
        time.ticks_diff(current_time, sw2_down_time) >= HOLD_TIME):
      hold_fired = True
      beaper.tone(TONE_SETTING, 300)
      beaper.LED2.value(1)
      enter_state(STATE_SETTING, current_time, "SW2 held - setting code")

  # ---- State: Unlocked ----
  if state == STATE_UNLOCKED:
    # Auto-lock when door closes (only if a code has been set)
    if code_set and door_is_closed():
      servo_angle(LOCKED_ANGLE)
      enter_state(STATE_LOCKED, current_time, "door closed")

  # ---- State: Setting new code ----
  elif state == STATE_SETTING:
    # Accept the next four button presses as the new code.
    # Each press beeps for confirmation. SW2 hold is ignored here.
    if pressed != -1:
      entry[entry_index] = pressed
      entry_index += 1
      beaper.tone(TONE_KEY, BEEP_SHORT)
      print("    code digit", entry_index, "set")

      if entry_index == CODE_LENGTH:
        # All four digits received - commit the new code
        # TODO: copy entry into code and set code_set = True.
        # TODO: sound the code-set confirmation tone (TONE_SETTING).
        # TODO: turn off LED2 and return to STATE_UNLOCKED.
        pass

  # ---- State: Locked ----
  elif state == STATE_LOCKED:
    if pressed != -1:
      # Accept digit - neutral beep, no correctness feedback until complete
      entry[entry_index] = pressed
      entry_index += 1
      beaper.tone(TONE_KEY, BEEP_SHORT)

      if entry_index == CODE_LENGTH:
        entry_index = 0
        if code_matches(entry):
          # TODO: sound TONE_UNLOCK, move servo to UNLOCKED_ANGLE, and
          #       enter STATE_UNLOCKED. Then call flash_attempts() if
          #       attempt_count > 0, and reset attempt_count to 0.
          pass
        else:
          # TODO: increment attempt_count and sound a brief TONE_WRONG.
          #       Do NOT flash any LEDs or give other visible feedback.
          #       The entry resets silently (entry_index already 0).
          pass

  time.sleep_ms(LOOP_DELAY)


"""
Capstone Development Guide

Work through these steps in order. Fully test each step before
proceeding to the next.

Step 1 - Servo setup and angles
  Before any state logic, verify your servo moves correctly.
  Temporarily add these lines after servo_angle(UNLOCKED_ANGLE)
  in the main program and run the program:

    time.sleep_ms(2000)
    servo_angle(LOCKED_ANGLE)
    time.sleep_ms(2000)
    servo_angle(UNLOCKED_ANGLE)

  Adjust LOCKED_ANGLE and UNLOCKED_ANGLE until the servo moves
  your locking bar or bolt to the correct positions. Remove the
  test lines when satisfied. Note: servo wiring requires the servo
  signal wire on the correct pin of H9 or H10.

Step 2 - Button edge detection
  Verify that read_any_press() returns the correct index (0-3) exactly
  once per physical press, not repeatedly while held. Add a temporary
  print statement inside the function to confirm each button maps to
  the expected index before implementing any state logic.

Step 3 - Door sensor calibration
  Choose your sensor mode and implement door_is_closed(). For optical
  mode, print light_level() while opening and closing the door to find
  the threshold. For contact mode, test that the correct pin value is
  returned for open and closed states. Verify door_is_closed() returns
  True only when the door is physically closed.

Step 4 - Code setting
  Implement the code commit logic in STATE_SETTING. Test:
  - LED2 lights on SW2 hold and extinguishes after four presses
  - Each of the four presses produces a short beep
  - A different code can be set by repeating the hold process
  - The safe remains physically unlocked throughout

Step 5 - Locking
  With a code set, close the door (or simulate the sensor) and verify
  the servo moves to LOCKED_ANGLE and the state transitions to LOCKED.
  Print the sensor reading and the result of door_is_closed() during
  this test to confirm the threshold is working correctly.

Step 6 - Code entry and unlock
  Implement the correct and wrong code branches in STATE_LOCKED.
  Test the complete lock/unlock cycle:
  - Set a code from UNLOCKED
  - Close the door (auto-locks)
  - Enter the correct code - servo should open
  - Enter a wrong code - silence, no visible feedback
  - Enter the correct code again after wrong attempts - verify
    flash_attempts() fires and attempt_count resets

Step 7 - Attempt display
  Implement flash_attempts(). The flash should be noticeable but not
  alarming - 3 slow flashes of LED5, for example. Verify the count
  is accurate and clears after display.

Step 8 - Extensions

  a) Auto-relock after timeout: after unlocking, if the door sensor
     shows the door has been open for RELOCK_TIMEOUT milliseconds,
     sound a warning beep and re-lock automatically. This prevents
     leaving the safe open accidentally.

  b) Lockout after repeated failures: after LOCKOUT_ATTEMPTS wrong
     codes in a row, freeze the keypad for LOCKOUT_TIME milliseconds.
     Flash LED5 continuously during lockout. No button presses accepted.
     This slows brute-force attempts significantly.

  c) Variable code length (up to 8 digits): replace CODE_LENGTH with
     a variable current_length. In code-setting mode, accept presses
     until SW2 is held briefly to commit, rather than waiting for a
     fixed count. Adjust entry[] and code[] arrays to size 8.
     How does this change the state logic in STATE_SETTING?

  d) Code change confirmation: require the existing code to be entered
     before the new code can be set. Add a STATE_VERIFY step between
     the SW2 hold and STATE_SETTING. Only enter SETTING if the current
     code is entered correctly first, preventing someone from changing
     the code without knowing the original.

"""
