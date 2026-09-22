# ================================================================================
# Capstone Project: Stepper Motor Controller [Stepper_Controller.py]
# Version: 1.1
# Updated: July 25, 2026
#
# Platform: mirobo.tech BEAPER Nano circuit (Robot configuration)
# Requires: BEAPER_Nano.py board module file
#
# A position-tracking stepper motor controller. Unlike a servo (which
# is commanded directly to an angle) or a DC motor (which only knows
# speed and direction), a stepper motor moves in small, precise,
# individually-countable steps - the motor itself has no idea where
# it is, but a program that counts every step it commands always
# knows the motor's exact position. This is the core idea this
# capstone explores.
#
# The example application rotates continuously, completing one full
# revolution every ROTATION_PERIOD_MS - like a clock hand, but not
# synced to real-world time (this curriculum has no real-time clock
# or network time source available). Set ROTATION_PERIOD_MS to 60000
# for something that behaves like a seconds hand, or to a much longer
# period for a slow display turntable - the same mechanism works for
# either application, or for one that visits a fixed set of preset
# positions instead of rotating continuously (see EA2).
#
# Hardware used:
#   SW2          - Start rotating
#   SW5          - Emergency stop (halts stepping, holds tracked position)
#   On-board LED - On while running
#
#   A two-coil (bipolar) stepper motor, driven through the SN754410NE
#   half-bridge driver already on the BEAPER Nano circuit - the same
#   chip that normally drives the two DC drive motors. Coil A
#   connects where the left motor normally would (M1A/M1B), and coil
#   B where the right motor normally would (M2A/M2B).
#
# IMPORTANT: this uses all four of the driver's half-bridges for the
# stepper's two coils, the same way two DC motors normally would.
# This project is a different robot configuration from Line Follower,
# Sumo Robot, or Wall Follower - it cannot run alongside two
# independent drive motors, since there are no half-bridges left over
# once the stepper is connected. Unlike an external unipolar stepper
# driver (such as a ULN2003 board), this approach needs no extra
# wiring beyond what the circuit already provides for DC motors, and
# leaves H1-H4 completely free for sensors or other input/output
# devices - a genuine advantage if your application needs them.
#
# --------------------------------------------------------------------------------
# How the step sequence works:
#
# A bipolar stepper has two coils, each needing current that can
# flow in EITHER direction - not just on or off. This is exactly what
# a full H-bridge motor driver already provides: left_motor_forward()
# and left_motor_reverse() drive coil A's current one way then the
# other, and right_motor_forward()/right_motor_reverse() do the same
# for coil B. A full rotation step advances through four
# combinations of these two coils' polarities:
#
#   Phase 0: coil A forward, coil B forward
#   Phase 1: coil A reverse, coil B forward
#   Phase 2: coil A reverse, coil B reverse
#   Phase 3: coil A forward, coil B reverse
#
# Each phase differs from the one before it by reversing exactly one
# coil's polarity - this is what produces smooth, single-step
# rotation rather than skipping steps. See Development Guide Step 1
# to verify this phase order (and which physical direction it
# produces) matches your specific motor's wiring.
#
# --------------------------------------------------------------------------------
# Stepper controller behaviour:
#   IDLE    - Motors stopped (no current, free to turn by hand).
#             Press SW2 to begin.
#   RUNNING - Continuously computing where the motor should be, based
#             on elapsed time, and stepping forward to catch up.
#   STOPPED - Stepping halted, motors stopped. Position tracking is
#             preserved, but note that a de-energised stepper can be
#             turned by hand or by an external force - if that
#             happens while stopped, the tracked position will no
#             longer match the real one. Press SW2 to resume; the
#             motor will step forward to catch up to where it should
#             be by now, exactly as a real clock hand would if it had
#             been temporarily held still while time kept passing.
#
# Before you begin - complete your capstone plan using the Capstone
# Preparation Guide: a plain-English description of your application
# (clock hand, turntable, or something else), how many steps your
# motor takes per revolution, your testing plan, and which of your
# stepper's four wires connect to which motor terminal.
# ================================================================================

# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32.
import BEAPER_Nano as beaper  # Set up BEAPER Nano I/O

import time

# --- State Constants -------------------
STATE_IDLE    = const(0)             # Motors off - waiting for start
STATE_RUNNING = const(1)             # Continuously stepping toward the target position
STATE_STOPPED = const(2)             # Halted - motors off, position tracking preserved

STATE_NAMES = {
  STATE_IDLE:    "IDLE",
  STATE_RUNNING: "RUNNING",
  STATE_STOPPED: "STOPPED",
}

# --- Motor Configuration ----------------
STEPS_PER_REVOLUTION = 200            # Steps for one full output-shaft revolution.
                                       # 200 is typical for a 1.8-degree-per-step
                                       # bipolar stepper (360 / 1.8 = 200), a common
                                       # size for small hobby bipolar motors - confirm
                                       # this for your motor, see Development Guide Step 2.

ROTATION_PERIOD_MS = 60000            # Time for one full revolution (ms).
                                       # 60000 = 1 revolution per minute (seconds-hand-like).

MIN_STEP_DELAY = const(5)             # Minimum time between steps (ms) - steppers can
                                       # skip or stall if stepped faster than they can
                                       # physically respond.

# --- Step Sequence -----------------------
# Four phases, each a combination of the two coils' polarities - see
# the header comment above for how this maps to the DC motor driver
# functions already used elsewhere in this curriculum. Verify and
# correct the phase order for your specific wiring in Development
# Guide Step 1.
SEQUENCE_LENGTH = 4                   # Number of phases in the sequence

# --- Timing Constants ---------------------
LOOP_DELAY = const(1)                 # Main loop delay (ms)

# --- Program Variables -------------------
state           = STATE_IDLE
state_start     = 0                   # Time the current state began (for diagnostics)

cycle_start     = 0                   # Time RUNNING was FIRST entered - never reset by
                                       # a later stop/resume, so elapsed time (and
                                       # therefore the target position) keeps advancing
                                       # even while stopped, the same way a real clock
                                       # does not forget what time it is while paused.

sequence_index  = 0                   # Current phase within the 4-phase sequence
current_position = 0                  # Tracked absolute position (0 to STEPS_PER_REVOLUTION-1)
last_step_time  = 0                   # Time of the most recent step


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

def step_forward():
  # Advance to the next of the four phases, setting the two coils'
  # polarity using the same DC motor driver functions used elsewhere
  # in this curriculum, then update the tracked position. Always
  # moves forward - see the header comment on why this capstone does
  # not need to step backward.
  global sequence_index, current_position
  sequence_index = (sequence_index + 1) % SEQUENCE_LENGTH

  if sequence_index == 0:
    beaper.left_motor_forward()
    beaper.right_motor_forward()
  elif sequence_index == 1:
    beaper.left_motor_reverse()
    beaper.right_motor_forward()
  elif sequence_index == 2:
    beaper.left_motor_reverse()
    beaper.right_motor_reverse()
  else:  # sequence_index == 3
    beaper.left_motor_forward()
    beaper.right_motor_reverse()

  current_position = (current_position + 1) % STEPS_PER_REVOLUTION

def target_position(elapsed_ms):
  # Compute which position the motor SHOULD be at right now, based on
  # elapsed time since cycle_start. Uses integer-only math (multiply
  # before dividing) - the same "scale by multiplying then dividing"
  # pattern used for PWM brightness scaling in Activity 10, applied
  # here to scale a time fraction into a step position instead.
  ms_into_cycle = elapsed_ms % ROTATION_PERIOD_MS
  return ms_into_cycle * STEPS_PER_REVOLUTION // ROTATION_PERIOD_MS


# --- Main Program ---------------------

beaper.motors_stop()
beaper.nano_led_off()

print("Stepper Motor Controller")
print("Steps per revolution:", STEPS_PER_REVOLUTION)
print("Rotation period:", ROTATION_PERIOD_MS, "ms")
print("SW2: start")
print("SW5: emergency stop")
print()

state_start = time.ticks_ms()
enter_state(STATE_IDLE, state_start, "startup")

while True:
  current_time = time.ticks_ms()

  # --- Emergency stop (SW5) - checked before all state logic ---
  if beaper.SW5.value() == 0 and state == STATE_RUNNING:
    beaper.motors_stop()
    beaper.nano_led_off()
    enter_state(STATE_STOPPED, current_time, "emergency stop")
    # cycle_start is NOT reset here - elapsed time keeps counting.

  # --- State: Idle ---
  elif state == STATE_IDLE:
    if beaper.SW2.value() == 0:
      beaper.nano_led_on()
      cycle_start    = current_time
      last_step_time = current_time
      enter_state(STATE_RUNNING, current_time, "SW2 pressed")

  # --- State: Running ---
  elif state == STATE_RUNNING:
    # TODO: compute where the motor should currently be:
    #       target = target_position(time.ticks_diff(current_time, cycle_start))
    #
    #       If current_position != target, and at least MIN_STEP_DELAY
    #       ms have passed since last_step_time, call step_forward()
    #       once and update last_step_time = current_time.
    #
    #       Only ONE step per loop iteration, even if the motor is far
    #       behind target - this keeps the loop non-blocking and lets
    #       SW5 (emergency stop) still be checked every iteration.
    #       Being one loop iteration "behind" is fine; it will catch
    #       up over the next few iterations.
    pass

  # --- State: Stopped ---
  elif state == STATE_STOPPED:
    if beaper.SW2.value() == 0:
      beaper.nano_led_on()
      last_step_time = current_time
      enter_state(STATE_RUNNING, current_time, "SW2 pressed")
      # Note: cycle_start is unchanged, so the motor will immediately
      # start stepping forward to catch up to the current target -
      # see the STOPPED description in the header comment.

  time.sleep_ms(LOOP_DELAY)


# ================================================================================
# Development Guide
# ================================================================================
#
# Work through these steps in order. Test the step sequence at a very
# slow, manually-triggered pace before running full-speed - a
# miswired sequence can make the motor buzz, vibrate, or turn the
# wrong direction without actually stepping usefully.
#
# --------------------------------------------------------------------------------
# Step 1 - Step sequence verification
# --------------------------------------------------------------------------------
#
# Temporarily add this loop after beaper.motors_stop() near the top
# of the program, and remove it once the sequence is confirmed
# correct:
#
# Example code:
#
# for i in range(20):
#   step_forward()
#   print("step", i, "position", current_position)
#   time.sleep_ms(300)
#
# Watch the motor. It should rotate smoothly in one direction, one
# small step per call. If it vibrates or buzzes without turning, two
# of your stepper's four wires are likely swapped on one coil's
# terminals, or the two coils are swapped between M1A/M1B and
# M2A/M2B - try swapping the wire pairs and testing again. If it
# turns the wrong direction for your application, that is fine to
# leave as-is (step_forward() always steps whichever way the phase
# order above produces) - simply consider "forward" to mean whichever
# direction this produces.
#
# --------------------------------------------------------------------------------
# Step 2 - Steps per revolution
# --------------------------------------------------------------------------------
#
# Mark the output shaft (a piece of tape works well) and count how
# many calls to step_forward() are needed for exactly one full
# revolution back to the mark. Set STEPS_PER_REVOLUTION to this
# measured value rather than trusting the 200 default, which varies
# between motors - check your specific motor's datasheet or markings
# for its degrees-per-step rating (200 steps assumes 1.8 degrees per
# step; a 7.5-degrees-per-step motor would need 48).
#
# --------------------------------------------------------------------------------
# Step 3 - Target position math
# --------------------------------------------------------------------------------
#
# Before wiring this into the main loop, test target_position() in
# the REPL with a few hand-picked values to build confidence in the
# formula:
#
# Example code:
#
# print(target_position(0))                        # 0 - the very start of a cycle
# print(target_position(ROTATION_PERIOD_MS // 2))   # STEPS_PER_REVOLUTION // 2 - halfway around
# print(target_position(ROTATION_PERIOD_MS))        # 0 - a full cycle has elapsed, wraps back to start
#
# Confirm each result makes sense before continuing - a full
# revolution's worth of elapsed time should return to position 0,
# and half a revolution's worth of time should return roughly half
# of STEPS_PER_REVOLUTION.
#
# --------------------------------------------------------------------------------
# Step 4 - Running state
# --------------------------------------------------------------------------------
#
# Implement the TODO in STATE_RUNNING. Test with a short
# ROTATION_PERIOD_MS first (try 10000, a 10-second revolution) so you
# do not need to wait long to see a complete rotation. Confirm the
# motor moves smoothly and completes a full revolution in
# approximately the expected time - some timing error is normal,
# since MIN_STEP_DELAY and STEPS_PER_REVOLUTION together set a
# maximum possible stepping rate, and very short ROTATION_PERIOD_MS
# values may not be achievable if they would require stepping faster
# than MIN_STEP_DELAY allows.
#
# --------------------------------------------------------------------------------
# Step 5 - Stop and resume
# --------------------------------------------------------------------------------
#
# Test SW5 mid-rotation and confirm the motor stops immediately and
# de-energises (you should be able to turn the shaft by hand with
# light resistance). Wait several seconds, then press SW2 to resume,
# and confirm the motor steps forward more quickly than normal for a
# moment as it catches up to the current target, then settles back
# into its normal rate. This catch-up behaviour is expected - review
# the STOPPED description in the header comment if it is not clear
# why.
#
# --------------------------------------------------------------------------------
# Step 6 - Set your real rotation period
# --------------------------------------------------------------------------------
#
# Once everything works correctly, set ROTATION_PERIOD_MS to the
# value that matches your actual application (60000 for a
# seconds-hand-like motion, or a much longer period for a slow
# display turntable) and do a final full-length test run.


# ================================================================================
# Extension Activities
# ================================================================================
#
# --------------------------------------------------------------------------------
# EA 1 - Bidirectional movement
# --------------------------------------------------------------------------------
#
# This capstone only ever steps forward, since its target position
# always advances predictably with elapsed time. A turntable that
# needs to move to an arbitrary requested position (rather than
# following a predictable cycle) might sometimes be closer to its
# target by stepping backward instead. Implement a step_backward()
# function (hint: it uses the same four phases in reverse order) and
# a decision in STATE_RUNNING about which direction is shorter to a
# requested target position.
#
# --------------------------------------------------------------------------------
# EA 2 - Preset positions
# --------------------------------------------------------------------------------
#
# Instead of continuous rotation, adapt this project into a display
# turntable that steps between a fixed set of preset positions,
# pausing at each - reusing the parallel-list pattern from Simon Game
# and Animatronic Controller for a list of target positions and a
# list of pause durations.
#
# --------------------------------------------------------------------------------
# EA 3 - Half-step sequence
# --------------------------------------------------------------------------------
#
# The sequence in this project is a full-step sequence (four phases,
# both coils always energised). An eight-phase half-step sequence
# (alternating between both coils energised and just one) doubles the
# effective resolution and produces smoother motion, at the cost of
# somewhat reduced torque. Look up the half-step phase sequence for a
# bipolar stepper and implement it as eight phases instead of four -
# you will need a way to leave one coil unenergised for some phases,
# which left_motor_stop()/right_motor_stop() already provide.
# Remember to update SEQUENCE_LENGTH and STEPS_PER_REVOLUTION (which
# will roughly double) to match.
#
# --------------------------------------------------------------------------------
# EA 4 - Speed ramping
# --------------------------------------------------------------------------------
#
# Stepper motors can stall if commanded to start at full speed
# instantly, especially with any real load attached. Add gradual
# acceleration at the start of a run and deceleration when
# approaching a stop, rather than moving at a constant MIN_STEP_DELAY
# throughout. What happens to a real motor's reliability, and to how
# "realistic" the motion looks, with and without ramping?
#
# --------------------------------------------------------------------------------
# EA 5 - Manual position display
# --------------------------------------------------------------------------------
#
# Add a periodic Serial printout showing current_position as a
# fraction of STEPS_PER_REVOLUTION - for example, as a percentage
# around the circle, or converted to a clock-style "hours and
# minutes" if ROTATION_PERIOD_MS represents a 12-hour cycle. This
# makes it possible to follow the motor's tracked position without
# watching the physical shaft.
#
# --------------------------------------------------------------------------------
# EA 6 - Use the freed-up headers
# --------------------------------------------------------------------------------
#
# Since this project leaves H1-H4 completely free, add a sensor or
# input device that the wheeled-robot capstones could not spare a
# header for - a light sensor to detect when a display turntable
# should stop rotating and pause on a spotlit item, for example, or a
# button that jumps straight to a specific position rather than
# waiting for the rotation cycle to reach it naturally.