/* ================================================================================
Project: Motor Controller [B10_Motor_Controller_Project]
Version: 1.2
Updated: September 14, 2026

Platform: mirobo.tech BEAPER Nano circuit (robot configuration)
Requires: BEAPERNano.h header file

Before starting this project, re-read GE 1, GE 2, GE 3, and GE 4
from Activity 10: Analog Output.

IMPORTANT HARDWARE NOTES:
  The H-bridge motor driver outputs share pins with LED2-LED5.
  Using this project will prevent LED2-LED5 from being used as
  status indicators.

  Motor wiring (standard robot configuration):
    M1A (LED2) / M1B (LED3) - Left motor
    M2A (LED4) / M2B (LED5) - Right motor

  Motor power must be connected separately from logic power.
  Always test motor direction at low speed (25%) before increasing
  to full speed. If a motor runs the wrong direction, swap its
  two wires at the motor terminal.

  NOTE: Arduino's analogWrite() uses a fixed hardware timer
  frequency that may not be ideal for all motor driver chips.
  Check the driver chip datasheet for its recommended PWM
  frequency range - see GE3 in Activity 10.

Controls:
  RV1 - left motor speed  (anti-clockwise = reverse, clockwise = forward)
  RV2 - right motor speed (anti-clockwise = reverse, clockwise = forward)
  SW5 - enable/disable drive (safety enable switch)
================================================================================*/
// IMPORTANT: Make sure that BEAPERNano.h is accessible as a tab in this project.
#include "BEAPERNano.h"

// ---- Program Constants ---------------
const int STEP_DELAY = 20;            // Main loop delay (ms)
const int DEADBAND   = 5;             // Speed % below which motor is stopped
const int MAX_SPEED  = 100;           // Maximum speed percentage

// ---- Program Variables ---------------
bool drive_enabled = false;           // Safety enable flag


// ---- Program Functions ---------------

void left_motor(int speed)
{
    // Drive the left motor at the given speed (-100 to 100 percent).
    // Positive speed drives forward (M1A active, M1B LOW).
    // Negative speed drives reverse (M1B active, M1A LOW).
    // Zero or within deadband stops the motor (both outputs LOW).
    speed = constrain(speed, -MAX_SPEED, MAX_SPEED);
    if (abs(speed) < DEADBAND)
    {
        analogWrite(LED2, 0);
        analogWrite(LED3, 0);
        return;
    }
    int pwm = map(abs(speed), 0, 100, 0, 255);
    if (speed > 0)
    {
        analogWrite(LED2, pwm);
        analogWrite(LED3, 0);
    }
    else
    {
        analogWrite(LED2, 0);
        analogWrite(LED3, pwm);
    }
}

void right_motor(int speed)
{
    // Drive the right motor at the given speed (-100 to 100 percent).
    // Positive speed drives forward (M2A active, M2B LOW).
    // Negative speed drives reverse (M2B active, M2A LOW).
    // TODO: implement using LED4 and LED5, following left_motor() above
}

void motors(int left_speed, int right_speed)
{
    // Drive both motors at the given speeds.
    // TODO: call left_motor() and right_motor() with their respective speeds
}

int pot_to_speed(int pot_value)
{
    // Convert a potentiometer reading (0-65535) to a motor speed (-100 to 100).
    // The centre of the pot range maps to 0 (stopped).
    // Values within DEADBAND percent of centre return 0.
    int speed = map(pot_value, 0, 65535, -MAX_SPEED, MAX_SPEED);
    speed = constrain(speed, -MAX_SPEED, MAX_SPEED);
    if (abs(speed) < DEADBAND)
        return 0;
    return speed;
}


void setup()
{
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, HIGH);

    // Configure motor output pins
    pinMode(LED2, OUTPUT);
    pinMode(LED3, OUTPUT);
    pinMode(LED4, OUTPUT);
    pinMode(LED5, OUTPUT);

    // Configure pushbuttons and potentiometers
    pinMode(SW2, INPUT_PULLUP);
    pinMode(SW3, INPUT_PULLUP);
    pinMode(SW4, INPUT_PULLUP);
    pinMode(SW5, INPUT_PULLUP);

    // Configure the ADC for 16-bit readings (0-65535), matching the
    // MicroPython board module's read_u16()-style scaling - see
    // Activity 10, GE1.
    analogReadResolution(16);

    Serial.begin(9600);
    delay(2000);                       // Give Serial Monitor time to
                                        // connect, without blocking
                                        // forever if it's never opened

    motors(0, 0);
    Serial.println("Motor Controller");
    Serial.println("SW5: enable/disable drive   RV1: left speed   RV2: right speed");
    Serial.println("Drive DISABLED - press SW5 to enable");
}

void loop()
{
    // SW5 toggles drive enable (press and release)
    if (digitalRead(SW5) == LOW)
    {
        drive_enabled = !drive_enabled;
        if (drive_enabled)
        {
            digitalWrite(LED_BUILTIN, HIGH);  // Status LED on
            Serial.println("Drive ENABLED");
        }
        else
        {
            motors(0, 0);
            digitalWrite(LED_BUILTIN, LOW);   // Status LED off
            Serial.println("Drive DISABLED");
        }
        while (digitalRead(SW5) == LOW) {}    // Wait for release
    }

    if (drive_enabled)
    {
        int left_speed  = pot_to_speed(RV1_level());
        // TODO: read RV2 and convert to right_speed using pot_to_speed()
        int right_speed = 0;
        motors(left_speed, right_speed);
        Serial.print("L: "); Serial.print(left_speed);
        Serial.print("  R: "); Serial.println(right_speed);
    }
    else
    {
        motors(0, 0);
    }

    delay(STEP_DELAY);
}


/* ================================================================================
Extension Activities
================================================================================

--------------------------------------------------------------------------------
EA 1 - Complete the skeleton
--------------------------------------------------------------------------------

BEAPER Nano will need to be powered using either a power supply
or a battery pack connected to the CON1 screw terminal strip to
run the motors.

Test the program with one motor connected to the left motor
terminals. Finish the right_motor() and motors() functions in
the program and test them to make sure they work.

--------------------------------------------------------------------------------
EA 2 - Acceleration limiting
--------------------------------------------------------------------------------

Add acceleration limiting so that motor speed changes gradually
rather than jumping to the target immediately. Declare static
variables inside 'loop()' to track the current speed for each
motor, and move each toward its target by a fixed step per
iteration. What step size gives a natural-feeling acceleration?

Example code:

static int current_left  = 0;
static int current_right = 0;

--------------------------------------------------------------------------------
EA 3 - Timed movement sequences
--------------------------------------------------------------------------------

Implement 'drive_timed(int left_spd, int right_spd, int ms)'
that drives both motors for a set duration then stops. Use it
to create a simple repeatable movement sequence. Note that
'delay()' inside this function blocks 'loop()' for its full
duration - Activity 11 introduces non-blocking timing that
allows other actions to continue during a timed movement.

--------------------------------------------------------------------------------
EA 4 - Four-pump or four-fan controller
--------------------------------------------------------------------------------

The H-bridge driver can control four independent single-direction
loads by wiring each load between one motor output pin and ground,
with the other pin held LOW. Use SW2-SW5 to enable each pump
independently and RV1 to set a shared duty cycle:

Example code:

// Enable pump 1 at the current duty cycle
analogWrite(LED2, duty);
analogWrite(LED3, 0);         // Hold opposite pin LOW

Add a maximum run time per pump using 'millis()' to prevent
overheating or tank overflow. This previews the non-blocking
timing technique covered in Activity 11.

*/
