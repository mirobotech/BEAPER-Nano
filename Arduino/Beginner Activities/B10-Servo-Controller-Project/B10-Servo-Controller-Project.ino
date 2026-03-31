/* ================================================================================
Project: Servo Controller [B10-Servo-Controller-Project]
March 31, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPERNano.h header file

Before starting this project, re-read GE1 and GE3
from Activity 10: Analog Output.

Servo position is controlled by PWM pulse width, not duty cycle.
The standard hobby servo protocol uses a 50 Hz signal where:
  - 1.0ms pulse = full anti-clockwise (~0 degrees)
  - 1.5ms pulse = centre position (~90 degrees)
  - 2.0ms pulse = full clockwise (~180 degrees)

Arduino's Servo library handles all of this automatically.
The servo.write(angle) function accepts an angle in degrees
(0-180) and generates the correct pulse width internally,
making servo control much simpler than raw PWM.

Servo connector locations on BEAPER Nano:
  H5 - Servo channel 1
  H6 - Servo channel 2
  H7 - Servo channel 3
  H8 - Servo channel 4

Controls:
  RV1 - servo 1 position (0-180 degrees, if pots installed)
  RV2 - servo 2 position (0-180 degrees, if pots installed)
  SW2/SW3 - servo 1 step anti-clockwise/clockwise (if no pots)
  SW4/SW5 - servo 2 step anti-clockwise/clockwise (if no pots)
================================================================================*/
// IMPORTANT: Make sure that BEAPERNano.h is accessible as a tab in this project.
#include "BEAPERNano.h"
#include <Servo.h>

// ---- Program Configuration -----------
bool POTS_INSTALLED = false;          // Set true if RV1 and RV2 are installed

// ---- Program Constants ---------------
const int STEP_DELAY  = 20;           // Main loop delay (ms)
const int ANGLE_STEP  = 2;           // Degrees per button press step

// ---- Servo objects -------------------
Servo servo1;                         // Servo on connector H5
Servo servo2;                         // Servo on connector H6

// ---- Program Variables ---------------
int servo1_angle = 90;               // Current angle for servo 1 (degrees)
int servo2_angle = 90;               // Current angle for servo 2 (degrees)


// ---- Program Functions ---------------

int set_servo(Servo &srv, int angle)
{
    // Set a servo to the given angle (0-180 degrees).
    // Clamps the angle to the valid range before writing.
    // Returns the clamped angle so the caller can store it.
    //
    // The '&' in 'Servo &srv' makes 'srv' a reference parameter -
    // the function works directly on the original Servo object
    // passed by the caller rather than making a copy of it.
    // This is necessary because Servo objects cannot be copied,
    // and it allows one function to work with servo1, servo2,
    // or any other Servo object passed to it.
    angle = constrain(angle, 0, 180);
    srv.write(angle);
    return angle;
}


void setup()
{
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, HIGH);

    // Attach servos to their output pins
    servo1.attach(H5);
    servo2.attach(H6);

    pinMode(SW2, INPUT_PULLUP);
    pinMode(SW3, INPUT_PULLUP);
    pinMode(SW4, INPUT_PULLUP);
    pinMode(SW5, INPUT_PULLUP);

    Serial.begin(9600);
    while (!Serial);

    // Move both servos to centre on startup
    servo1_angle = set_servo(servo1, servo1_angle);
    servo2_angle = set_servo(servo2, servo2_angle);

    Serial.println("Servo Controller");
    if (POTS_INSTALLED)
        Serial.println("RV1: servo 1   RV2: servo 2");
    else
        Serial.println("SW2/SW3: servo 1 anti-CW/CW   SW4/SW5: servo 2 anti-CW/CW");
    Serial.println("Servos at centre (90 degrees)");
}

void loop()
{
    if (POTS_INSTALLED)
    {
        servo1_angle = map(analogRead(RV1), 0, 1023, 0, 180);
        servo2_angle = map(analogRead(RV2), 0, 1023, 0, 180);
    }
    else
    {
        if (digitalRead(SW2) == LOW)
            servo1_angle -= ANGLE_STEP;
        else if (digitalRead(SW3) == LOW)
            servo1_angle += ANGLE_STEP;

        if (digitalRead(SW4) == LOW)
            servo2_angle -= ANGLE_STEP;
        else if (digitalRead(SW5) == LOW)
            servo2_angle += ANGLE_STEP;
    }

    servo1_angle = set_servo(servo1, servo1_angle);
    servo2_angle = set_servo(servo2, servo2_angle);

    Serial.print("S1: "); Serial.print(servo1_angle);
    Serial.print(" deg   S2: "); Serial.print(servo2_angle);
    Serial.println(" deg");

    delay(STEP_DELAY);
}


/*
Extension Activities

1.  The Servo library's 'write()' function accepts angles in
    degrees and converts them to pulse widths internally. The
    library also provides 'writeMicroseconds(us)' for direct
    pulse width control in microseconds.

    Try calling 'servo1.writeMicroseconds(1000)', then 1500,
    then 2000. Do these correspond to the 0, 90, and 180 degree
    positions from 'write()'? Are the endpoints exactly the
    same, or does your servo respond to a wider range?

    Compare 'write()' with 'writeMicroseconds()' - which gives
    you more control over the exact servo position? For standard
    applications 'write()' is simpler, but 'writeMicroseconds()'
    is useful when you need to fine-tune the endpoints or work
    with servos that use a non-standard pulse width range.

2.  Write a 'sweep(Servo &srv, int start, int end, int step_ms)'
    function that moves a servo smoothly from start to end angle,
    pausing step_ms milliseconds between each degree. Use it to
    create a continuous scanning motion between 0 and 180 degrees.

    Note that 'delay()' inside 'sweep()' blocks 'loop()' for
    its full duration. How would you allow two servos to sweep
    simultaneously? This is the problem Activity 11's non-blocking
    timing solves.

3.  Implement a servo sequencer using a 2D array of position and
    dwell-time pairs, similar to the Sound Player's melody array:

  const int sequence[][2] = {
      {  10, 500 },   // Position, dwell time (ms)
      {  90, 300 },
      { 170, 500 },
      {  90, 300 },
  };
  const int SEQ_LENGTH = sizeof(sequence) / sizeof(sequence[0]);

    Write a 'play_sequence(Servo &srv)' function that steps through
    the array, moving the servo to each position and waiting the
    specified dwell time.

4.  Attach a third servo to H7 (pin S3) and add a second
    'Servo servo3' object and 'servo3_angle' variable. Extend
    'setup()' with 'servo3.attach(H7)' and add controls for
    servo 3. With three servos you can create a simple 3-DOF
    (degrees of freedom) manipulator arm.

*/
