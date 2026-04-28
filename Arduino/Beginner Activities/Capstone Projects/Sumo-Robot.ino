/* ================================================================================
Capstone Project: Sumo Robot Capstone Project [Sumo-Robot]
April 28, 2026

Platform: mirobo.tech BEAPER Nano circuit (Robot configuration)
Requires: BEAPERNano.h header file

Hardware used:
  SW2        - Start match (begins countdown then releases robot)
  SW5        - Emergency stop (halts from any state)
  LS1        - Piezo speaker (countdown beeps, state feedback tones)
  LED_BUILTIN - Status indicator (on while match is active)

  Q1 (JP1=Robot) - Left floor sensor (ring-edge detection)
  Q3 (JP3=Robot) - Right floor sensor (ring-edge detection)
  SONAR on H2/H3 - Ultrasonic distance sensor (opponent detection)

  Motor 1 (M1A/M1B) - Left drive motor
  Motor 2 (M2A/M2B) - Right drive motor

IMPORTANT - Jumper settings for Robot mode:
  JP1 = Robot   (connects Q1 left floor sensor to A0)
  JP2 = Robot   (optional: connects Q2 centre sensor to A1)
  JP3 = Robot   (connects Q3 right floor sensor to A2)
  JP4 = Robot   (connects VDIV battery monitor to A3)

IMPORTANT - LED / motor pin sharing:
  LED2-LED5 share pins with the motor driver. The LEDs cannot be
  used while the motors are running, but instead show motor states.

Sensor wiring:
  Mount the SONAR module on headers H2 (TRIG) and H3 (ECHO).
  Mount Q1 (left) and Q3 (right) floor sensors at the front-left
  and front-right corners of the robot. The ring
  boundary (typically white tape on a dark surface, or dark tape on
  a light surface) will produce a sudden change in the Q1/Q3 readings
  as the sensor crosses the line.

--------------------------------------------------------------------------------
Sumo robot behaviour:
  IDLE      - Robot stationary. Press SW2 to begin the match.
              LED2-LED5 flash in a sequence to show the robot is ready.
              SW5 does nothing (already stopped).

  COUNTDOWN - Mandatory pre-match delay (START_DELAY ms). During this
              time the robot is stationary. The speaker counts down
              with beeps. Motors do not move.

  SEARCH    - No opponent within DETECT_RANGE cm. Robot executes a
              slow rotation to sweep the SONAR across the ring.
              If SONAR detects an opponent, transition to PUSH.
              If a floor sensor trips, transition to EDGE.

  PUSH      - Opponent detected within DETECT_RANGE cm. Robot drives
              forward at full speed to push the opponent out.
              SONAR is checked continuously: if opponent disappears
              (pushed out or dodged), return to SEARCH.
              If a floor sensor trips, transition to EDGE immediately.

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
================================================================================*/
// IMPORTANT: Make sure that BEAPERNano.h is accessible as a tab in this project.
#include "BEAPERNano.h"

// ---- State Constants -----------------
const int STATE_IDLE      = 0;  // Waiting for start - robot stationary
const int STATE_COUNTDOWN = 1;  // Pre-match delay - stationary, counting down
const int STATE_SEARCH    = 2;  // No opponent in range - rotating to sweep SONAR
const int STATE_PUSH      = 3;  // Opponent detected - driving forward to push
const int STATE_EDGE      = 4;  // Ring edge detected - backing up and turning away
const int STATE_STOPPED   = 5;  // Match ended or emergency stop

const char* STATE_NAMES[] = {
    "IDLE", "COUNTDOWN", "SEARCH", "PUSH", "EDGE", "STOPPED"
};

// ---- Timing Constants ----------------
const int          START_DELAY    = 5000; // Mandatory pre-match countdown (ms)
const int          BEEP_INTERVAL  = 1000; // Countdown beep interval (ms)
const int          BACKUP_TIME    = 400;  // Time to reverse after edge detection (ms)
const int          TURN_TIME      = 350;  // Time to turn away from edge (ms)
const unsigned int SONAR_INTERVAL = 50;   // Minimum time between SONAR readings (ms)

// ---- Sensor Thresholds ---------------
// Floor sensor threshold: readings above this value indicate the ring
// surface (10-bit ADC, range 0-1023). Calibrate by printing Q1_level()
// and Q3_level() on the ring surface and on the boundary tape before use.
const int EDGE_THRESHOLD = 200;  // Adjust for your surface and lighting

// SONAR opponent detection range. The robot charges when an opponent
// is detected within this distance.
const int DETECT_RANGE   = 40;   // cm - robot charges when opponent within this range

// ---- Loop Constant -------------------
const int LOOP_DELAY     = 10;   // Main loop delay (ms)

// ---- Program Variables ---------------
int           state           = STATE_IDLE;
unsigned long state_start     = 0;

unsigned long last_beep_time  = 0;   // Last countdown beep timestamp
unsigned long last_sonar_time = 0;   // Last SONAR reading timestamp
int           sonar_distance  = 999; // Most recent SONAR reading (cm)

// Edge direction detected (set in check_edge(), used in STATE_EDGE)
// 0 = both, 1 = left, 2 = right
int  edge_direction = 0;
const int EDGE_BOTH  = 0;
const int EDGE_LEFT  = 1;
const int EDGE_RIGHT = 2;

// Sub-state within STATE_EDGE
bool edge_in_backup = true;  // true = backup phase, false = turn phase


// ---- Program Functions ---------------

void enter_state(int new_state, unsigned long current_time, const char* reason = "")
{
    motors_stop();
    state           = new_state;
    state_start     = current_time;
    edge_in_backup  = true;           // Reset edge phase on every transition
    Serial.print("--> ");
    Serial.print(STATE_NAMES[new_state]);
    if (strlen(reason) > 0)
    {
        Serial.print(" (");
        Serial.print(reason);
        Serial.print(")");
    }
    Serial.println();
}

bool check_edge()
{
    // Read both floor sensors and return true if either detects the ring
    // boundary. Also sets edge_direction for the EDGE state.
    // Higher Q1/Q3 values indicate the ring surface (reflective mat).
    // A DROP below EDGE_THRESHOLD indicates the boundary tape.
    bool left_on_edge  = Q1_level() < EDGE_THRESHOLD;
    bool right_on_edge = Q3_level() < EDGE_THRESHOLD;
    if (left_on_edge && right_on_edge)
        { edge_direction = EDGE_BOTH;  return true; }
    else if (left_on_edge)
        { edge_direction = EDGE_LEFT;  return true; }
    else if (right_on_edge)
        { edge_direction = EDGE_RIGHT; return true; }
    return false;
}

void read_sonar(unsigned long current_time)
{
    // Read the SONAR sensor at most once every SONAR_INTERVAL ms.
    // Updates sonar_distance with the latest reading.
    if ((current_time - last_sonar_time) >= SONAR_INTERVAL)
    {
        int result = int(sonar_range(DETECT_RANGE + 20));
        if (result >= 0)
            sonar_distance = result;
        last_sonar_time = current_time;
    }
}

bool opponent_detected()
{
    return (sonar_distance > 0 && sonar_distance <= DETECT_RANGE);
}


void setup()
{
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, LOW);   // Off initially

    pinMode(LED2, OUTPUT);
    pinMode(LED3, OUTPUT);
    pinMode(LED4, OUTPUT);
    pinMode(LED5, OUTPUT);
    leds_off();

    pinMode(SW2, INPUT_PULLUP);
    pinMode(SW5, INPUT_PULLUP);

    pinMode(TRIG, OUTPUT);
    pinMode(ECHO, INPUT);
    digitalWrite(TRIG, LOW);

    Serial.begin(9600);
    while (!Serial);

    Serial.println("Sumo Robot");
    Serial.println("SW2: start match (5-second countdown)");
    Serial.println("SW5: emergency stop");
    Serial.println();
    Serial.println("Jumper check: JP1=Robot, JP3=Robot for floor sensors");
    Serial.print("Sensor check:  Q1="); Serial.print(Q1_level());
    Serial.print("  Q3="); Serial.print(Q3_level());
    Serial.print("  SONAR="); Serial.print(sonar_range_cm(100));
    Serial.println("cm");
    Serial.println();

    state_start    = millis();
    last_beep_time = millis();

    enter_state(STATE_IDLE, state_start, "startup");
}


void loop()
{
    unsigned long current_time = millis();
    unsigned long elapsed      = current_time - state_start;

    // ---- Emergency stop (SW5) - checked before all state logic ----
    if (digitalRead(SW5) == LOW &&
        state != STATE_IDLE && state != STATE_STOPPED)
    {
        motors_stop();
        tone(LS1, 200, 300);
        digitalWrite(LED_BUILTIN, LOW);
        enter_state(STATE_STOPPED, current_time, "emergency stop");
    }

    // ---- State: Idle ----
    else if (state == STATE_IDLE)
    {
        // Robot is stationary, waiting for match start.
        // LED2-LED5 are available here (motors stopped).
        // TODO: implement a ready animation on LED2-LED5 (e.g. a slow
        //       rotating pattern) using the Activity 11 repeating-timer
        //       pattern with a separate last_idle_time variable.

        if (digitalRead(SW2) == LOW)
        {
            digitalWrite(LED_BUILTIN, HIGH);   // On while match is active
            last_beep_time = current_time;
            enter_state(STATE_COUNTDOWN, current_time, "SW2 pressed");
        }
    }

    // ---- State: Countdown ----
    else if (state == STATE_COUNTDOWN)
    {
        // Pre-match mandatory delay. Robot is stationary.
        // TODO: beep once per BEEP_INTERVAL ms using last_beep_time.
        //       Calculate the remaining seconds from elapsed and START_DELAY
        //       and print each countdown second to the serial monitor.

        if (elapsed >= (unsigned long)START_DELAY)
        {
            enter_state(STATE_SEARCH, current_time, "countdown complete");
        }
    }

    // ---- State: Search ----
    else if (state == STATE_SEARCH)
    {
        // Edge detection is the highest priority - check before anything else.
        if (check_edge())
        {
            const char* dir = (edge_direction == EDGE_LEFT)  ? "left edge"  :
                              (edge_direction == EDGE_RIGHT) ? "right edge" : "both edges";
            enter_state(STATE_EDGE, current_time, dir);
        }
        else
        {
            read_sonar(current_time);
            if (opponent_detected())
            {
                char reason[24];
                snprintf(reason, sizeof(reason), "opponent at %dcm", sonar_distance);
                enter_state(STATE_PUSH, current_time, reason);
            }
            else
            {
                // TODO: implement a search rotation. A simple approach is to
                //       rotate one motor forward and one reverse (spin in place).
                //       More advanced: alternate sweep directions after a timeout,
                //       or drive in a slow arc to cover the ring surface.
                //       Remember: both forward directions must be correct for your
                //       motor wiring. Test left_motor_forward() and
                //       right_motor_forward() individually first.
            }
        }
    }

    // ---- State: Push ----
    else if (state == STATE_PUSH)
    {
        // Edge detection first - always the highest priority.
        if (check_edge())
        {
            const char* dir = (edge_direction == EDGE_LEFT)  ? "left edge"  :
                              (edge_direction == EDGE_RIGHT) ? "right edge" : "both edges";
            enter_state(STATE_EDGE, current_time, dir);
        }
        else
        {
            read_sonar(current_time);
            if (!opponent_detected())
            {
                enter_state(STATE_SEARCH, current_time, "opponent lost");
            }
            else
            {
                // TODO: drive both motors forward to push.
            }
        }
    }

    // ---- State: Edge ----
    else if (state == STATE_EDGE)
    {
        // Ring boundary detected. Back up, then turn away from the edge,
        // then return to SEARCH.
        //
        // Two sub-phases handled by edge_in_backup:
        //   true  - reverse for BACKUP_TIME ms
        //   false - turn away from detected edge for TURN_TIME ms
        //
        // edge_direction tells us which way to turn:
        //   EDGE_LEFT  - back up, then turn right (reverse left, forward right)
        //   EDGE_RIGHT - back up, then turn left  (forward left, reverse right)
        //   EDGE_BOTH  - straight back, then turn right (arbitrary choice)

        if (edge_in_backup)
        {
            // TODO: drive both motors in reverse.
            if (elapsed >= (unsigned long)BACKUP_TIME)
            {
                edge_in_backup = false;
                state_start    = current_time;  // Reset timer for the turn phase
            }
        }
        else
        {
            // TODO: turn away from the detected edge direction.
            if (edge_direction == EDGE_LEFT)
            {
                // TODO: Turn right (away from left edge)
            }
            else
            {
                // TODO: Turn left (away from right or both)
            }

            if (elapsed >= (unsigned long)TURN_TIME)
                enter_state(STATE_SEARCH, current_time, "edge cleared");
        }
    }

    // ---- State: Stopped ----
    else if (state == STATE_STOPPED)
    {
        if (digitalRead(SW2) == LOW)
        {
            digitalWrite(LED_BUILTIN, LOW);
            enter_state(STATE_IDLE, current_time, "SW2 pressed");
        }
    }

    delay(LOOP_DELAY);
}


/*
Capstone Development Guide

Work through these steps in order. Never attach the robot to a surface
during motor testing unless you are certain of the motor directions -
motors can drive the robot off a table unexpectedly. Test on the floor
or hold the robot clear of any surface.

Step 1 - Sensor calibration
  Before writing any state logic, calibrate your sensors. Add temporary
  Serial.print statements in setup() to print readings in a loop:

    while (true) {
        Serial.print("Q1:"); Serial.print(Q1_level());
        Serial.print(" Q3:"); Serial.print(Q3_level());
        Serial.print(" SONAR:"); Serial.print(sonar_range_cm(100));
        Serial.println("cm");
        delay(100);
    }

  Place the robot on the ring surface and note the Q1 and Q3 readings.
  Move the robot to the boundary tape and note the change. Set
  EDGE_THRESHOLD to a value midway between the two readings. Test with
  the same lighting conditions you will use during the match.

  For SONAR, hold an object at 10, 20, 30, and 40 cm and verify the
  readings are consistent. Set DETECT_RANGE to comfortably less than
  the ring diameter.

Step 2 - Motor direction verification
  Verify motor directions before connecting to drive wheels. Add
  temporary code in setup() and confirm "forward" moves the robot in
  the intended direction:

    left_motor_forward();
    delay(500);
    motors_stop();

  If a motor runs backward, swap its wiring on CON1 (the motor terminal
  block) rather than changing the code. Both motors should drive the
  robot forward when left_motor_forward() and right_motor_forward() are
  called together.

Step 3 - Edge detection response
  Test STATE_EDGE in isolation before combining with other states.
  Temporarily enter STATE_EDGE from IDLE and confirm the robot backs
  up, then turns in the correct direction for each edge_direction value.
  Walk the robot to each edge of the ring and verify the correct
  direction prints to the serial monitor.

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

  d) Battery monitoring: VDIV_level() reads the battery voltage through
     a resistor divider (JP4=Robot). Low battery causes erratic motor
     behaviour that can look like software bugs. Print the VDIV reading
     at startup and periodically during the match. Add a low-battery
     warning (beep and slow flashing LED) if the reading drops below a
     threshold you determine experimentally.

  e) Match timer: real sumo matches have a time limit. Add a
     MATCH_DURATION constant and transition from any active state to
     STATE_STOPPED when the time since COUNTDOWN ended exceeds
     MATCH_DURATION. Print the match duration to the serial monitor
     when the match ends.

*/
