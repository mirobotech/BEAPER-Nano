/* ================================================================================
Capstone Project: Wall-Following Maze Solver [BEAPERNano-Capstone-Wall-Follower]
Version: 1.2
Updated: November 24, 2026

Platform: mirobo.tech BEAPER Nano circuit (Robot configuration)
Requires: BEAPERNano_v1_2.h header file

A maze-solving robot using the wall-following algorithm: keep one
side of the robot a fixed distance from a wall, and you will
eventually traverse every corridor connected to your starting point
- this is a well-known property of simply-connected mazes (mazes
with no isolated loops), not something this program has to detect
or plan for specially. The same simple rule, applied repeatedly,
handles corners, dead ends, and long straight corridors alike.

Hardware used:
  SW1          - Start following
  SW4          - Emergency stop (halts from any state)
  LS1          - Piezo speaker (start beep, turn beep)
  On-board LED - On while following

  SONAR on H2/H3     - Ultrasonic distance sensor (front and side walls)
  Servo on H5        - Sweeps the SONAR between a side-looking and a
                       forward-looking angle, using the Arduino Servo library

  Motor 1 (M1A/M1B) - Left drive motor
  Motor 2 (M2A/M2B) - Right drive motor

--------------------------------------------------------------------------------
Sensing approach:

A single SONAR sensor cannot look in two directions simultaneously,
so this program mounts it on a servo and sweeps between two fixed
angles - SIDE_ANGLE (facing the wall being followed) and
FRONT_ANGLE (facing straight ahead) - reading the distance at each
position before moving to the next. This is a non-blocking sweep:
driving continues throughout, and steering decisions use the most
recently completed pair of readings rather than pausing to wait for
a fresh one every single loop iteration.

Mount the servo so that SIDE_ANGLE points the SONAR toward
FOLLOW_RIGHT_WALL's side (right if true, left if false), and
FRONT_ANGLE points it straight ahead. The exact angle values will
depend on your specific mechanical mounting - see Development
Guide Step 1.

--------------------------------------------------------------------------------
Wall-following behaviour (three cases, checked every sweep cycle):

  Wall ahead (front distance < FRONT_WALL_THRESHOLD):
    Cannot continue straight. Turn AWAY from the followed wall -
    this eventually brings the followed wall back into range as
    the corner is completed. A dead end simply means several of
    these turns happen in a row until the robot is facing back out.

  Gap in the followed wall (side distance > SIDE_GAP_THRESHOLD):
    The wall has ended - an opening, a side corridor, or an outer
    corner. Turn INTO the gap to keep following the wall around it.

  Otherwise:
    The wall is where it should be. Drive forward, with small
    steering corrections to keep the side distance close to
    TARGET_SIDE_DISTANCE.

--------------------------------------------------------------------------------
Wall-follower behaviour:
  IDLE      - Robot stationary. Press SW1 to begin.
  FOLLOWING - Sweeping SONAR, driving, and steering as described above.
  TURNING   - Executing a turn (away from a wall ahead, or into a
              gap) for TURN_TIME ms, then returning to FOLLOWING.
  STOPPED   - Motors halted. Press SW1 to return to IDLE.

Before you begin - complete your capstone plan using the Capstone
Preparation Guide: project description, state diagram, state
details table, constants and variables, and testing plan. Test the
servo sweep and SONAR readings independently before combining them
into the following behaviour.
=================================================================================*/
// IMPORTANT: Make sure that BEAPERNano_v1_2.h is accessible as a tab in this project.
#include "BEAPERNano_v1_2.h"   // Define BEAPER Nano I/O devices
#include <Servo.h>

// ---- State Constants -------------------
const int STATE_IDLE      = 0;       // Waiting for start - robot stationary
const int STATE_FOLLOWING = 1;       // Sweeping, driving, and steering
const int STATE_TURNING   = 2;       // Executing a turn - away from a wall or into a gap
const int STATE_STOPPED   = 3;       // Halted - press SW1 to return to idle

// State names, indexed by the constants above - used for Serial output
const char* STATE_NAMES[] = { "IDLE", "FOLLOWING", "TURNING", "STOPPED" };

// ---- Wall-Following Configuration ---------
bool FOLLOW_RIGHT_WALL = true;       // true: follow the wall on the right.
                                      // false: follow the wall on the left.
                                      // Must match which side SIDE_ANGLE
                                      // actually points the SONAR toward.

// ---- Servo Sweep Configuration -------------
// Angles depend on your servo mounting - see Development Guide Step 1.
const int SIDE_ANGLE  = 0;           // Servo angle (degrees) facing the followed wall
const int FRONT_ANGLE = 90;          // Servo angle (degrees) facing straight ahead

const int SWEEP_SETTLE_TIME = 150;   // Time to wait after moving the servo
                                      // before a SONAR reading is valid (ms)

Servo sonarServo;                    // Attached to H5 in setup()

// ---- Sweep Phase Constants -----------------
const int PHASE_LOOKING_SIDE  = 0;
const int PHASE_LOOKING_FRONT = 1;

// ---- Turn Type Constants -------------------
const int TURN_AWAY = 0;             // Wall ahead - turning away from the followed wall
const int TURN_INTO = 1;             // Gap in the followed wall - turning into it

// ---- Distance Thresholds -------------------
const float FRONT_WALL_THRESHOLD  = 15;   // cm - closer than this means a wall is ahead
const float SIDE_GAP_THRESHOLD    = 30;   // cm - farther than this means the wall has ended
const float TARGET_SIDE_DISTANCE  = 10;   // cm - ideal distance to maintain from the followed wall
const float DISTANCE_TOLERANCE    = 2;    // cm - readings within this of the target need no correction

// ---- Timing Constants -----------------------
const int TURN_TIME  = 400;          // How long to execute a turn (ms)
const int LOOP_DELAY  = 10;          // Main loop delay (ms)

// ---- Program Variables -----------------------
int  state             = STATE_IDLE;
unsigned long state_start = 0;

int   sweep_phase     = PHASE_LOOKING_SIDE;   // Which direction the servo is currently facing
unsigned long last_sweep_time = 0;            // Time the servo last moved to its current angle
float side_distance   = 999;                  // Most recent side-facing SONAR reading (cm)
float front_distance  = 999;                  // Most recent front-facing SONAR reading (cm)

int  turn_type = TURN_AWAY;          // Set when entering STATE_TURNING
bool turn_left = true;               // Set when entering STATE_TURNING


// ---- Program Functions -----------------------

void enter_state(int new_state, unsigned long current_time, const char* reason = "")
{
    state       = new_state;
    state_start = current_time;
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

float read_sonar()
{
    // Read the SONAR sensor once. Called only immediately after the
    // servo has settled at its target angle - see the sweep logic in
    // STATE_FOLLOWING.
    return sonar_range(SIDE_GAP_THRESHOLD + 20);
}

void start_turn(int new_turn_type, unsigned long current_time)
{
    // Begin a turn. Works out which physical direction (left or right)
    // to turn based on both the turn type and which wall is being
    // followed - see the table below.
    turn_type = new_turn_type;

    // FOLLOW_RIGHT_WALL   turn_type    turn_left
    //   true              TURN_AWAY    true   (wall ahead - turn away from the right wall)
    //   true              TURN_INTO    false  (gap on the right - turn into it)
    //   false             TURN_AWAY    false  (wall ahead - turn away from the left wall)
    //   false             TURN_INTO    true   (gap on the left - turn into it)
    if (FOLLOW_RIGHT_WALL)
        turn_left = (new_turn_type == TURN_AWAY);
    else
        turn_left = (new_turn_type == TURN_INTO);

    const char* reason = (new_turn_type == TURN_AWAY) ? "wall ahead" : "gap detected";
    enter_state(STATE_TURNING, current_time, reason);
}


void setup()
{
    // Configure Arduino Nano ESP32 status LED as output
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, LOW);

    // Configure BEAPER Nano pushbuttons as inputs
    pinMode(SW1, INPUT_PULLUP);
    pinMode(SW4, INPUT_PULLUP);

    Serial.begin(9600);
    delay(2000);                       // Give Serial Monitor time to
                                        // connect, without blocking
                                        // forever if it's never opened

    sonarServo.attach(H5);
    sonarServo.write(SIDE_ANGLE);
    sonar_setup();                     // Configures TRIG/ECHO pins for SONAR use

    motors_stop();
    digitalWrite(LED_BUILTIN, LOW);

    Serial.println("Wall-Following Maze Solver");
    Serial.print("Following the ");
    Serial.print(FOLLOW_RIGHT_WALL ? "right" : "left");
    Serial.println(" wall");
    Serial.println("SW1: start following");
    Serial.println("SW4: emergency stop");
    Serial.println();

    state_start     = millis();
    last_sweep_time = state_start;
    enter_state(STATE_IDLE, state_start, "startup");
}

void loop()
{
    unsigned long current_time = millis();
    unsigned long elapsed      = current_time - state_start;

    // ---- Emergency stop (SW4) - checked before all state logic ----
    if (digitalRead(SW4) == LOW && state != STATE_IDLE && state != STATE_STOPPED)
    {
        motors_stop();
        digitalWrite(LED_BUILTIN, LOW);
        enter_state(STATE_STOPPED, current_time, "emergency stop");
    }

    // ---- State: Idle ----
    else if (state == STATE_IDLE)
    {
        if (digitalRead(SW1) == LOW)
        {
            tone(LS1, 880, 100);
            digitalWrite(LED_BUILTIN, HIGH);
            sonarServo.write(SIDE_ANGLE);
            sweep_phase     = PHASE_LOOKING_SIDE;
            last_sweep_time = current_time;
            enter_state(STATE_FOLLOWING, current_time, "SW1 pressed");
        }
    }

    // ---- State: Following ----
    else if (state == STATE_FOLLOWING)
    {
        // Non-blocking servo sweep: alternate between looking at the side
        // wall and looking ahead, taking a reading each time the servo has
        // had time to settle. A full sweep cycle (side reading, then front
        // reading) triggers one steering decision.
        if ((current_time - last_sweep_time) >= (unsigned long)SWEEP_SETTLE_TIME)
        {
            if (sweep_phase == PHASE_LOOKING_SIDE)
            {
                // TODO: the servo has been at SIDE_ANGLE for SWEEP_SETTLE_TIME -
                //       take a reading with read_sonar() and store it in
                //       side_distance. Then move the servo to FRONT_ANGLE with
                //       sonarServo.write(FRONT_ANGLE), set
                //       sweep_phase = PHASE_LOOKING_FRONT, and reset
                //       last_sweep_time = current_time.
            }
            else  // PHASE_LOOKING_FRONT
            {
                // TODO: the servo has been at FRONT_ANGLE for SWEEP_SETTLE_TIME -
                //       take a reading with read_sonar() and store it in
                //       front_distance. Then move the servo back to SIDE_ANGLE,
                //       set sweep_phase = PHASE_LOOKING_SIDE, and reset
                //       last_sweep_time = current_time.
                //
                //       Both side_distance and front_distance are now fresh -
                //       this is the moment to decide steering:
                //
                //       if (front_distance < FRONT_WALL_THRESHOLD)
                //           start_turn(TURN_AWAY, current_time);
                //       else if (side_distance > SIDE_GAP_THRESHOLD)
                //           start_turn(TURN_INTO, current_time);
                //       else
                //       {
                //           // TODO: drive forward, adjusting steering to bring
                //           //       side_distance toward TARGET_SIDE_DISTANCE:
                //           //       - if side_distance is more than
                //           //         DISTANCE_TOLERANCE below the target,
                //           //         steer away from the wall slightly
                //           //       - if more than DISTANCE_TOLERANCE above,
                //           //         steer toward the wall slightly
                //           //       - otherwise drive straight
                //           //       "Steer" can be as simple as briefly running
                //           //       one motor slower than the other, or
                //           //       pausing one motor for a fraction of a
                //           //       second - your choice, matching how
                //           //       Line Follower's differential steering works.
                //       }
            }
        }
    }

    // ---- State: Turning ----
    else if (state == STATE_TURNING)
    {
        // TODO: while elapsed < TURN_TIME, turn in the direction set by
        //       turn_left (true = rotate left, false = rotate right) -
        //       reuse the differential-drive turning approach from Line
        //       Follower or Sumo Robot.
        // TODO: once elapsed >= (unsigned long)TURN_TIME, enter_state(STATE_FOLLOWING,
        //       current_time) and reset sweep_phase = PHASE_LOOKING_SIDE,
        //       last_sweep_time = current_time, and move the servo back
        //       to SIDE_ANGLE, so the next sweep cycle starts cleanly.
    }

    // ---- State: Stopped ----
    else if (state == STATE_STOPPED)
    {
        if (digitalRead(SW1) == LOW)
        {
            digitalWrite(LED_BUILTIN, LOW);
            enter_state(STATE_IDLE, current_time, "SW1 pressed");
        }
    }

    delay(LOOP_DELAY);
}


/* ================================================================================
Development Guide
================================================================================

Work through these steps in order. Test on the floor with the robot
clear of obstacles when testing motor and servo directions for the
first time.

--------------------------------------------------------------------------------
Step 1 - Servo mounting and angle calibration
--------------------------------------------------------------------------------

Mount the SONAR on the servo horn so it can sweep between facing
the side you intend to follow and facing straight ahead. Temporarily
add these lines after sonarServo.write(SIDE_ANGLE) in setup():

Example code:

delay(2000);
sonarServo.write(FRONT_ANGLE);
delay(2000);
sonarServo.write(SIDE_ANGLE);

Adjust SIDE_ANGLE and FRONT_ANGLE until the SONAR genuinely points
to the side you want to follow (matching FOLLOW_RIGHT_WALL) and
then straight ahead. Remove the test lines once satisfied.

--------------------------------------------------------------------------------
Step 2 - SONAR readings at both angles
--------------------------------------------------------------------------------

Verify read_sonar() returns sensible distances at each angle. Place
a wall or box at a known distance to the side, move the servo to
SIDE_ANGLE, wait, and print the reading - repeat for FRONT_ANGLE
with an object ahead. Set FRONT_WALL_THRESHOLD, SIDE_GAP_THRESHOLD,
and TARGET_SIDE_DISTANCE from real measurements of your maze
corridors, not guesses.

--------------------------------------------------------------------------------
Step 3 - Motor direction verification
--------------------------------------------------------------------------------

Verify motor directions before driving in a maze:

Example code:

left_motor_forward();
delay(500);
motors_stop();

If a motor runs backward, swap its wiring rather than changing the
code. Confirm both motors together drive the robot straight forward.

--------------------------------------------------------------------------------
Step 4 - The sweep cycle
--------------------------------------------------------------------------------

Implement the two TODO blocks in STATE_FOLLOWING's sweep logic,
without the steering decision yet - just get the servo alternating
between SIDE_ANGLE and FRONT_ANGLE, printing side_distance and
front_distance each time a full cycle completes. Confirm both
readings update correctly as you move objects around the robot.

--------------------------------------------------------------------------------
Step 5 - Driving straight with steering correction
--------------------------------------------------------------------------------

Implement the "otherwise" branch: drive forward, adjusting slightly
based on side_distance versus TARGET_SIDE_DISTANCE. Test by placing
the robot parallel to a wall, slightly too close and then slightly
too far, and confirming it steers back toward the target distance
each time.

--------------------------------------------------------------------------------
Step 6 - Turning
--------------------------------------------------------------------------------

Implement STATE_TURNING. Test both turn types separately: place a
wall directly ahead of the robot (triggers TURN_AWAY) and separately
create a gap in the followed wall (triggers TURN_INTO). Confirm the
robot turns the correct physical direction for each - review the
table in start_turn() if a turn direction seems backward.

--------------------------------------------------------------------------------
Step 7 - Full maze run
--------------------------------------------------------------------------------

Build or find a simple maze (cardboard walls work well) and test a
complete run. Watch the Serial Monitor for state transitions. Try a
maze with at least one dead end and confirm the robot escapes it
through repeated TURN_AWAY turns, without any special dead-end
handling - this is the wall-following algorithm's key property.

*/


/* ================================================================================
Extension Activities
================================================================================

--------------------------------------------------------------------------------
EA 1 - Goal detection
--------------------------------------------------------------------------------

Detect when the robot has reached the maze exit and stop instead of
continuing to follow walls forever. Options include a light sensor
detecting a bright exit, a floor sensor detecting a marked finish
line (reusing Line Follower's Q2/Q3 technique), or simply a fixed
number of turns or a timeout if your maze layout is known in
advance. Which approach fits the mazes you plan to test with?

--------------------------------------------------------------------------------
EA 2 - Full-range sweep
--------------------------------------------------------------------------------

Instead of two fixed angles, sweep the servo through a wider range
(for example five angles from -45 to +90 degrees relative to the
robot) and take a reading at each. This gives a much richer picture
of the maze around the robot and can detect an upcoming turn before
the robot is close enough for the current two-angle version to
react. How would you change the steering decision to use five
readings instead of two?

--------------------------------------------------------------------------------
EA 3 - Adaptive turn duration
--------------------------------------------------------------------------------

TURN_TIME is currently fixed, which can under- or over-turn
depending on corridor width. After a TURN_AWAY or TURN_INTO turn,
have the robot check the side distance again before returning to
FOLLOWING, and continue turning in small increments until the side
distance is close to TARGET_SIDE_DISTANCE, rather than turning for
a fixed time regardless of the result.

--------------------------------------------------------------------------------
EA 4 - Path recording
--------------------------------------------------------------------------------

Record each turn (direction and approximate time or distance
travelled since the last turn) to build a simple map of the path
taken. Print the recorded path once the goal is reached (see EA1).
This is a basic version of the "left-hand rule" maze-mapping
technique used in real micromouse competitions.

--------------------------------------------------------------------------------
EA 5 - Switch which wall is followed
--------------------------------------------------------------------------------

The servo sweep only covers one side, chosen by how you physically
mounted the SONAR. What would a robot need, in hardware, to switch
between following the left wall and the right wall without manually
re-mounting anything? Consider a second SONAR facing the opposite
side, or widening the servo's sweep range to cover both sides in
one cycle (see EA2) and choosing which side's readings to act on
based on FOLLOW_RIGHT_WALL.

*/
