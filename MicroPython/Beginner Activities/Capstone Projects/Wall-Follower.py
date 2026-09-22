# ================================================================================
# Capstone Project: Wall-Following Maze Solver [Wall_Follower.py]
# Version: 1.0
# Updated: July 25, 2026
#
# Platform: mirobo.tech BEAPER Nano circuit (Robot configuration)
# Requires: BEAPER_Nano.py board module file
#
# A maze-solving robot using the wall-following algorithm: keep one
# side of the robot a fixed distance from a wall, and you will
# eventually traverse every corridor connected to your starting point
# - this is a well-known property of simply-connected mazes (mazes
# with no isolated loops), not something this program has to detect
# or plan for specially. The same simple rule, applied repeatedly,
# handles corners, dead ends, and long straight corridors alike.
#
# Hardware used:
#   SW2          - Start following
#   SW5          - Emergency stop (halts from any state)
#   LS1          - Piezo speaker (start beep, turn beep)
#   On-board LED - On while following
#
#   SONAR on H2/H3     - Ultrasonic distance sensor (front and side walls)
#   Servo on H5        - Sweeps the SONAR between a side-looking and a
#                        forward-looking angle
#
#   Motor 1 (M1A/M1B) - Left drive motor
#   Motor 2 (M2A/M2B) - Right drive motor
#
# --------------------------------------------------------------------------------
# Sensing approach:
#
# A single SONAR sensor cannot look in two directions simultaneously,
# so this program mounts it on a servo and sweeps between two fixed
# angles - SIDE_ANGLE (facing the wall being followed) and
# FRONT_ANGLE (facing straight ahead) - reading the distance at each
# position before moving to the next. This is a non-blocking sweep:
# driving continues throughout, and steering decisions use the most
# recently completed pair of readings rather than pausing to wait for
# a fresh one every single loop iteration.
#
# Mount the servo so that SIDE_ANGLE points the SONAR toward
# FOLLOW_RIGHT_WALL's side (right if True, left if False), and
# FRONT_ANGLE points it straight ahead. The exact angle values will
# depend on your specific mechanical mounting - see Development
# Guide Step 1.
#
# --------------------------------------------------------------------------------
# Wall-following behaviour (three cases, checked every sweep cycle):
#
#   Wall ahead (front distance < FRONT_WALL_THRESHOLD):
#     Cannot continue straight. Turn AWAY from the followed wall -
#     this eventually brings the followed wall back into range as
#     the corner is completed. A dead end simply means several of
#     these turns happen in a row until the robot is facing back out.
#
#   Gap in the followed wall (side distance > SIDE_GAP_THRESHOLD):
#     The wall has ended - an opening, a side corridor, or an outer
#     corner. Turn INTO the gap to keep following the wall around it.
#
#   Otherwise:
#     The wall is where it should be. Drive forward, with small
#     steering corrections to keep the side distance close to
#     TARGET_SIDE_DISTANCE.
#
# --------------------------------------------------------------------------------
# Wall-follower behaviour:
#   IDLE      - Robot stationary. Press SW2 to begin.
#   FOLLOWING - Sweeping SONAR, driving, and steering as described above.
#   TURNING   - Executing a turn (away from a wall ahead, or into a
#               gap) for TURN_TIME ms, then returning to FOLLOWING.
#   STOPPED   - Motors halted. Press SW2 to return to IDLE.
#
# Before you begin - complete your capstone plan using the Capstone
# Preparation Guide: project description, state diagram, state
# details table, constants and variables, and testing plan. Test the
# servo sweep and SONAR readings independently before combining them
# into the following behaviour.
# ================================================================================

# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32.
import BEAPER_Nano as beaper  # Set up BEAPER Nano I/O

import time
from machine import Pin, PWM

# --- State Constants -------------------
STATE_IDLE      = const(0)           # Waiting for start - robot stationary
STATE_FOLLOWING = const(1)           # Sweeping, driving, and steering
STATE_TURNING   = const(2)           # Executing a turn - away from a wall or into a gap
STATE_STOPPED   = const(3)           # Halted - press SW2 to return to idle

STATE_NAMES = {
  STATE_IDLE:      "IDLE",
  STATE_FOLLOWING: "FOLLOWING",
  STATE_TURNING:   "TURNING",
  STATE_STOPPED:   "STOPPED",
}

# --- Wall-Following Configuration -------
FOLLOW_RIGHT_WALL = True             # True: follow the wall on the right.
                                      # False: follow the wall on the left.
                                      # Must match which side SIDE_ANGLE
                                      # actually points the SONAR toward.

# --- Servo Sweep Configuration ----------
# Angles depend on your servo mounting - see Development Guide Step 1.
SIDE_ANGLE  = 0                      # Servo angle (degrees) facing the followed wall
FRONT_ANGLE = 90                     # Servo angle (degrees) facing straight ahead

SWEEP_SETTLE_TIME = const(150)       # Time to wait after moving the servo
                                      # before a SONAR reading is valid (ms)

# --- Sweep Phase Constants --------------
PHASE_LOOKING_SIDE  = const(0)
PHASE_LOOKING_FRONT = const(1)

# --- Turn Type Constants ----------------
TURN_AWAY = const(0)                 # Wall ahead - turning away from the followed wall
TURN_INTO = const(1)                 # Gap in the followed wall - turning into it

# --- Distance Thresholds ----------------
FRONT_WALL_THRESHOLD  = 15           # cm - closer than this means a wall is ahead
SIDE_GAP_THRESHOLD    = 30           # cm - farther than this means the wall has ended
TARGET_SIDE_DISTANCE  = 10           # cm - ideal distance to maintain from the followed wall
DISTANCE_TOLERANCE    = 2            # cm - readings within this of the target need no correction

# --- Timing Constants -------------------
TURN_TIME  = const(400)              # How long to execute a turn (ms)
LOOP_DELAY = const(10)               # Main loop delay (ms)

# --- Program Variables ------------------
state       = STATE_IDLE
state_start = 0

sweep_phase     = PHASE_LOOKING_SIDE   # Which direction the servo is currently facing
last_sweep_time = 0                    # Time the servo last moved to its current angle
side_distance   = 999                  # Most recent side-facing SONAR reading (cm)
front_distance  = 999                  # Most recent front-facing SONAR reading (cm)

turn_type  = TURN_AWAY                 # Set when entering STATE_TURNING
turn_left  = True                      # Set when entering STATE_TURNING


# --- Hardware Setup ----------------------
# BEAPER_Nano.py's SERVO1-4 constants are commented out, since H5-H8
# share pins with H1-H4 and I2C - only uncomment the one you are
# using. This project constructs SERVO1 (H5) directly instead.
SERVO1 = PWM(Pin(beaper.H5_PIN), freq=50, duty_u16=4915)


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

def read_sonar():
  # Read the SONAR sensor once. Called only immediately after the
  # servo has settled at its target angle - see the sweep logic in
  # STATE_FOLLOWING.
  return beaper.sonar_range(SIDE_GAP_THRESHOLD + 20)

def start_turn(new_turn_type, current_time):
  # Begin a turn. Works out which physical direction (left or right)
  # to turn based on both the turn type and which wall is being
  # followed - see the table below.
  global turn_type, turn_left

  turn_type = new_turn_type

  # FOLLOW_RIGHT_WALL   turn_type    turn_left
  #   True              TURN_AWAY    True   (wall ahead - turn away from the right wall)
  #   True              TURN_INTO    False  (gap on the right - turn into it)
  #   False             TURN_AWAY    False  (wall ahead - turn away from the left wall)
  #   False             TURN_INTO    True   (gap on the left - turn into it)
  if FOLLOW_RIGHT_WALL:
    turn_left = (new_turn_type == TURN_AWAY)
  else:
    turn_left = (new_turn_type == TURN_INTO)

  reason = "wall ahead" if new_turn_type == TURN_AWAY else "gap detected"
  enter_state(STATE_TURNING, current_time, reason)


# --- Main Program ---------------------

beaper.motors_stop()
beaper.nano_led_off()
beaper.set_servo(SERVO1, SIDE_ANGLE)

print("Wall-Following Maze Solver")
print("Following the", "right" if FOLLOW_RIGHT_WALL else "left", "wall")
print("SW2: start following")
print("SW5: emergency stop")
print()

state_start     = time.ticks_ms()
last_sweep_time = state_start
enter_state(STATE_IDLE, state_start, "startup")

while True:
  current_time = time.ticks_ms()
  elapsed      = time.ticks_diff(current_time, state_start)

  # --- Emergency stop (SW5) - checked before all state logic ---
  if beaper.SW5.value() == 0 and state != STATE_IDLE and state != STATE_STOPPED:
    beaper.motors_stop()
    beaper.nano_led_off()
    enter_state(STATE_STOPPED, current_time, "emergency stop")

  # --- State: Idle ---
  elif state == STATE_IDLE:
    if beaper.SW2.value() == 0:
      beaper.tone(880, 100)
      beaper.nano_led_on()
      beaper.set_servo(SERVO1, SIDE_ANGLE)
      sweep_phase     = PHASE_LOOKING_SIDE
      last_sweep_time = current_time
      enter_state(STATE_FOLLOWING, current_time, "SW2 pressed")

  # --- State: Following ---
  elif state == STATE_FOLLOWING:
    # Non-blocking servo sweep: alternate between looking at the side
    # wall and looking ahead, taking a reading each time the servo has
    # had time to settle. A full sweep cycle (side reading, then front
    # reading) triggers one steering decision.
    if time.ticks_diff(current_time, last_sweep_time) >= SWEEP_SETTLE_TIME:
      if sweep_phase == PHASE_LOOKING_SIDE:
        # TODO: the servo has been at SIDE_ANGLE for SWEEP_SETTLE_TIME -
        #       take a reading with read_sonar() and store it in
        #       side_distance. Then move the servo to FRONT_ANGLE with
        #       beaper.set_servo(SERVO1, FRONT_ANGLE), set
        #       sweep_phase = PHASE_LOOKING_FRONT, and reset
        #       last_sweep_time = current_time.
        pass

      else:  # PHASE_LOOKING_FRONT
        # TODO: the servo has been at FRONT_ANGLE for SWEEP_SETTLE_TIME -
        #       take a reading with read_sonar() and store it in
        #       front_distance. Then move the servo back to SIDE_ANGLE,
        #       set sweep_phase = PHASE_LOOKING_SIDE, and reset
        #       last_sweep_time = current_time.
        #
        #       Both side_distance and front_distance are now fresh -
        #       this is the moment to decide steering:
        #
        #       if front_distance < FRONT_WALL_THRESHOLD:
        #           start_turn(TURN_AWAY, current_time)
        #       elif side_distance > SIDE_GAP_THRESHOLD:
        #           start_turn(TURN_INTO, current_time)
        #       else:
        #           # TODO: drive forward, adjusting steering to bring
        #           #       side_distance toward TARGET_SIDE_DISTANCE:
        #           #       - if side_distance is more than
        #           #         DISTANCE_TOLERANCE below the target,
        #           #         steer away from the wall slightly
        #           #       - if more than DISTANCE_TOLERANCE above,
        #           #         steer toward the wall slightly
        #           #       - otherwise drive straight
        #           #       "Steer" can be as simple as briefly running
        #           #       one motor slower than the other, or
        #           #       pausing one motor for a fraction of a
        #           #       second - your choice, matching how
        #           #       Line Follower's differential steering works.
        #           pass
        pass

  # --- State: Turning ---
  elif state == STATE_TURNING:
    # TODO: while elapsed < TURN_TIME, turn in the direction set by
    #       turn_left (True = rotate left, False = rotate right) -
    #       reuse the differential-drive turning approach from Line
    #       Follower or Sumo Robot.
    # TODO: once elapsed >= TURN_TIME, enter_state(STATE_FOLLOWING,
    #       current_time) and reset sweep_phase = PHASE_LOOKING_SIDE,
    #       last_sweep_time = current_time, and move the servo back
    #       to SIDE_ANGLE, so the next sweep cycle starts cleanly.
    pass

  # --- State: Stopped ---
  elif state == STATE_STOPPED:
    if beaper.SW2.value() == 0:
      beaper.nano_led_off()
      enter_state(STATE_IDLE, current_time, "SW2 pressed")

  time.sleep_ms(LOOP_DELAY)


# ================================================================================
# Development Guide
# ================================================================================
#
# Work through these steps in order. Test on the floor with the robot
# clear of obstacles when testing motor and servo directions for the
# first time.
#
# --------------------------------------------------------------------------------
# Step 1 - Servo mounting and angle calibration
# --------------------------------------------------------------------------------
#
# Mount the SONAR on the servo horn so it can sweep between facing
# the side you intend to follow and facing straight ahead. Temporarily
# add these lines after beaper.set_servo(SERVO1, SIDE_ANGLE) near the
# top of the program:
#
# Example code:
#
# time.sleep_ms(2000)
# beaper.set_servo(SERVO1, FRONT_ANGLE)
# time.sleep_ms(2000)
# beaper.set_servo(SERVO1, SIDE_ANGLE)
#
# Adjust SIDE_ANGLE and FRONT_ANGLE until the SONAR genuinely points
# to the side you want to follow (matching FOLLOW_RIGHT_WALL) and
# then straight ahead. Remove the test lines once satisfied.
#
# --------------------------------------------------------------------------------
# Step 2 - SONAR readings at both angles
# --------------------------------------------------------------------------------
#
# Verify read_sonar() returns sensible distances at each angle. Place
# a wall or box at a known distance to the side, move the servo to
# SIDE_ANGLE, wait, and print the reading - repeat for FRONT_ANGLE
# with an object ahead. Set FRONT_WALL_THRESHOLD, SIDE_GAP_THRESHOLD,
# and TARGET_SIDE_DISTANCE from real measurements of your maze
# corridors, not guesses.
#
# --------------------------------------------------------------------------------
# Step 3 - Motor direction verification
# --------------------------------------------------------------------------------
#
# Verify motor directions before driving in a maze:
#
# Example code:
#
# beaper.left_motor_forward()
# time.sleep_ms(500)
# beaper.motors_stop()
#
# If a motor runs backward, swap its wiring rather than changing the
# code. Confirm both motors together drive the robot straight forward.
#
# --------------------------------------------------------------------------------
# Step 4 - The sweep cycle
# --------------------------------------------------------------------------------
#
# Implement the two TODO blocks in STATE_FOLLOWING's sweep logic,
# without the steering decision yet - just get the servo alternating
# between SIDE_ANGLE and FRONT_ANGLE, printing side_distance and
# front_distance each time a full cycle completes. Confirm both
# readings update correctly as you move objects around the robot.
#
# --------------------------------------------------------------------------------
# Step 5 - Driving straight with steering correction
# --------------------------------------------------------------------------------
#
# Implement the "otherwise" branch: drive forward, adjusting slightly
# based on side_distance versus TARGET_SIDE_DISTANCE. Test by placing
# the robot parallel to a wall, slightly too close and then slightly
# too far, and confirming it steers back toward the target distance
# each time.
#
# --------------------------------------------------------------------------------
# Step 6 - Turning
# --------------------------------------------------------------------------------
#
# Implement STATE_TURNING. Test both turn types separately: place a
# wall directly ahead of the robot (triggers TURN_AWAY) and separately
# create a gap in the followed wall (triggers TURN_INTO). Confirm the
# robot turns the correct physical direction for each - review the
# table in start_turn() if a turn direction seems backward.
#
# --------------------------------------------------------------------------------
# Step 7 - Full maze run
# --------------------------------------------------------------------------------
#
# Build or find a simple maze (cardboard walls work well) and test a
# complete run. Watch the Serial Monitor for state transitions. Try a
# maze with at least one dead end and confirm the robot escapes it
# through repeated TURN_AWAY turns, without any special dead-end
# handling - this is the wall-following algorithm's key property.


# ================================================================================
# Extension Activities
# ================================================================================
#
# --------------------------------------------------------------------------------
# EA 1 - Goal detection
# --------------------------------------------------------------------------------
#
# Detect when the robot has reached the maze exit and stop instead of
# continuing to follow walls forever. Options include a light sensor
# detecting a bright exit, a floor sensor detecting a marked finish
# line (reusing Line Follower's Q2/Q3 technique), or simply a fixed
# number of turns or a timeout if your maze layout is known in
# advance. Which approach fits the mazes you plan to test with?
#
# --------------------------------------------------------------------------------
# EA 2 - Full-range sweep
# --------------------------------------------------------------------------------
#
# Instead of two fixed angles, sweep the servo through a wider range
# (for example five angles from -45 to +90 degrees relative to the
# robot) and take a reading at each. This gives a much richer picture
# of the maze around the robot and can detect an upcoming turn before
# the robot is close enough for the current two-angle version to
# react. How would you change the steering decision to use five
# readings instead of two?
#
# --------------------------------------------------------------------------------
# EA 3 - Adaptive turn duration
# --------------------------------------------------------------------------------
#
# TURN_TIME is currently fixed, which can under- or over-turn
# depending on corridor width. After a TURN_AWAY or TURN_INTO turn,
# have the robot check the side distance again before returning to
# FOLLOWING, and continue turning in small increments until the side
# distance is close to TARGET_SIDE_DISTANCE, rather than turning for
# a fixed time regardless of the result.
#
# --------------------------------------------------------------------------------
# EA 4 - Path recording
# --------------------------------------------------------------------------------
#
# Record each turn (direction and approximate time or distance
# travelled since the last turn) to build a simple map of the path
# taken. Print the recorded path once the goal is reached (see EA1).
# This is a basic version of the "left-hand rule" maze-mapping
# technique used in real micromouse competitions.
#
# --------------------------------------------------------------------------------
# EA 5 - Switch which wall is followed
# --------------------------------------------------------------------------------
#
# The servo sweep only covers one side, chosen by how you physically
# mounted the SONAR. What would a robot need, in hardware, to switch
# between following the left wall and the right wall without manually
# re-mounting anything? Consider a second SONAR facing the opposite
# side, or widening the servo's sweep range to cover both sides in
# one cycle (see EA2) and choosing which side's readings to act on
# based on FOLLOW_RIGHT_WALL.