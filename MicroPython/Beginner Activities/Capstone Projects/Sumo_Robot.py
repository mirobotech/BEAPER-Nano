"""
================================================================================
Capstone Project: Sumo Robot [Sumo_Robot.py]
April 22, 2026

Platform: mirobo.tech BEAPER Nano circuit (Robot configuration)
Requires: BEAPER_Nano.py board module file.

Hardware used:
  SW2        - Start match (begins countdown then releases robot)
  SW5        - Emergency stop (halts from any state)
  LS1        - Piezo speaker (countdown beeps, state feedback tones)
  On-board LED - Status indicator (on while armed/running)

  Q1 (JP1=Robot) - Left floor sensor (ring-edge detection)
  Q3 (JP3=Robot) - Right floor sensor (ring-edge detection)
  SONAR on H2/H3 - Ultrasonic distance sensor (opponent detection)

  Motor 1 (M1A/M1B) - Left drive motor
  Motor 2 (M2A/M2B) - Right drive motor

IMPORTANT - Jumper settings for Robot mode:
  JP1 = Robot   (connects Q1 left floor sensor to ADC0)
  JP2 = Robot   (optional: connects Q2 centre sensor to ADC1)
  JP3 = Robot   (connects Q3 right floor sensor to ADC2)
  JP4 = Robot   (connects VDIV battery monitor to ADC3)

IMPORTANT - LED / motor pin sharing:
  LED2-LED5 share pins with the motor driver. The LEDs cannot be
  used while the motors are running, but instead show motor states.

Sensor wiring:
  Mount the SONAR module on headers H2 (TRIG) and H3 (ECHO).
  Mount Q1 (left) and Q3 (right) floor sensors at the front-left and
  front-right corners of the robot. The ring boundary (typically white
  tape on a dark surface, or dark tape on a light surface) will produce
  a sudden change in the Q1/Q3 readings as the sensor crosses the line.

--------------------------------------------------------------------------------
Sumo robot behaviour:
  IDLE      - Robot stationary. Press SW2 to begin the match. Flash
              the Arduino LED to show the robot is ready. SW5 does
              nothing (already stopped).

  COUNTDOWN - Mandatory pre-match delay (START_DELAY ms). During this
              time the robot is stationary. The speaker counts down
              with beeps. Motors do not move.

  SEARCH    - No opponent within DETECT_RANGE cm. Robot executes a
              slow rotation to sweep the SONAR across the ring. If
              SONAR detects an opponent, transition to PUSH. If a
              floor sensor trips, transition to EDGE.

  PUSH      - Opponent detected within DETECT_RANGE cm. Robot drives
              forward at full speed to push the opponent out. SONAR
              is checked continuously: if opponent disappears (pushed
              out or dodged), return to SEARCH. If a floor sensor
              trips, transition to EDGE immediately.

  EDGE      - A floor sensor has detected the ring boundary. Robot
              backs up for BACKUP_TIME ms, then turns away from the
              detected edge for TURN_TIME ms, then returns to SEARCH.
              Edge detection is the highest-priority condition and
              interrupts any other state immediately.

  STOPPED   - Motors halted. Match ended, emergency stop pressed, or
              error state. Press SW2 to return to IDLE.
--------------------------------------------------------------------------------
Before you begin - complete your capstone plan:
  1. Write a plain-English description from the robot's perspective:
     what does it sense, what does it decide, what does it do?
  2. List all states and draw your state diagram with transitions.
  3. Complete the state details table (outputs, transitions, next states).
  4. List all constants and variables you will need.
  5. Write your testing plan - test each sensor and motor independently
     before combining them into state logic.
================================================================================
"""
# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32
import BEAPER_Nano as beaper

import time

# --- State Constants ------------------
STATE_IDLE      = const(0)  # Waiting for start - robot stationary
STATE_COUNTDOWN = const(1)  # Pre-match delay - stationary, counting down
STATE_SEARCH    = const(2)  # No opponent in range - rotating to sweep SONAR
STATE_PUSH      = const(3)  # Opponent detected - driving forward to push
STATE_EDGE      = const(4)  # Ring edge detected - backing up and turning away
STATE_STOPPED   = const(5)  # Match ended or emergency stop

STATE_NAMES = {
  STATE_IDLE:      "IDLE",
  STATE_COUNTDOWN: "COUNTDOWN",
  STATE_SEARCH:    "SEARCH",
  STATE_PUSH:      "PUSH",
  STATE_EDGE:      "EDGE",
  STATE_STOPPED:   "STOPPED",
}

# --- Timing Constants -----------------
START_DELAY    = const(5000)  # Mandatory pre-match countdown (ms) - real sumo rules
BEEP_INTERVAL  = const(1000)  # Countdown beep interval (ms)
BACKUP_TIME    = const(400)   # Time to reverse after edge detection (ms)
TURN_TIME      = const(350)   # Time to turn away from edge before resuming search (ms)
SONAR_INTERVAL = const(50)    # Minimum time between SONAR readings (ms)

# --- Sensor Thresholds ----------------
# Floor sensor threshold: readings above this value indicate the ring
# surface. Readings below this value indicate the boundary (white tape
# on dark mat) or vice versa. Calibrate by printing Q1_level() and
# Q3_level() on the ring surface and on the boundary tape before use.
EDGE_THRESHOLD = 20000        # Adjust for your surface and lighting

# SONAR opponent detection range. The robot charges when an opponent
# is detected within this distance. Set to the ring diameter minus a
# small margin so the robot does not charge at the ring wall.
DETECT_RANGE   = 40           # cm - robot charges when opponent within this range

# --- Loop Constant --------------------
LOOP_DELAY     = const(10)    # Main loop delay (ms)

# --- Program Variables ----------------
state          = STATE_IDLE
state_start    = 0

last_beep_time = 0            # Last countdown beep timestamp
last_sonar_time = 0           # Last SONAR reading timestamp
sonar_distance = 999          # Most recent SONAR reading (cm)

# Edge direction detected (set in check_edge(), used in STATE_EDGE)
# "left", "right", or "both"
edge_direction = "both"

# Sub-state within STATE_EDGE: "backup" then "turn"
edge_phase     = "backup"


# --- Program Functions ----------------

def enter_state(new_state, current_time, reason=""):
  global state, state_start, edge_phase
  beaper.motors_stop()
  state       = new_state
  state_start = current_time
  edge_phase  = "backup"          # Reset edge phase on every transition
  print("-->", STATE_NAMES[new_state], end="")
  if reason:
    print(" (", reason, ")", sep="")
  else:
    print()

def check_edge():
  # Read both floor sensors and return True if either detects the ring
  # boundary. Also sets edge_direction for the EDGE state to use when
  # deciding which way to turn away.
  global edge_direction
  left_on_edge  = beaper.Q1_level() < EDGE_THRESHOLD
  right_on_edge = beaper.Q3_level() < EDGE_THRESHOLD
  if left_on_edge and right_on_edge:
    edge_direction = "both"
    return True
  elif left_on_edge:
    edge_direction = "left"
    return True
  elif right_on_edge:
    edge_direction = "right"
    return True
  return False

def read_sonar(current_time):
  # Read the SONAR sensor at most once every SONAR_INTERVAL ms to avoid
  # triggering before the previous echo has cleared. Updates sonar_distance.
  # Returns the distance in cm, or the previous reading if called too soon.
  global sonar_distance, last_sonar_time
  if time.ticks_diff(current_time, last_sonar_time) >= SONAR_INTERVAL:
    result = beaper.sonar_range(max=DETECT_RANGE + 20)
    if result >= 0:                 # Ignore error codes (-1, -2)
      sonar_distance = result
    last_sonar_time = current_time
  return sonar_distance

def opponent_detected():
  # Return True if the most recent SONAR reading is within DETECT_RANGE.
  return 0 < sonar_distance <= DETECT_RANGE


# --- Main Program ---------------------

beaper.motors_stop()
beaper.nano_led_off()
print("Sumo Robot")
print("SW2: start match (5-second countdown)")
print("SW5: emergency stop")
print()
print("Jumper check: JP1=Robot, JP3=Robot for floor sensors")
print("Sensor check:")
print("  Q1 (left floor):", beaper.Q1_level())
print("  Q3 (right floor):", beaper.Q3_level())
print("  SONAR range:", beaper.sonar_range(), "cm")
print()

state_start    = time.ticks_ms()
last_beep_time = time.ticks_ms()

enter_state(STATE_IDLE, state_start, "startup")

while True:
  current_time = time.ticks_ms()
  elapsed      = time.ticks_diff(current_time, state_start)

  # --- Emergency stop (SW5) - checked before all state logic ---
  # SW5 halts the robot from any moving state immediately.
  if beaper.SW5.value() == 0 and state not in (STATE_IDLE, STATE_STOPPED):
    beaper.motors_stop()
    beaper.tone(200, 300)
    enter_state(STATE_STOPPED, current_time, "emergency stop")

  # --- State: Idle ---
  elif state == STATE_IDLE:
    # Robot is stationary, waiting for match start.
    # TODO: implement a flashing pattern on the Arduino Nano ESP32
    #       on-board LED or set a color on the RGB LED to show the (e.g. a slow
    #       robot is powered and waiting. Use the Activity 11 
    #       repeating-timer pattern.

    # Start match when SW2 pressed
    if beaper.SW2.value() == 0:
      beaper.nano_led_on()            # On-board LED stays on while match is active
      last_beep_time = current_time
      enter_state(STATE_COUNTDOWN, current_time, "SW2 pressed")

  # --- State: Countdown ---
  elif state == STATE_COUNTDOWN:
    # Pre-match mandatory delay. Robot is stationary. Beep once per
    # second to count down, then release into SEARCH when START_DELAY
    # elapses.
    # TODO: beep once per BEEP_INTERVAL ms using last_beep_time.
    #       Calculate the remaining seconds from elapsed and START_DELAY
    #       and print each countdown second to the serial monitor.

    if elapsed >= START_DELAY:
      enter_state(STATE_SEARCH, current_time, "countdown complete")

  # --- State: Search ---
  elif state == STATE_SEARCH:
    # No opponent in range. Rotate slowly to sweep the SONAR across
    # the ring and find the opponent.

    # Edge detection is the highest priority - check before anything else.
    if check_edge():
      enter_state(STATE_EDGE, current_time, edge_direction + " edge")

    else:
      read_sonar(current_time)
      if opponent_detected():
        enter_state(STATE_PUSH, current_time, "opponent at " + str(sonar_distance) + "cm")
      else:
        # TODO: implement a search rotation. A simple approach is to
        #       rotate one motor forward and one reverse (spin in 
        #       place). More advanced: alternate sweep directions
        #       after a timeout, or drive in a slow arc to cover the
        #       ring surface. Test left_motor_forward() and
        #       right_motor_forward() individually first.

  # --- State: Push ---
  elif state == STATE_PUSH:
    # Opponent is detected in front. Drive forward at full speed to push.

    # Edge detection first - always the highest priority.
    if check_edge():
      enter_state(STATE_EDGE, current_time, edge_direction + " edge")

    else:
      read_sonar(current_time)
      if not opponent_detected():
        # Opponent moved out of range - could be pushed out or dodged.
        enter_state(STATE_SEARCH, current_time, "opponent lost")
      else:
        # TODO: drive both motors forward to push.

  # --- State: Edge ---
  elif state == STATE_EDGE:
    # Ring boundary detected. Back up, then turn away from the edge,
    # then return to SEARCH.
    #
    # Two sub-phases handled by edge_phase:
    #   "backup" - reverse for BACKUP_TIME ms
    #   "turn"   - turn away from detected edge for TURN_TIME ms
    #
    # edge_direction tells us which way to turn:
    #   "left"  - back up, then turn right
    #   "right" - back up, then turn left 
    #   "both"  - straight back, then turn (arbitrary direction)

    if edge_phase == "backup":
      # TODO: drive both motors in reverse.
      if elapsed >= BACKUP_TIME:
        edge_phase  = "turn"
        state_start = current_time    # Reset timer for the turn phase

    elif edge_phase == "turn":
      # TODO: turn away from the detected edge direction.
      if edge_direction == "left":
        # TODO: turn right (away from left edge)
      else:
        # TODO: turn left (away from right or both)

      if elapsed >= TURN_TIME:
        enter_state(STATE_SEARCH, current_time, "edge cleared")

  # --- State: Stopped ---
  elif state == STATE_STOPPED:
    # Robot is halted. Motors off. Wait for SW2 to return to IDLE.
    if beaper.SW2.value() == 0:
      enter_state(STATE_IDLE, current_time, "SW2 pressed")

  time.sleep_ms(LOOP_DELAY)


"""
Capstone Development Guide

Work through these steps in order. Never attach the robot to a surface
during motor testing unless you are certain of the motor directions -
motors can drive the robot off a table unexpectedly. Test on the floor
or hold the robot clear of any surface.

Step 1 - Sensor calibration
  Before writing any state logic, calibrate your sensors. Add temporary
  print statements after the startup sensor check to print readings in
  a loop:

    while True:
      print("Q1:", beaper.Q1_level(), "Q3:", beaper.Q3_level(),
            "SONAR:", beaper.sonar_range(), "cm")
      time.sleep_ms(100)

  Place the robot on the ring surface and note the Q1 and Q3 readings.
  Move the robot to the boundary tape and note the change. Set
  EDGE_THRESHOLD to a value midway between the two readings. Test with
  the same lighting conditions you will use during the match.

  For SONAR, hold an object at 10, 20, 30, and 40cm and verify the
  readings are consistent. Set DETECT_RANGE to comfortably less than
  the ring diameter.

Step 2 - Motor direction verification
  Verify motor directions before connecting to drive wheels. Call each
  motor function individually and confirm that "forward" moves the robot
  in the intended direction:

    beaper.left_motor_forward()
    time.sleep_ms(500)
    beaper.motors_stop()

  If a motor runs backward, swap its wiring on CON1 (the motor terminal
  block) rather than changing the code. Both motors should drive the
  robot forward when left_motor_forward() and right_motor_forward() are
  called together.

Step 3 - Edge detection response
  Test STATE_EDGE in isolation before combining with other states.
  Temporarily enter STATE_EDGE from IDLE and confirm the robot backs
  up, then turns in the correct direction for each edge_direction value.
  Walk the robot to each edge of the ring and verify the correct
  edge_direction is printed.

Step 4 - Search behaviour
  With edge detection working, test STATE_SEARCH. The robot should spin
  in place and transition to PUSH when an object is held within
  DETECT_RANGE. Verify it returns to SEARCH when the object is removed.
  Adjust the spin direction if needed by swapping left_motor_forward()
  and right_motor_reverse() in the SEARCH state.

Step 5 - Full match cycle
  Run the complete state machine from IDLE through COUNTDOWN to SEARCH.
  Watch the serial monitor to confirm state transitions print correctly.
  Test the emergency stop (SW5) from SEARCH and PUSH. Test the return
  to IDLE from STOPPED.

Step 6 - Extensions and strategy improvements

  a) Proportional SONAR steering: in STATE_PUSH, if the opponent
     moves slightly to one side, correct course by briefly slowing
     one motor while continuing to drive forward. To detect sideways
     movement, take two SONAR readings in quick succession while
     rotating slightly left and right, and compare which direction
     gives the shorter reading. This is a simplified radar sweep.

  b) Floor sensor ring check in PUSH: if both floor sensors read the
     ring surface consistently, you are in a safe central position.
     If one sensor reads lower (approaching an edge) during a push,
     steer away from that side. This prevents chasing the opponent
     all the way to your own edge.

  c) Search strategy improvement: simple spin-in-place misses an
     opponent who mirrors your rotation. Add a STATE_ADVANCE that
     drives forward for a short burst between search sweeps, forcing
     position changes that break the mirror pattern.

  d) Battery monitoring: VDIV_level() reads the battery voltage
     through a voltage divider (set JP4=Robot). Low battery causes
     erratic motor behaviour that can look like software bugs. Print
     the VDIV reading at startup and periodically during the match.
     Add a low-battery warning (beep and/or slow flashing LED) if the
     reading drops below a threshold you determine experimentally.

  e) Match timer: real sumo matches have a time limit. Add a
     MATCH_DURATION constant and transition from any active state to
     STATE_STOPPED when the time since COUNTDOWN ended exceeds
     MATCH_DURATION. Print the match duration to the serial monitor
     when the match ends.

"""