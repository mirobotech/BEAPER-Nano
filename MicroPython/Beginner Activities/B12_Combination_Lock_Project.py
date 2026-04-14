"""
================================================================================
Project: Combination Lock [B12_Combination_Lock_Project.py]
April 14, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPER_Nano.py board module file.

Before starting, re-read GE1, GE2, and GE3 from
Activity 12: State Machines.

This skeleton implements a three-button combination lock as a
state machine. The correct combination is SW2, SW3, SW4 pressed
in sequence. Any wrong button press triggers the alarm state.
SW5 resets from any state.

State diagram:
  LOCKED --> (SW2 correct) --> STEP_1
  STEP_1 --> (SW3 correct) --> STEP_2
  STEP_2 --> (SW4 correct) --> UNLOCKED
  Any state --> (wrong button) --> ALARM
  Any state --> (SW5)        --> LOCKED

Outputs per state:
  LOCKED:   LED2 on (locked indicator)
  STEP_1:   LED2 + LED3 on (one correct press)
  STEP_2:   LED2 + LED3 + LED4 on (two correct presses)
  UNLOCKED: LED5 on, short beep (access granted)
  ALARM:    LED2-LED5 flashing rapidly, repeated beeps (alarm)
================================================================================
"""
# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32
import BEAPER_Nano as beaper

import time

# --- State Constants ------------------
STATE_LOCKED   = const(0)            # Awaiting first correct button
STATE_STEP_1   = const(1)            # First button correct, awaiting second
STATE_STEP_2   = const(2)            # Second button correct, awaiting third
STATE_UNLOCKED = const(3)            # Correct sequence completed
STATE_ALARM    = const(4)            # Wrong button pressed

# --- Program Constants ----------------
LOOP_DELAY      = const(10)          # Main loop delay (ms)
FLASH_INTERVAL  = const(150)         # Alarm flash toggle interval (ms)
ALARM_BEEP_ON   = const(100)         # Alarm beep on duration (ms)
ALARM_BEEP_OFF  = const(200)         # Alarm beep off duration (ms)
RESET_HOLD_TIME = const(1000)        # Time to hold SW5 to reset from UNLOCKED

# --- Program Variables ----------------
state           = STATE_LOCKED
state_start     = 0
last_flash_time = 0
flash_on        = False

# Debounce variables - prevent a single press registering multiple times
last_sw2_state  = 1                  # 1 = not pressed (active-LOW convention)
last_sw3_state  = 1
last_sw4_state  = 1
last_sw5_state  = 1


# --- Program Functions ----------------

def all_leds_off():
  beaper.LED2.value(0)
  beaper.LED3.value(0)
  beaper.LED4.value(0)
  beaper.LED5.value(0)

def enter_state(new_state, current_time, reason=""):
  # Transition to a new state: clear outputs, update state variable,
  # record transition time, and print a diagnostic message.
  global state, state_start, flash_on
  all_leds_off()
  beaper.LS1.duty_u16(0)             # Silence speaker
  state = new_state
  state_start = current_time
  flash_on = False

  state_names = {
    STATE_LOCKED:   "LOCKED",
    STATE_STEP_1:   "STEP_1",
    STATE_STEP_2:   "STEP_2",
    STATE_UNLOCKED: "UNLOCKED",
    STATE_ALARM:    "ALARM",
  }
  print("-->", state_names[new_state], end="")
  if reason:
    print(" (", reason, ")", sep="")
  else:
    print()

def button_just_pressed(current_val, last_val):
  # Return True if the button has just transitioned from not-pressed to pressed.
  # Uses the active-LOW convention: pressed = 0, not pressed = 1.
  return current_val == 0 and last_val == 1


# --- Main Program ---------------------

beaper.nano_led_on()
all_leds_off()
state_start = time.ticks_ms()
last_flash_time = time.ticks_ms()

print("Combination Lock")
print("Enter combination: SW2, SW3, SW4")
print("SW5: reset")
print()

# Set initial state outputs
enter_state(STATE_LOCKED, state_start, "startup")
beaper.LED2.value(1)

while True:
  current_time = time.ticks_ms()

  # Read all buttons
  sw2 = beaper.SW2.value()
  sw3 = beaper.SW3.value()
  sw4 = beaper.SW4.value()
  sw5 = beaper.SW5.value()

  # Detect fresh button presses (transition from not-pressed to pressed)
  sw2_pressed = button_just_pressed(sw2, last_sw2_state)
  sw3_pressed = button_just_pressed(sw3, last_sw3_state)
  sw4_pressed = button_just_pressed(sw4, last_sw4_state)
  sw5_pressed = button_just_pressed(sw5, last_sw5_state)

  # SW5 resets to LOCKED from any state except UNLOCKED
  # (UNLOCKED requires a hold - see EA1)
  if sw5_pressed and state != STATE_UNLOCKED:
    enter_state(STATE_LOCKED, current_time, "SW5 reset")
    beaper.LED2.value(1)

  # --- State machine ---

  elif state == STATE_LOCKED:
    # TODO: if SW2 pressed, transition to STEP_1 and update LEDs
    # TODO: if SW3 or SW4 pressed, transition to ALARM
    pass

  elif state == STATE_STEP_1:
    # TODO: if SW3 pressed, transition to STEP_2 and update LEDs
    # TODO: if SW2 or SW4 pressed, transition to ALARM
    pass

  elif state == STATE_STEP_2:
    # TODO: if SW4 pressed, transition to UNLOCKED and update LEDs
    # TODO: if SW2 or SW3 pressed, transition to ALARM
    pass

  elif state == STATE_UNLOCKED:
    # Lock is open - LED5 on (set on entry, maintained here)
    # SW5 held for RESET_HOLD_TIME re-locks
    # TODO: check if SW5 is held for RESET_HOLD_TIME using the
    #       button_is_down / button_down_time pattern from Activity 11,
    #       then transition to LOCKED
    pass

  elif state == STATE_ALARM:
    # Flash all LEDs and sound repeated beeps while in alarm state
    # TODO: flash LED2-LED5 together at FLASH_INTERVAL using last_flash_time
    # TODO: produce a repeating beep pattern using the speaker:
    #       on for ALARM_BEEP_ON ms, off for ALARM_BEEP_OFF ms
    #       Hint: use elapsed time within the flash cycle to determine
    #       beep on/off, so beep timing stays aligned with the flash
    pass

  # Update last button states for next iteration
  last_sw2_state = sw2
  last_sw3_state = sw3
  last_sw4_state = sw4
  last_sw5_state = sw5

  time.sleep_ms(LOOP_DELAY)


"""
Extension Activities

1.  The UNLOCKED state currently does nothing useful after the
    lock opens - LED5 stays on indefinitely. Implement a re-lock
    mechanism: SW5 must be held for RESET_HOLD_TIME milliseconds
    to re-lock. Use the 'button_is_down' and 'button_down_time'
    pattern from Activity 11.

    Why require a hold rather than a tap to re-lock? Think about
    what would happen in a real access-control system if the door
    accidentally re-locked while someone was passing through.

2.  Add a lockout after three failed attempts. Declare an
    'attempt_count' variable that increments each time the lock
    transitions to ALARM from any step state. After three failed
    attempts, enter a LOCKOUT state that ignores all input for
    LOCKOUT_TIME milliseconds before returning to LOCKED.

    Add LOCKOUT to your state diagram and identify the new
    transitions. How does this change the security of the lock
    compared to the version with no lockout?

3.  Make the combination configurable. Store the correct sequence
    as a tuple:

  COMBINATION = (beaper.SW2, beaper.SW3, beaper.SW4)

    Rewrite the state machine to work with any length combination
    stored in this tuple, using a 'step' index variable instead of
    separate STEP_1 and STEP_2 states. How does the number of
    states in the new design compare to the original? What are
    the tradeoffs of the two approaches?

4.  Consider how this combination lock could form the arm/disarm
    mechanism for a security alarm capstone project. What would
    the full system's state diagram look like, including:
    - Disarmed state (lock is open, sensors ignored)
    - Arming state (countdown delay while you leave)
    - Armed state (sensors active)
    - Triggered state (alarm sounding)
    - Each combination lock state for disarming

    Draw the complete state diagram. How many states does the
    full system have? How does the lock's state machine nest
    inside the alarm system's state machine?

"""