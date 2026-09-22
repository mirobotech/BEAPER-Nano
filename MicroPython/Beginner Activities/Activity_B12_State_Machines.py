# ================================================================================
# Beginner Activity 12: State Machines [Activity_B12_State_Machines.py]
# Version: 1.2
# Updated: September 22, 2026
#
# Platform: mirobo.tech BEAPER Nano circuit (any configuration)
# Requires: BEAPER_Nano.py board module file
#
# This program uses a state machine to implement a three-button
# combination lock, styled after a digital hotel safe lock. SW2, SW3,
# and SW4 can be pressed at each step to enter the code. Each press
# beeps and lights the next progress LED. After all three presses
# have been entered, the program checks whether they matched the
# correct combination (SW2, SW3, SW4, in that order). SW5 restarts
# code entry from any state except UNLOCKED.
#
# State diagram:
#   ENTRY_1 --(any button)--> ENTRY_2
#   ENTRY_2 --(any button)--> ENTRY_3
#   ENTRY_3 --(any button, correct sequence)--> UNLOCKED
#   ENTRY_3 --(any button, wrong sequence)   --> ALARM
#   ALARM --(3 alarm beeps complete)--> ENTRY_1
#   Any state except UNLOCKED --(SW5)--> ENTRY_1
#
# Outputs per state:
#   ENTRY_1:  LED2 on (ready, no digits entered)
#   ENTRY_2:  LED2 + LED3 on (one digit entered)
#   ENTRY_3:  LED2 + LED3 + LED4 on (two digits entered)
#   UNLOCKED: LED5 on, beep (access granted)
#   ALARM:    LED2-LED5 flashing, 3 beeps, then returns to ENTRY_1
# ================================================================================

# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32.
import BEAPER_Nano as beaper  # Set up BEAPER Nano I/O

import time

# --- State Constants ------------------
# States are given named integer constants to match the state diagram.
STATE_ENTRY_1  = const(0)            # Waiting for the first button press
STATE_ENTRY_2  = const(1)            # One press entered, waiting for the second
STATE_ENTRY_3  = const(2)            # Two presses entered, waiting for the third
STATE_UNLOCKED = const(3)            # Correct sequence entered
STATE_ALARM    = const(4)            # Wrong sequence entered

# --- The Correct Combination ----------
# Each correct button is stored in its own named constant, in order.
CORRECT_1 = const(2)                 # First press should be SW2
CORRECT_2 = const(3)                 # Second press should be SW3
CORRECT_3 = const(4)                 # Third press should be SW4

# --- Program Constants ----------------
LOOP_DELAY       = const(10)         # Main loop delay (ms)
ENTRY_BEEP_FREQ  = const(1500)       # Beep frequency for each digit entered (Hz)
ENTRY_BEEP_MS    = const(80)         # Beep duration for each digit entered (ms)
UNLOCK_FREQ      = const(2000)       # Access-granted beep frequency (Hz)
UNLOCK_BEEP_MS   = const(300)        # Access-granted beep duration (ms)
ALARM_FREQ       = const(2500)       # Alarm beep frequency (Hz)
ALARM_BEEP_ON    = const(150)        # Alarm beep on duration (ms)
ALARM_BEEP_OFF   = const(150)        # Alarm beep off duration (ms)
ALARM_BEEP_COUNT = const(3)          # Number of beeps before returning to entry
FLASH_INTERVAL   = const(150)        # Alarm LED flash toggle interval (ms)

# --- Program Variables ----------------
state            = STATE_ENTRY_1
state_start      = 0
entered_1        = 0                 # Button pressed first this attempt (0-4)
entered_2        = 0                 # Button pressed second this attempt
entered_3        = 0                 # Button pressed third this attempt
last_flash_time  = 0                 # Alarm: last time LEDs toggled
flash_on         = False             # Alarm: current LED flash state
last_beep_time   = 0                 # Alarm: last time the beep toggled
beep_on          = False             # Alarm: current beep on/off state
alarm_beep_count = 0                 # Alarm: number of beeps completed so far


# --- Program Functions ----------------

def all_leds_off():
  beaper.LED2.value(0)
  beaper.LED3.value(0)
  beaper.LED4.value(0)
  beaper.LED5.value(0)

def read_button():
  # Return 2, 3, or 4 if that button is currently pressed, or 0 if
  # none of the three combination buttons are pressed.
  if beaper.SW2.value() == 0:
    return 2
  elif beaper.SW3.value() == 0:
    return 3
  elif beaper.SW4.value() == 0:
    return 4
  else:
    return 0

def wait_for_release():
  # Block until SW2, SW3, and SW4 are all released. Called after
  # a button press is detected.
  while beaper.SW2.value() == 0 or beaper.SW3.value() == 0 or beaper.SW4.value() == 0:
    pass

def enter_state(new_state, current_time, reason=""):
  # Transition to a new state: clear outputs, update state variable,
  # record transition time, and print a diagnostic message.
  global state, state_start, flash_on, beep_on, alarm_beep_count
  all_leds_off()
  beaper.noTone()                    # Silence speaker
  state = new_state
  state_start = current_time
  flash_on = False
  beep_on = False
  alarm_beep_count = 0

  state_names = {
    STATE_ENTRY_1:  "ENTRY_1",
    STATE_ENTRY_2:  "ENTRY_2",
    STATE_ENTRY_3:  "ENTRY_3",
    STATE_UNLOCKED: "UNLOCKED",
    STATE_ALARM:    "ALARM",
  }
  print("-->", state_names[new_state], end="")
  if reason:
    print(" (", reason, ")", sep="")
  else:
    print()


# --- Main Program ---------------------

beaper.nano_led_on()  # Status LED on
all_leds_off()
state_start = time.ticks_ms()
last_flash_time = time.ticks_ms()

print("Combination Lock")
print("Enter combination: SW2, SW3, SW4")
print("SW5: restart entry")
print()

# Set initial state outputs
enter_state(STATE_ENTRY_1, state_start, "startup")
beaper.LED2.value(1)

while True:
  current_time = time.ticks_ms()

  # SW5 restarts entry from any state except UNLOCKED
  if beaper.SW5.value() == 0 and state != STATE_UNLOCKED:
    while beaper.SW5.value() == 0:    # Wait for release
      pass
    enter_state(STATE_ENTRY_1, current_time, "SW5 reset")
    beaper.LED2.value(1)

  # --- State machine ---

  elif state == STATE_ENTRY_1:
    pressed = read_button()
    if pressed != 0:
      entered_1 = pressed
      beaper.tone(ENTRY_BEEP_FREQ, ENTRY_BEEP_MS)
      wait_for_release()
      enter_state(STATE_ENTRY_2, current_time)
      beaper.LED2.value(1)
      beaper.LED3.value(1)

  elif state == STATE_ENTRY_2:
    pressed = read_button()
    if pressed != 0:
      entered_2 = pressed
      beaper.tone(ENTRY_BEEP_FREQ, ENTRY_BEEP_MS)
      wait_for_release()
      enter_state(STATE_ENTRY_3, current_time)
      beaper.LED2.value(1)
      beaper.LED3.value(1)
      beaper.LED4.value(1)

  elif state == STATE_ENTRY_3:
    pressed = read_button()
    if pressed != 0:
      entered_3 = pressed
      beaper.tone(ENTRY_BEEP_FREQ, ENTRY_BEEP_MS)
      wait_for_release()
      if entered_1 == CORRECT_1 and entered_2 == CORRECT_2 and entered_3 == CORRECT_3:
        enter_state(STATE_UNLOCKED, current_time, "correct combination")
        beaper.LED5.value(1)
        beaper.tone(UNLOCK_FREQ, UNLOCK_BEEP_MS)
      else:
        enter_state(STATE_ALARM, current_time, "wrong combination")

  elif state == STATE_UNLOCKED:
    # Lock is open - LED5 stays on (set on entry). No exit transition
    # yet - see Extension Activity 1 to add a hold-to-relock feature.
    pass

  elif state == STATE_ALARM:
    # Flash all LEDs together at FLASH_INTERVAL - a repeating timer
    if time.ticks_diff(current_time, last_flash_time) >= FLASH_INTERVAL:
      flash_on = not flash_on
      if flash_on:
        beaper.LED2.value(1)
        beaper.LED3.value(1)
        beaper.LED4.value(1)
        beaper.LED5.value(1)
      else:
        all_leds_off()
      last_flash_time = current_time

    # Repeating beep, running independently of the flash timer above.
    # After ALARM_BEEP_COUNT beeps, return to entry automatically.
    if beep_on:
      if time.ticks_diff(current_time, last_beep_time) >= ALARM_BEEP_ON:
        beaper.noTone()
        beep_on = False
        last_beep_time = current_time
        alarm_beep_count += 1
        if alarm_beep_count >= ALARM_BEEP_COUNT:
          enter_state(STATE_ENTRY_1, current_time, "alarm complete")
          beaper.LED2.value(1)
    else:
      if time.ticks_diff(current_time, last_beep_time) >= ALARM_BEEP_OFF:
        beaper.tone(ALARM_FREQ)
        beep_on = True
        last_beep_time = current_time

  time.sleep_ms(LOOP_DELAY)


# ================================================================================
# Guided Exploration
# ================================================================================
#
# Activities 9 through 11 focused on a single technical problem at a
# time: analog input, output, and non-blocking timing. Each activity's
# program grew more capable, but the overall structure stayed the
# same - a loop that checks conditions and updates outputs directly.
# This works well when a program's behaviour depends only on its
# current inputs, but breaks down when a program needs to behave
# differently depending on what has happened before. For example,
# the same button could mean something different depending what part
# of the program is currently running.
#
# This activity introduces state machines: a way of organising a
# program around a set of named states, with explicit rules for when
# to move between them, and what to do while each state is active.
# You have actually built a similar combination lock program twice
# before - as a step-counter in Activity 6, and refactored with
# functions in Activity 8. This activity solves the same problem a
# third time as a proper state machine, allowing you to compare all
# three approaches directly.
#
# --------------------------------------------------------------------------------
# GE 1 - The state diagram
# --------------------------------------------------------------------------------
#
# A state machine can be described visually using a state diagram:
# circles represent states and arrows represent transitions between
# them. Each arrow is labelled with the event that triggers it.
#
# Draw the state diagram for this program. Your diagram should
# have five circles (ENTRY_1, ENTRY_2, ENTRY_3, UNLOCKED, ALARM)
# and an arrow for every transition described in the header
# comment.
#
# Compare your diagram to the state machine section of the main
# loop. Can you find a direct correspondence between each arrow in
# your diagram and a specific 'elif' branch in the code?
#
# --------------------------------------------------------------------------------
# GE 2 - Named state constants
# --------------------------------------------------------------------------------
#
# States are defined using named integer constants:
#
# Example code:
#
# STATE_ENTRY_1  = const(0)
# STATE_ENTRY_2  = const(1)
# STATE_ENTRY_3  = const(2)
# STATE_UNLOCKED = const(3)
# STATE_ALARM    = const(4)
#
# The program could instead use raw numbers (0, 1, 2, 3, 4) directly
# in the 'if' statements. What would be lost? Consider what happens
# if you need to insert a new state between ENTRY_2 and ENTRY_3 and
# must renumber the existing states.
#
# Named constants also make the serial output meaningful. The
# 'enter_state()' function uses a dictionary to look up the state
# name for printing. What would the output look like if raw numbers
# were used instead of names?
#
# --------------------------------------------------------------------------------
# GE 3 - enter_state() and centralized transitions
# --------------------------------------------------------------------------------
#
# Every state transition goes through 'enter_state()' rather than
# setting 'state' directly. This function clears every output
# before setting the new state, resetting 'flash_on', 'beep_on',
# and 'alarm_beep_count' at the same time. Each caller then turns
# on only what the new state needs.
#
# Compare this to an alternative design where every state's
# outputs are checked and set fresh on every single loop
# iteration, regardless of whether the state just changed. What
# would be different about the program's behaviour, readability,
# and efficiency?
#
# Why does 'enter_state()' reset 'alarm_beep_count' to 0 even
# though it is only used inside STATE_ALARM? What would happen on
# the second time the lock enters ALARM if this reset were
# missing?
#
# --------------------------------------------------------------------------------
# GE 4 - Reading buttons: read_button() and wait_for_release()
# --------------------------------------------------------------------------------
#
# Reading the buttons uses two small functions:
#
# Example code:
#
# def read_button():
#   if beaper.SW2.value() == 0:
#     return 2
#   elif beaper.SW3.value() == 0:
#     return 3
#   elif beaper.SW4.value() == 0:
#     return 4
#   else:
#     return 0
#
# def wait_for_release():
#   while beaper.SW2.value() == 0 or beaper.SW3.value() == 0 or beaper.SW4.value() == 0:
#     pass
#
# 'read_button()' uses the same 'beaper.SWx.value() == 0' check
# you have used since Activity 3 - nothing new there. The only new
# idea is 'wait_for_release()': once a press is detected and
# recorded, the program deliberately pauses until the button is
# physically released, before continuing.
#
# Why is this necessary? Consider what would happen without
# 'wait_for_release()' if a press were held down for 300ms: at
# LOOP_DELAY = 10ms, how many loop iterations would that span, and
# what would 'entered_1' end up containing after all of them?
#
# This pattern - detect a press, then wait for release before
# continuing - is a simplified version of 'read_keypad()' from
# Activity 8, which did the same thing across all four buttons.
# Compare the two: what does 'read_keypad()' do that
# 'read_button()' plus 'wait_for_release()' does not?
#
# Note that 'wait_for_release()' blocks the program - it is not
# the non-blocking style from Activity 11. Why is blocking
# acceptable here but not in STATE_ALARM below? Think about what
# else the program needs to keep doing while each state is active.
#
# --------------------------------------------------------------------------------
# GE 5 - Tracing the happy path
# --------------------------------------------------------------------------------
#
# Trace through the "happy path" - the sequence of transitions
# when the combination is entered correctly:
#
# Example code:
#
# Start in ENTRY_1
# Press SW2 --> ENTRY_2 (entered_1 = 2)
# Press SW3 --> ENTRY_3 (entered_2 = 3)
# Press SW4 --> UNLOCKED (entered_3 = 4, all three correct)
#
# For each transition, identify: which 'elif' branch handles it,
# which LEDs turn on, and what gets printed to the console. Run
# the program and verify your trace against the actual serial
# output.
#
# Now trace an incorrect attempt: SW3, SW2, SW4. Which state does
# each press lead to? Is anything different about how ENTRY_2 and
# ENTRY_3 behave for this attempt compared to the correct one, or
# do they behave identically until the final check?
#
# --------------------------------------------------------------------------------
# GE 6 - Why check the whole combination at once
# --------------------------------------------------------------------------------
#
# Notice that pressing a wrong button during ENTRY_1 or ENTRY_2
# does not trigger the alarm immediately - it is simply recorded
# and the program moves on to the next entry state, exactly as if
# it were correct. The combination is only checked once, after
# all three presses have been entered, in STATE_ENTRY_3.
#
# Why might this be a better design than checking each button as
# it is pressed and triggering the alarm on the first wrong one?
# Think about someone trying to guess the combination by trial and
# error: what could they learn from a lock that reveals which
# specific digit was wrong, that they could not learn from a lock
# that only reveals whether the whole sequence was right or wrong?
#
# --------------------------------------------------------------------------------
# GE 7 - Independent timers inside the alarm state
# --------------------------------------------------------------------------------
#
# The ALARM state contains two independent repeating timers
# running simultaneously - the same multi-rate timing pattern
# from Activity 11, but now happening inside a single state
# rather than across the whole program:
#
# - 'last_flash_time' controls when the LEDs toggle, at
#   FLASH_INTERVAL.
# - 'last_beep_time' controls when the beep toggles, using two
#   different intervals depending on 'beep_on': ALARM_BEEP_ON
#   while beeping, ALARM_BEEP_OFF while silent.
#
# Trace through several iterations of the loop while in
# STATE_ALARM and verify that the flash and beep timers advance
# independently - one does not wait for or reset the other.
#
# 'alarm_beep_count' increments each time a beep finishes (when
# 'beep_on' changes from True to False). Once it reaches
# ALARM_BEEP_COUNT, the program calls 'enter_state(STATE_ENTRY_1,
# ...)' - from inside the alarm-handling code itself, not from a
# button press. What does this tell you about what can trigger a
# state transition? Must it always be a button press?
#
# --------------------------------------------------------------------------------
# GE 8 - Comparing three versions of the same lock
# --------------------------------------------------------------------------------
#
# You have now seen three variations of the same combination lock:
# a step-counter with 'if attempts == 1: ... elif attempts == 2:'
# logic in Activity 6, a version refactored to use functions in
# Activity 8, and now this state machine version - which also
# behaves differently, checking the whole combination at once
# rather than rejecting on the first wrong button.
#
# Compare all three versions (open your earlier files if you
# still have them). What does naming the states explicitly add
# that the attempts-counter versions did not have? Is there
# anything the earlier versions did more simply? A state machine
# is a tool, not always the best tool - when would a simple
# counter be preferable to a full state machine?
#
#
# ================================================================================
# Extension Activities
# ================================================================================
#
# --------------------------------------------------------------------------------
# EA 1 - Hold-to-relock from UNLOCKED
# --------------------------------------------------------------------------------
#
# The UNLOCKED state currently does nothing useful after the
# lock opens - LED5 stays on indefinitely. Implement a re-lock
# mechanism: SW5 must be held for RESET_HOLD_TIME milliseconds
# to re-lock. Use the 'button_is_down' and 'button_down_time'
# pattern from Activity 11.
#
# Why require a hold rather than a tap to re-lock? Think about
# what would happen in a real access-control system if the door
# accidentally re-locked while someone was passing through.
#
# --------------------------------------------------------------------------------
# EA 2 - Lockout after failed attempts
# --------------------------------------------------------------------------------
#
# Add a lockout after three failed attempts. Declare an
# 'attempt_count' variable that increments each time the lock
# transitions to ALARM (which only happens from STATE_ENTRY_3).
# After three failed attempts, enter a LOCKOUT state that ignores
# all input for LOCKOUT_TIME milliseconds before returning to
# ENTRY_1.
#
# Add LOCKOUT to your state diagram and identify the new
# transitions. How does this change the security of the lock
# compared to the version with no lockout?
#
# --------------------------------------------------------------------------------
# EA 3 - A four-button combination
# --------------------------------------------------------------------------------
#
# Extend the lock to a four-button combination. Add a
# 'CORRECT_4' constant, an 'entered_4' variable, and a new
# 'STATE_ENTRY_4' state following the same pattern as
# ENTRY_1 through ENTRY_3. Update the state diagram and the
# final check in what is now STATE_ENTRY_4 to compare all four
# entered values.
#
# What did you have to change in how many places to add one more
# digit? A fully flexible version - supporting any combination
# length without adding a new state and a new variable for each
# digit - would store the combination as a list and use a loop
# with an index variable instead. Lists and indexing are covered
# in the intermediate activities; for now, four independent
# variables is a reasonable way to extend this design by one step.
#
# --------------------------------------------------------------------------------
# EA 4 - Designing a security alarm capstone
# --------------------------------------------------------------------------------
#
# Consider how this combination lock could form the arm/disarm
# mechanism for a security alarm capstone project. What would
# the full system's state diagram look like, including:
# - Disarmed state (lock is open, sensors ignored)
# - Arming state (countdown delay while you leave)
# - Armed state (sensors active)
# - Triggered state (alarm sounding)
# - Each combination lock state for disarming
#
# Draw the complete state diagram. How many states does the
# full system have? How does the lock's state machine nest
# inside the alarm system's state machine?
#
# --------------------------------------------------------------------------------
# EA 5 - Traffic Light Controller
# --------------------------------------------------------------------------------
#
# Apply what you have learned to a different kind of state
# machine - one driven mostly by elapsed time rather than button
# presses, with events (a simulated car and pedestrian) setting
# flags that are checked later rather than triggering an immediate
# transition. Open: B12_Traffic_Light_Controller_Project.py
#
# This project is a skeleton, not a finished program - re-read
# GE1 through GE7 before starting, since the traffic light reuses
# the same enter_state() and named-constant patterns as the
# combination lock above.