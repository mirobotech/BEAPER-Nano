/* ================================================================================
Capstone Project: Sumo Robot [BEAPERNano-Capstone-Sumo-Robot]
Version: 1.2
Updated: November 24, 2026

Platform: mirobo.tech BEAPER Nano circuit (Robot configuration)
Requires: BEAPERNano_v1_2.h header file

Hardware used:
  SW1          - Start match (begins countdown then releases robot)
  SW4          - Emergency stop (halts from any state)
  LS1          - Piezo speaker (countdown beeps, state feedback tones)
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
  LED1-LED4 share pins with the motor driver. The LEDs cannot be
  used while the motors are running, but instead show motor states.

Sensor wiring:
  Mount the SONAR module on headers H2 (TRIG) and H3 (ECHO).
  Mount Q1 (left) and Q3 (right) floor sensors at the front-left and
  front-right corners of the robot. The ring boundary (typically white
  tape on a dark surface, or dark tape on a light surface) will produce
  a sudden change in the Q1/Q3 readings as the sensor crosses the line.

--------------------------------------------------------------------------------
Sumo robot behaviour:
  IDLE      - Robot stationary. Press SW1 to begin the match. Flash
              the Arduino LED to show the robot is ready. SW4 does
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
              error state. Press SW1 to return to IDLE.

Before you begin - complete your capstone plan using the Capstone
Preparation Guide: a plain-English description from the robot's
perspective (what does it sense, decide, and do), state diagram,
state details table, constants and variables, and testing plan.
Test each sensor and motor independently before combining them
into state logic.
=================================================================================*/
// IMPORTANT: Make sure that BEAPERNano_v1_2.h is accessible as a tab in this project.
#include "BEAPERNano_v1_2.h"   // Define BEAPER Nano I/O devices

// ---- State Constants -------------------
const int STATE_IDLE      = 0;       // Waiting for start - robot stationary
const int STATE_COUNTDOWN = 1;       // Pre-match delay - stationary, counting down
const int STATE_SEARCH    = 2;       // No opponent in range - rotating to sweep SONAR
const int STATE_PUSH      = 3;       // Opponent detected - driving forward to push
const int STATE_EDGE      = 4;       // Ring edge detected - backing up and turning away
const int STATE_STOPPED   = 5;       // Match ended or emergency stop

// State names, indexed by the constants above - used for Serial output
const char* STATE_NAMES[] = { "IDLE", "COUNTDOWN", "SEARCH", "PUSH", "EDGE", "STOPPED" };

// ---- Timing Constants ---------------------
const int START_DELAY    = 5000;     // Mandatory pre-match countdown (ms) - real sumo rules
const int BEEP_INTERVAL  = 1000;     // Countdown beep interval (ms)
const int BACKUP_TIME    = 400;      // Time to reverse after edge detection (ms)
const int TURN_TIME      = 350;      // Time to turn away from edge before resuming search (ms)
const int SONAR_INTERVAL = 50;       // Minimum time between SONAR readings (ms)

// ---- Sensor Thresholds -------------------
// Floor sensor threshold: readings above this value indicate the ring
// surface. Readings below this value indicate the boundary (white tape
// on dark mat) or vice versa. Calibrate by printing Q1_level() and
// Q3_level() on the ring surface and on the boundary tape before use.
const int EDGE_THRESHOLD = 20000;    // Adjust for your surface and lighting

// SONAR opponent detection range. The robot charges when an opponent
// is detected within this distance. Set to the ring diameter minus a
// small margin so the robot does not charge at the ring wall.
const int DETECT_RANGE = 40;         // cm - robot charges when opponent within this range

// ---- Loop Constant -----------------------
const int LOOP_DELAY = 10;           // Main loop delay (ms)

// ---- Program Variables -----------------------
int  state             = STATE_IDLE;
unsigned long state_start = 0;

unsigned long last_beep_time  = 0;   // Last countdown beep timestamp
unsigned long last_sonar_time = 0;   // Last SONAR reading timestamp
float sonar_distance   = 999;        // Most recent SONAR reading (cm) - sonar_range() returns float

// Edge direction detected (set in check_edge(), used in STATE_EDGE)
// "left", "right", or "both"
const char* edge_direction = "both";

// Sub-state within STATE_EDGE: "backup" then "turn"
const char* edge_phase = "backup";


// ---- Program Functions -----------------------

void enter_state(int new_state, unsigned long current_time, const char* reason = "")
{
    motors_stop();
    state       = new_state;
    state_start = current_time;
    edge_phase  = "backup";           // Reset edge phase on every transition
    Serial.print("--> ");
    Serial.print(STATE_NAMES[new_state]);
    if (reason[0] != '\0')
    {
        Serial.print(" (");
        Serial.print(reason);
        Serial.println(")");
    }
    else
    {
        Serial.println();
    }
}

bool check_edge()
{
    // Read both floor sensors and return true if either detects the
    // ring boundary. Also sets edge_direction for the EDGE state to
    // use when deciding which way to turn away.
    bool left_on_edge  = Q1_level() < EDGE_THRESHOLD;
    bool right_on_edge = Q3_level() < EDGE_THRESHOLD;
    if (left_on_edge && right_on_edge)
    {
        edge_direction = "both";
        return true;
    }
    else if (left_on_edge)
    {
        edge_direction = "left";
        return true;
    }
    else if (right_on_edge)
    {
        edge_direction = "right";
        return true;
    }
    return false;
}

float read_sonar(unsigned long current_time)
{
    // Read the SONAR sensor at most once every SONAR_INTERVAL ms to
    // avoid triggering before the previous echo has cleared. Updates
    // sonar_distance. Returns the distance in cm, or the previous
    // reading if called too soon.
    if ((current_time - last_sonar_time) >= (unsigned long)SONAR_INTERVAL)
    {
        float result = sonar_range(DETECT_RANGE + 20);
        if (result >= 0)                // Ignore error codes (-1, -2)
            sonar_distance = result;
        last_sonar_time = current_time;
    }
    return sonar_distance;
}

bool opponent_detected()
{
    // Return true if the most recent SONAR reading is within DETECT_RANGE.
    return sonar_distance > 0 && sonar_distance <= DETECT_RANGE;
}


void setup()
{
    // Configure Arduino Nano ESP32 status LED as output
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, LOW);

    // Configure BEAPER Nano pushbuttons as inputs
    pinMode(SW1, INPUT_PULLUP);
    pinMode(SW4, INPUT_PULLUP);

    // Configure the ADC for 16-bit readings (0-65535), matching the
    // MicroPython board module's read_u16()-style scaling - see
    // Activity 9, GE1.
    analogReadResolution(16);

    sonar_setup();                     // Configures TRIG/ECHO pins for SONAR use

    Serial.begin(9600);
    delay(2000);                       // Give Serial Monitor time to
                                        // connect, without blocking
                                        // forever if it's never opened

    motors_stop();
    Serial.println("Sumo Robot");
    Serial.println("SW1: start match (5-second countdown)");
    Serial.println("SW4: emergency stop");
    Serial.println();
    Serial.println("Jumper check: JP1=Robot, JP3=Robot for floor sensors");
    Serial.println("Sensor check:");
    Serial.print("  Q1 (left floor): "); Serial.println(Q1_level());
    Serial.print("  Q3 (right floor): "); Serial.println(Q3_level());
    Serial.print("  SONAR range: "); Serial.print(sonar_range()); Serial.println(" cm");
    Serial.println();

    state_start    = millis();
    last_beep_time = millis();

    enter_state(STATE_IDLE, state_start, "startup");
}

void loop()
{
    unsigned long current_time = millis();
    unsigned long elapsed = current_time - state_start;

    // ---- Emergency stop (SW4) - checked before all state logic ----
    // SW4 halts the robot from any moving state immediately.
    if (digitalRead(SW4) == LOW && state != STATE_IDLE && state != STATE_STOPPED)
    {
        motors_stop();
        tone(LS1, 200, 300);
        enter_state(STATE_STOPPED, current_time, "emergency stop");
    }

    // ---- State: Idle ----
    else if (state == STATE_IDLE)
    {
        // Robot is stationary, waiting for match start.
        // TODO: implement a flashing pattern on the Arduino Nano ESP32
        //       on-board LED to show the robot is powered and waiting.
        //       Use the Activity 11 repeating-timer pattern.

        // Start match when SW1 pressed
        if (digitalRead(SW1) == LOW)
        {
            digitalWrite(LED_BUILTIN, HIGH);   // On-board LED stays on while match is active
            last_beep_time = current_time;
            enter_state(STATE_COUNTDOWN, current_time, "SW1 pressed");
        }
    }

    // ---- State: Countdown ----
    else if (state == STATE_COUNTDOWN)
    {
        // Pre-match mandatory delay. Robot is stationary. Beep once
        // per second to count down, then release into SEARCH when
        // START_DELAY elapses.
        // TODO: beep once per BEEP_INTERVAL ms using last_beep_time.
        //       Calculate the remaining seconds from elapsed and
        //       START_DELAY and print each countdown second to the
        //       Serial Monitor.

        if (elapsed >= (unsigned long)START_DELAY)
            enter_state(STATE_SEARCH, current_time, "countdown complete");
    }

    // ---- State: Search ----
    else if (state == STATE_SEARCH)
    {
        // No opponent in range. Rotate slowly to sweep the SONAR
        // across the ring and find the opponent.

        // Edge detection is the highest priority - check before anything else.
        if (check_edge())
        {
            Serial.print("Edge direction: ");
            Serial.println(edge_direction);
            enter_state(STATE_EDGE, current_time, "edge detected");
        }
        else
        {
            read_sonar(current_time);
            if (opponent_detected())
            {
                Serial.print("Opponent at ");
                Serial.print(sonar_distance);
                Serial.println("cm");
                enter_state(STATE_PUSH, current_time, "opponent detected");
            }
            else
            {
                // TODO: implement a search rotation. A simple approach
                //       is to rotate one motor forward and one reverse
                //       (spin in place). More advanced: alternate
                //       sweep directions after a timeout, or drive in
                //       a slow arc to cover the ring surface. Test
                //       left_motor_forward() and right_motor_forward()
                //       individually first.
            }
        }
    }

    // ---- State: Push ----
    else if (state == STATE_PUSH)
    {
        // Opponent is detected in front. Drive forward at full speed to push.

        // Edge detection first - always the highest priority.
        if (check_edge())
        {
            Serial.print("Edge direction: ");
            Serial.println(edge_direction);
            enter_state(STATE_EDGE, current_time, "edge detected");
        }
        else
        {
            read_sonar(current_time);
            if (!opponent_detected())
            {
                // Opponent moved out of range - could be pushed out or dodged.
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
        // Ring boundary detected. Back up, then turn away from the
        // edge, then return to SEARCH.
        //
        // Two sub-phases handled by edge_phase:
        //   "backup" - reverse for BACKUP_TIME ms
        //   "turn"   - turn away from detected edge for TURN_TIME ms
        //
        // edge_direction tells us which way to turn:
        //   "left"  - back up, then turn right
        //   "right" - back up, then turn left
        //   "both"  - straight back, then turn (arbitrary direction)

        if (strcmp(edge_phase, "backup") == 0)
        {
            // TODO: drive both motors in reverse.
            if (elapsed >= (unsigned long)BACKUP_TIME)
            {
                edge_phase  = "turn";
                state_start = current_time;    // Reset timer for the turn phase
            }
        }
        else if (strcmp(edge_phase, "turn") == 0)
        {
            // TODO: turn away from the detected edge direction.
            if (strcmp(edge_direction, "left") == 0)
            {
                // TODO: turn right (away from left edge)
            }
            else
            {
                // TODO: turn left (away from right or both)
            }

            if (elapsed >= (unsigned long)TURN_TIME)
                enter_state(STATE_SEARCH, current_time, "edge cleared");
        }
    }

    // ---- State: Stopped ----
    else if (state == STATE_STOPPED)
    {
        // Robot is halted. Motors off. Wait for SW1 to return to IDLE.
        if (digitalRead(SW1) == LOW)
            enter_state(STATE_IDLE, current_time, "SW1 pressed");
    }

    delay(LOOP_DELAY);
}


/* ================================================================================
Development Guide
================================================================================

Work through these steps in order. Never attach the robot to a
surface during motor testing unless you are certain of the motor
directions - motors can drive the robot off a table unexpectedly.
Test on the floor or hold the robot clear of any surface.

--------------------------------------------------------------------------------
Step 1 - Sensor calibration
--------------------------------------------------------------------------------

Before writing any state logic, calibrate your sensors. Add
temporary print statements after the startup sensor check to print
readings in a loop:

Example code:

while (true)
{
    Serial.print("Q1: "); Serial.print(Q1_level());
    Serial.print("  Q3: "); Serial.print(Q3_level());
    Serial.print("  SONAR: "); Serial.print(sonar_range());
    Serial.println(" cm");
    delay(100);
}

Place the robot on the ring surface and note the Q1 and Q3 readings.
Move the robot to the boundary tape and note the change. Set
EDGE_THRESHOLD to a value midway between the two readings. Test with
the same lighting conditions you will use during the match.

For SONAR, hold an object at 10, 20, 30, and 40cm and verify the
readings are consistent. Set DETECT_RANGE to comfortably less than
the ring diameter.

--------------------------------------------------------------------------------
Step 2 - Motor direction verification
--------------------------------------------------------------------------------

Verify motor directions before connecting to drive wheels. Call each
motor function individually and confirm that "forward" moves the
robot in the intended direction:

Example code:

left_motor_forward();
delay(500);
motors_stop();

If a motor runs backward, swap its wiring on CON1 (the motor
terminal block) rather than changing the code. Both motors should
drive the robot forward when left_motor_forward() and
right_motor_forward() are called together.

--------------------------------------------------------------------------------
Step 3 - Edge detection response
--------------------------------------------------------------------------------

Test STATE_EDGE in isolation before combining with other states.
Temporarily enter STATE_EDGE from IDLE and confirm the robot backs
up, then turns in the correct direction for each edge_direction
value. Walk the robot to each edge of the ring and verify the
correct edge_direction is printed.

--------------------------------------------------------------------------------
Step 4 - Search behaviour
--------------------------------------------------------------------------------

With edge detection working, test STATE_SEARCH. The robot should
spin in place and transition to PUSH when an object is held within
DETECT_RANGE. Verify it returns to SEARCH when the object is
removed. Adjust the spin direction if needed by swapping
left_motor_forward() and right_motor_reverse() in the SEARCH state.

--------------------------------------------------------------------------------
Step 5 - Full match cycle
--------------------------------------------------------------------------------

Run the complete state machine from IDLE through COUNTDOWN to
SEARCH. Watch the Serial Monitor to confirm state transitions print
correctly. Test the emergency stop (SW4) from SEARCH and PUSH. Test
the return to IDLE from STOPPED.

*/


/* ================================================================================
Extension Activities
================================================================================

--------------------------------------------------------------------------------
EA 1 - Proportional SONAR steering
--------------------------------------------------------------------------------

In STATE_PUSH, if the opponent moves slightly to one side, correct
course by briefly slowing one motor while continuing to drive
forward. To detect sideways movement, take two SONAR readings in
quick succession while rotating slightly left and right, and compare
which direction gives the shorter reading. This is a simplified
radar sweep.

--------------------------------------------------------------------------------
EA 2 - Floor sensor ring check in PUSH
--------------------------------------------------------------------------------

If both floor sensors read the ring surface consistently, you are in
a safe central position. If one sensor reads lower (approaching an
edge) during a push, steer away from that side. This prevents
chasing the opponent all the way to your own edge.

--------------------------------------------------------------------------------
EA 3 - Search strategy improvement
--------------------------------------------------------------------------------

Simple spin-in-place misses an opponent who mirrors your rotation.
Add a STATE_ADVANCE that drives forward for a short burst between
search sweeps, forcing position changes that break the mirror
pattern.

--------------------------------------------------------------------------------
EA 4 - Battery monitoring
--------------------------------------------------------------------------------

VDIV_level() reads the battery voltage through a voltage divider
(set JP4=Robot). Low battery causes erratic motor behaviour that can
look like software bugs. Print the VDIV reading at startup and
periodically during the match. Add a low-battery warning (beep
and/or slow flashing LED) if the reading drops below a threshold you
determine experimentally.

--------------------------------------------------------------------------------
EA 5 - Match timer
--------------------------------------------------------------------------------

Real sumo matches have a time limit. Add a MATCH_DURATION constant
and transition from any active state to STATE_STOPPED when the time
since COUNTDOWN ended exceeds MATCH_DURATION. Print the match
duration to the Serial Monitor when the match ends.

*/
