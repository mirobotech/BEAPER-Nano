"""
================================================================================
Capstone Project: Line Follower Robot [Line_Follower.py]
March 2, 2026

Platform: mirobo.tech BEAPER Nano circuit (Robot configuration)
Requires: BEAPER_Nano.py board module file.

Hardware used:
  SW2        - Start following (begins immediately, no countdown)
  SW5        - Emergency stop (halts from any state)
  LS1        - Piezo speaker (start beep, line-lost alert)
  On-board LED - Status indicator (on while running)

  Q1 (JP1=Robot) - Left line sensor
  Q2 (JP2=Robot) - Centre line sensor
  Q3 (JP3=Robot) - Right line sensor

  Motor 1 (M1A/M1B) - Left drive motor
  Motor 2 (M2A/M2B) - Right drive motor

IMPORTANT - Jumper settings for Robot mode:
  JP1 = Robot   (connects Q1 left line sensor to ADC0)
  JP2 = Robot   (connects Q2 centre line sensor to ADC1)
  JP3 = Robot   (connects Q3 right line sensor to ADC2)

IMPORTANT - LED / motor pin sharing:
  LED2-LED5 share pins with the motor driver. The LEDs cannot be
  used while the motors are running. This program uses the on-board
  LED as the only status indicator during motor states.

Line following setup:
  Mount Q1, Q2, and Q3 in a row facing downward across the front of
  the robot, centred on the drive axis. Q1 should be on the left side,
  Q2 in the centre, and Q3 on the right side.

  This program follows a dark line on a light surface (e.g. black tape
  on white paper or a light-coloured floor). The sensors return higher
  values on the light surface and lower values over the dark line.
  Calibrate LINE_THRESHOLD to a value midway between your two surfaces.
  If your course uses a light line on a dark surface, invert the
  on_line() comparison in the read_sensors() function.

--------------------------------------------------------------------------------
Line follower behaviour:
  IDLE      - Robot stationary. Press SW2 to begin following.
              Motors off. SW5 does nothing (already stopped).

  FOLLOW    - Sensors drive continuous differential steering:
                Both Q2 on line, Q1/Q3 off  -> forward (on track)
                Q1 on line (left of centre)  -> turn left
                Q3 on line (right of centre) -> turn right
                All sensors on line         -> forward (crossing)
              If all sensors leave the line, transition to RECOVER.

  RECOVER   - Line lost. Robot rotates in the last-known turn direction
              for RECOVER_TIME ms to sweep back across the line.
              If the line is found again, return to FOLLOW immediately.
              If RECOVER_TIME elapses without finding the line, try the
              opposite direction for RECOVER_TIME ms. If still not found,
              transition to STOPPED.

  STOPPED   - Motors halted. Press SW2 to return to IDLE.
--------------------------------------------------------------------------------
Before you begin - complete your capstone plan:
  1. Write a plain-English description of the robot's following behaviour.
  2. Draw the state diagram with all transitions.
  3. Complete the state details table (outputs, transitions, next states).
  4. List all constants and variables you will need.
  5. Write your testing plan - test each sensor individually before
     testing the complete following behaviour.
================================================================================
"""
# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32
import BEAPER_Nano as beaper

import time

# --- State Constants ------------------
STATE_IDLE    = const(0)  # Waiting for start - robot stationary
STATE_FOLLOW  = const(1)  # Following the line using differential steering
STATE_RECOVER = const(2)  # Line lost - searching for the line
STATE_STOPPED = const(3)  # Halted - press SW2 to return to idle

STATE_NAMES = {
  STATE_IDLE:    "IDLE",
  STATE_FOLLOW:  "FOLLOW",
  STATE_RECOVER: "RECOVER",
  STATE_STOPPED: "STOPPED",
}

# --- Sensor Threshold -----------------
# Readings below LINE_THRESHOLD indicate the sensor is over the dark line.
# Readings above LINE_THRESHOLD indicate the sensor is over the light surface.
# Calibrate by printing Q1/Q2/Q3 levels on both surfaces and choosing a
# value midway between them. The 16-bit ADC range is 0-65535.
LINE_THRESHOLD = 30000        # Adjust for your line and surface colours

# --- Timing Constants -----------------
RECOVER_TIME   = const(600)   # Time to rotate in one direction when line is lost (ms)
LOOP_DELAY     = const(5)     # Main loop delay (ms) - short for responsive steering

# --- Program Variables ----------------
state          = STATE_IDLE
state_start    = 0

# Sensor readings - updated every loop iteration in FOLLOW and RECOVER
left_on_line   = False        # True when Q1 detects the line
centre_on_line = False        # True when Q2 detects the line
right_on_line  = False        # True when Q3 detects the line

# Recovery direction: True = turn left, False = turn right
# Set when the line is first lost, based on which side last saw the line.
# Updated between recovery attempts (first try, then opposite direction).
recover_turn_left  = True
recover_attempt    = 0        # 0 = first direction, 1 = opposite direction


# --- Program Functions ----------------

def enter_state(new_state, current_time, reason=""):
  global state, state_start
  beaper.motors_stop()
  state       = new_state
  state_start = current_time
  print("-->", STATE_NAMES[new_state], end="")
  if reason:
    print(" (", reason, ")", sep="")
  else:
    print()

def read_sensors():
  # Read all three line sensors and update the on-line flags.
  # Lower readings indicate the dark line; higher readings indicate
  # the light surface. Update LINE_THRESHOLD to suit your course.
  global left_on_line, centre_on_line, right_on_line
  left_on_line   = beaper.Q1_level() < LINE_THRESHOLD
  centre_on_line = beaper.Q2_level() < LINE_THRESHOLD
  right_on_line  = beaper.Q3_level() < LINE_THRESHOLD

def any_on_line():
  # Return True if any sensor currently detects the line.
  return left_on_line or centre_on_line or right_on_line

def print_sensors():
  # Print a compact sensor reading for debugging. Call from the main
  # loop temporarily to calibrate LINE_THRESHOLD.
  print("Q1:", beaper.Q1_level(),
        "Q2:", beaper.Q2_level(),
        "Q3:", beaper.Q3_level(),
        "| L:", left_on_line,
        "C:", centre_on_line,
        "R:", right_on_line)


# --- Main Program ---------------------

beaper.motors_stop()
beaper.nano_led_off()
print("Line Follower Robot")
print("SW2: start following")
print("SW5: emergency stop")
print()
print("Jumper check: JP1=Robot, JP2=Robot, JP3=Robot for line sensors")
print("Sensor check (raw ADC values):")
print("  Q1 (left)  :", beaper.Q1_level())
print("  Q2 (centre):", beaper.Q2_level())
print("  Q3 (right) :", beaper.Q3_level())
print("  LINE_THRESHOLD:", LINE_THRESHOLD)
print()

state_start = time.ticks_ms()
enter_state(STATE_IDLE, state_start, "startup")

while True:
  current_time = time.ticks_ms()
  elapsed      = time.ticks_diff(current_time, state_start)

  # --- Emergency stop (SW5) - checked before all state logic ---
  if beaper.SW5.value() == 0 and state not in (STATE_IDLE, STATE_STOPPED):
    beaper.tone(200, 300)
    beaper.nano_led_off()
    enter_state(STATE_STOPPED, current_time, "emergency stop")

  # --- State: Idle ---
  elif state == STATE_IDLE:
    if beaper.SW2.value() == 0:
      beaper.tone(880, 100)
      beaper.nano_led_on()
      enter_state(STATE_FOLLOW, current_time, "SW2 pressed")

  # --- State: Follow ---
  elif state == STATE_FOLLOW:
    read_sensors()

    if not any_on_line():
      # All sensors off the line - transition to recovery
      # Set recovery direction based on which outer sensor last saw the line.
      # If only the right sensor was on last time, turn right to recover.
      global recover_turn_left, recover_attempt
      recover_turn_left = not right_on_line  # left if right wasn't on line
      recover_attempt   = 0
      beaper.tone(330, 80)
      enter_state(STATE_RECOVER, current_time, "line lost")

    else:
      # Differential steering: steer toward whichever sensor sees the line.
      # The three-sensor pattern allows four meaningful cases:
      #
      #   Case 1: Only centre (Q2) on line, or all on line
      #           -> drive straight ahead (on track or crossing)
      #
      #   Case 2: Left sensor (Q1) on line
      #           -> line is to the left: turn left
      #              stop left motor, right motor forward
      #
      #   Case 3: Right sensor (Q3) on line
      #           -> line is to the right: turn right
      #              stop right motor, left motor forward
      #
      # Priority: outer sensors take priority over centre (they indicate
      # the robot is drifting). If both outer sensors trigger simultaneously
      # the robot is straddling the line - drive straight.

      if left_on_line and not right_on_line:
        # TODO: implement left correction - stop left motor, right forward.
        beaper.left_motor_stop()
        beaper.right_motor_forward()

      elif right_on_line and not left_on_line:
        # TODO: implement right correction - stop right motor, left forward.
        beaper.right_motor_stop()
        beaper.left_motor_forward()

      else:
        # Centre only, both outer, or all three - drive straight.
        # TODO: drive both motors forward.
        beaper.left_motor_forward()
        beaper.right_motor_forward()

  # --- State: Recover ---
  elif state == STATE_RECOVER:
    read_sensors()

    if any_on_line():
      # Line found - return to following immediately
      enter_state(STATE_FOLLOW, current_time, "line found")

    elif elapsed < RECOVER_TIME:
      # Still searching - rotate in the recovery direction
      # TODO: rotate toward recover_turn_left:
      #       if recover_turn_left: left reverse, right forward
      #       else:                 left forward, right reverse
      if recover_turn_left:
        beaper.left_motor_reverse()
        beaper.right_motor_forward()
      else:
        beaper.left_motor_forward()
        beaper.right_motor_reverse()

    else:
      # First recovery attempt timed out without finding the line
      if recover_attempt == 0:
        # Try the opposite direction for another RECOVER_TIME
        recover_turn_left = not recover_turn_left
        recover_attempt   = 1
        state_start       = current_time   # Reset timer for second attempt
        print("    recovery attempt 2: opposite direction")
      else:
        # Both directions exhausted - line is truly lost
        beaper.tone(220, 500)
        beaper.nano_led_off()
        enter_state(STATE_STOPPED, current_time, "line not found")

  # --- State: Stopped ---
  elif state == STATE_STOPPED:
    if beaper.SW2.value() == 0:
      beaper.nano_led_off()
      enter_state(STATE_IDLE, current_time, "SW2 pressed")

  time.sleep_ms(LOOP_DELAY)


"""
Capstone Development Guide

Work through these steps in order. Test on the floor and hold the robot
clear of any surface when testing motor directions for the first time.

Step 1 - Sensor calibration
  Before any state logic, calibrate your line sensors. Add a temporary
  calibration loop after the startup sensor check:

    while True:
      print("Q1:", beaper.Q1_level(),
            "Q2:", beaper.Q2_level(),
            "Q3:", beaper.Q3_level())
      time.sleep_ms(100)

  Hold each sensor over the light surface and note the readings, then
  over the dark tape. Set LINE_THRESHOLD to a value comfortably midway
  between the two. A good threshold leaves a clear gap on both sides
  so that minor lighting variation does not trigger false readings.

  If your course uses a light line on a dark surface, change the
  comparison in read_sensors() from < to > for all three sensors.

Step 2 - Motor direction verification
  Verify motor directions before driving on a course:

    beaper.left_motor_forward()
    time.sleep_ms(500)
    beaper.motors_stop()

  If a motor runs backward, swap its wiring on CON1. Both motors should
  drive the robot forward when both are set to forward.

Step 3 - Straight-line following
  Place the robot on a straight section of the line and verify that
  STATE_FOLLOW drives it straight without corrections. Print the sensor
  flags each loop iteration (call print_sensors() temporarily) and
  confirm that only centre_on_line is True when the robot is centred.

Step 4 - Steering corrections
  Test each steering correction on a gentle curve. Confirm that:
  - The robot turns left when the line moves left (Q1 triggers)
  - The robot turns right when the line moves right (Q3 triggers)
  If the corrections are in the wrong direction, check that Q1 is
  physically on the left side of the robot (from the front).

Step 5 - Recovery
  Test STATE_RECOVER by lifting the robot off the line mid-follow and
  placing it back. Confirm it finds the line and returns to FOLLOW.
  Test the two-attempt recovery by placing the robot away from the line
  and verifying it transitions to STOPPED after both attempts fail.

Step 6 - Complete course
  Run the robot on a closed loop. Watch the serial monitor for state
  transitions. A well-tuned robot should stay in STATE_FOLLOW for the
  entire lap except when crossing intersections or junctions.

Step 7 - Extensions

  a) Speed and turn sharpness tuning: the binary motor control used here
     (full forward or full stop) produces abrupt corrections that can
     cause oscillation on straight sections. Investigate using
     left_motor_reverse() instead of left_motor_stop() for tighter
     turns on sharp curves, and confirm the trade-off between straight-
     line speed and cornering ability.

  b) Intersection handling: on a course with junctions, all three
     sensors may simultaneously trigger (line wider than sensor spacing)
     or a side branch may pull the outer sensors. Add an INTERSECTION
     state that drives straight for CROSS_TIME ms when all three sensors
     trigger together, overriding the normal steering logic. This treats
     every intersection as a straight-ahead crossing.

  c) Speed gradient using PWM: the motor driver supports PWM speed
     control through the LED/motor shared pins. Instead of stopping a
     motor for corrections, reduce its duty cycle proportionally to how
     far off-centre the robot is. This produces much smoother following.
     Investigate how to set a PWM duty cycle on the motor pins using
     beaper.M1A.duty_u16() and compare the result to the binary approach.

  d) Lap counter: increment a counter each time the robot crosses a
     specific marker on the track (detected by all three sensors
     triggering simultaneously for more than MARKER_TIME ms without
     having been at an intersection recently). Print the lap count and
     lap time each lap.

  e) Course map: add a list that records each steering correction as a
     direction (left / straight / right) and the elapsed time since the
     previous correction. After one lap, print the map to the serial
     console. Can you predict what the course looks like from the map?

"""