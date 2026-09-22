/* ================================================================================
Capstone Project: Line Follower Robot [BEAPERNano-Capstone-Line-Follower]
Version: 1.0
Updated: July 25, 2026

Platform: mirobo.tech BEAPER Nano circuit (Robot configuration)
Requires: BEAPERNano.h header file

Hardware used:
  SW2          - Start following (begins immediately, no countdown)
  SW5          - Emergency stop (halts from any state)
  LS1          - Piezo speaker (start beep, line-lost alert)
  On-board LED - Status indicator (on while running)

  Q2 - Left line sensor  (R sensor module, left position)
  Q3 - Right line sensor (R sensor module, right position)
  Q1 - Line sensor (L sensor module, for alternate configurations)

  Motor 1 (M1A/M1B) - Left drive motor
  Motor 2 (M2A/M2B) - Right drive motor

IMPORTANT - Jumper settings for two-sensor line following:
  JP2 = Robot   (connects Q2 to ADC1 - left sensor)
  JP3 = Robot   (connects Q3 to ADC2 - right sensor)
  JP1 = Robot   (used in alternate configurations)

IMPORTANT - LED / motor pin sharing:
  LED2-LED5 share pins with the motor driver. The LEDs cannot be
  used while the motors are running, but instead show motor states.

Sensor module setup - two-sensor configuration (starting point):
  Install the R sensor module ('Line/Floor', labelled 'R') on the
  robot's centreline. The module contains two phototransistors: Q2 in
  the left position, and Q3 in the right position. When centred on the
  line, both Q2 and Q3 'see' the line. This works well for following
  a simple tape line (20mm or 3/4" electrical tape works well).

  This program follows a dark line on a light surface (e.g. black tape
  on a white floor). Sensors return higher values on the light surface
  and lower values over the dark line. Calibrate LINE_THRESHOLD to a
  value midway between your two surfaces. If your course uses a light
  line on a dark surface, invert the comparisons in read_sensors().

--------------------------------------------------------------------------------
Other sensor arrangements (see the Development Guide, below):

  Two-sensor floor detection (wider lines, T-stops, + intersections):
    Use two sensor modules, with the 'L' module on the robot's right,
    and the 'R' module on the robot's left. Q3 becomes the left sensor
    and Q1 becomes the right sensor, with both sensors detecting the
    floor on either side of the line. Update read_sensors() to read
    Q1_level() and Q3_level().

  Three-sensor row (narrower lines, sharper curves):
    Use two sensor modules, with the 'L' module on the robot's right,
    and the 'R' module on the robot's left, aligning the three
    phototransistors in an equally-spaced row: Q2 detects the left of
    a wide line or the floor to the left of a narrow line, Q3 detects
    the centre of the line, and Q1 detects the right of a wide line
    or the floor to the right of a narrow line. This gives three
    independent sensors and enables the priority-based steering used
    in the three-sensor step in the Development Guide.
--------------------------------------------------------------------------------
Line follower behaviour:
  IDLE      - Robot stationary. Press SW2 to begin following.
              Motors off. SW5 does nothing (already stopped).

  FOLLOW    - Two-sensor differential steering:
                Q2 on line only -> turn left
                Q3 on line only -> turn right
                Both on line    -> drive straight
                Neither on line -> line lost, enter RECOVER

  RECOVER   - Line lost. Robot rotates opposite the last-known turn
              direction for RECOVER_TIME ms to sweep back across the
              line. If the line is found again, return to FOLLOW
              immediately. If RECOVER_TIME elapses without finding
              the line, try changing to the opposite direction for
              RECOVER_TIME ms. If still not found, transition to
              STOPPED.

  STOPPED   - Motors halted. Press SW2 to return to IDLE.

Before you begin - complete your capstone plan using the Capstone
Preparation Guide: project description, state diagram, state
details table, constants and variables, and testing plan. Test each
sensor individually before testing the complete following behaviour.
=================================================================================*/
// IMPORTANT: Make sure that BEAPERNano.h is accessible as a tab in this project.
#include "BEAPERNano.h"   // Define BEAPER Nano I/O devices

// ---- State Constants -------------------
const int STATE_IDLE    = 0;         // Waiting for start - robot stationary
const int STATE_FOLLOW  = 1;         // Following the line using differential steering
const int STATE_RECOVER = 2;         // Line lost - searching for the line
const int STATE_STOPPED = 3;         // Halted - press SW2 to return to idle

// State names, indexed by the constants above - used for Serial output
const char* STATE_NAMES[] = { "IDLE", "FOLLOW", "RECOVER", "STOPPED" };

// ---- Sensor Threshold -------------------
// Calibrate by printing Q2/Q3 levels on both surfaces and choosing a
// value midway between them. The 16-bit ADC range is 0-65535.
const int LINE_THRESHOLD = 30000;    // Adjust for your line and surface colours

// ---- Timing Constants ---------------------
const int RECOVER_TIME = 600;        // Time to rotate in one direction when line is lost (ms)
const int LOOP_DELAY   = 5;          // Main loop delay (ms) - short for responsive steering

// ---- Program Variables -----------------------
int  state             = STATE_IDLE;
unsigned long state_start = 0;

// Sensor readings - updated every loop iteration in FOLLOW and RECOVER.
bool left_on_line  = false;          // True when Q2 (left) detects the line
bool right_on_line = false;          // True when Q3 (right) detects the line

// Recovery direction: true = turn left, false = turn right.
// Set when the line is first lost, based on which sensor last saw the
// line. Updated between recovery attempts (first try, then opposite
// direction for second try).
bool recover_turn_left = true;
int  recover_attempt   = 0;          // 0 = first direction, 1 = opposite direction


// ---- Program Functions -----------------------

void enter_state(int new_state, unsigned long current_time, const char* reason = "")
{
    motors_stop();
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

void read_sensors()
{
    // Read the two active line sensors and update the on-line flags.
    // Update LINE_THRESHOLD to suit your course.
    left_on_line  = Q2_level() < LINE_THRESHOLD;   // Q2: left
    right_on_line = Q3_level() < LINE_THRESHOLD;   // Q3: right
}

bool any_on_line()
{
    // Return true if either sensor currently detects the line.
    return left_on_line || right_on_line;
}

void print_sensors()
{
    // Print a compact sensor reading for debugging. Call from loop()
    // temporarily to calibrate LINE_THRESHOLD.
    Serial.print("Q2: "); Serial.print(Q2_level());
    Serial.print("  Q3: "); Serial.print(Q3_level());
    Serial.print(" | L: "); Serial.print(left_on_line);
    Serial.print(" R: "); Serial.println(right_on_line);
}


void setup()
{
    // Configure Arduino Nano ESP32 status LED as output
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, LOW);

    // Configure BEAPER Nano pushbuttons as inputs
    pinMode(SW2, INPUT_PULLUP);
    pinMode(SW5, INPUT_PULLUP);

    // Configure the ADC for 16-bit readings (0-65535), matching the
    // MicroPython board module's read_u16()-style scaling - see
    // Activity 9, GE1.
    analogReadResolution(16);

    Serial.begin(9600);
    delay(2000);                       // Give Serial Monitor time to
                                        // connect, without blocking
                                        // forever if it's never opened

    motors_stop();
    Serial.println("Line Follower Robot");
    Serial.println("SW2: start following");
    Serial.println("SW5: emergency stop");
    Serial.println();
    Serial.println("Jumper check: JP2=Robot, JP3=Robot for two-sensor line following");
    Serial.println("Sensor check (raw ADC values):");
    Serial.print("  Q2: "); Serial.println(Q2_level());
    Serial.print("  Q3: "); Serial.println(Q3_level());
    Serial.print("  LINE_THRESHOLD: "); Serial.println(LINE_THRESHOLD);
    Serial.println();

    state_start = millis();
    enter_state(STATE_IDLE, state_start, "startup");
}

void loop()
{
    unsigned long current_time = millis();
    unsigned long elapsed = current_time - state_start;

    // ---- Emergency stop (SW5) - checked before all state logic ----
    if (digitalRead(SW5) == LOW && state != STATE_IDLE && state != STATE_STOPPED)
    {
        digitalWrite(LED_BUILTIN, LOW);
        enter_state(STATE_STOPPED, current_time, "emergency stop");
    }

    // ---- State: Idle ----
    else if (state == STATE_IDLE)
    {
        if (digitalRead(SW2) == LOW)
        {
            tone(LS1, 880, 100);
            digitalWrite(LED_BUILTIN, HIGH);
            enter_state(STATE_FOLLOW, current_time, "SW2 pressed");
        }
    }

    // ---- State: Follow ----
    else if (state == STATE_FOLLOW)
    {
        read_sensors();

        if (!any_on_line())
        {
            // Both sensors off the line - transition to recovery.
            // Set recovery direction based on which sensor last saw
            // the line. If the right sensor (Q3) was last on, the
            // line is to the right - turn right. Otherwise turn left.
            recover_turn_left = !right_on_line;
            recover_attempt   = 0;
            enter_state(STATE_RECOVER, current_time, "line lost");
        }
        else
        {
            if (left_on_line && !right_on_line)
            {
                // Q2 on line only:
                //   Robot has drifted right - line is now under Q2.
                // TODO: turn robot left (implement left correction)
            }
            else if (right_on_line && !left_on_line)
            {
                // Q3 on line only:
                //   Robot has drifted left - line is now under Q3.
                // TODO: turn robot right (implement right correction)
            }
            else
            {
                // Both sensors on line - drive straight.
                // TODO: drive both motors forward.
            }
        }
    }

    // ---- State: Recover ----
    else if (state == STATE_RECOVER)
    {
        read_sensors();

        if (any_on_line())
        {
            // Line found - return to following immediately
            enter_state(STATE_FOLLOW, current_time, "line found");
        }
        else if (elapsed < (unsigned long)RECOVER_TIME)
        {
            // Still searching - rotate in the recovery direction.
            // TODO: rotate toward recover_turn_left:
            //       if (recover_turn_left) left reverse, right forward
            //       else                    left forward, right reverse
            if (recover_turn_left)
            {
                // TODO: turn robot left
            }
            else
            {
                // TODO: turn robot right
            }
        }
        else
        {
            // First recovery attempt timed out without finding the line
            if (recover_attempt == 0)
            {
                // Try the opposite direction for another RECOVER_TIME
                recover_turn_left = !recover_turn_left;
                recover_attempt   = 1;
                state_start       = current_time;   // Reset timer for second attempt
                Serial.println("    recovery attempt 2: opposite direction");
            }
            else
            {
                // Both directions exhausted - line is truly lost
                tone(LS1, 220, 500);
                digitalWrite(LED_BUILTIN, LOW);
                enter_state(STATE_STOPPED, current_time, "line not found");
            }
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


/* ================================================================================
Development Guide
================================================================================

Work through these steps in order. Test on the floor and hold the
robot clear of any surface when testing motor directions for the
first time.

--------------------------------------------------------------------------------
Step 1 - Sensor calibration
--------------------------------------------------------------------------------

Before any state logic, calibrate your line sensors. Add a temporary
calibration loop after the startup sensor check:

Example code:

while (true)
{
    Serial.print("Q2: "); Serial.print(Q2_level());
    Serial.print("  Q3: "); Serial.println(Q3_level());
    delay(100);
}

Hold each sensor over the light surface and note the readings, then
over the dark tape. Set LINE_THRESHOLD to a value comfortably midway
between the two. A good threshold leaves a clear gap on both sides
so that minor lighting variation does not trigger false readings.

If your course uses a light line on a dark surface, change the
comparisons in read_sensors() from < to >.

--------------------------------------------------------------------------------
Step 2 - Motor direction verification
--------------------------------------------------------------------------------

Verify motor directions before driving on a course:

Example code:

left_motor_forward();
delay(500);
motors_stop();

If a motor runs backward, swap its wiring on CON1. Both motors
should drive the robot forward when both are set to forward.

--------------------------------------------------------------------------------
Step 3 - Straight-line following
--------------------------------------------------------------------------------

Place the robot centred on the line and verify that STATE_FOLLOW
drives it straight with both sensors triggering. Print the sensor
flags each loop iteration (call print_sensors() temporarily) and
confirm that both left_on_line and right_on_line are true when
centred.

--------------------------------------------------------------------------------
Step 4 - Steering corrections
--------------------------------------------------------------------------------

Test each steering correction on a gentle curve. Confirm that:
- The robot turns left when only Q2 (left) triggers
- The robot turns right when only Q3 (right) triggers
If the corrections are in the wrong direction, verify that JP2 and
JP3 are both set to Robot and that Q2 and Q3 are reading correctly.

--------------------------------------------------------------------------------
Step 5 - Recovery
--------------------------------------------------------------------------------

Test STATE_RECOVER by lifting the robot off the line mid-follow and
placing it back. Confirm it finds the line and returns to FOLLOW.
Test the two-attempt recovery by placing the robot away from the
line and verifying it transitions to STOPPED after both attempts
fail.

--------------------------------------------------------------------------------
Step 6 - Complete course
--------------------------------------------------------------------------------

Run the robot on a closed loop. Watch the Serial Monitor for state
transitions. A well-tuned robot should stay in STATE_FOLLOW for the
entire lap except when recovering from sharp curves.

--------------------------------------------------------------------------------
Step 7 - Alternate configuration: two-sensor floor detection
--------------------------------------------------------------------------------

For wider lines, T-stops, and + intersections: swap the L and R
sensor modules so the R module ('Line/Floor') is on the robot's
LEFT side and the L module ('Floor') is on the RIGHT side. Q3 (R
module, now on the left) becomes the left floor sensor, and Q1 (L
module, now on the right) becomes the right floor sensor. Set
JP1=Robot and JP3=Robot.

In this arrangement both inboard phototransistors detect the floor
on either side of the line rather than the line itself. The robot
follows by keeping floor on both sides (both sensors off the line).
This handles wider lines, T-junctions, and + intersections more
reliably than the narrow-line two-sensor approach.

Update read_sensors() for floor detection:

Example code:

left_on_line  = Q3_level() < LINE_THRESHOLD;  // floor = low
right_on_line = Q1_level() < LINE_THRESHOLD;

Invert the steering logic: if both sensors are HIGH (on the floor),
drive straight. Correct when one sensor goes LOW (over the line).

--------------------------------------------------------------------------------
Step 8 - Alternate configuration: three-sensor row
--------------------------------------------------------------------------------

For narrower lines and sharper curves: swap the L and R sensor
modules and align the three phototransistors in a row across the
front of the robot:
  Q2 (R module, left position)  - left of line
  Q3 (R module, right position) - centre, on the line
  Q1 (L module, left position)  - right of line
Set JP1=Robot, JP2=Robot, JP3=Robot.

This gives a true three-sensor arrangement where Q3 tracks the line
centre and Q2/Q1 detect drift to either side. Priority-based
steering becomes possible: outer sensors (Q2, Q1) take priority over
the centre sensor (Q3), and the robot can detect intersections when
all three trigger simultaneously.

Update read_sensors() for three-sensor mode:

Example code:

bool left_on_line   = Q2_level() < LINE_THRESHOLD;  // Q2: left
bool centre_on_line = Q3_level() < LINE_THRESHOLD;  // Q3: centre
bool right_on_line  = Q1_level() < LINE_THRESHOLD;  // Q1: right

Update the steering logic in STATE_FOLLOW to use all three flags:

Example code:

if (left_on_line && !right_on_line)      turn left
else if (right_on_line && !left_on_line) turn right
else                                     drive straight

*/


/* ================================================================================
Extension Activities
================================================================================

--------------------------------------------------------------------------------
EA 1 - Speed gradient using PWM
--------------------------------------------------------------------------------

Rather than stopping a motor for corrections, reduce its duty cycle
proportionally. This produces smoother following and reduces
oscillation on straight sections. Investigate using analogWrite() on
the motor pins (M1A, M1B, M2A, M2B) and compare the result to the
binary approach - see Activity 10's Motor Controller project for the
PWM speed-control pattern this builds on.

--------------------------------------------------------------------------------
EA 2 - Lap counter
--------------------------------------------------------------------------------

Increment a counter each time both sensors trigger simultaneously
for more than MARKER_TIME ms without having been at a recovery event
recently. Print the lap count and lap time each lap.

--------------------------------------------------------------------------------
EA 3 - Course map
--------------------------------------------------------------------------------

Record each steering correction as a direction and elapsed time
since the previous correction. After one lap, print the map to the
Serial Monitor. Can you predict the course layout from the map?

*/
