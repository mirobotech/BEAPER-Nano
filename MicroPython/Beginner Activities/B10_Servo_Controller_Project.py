"""
================================================================================
Project: Servo Controller [B10_Servo_Controller_Project.py]
March 31, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPER_Nano.py board module file.

Before starting this project, re-read GE1 and GE3
from Activity 10: Analog Output.

IMPORTANT - How servo PWM differs from LED and motor PWM:

For LEDs and motors, the duty cycle (proportion of on-time) is
what matters. The PWM frequency can vary within a wide range.

For hobby servos, position is encoded differently: the servo
expects a pulse of a specific width, repeated at a fixed rate.
The standard is a 50 Hz signal (one pulse every 20ms), but the
pulse width is different depending on the servo's travel angle:

For 90 degree travel servos:
  - 1.0ms pulse width = full anti-clockwise (~0 degrees)
  - 1.5ms pulse width = centre position (~45 degrees)
  - 2.0ms pulse width = full clockwise (~90 degrees)

For 180 degree travel servos:
  - 0.5ms pulse width = full anti-clockwise (~0 degrees)
  - 1.5ms pulse width = centre position (~90 degrees)
  - 2.5ms pulse width = full clockwise (~180 degrees)

Servo connector locations on BEAPER Nano:
  H5 - Servo channel 1 (use beaper.set_servo(SERVO1, angle))
  H6 - Servo channel 2 (use beaper.set_servo(SERVO2, angle))
  H7 - Servo channel 3 (use beaper.set_servo(SERVO3, angle))
  H8 - Servo channel 4 (use beaper.set_servo(SERVO4, angle))

Controls:
  RV1 - servo 1 position (0-90 degrees, if pots installed)
  RV2 - servo 2 position (0-90 degrees, if pots installed)
  SW2/SW5 - servo 1 step clockwise/anti-clockwise (if no pots)
  SW3/SW4 - servo 2 step clockwise/anti-clockwise (if no pots)
================================================================================
"""
# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32
import BEAPER_Nano as beaper

import time

# --- Program Configuration ------------
POTS_INSTALLED = False                # Set True if RV1 and RV2 are installed

# --- Program Constants ----------------
STEP_DELAY    = 20                    # Main loop delay (ms)
ANGLE_STEP    = 2                     # Degrees per button press step

# --- Program Variables ----------------
servo1_angle = 45                     # Current angle for servo 1 (degrees)
servo2_angle = 45                     # Current angle for servo 2 (degrees)


# --- Main Program ---------------------

beaper.nano_led_on()
print("Servo Controller")

# Move both servos to centre position on startup
beaper.set_servo(beaper.SERVO1, servo1_angle)
beaper.set_servo(beaper.SERVO2, servo2_angle)
print("Servos at centre (45 degrees)")

if POTS_INSTALLED:
  print("RV1: servo 1 position   RV2: servo 2 position")
else:
  print("SW2/SW5: servo 1 anti-CW/CW   SW3/SW4: servo 2 anti-CW/CW")

while True:
  SW2_pressed = beaper.SW2.value() == 0
  SW3_pressed = beaper.SW3.value() == 0
  SW4_pressed = beaper.SW4.value() == 0
  SW5_pressed = beaper.SW5.value() == 0
  
  if POTS_INSTALLED:
    servo1_angle = int(beaper.RV1_level() * 90 / 65535)
    servo2_angle = int(beaper.RV2_level() * 90 / 65535)
  else:
    if SW2_pressed:
      servo1_angle -= ANGLE_STEP
    elif SW5_pressed:
      servo1_angle += ANGLE_STEP
    if SW3_pressed:
      servo2_angle -= ANGLE_STEP
    elif SW4_pressed:
      servo2_angle += ANGLE_STEP

  servo1_angle = beaper.set_servo(beaper.SERVO1, servo1_angle)
  servo2_angle = beaper.set_servo(beaper.SERVO2, servo2_angle)
  print("S1:", servo1_angle, "deg   S2:", servo2_angle, "deg", end="\r")

  time.sleep_ms(STEP_DELAY)


"""
Extension Activities

1.  Open BEAPER_Nano.py and read the 'set_servo()' function and
    the three constants above it: 'SERVO_MIN_US', 'SERVO_MAX_US',
    and 'SERVO_RANGE'.

    Trace through 'set_servo()' with angle=0, angle=45, and
    angle=90. What pulse width in microseconds does each produce?
    Do the results match the 1.0ms, 1.5ms, and 2.0ms values
    described in the header above?

    The function uses 'servo.duty_ns()' rather than
    'servo.duty_u16()'. Why is expressing the pulse in nanoseconds
    more direct for servo control than expressing it as a duty
    cycle percentage? At 50 Hz (20ms period), what duty_u16 value
    would correspond to a 1.5ms pulse - calculate it and compare
    with the 4915 initialisation value used in the board module.

    Try calling 'beaper.set_servo(beaper.SERVO1, 0)',
    'beaper.set_servo(beaper.SERVO1, 45)', and
    'beaper.set_servo(beaper.SERVO1, 90)' directly from the
    console while the program is stopped. Observe the servo
    position for each call and confirm it matches the calculated
    pulse widths.

2.  Write a 'sweep(servo_fn, start_angle, end_angle, step_ms)'
    function that moves a servo smoothly from start_angle to
    end_angle, pausing step_ms milliseconds between each degree
    of movement. Use it to create a scanning motion - sweep from
    0 to 90 and back continuously.

    Note that 'sweep()' uses 'time.sleep_ms()' internally, which
    blocks the main loop for its full duration. How would you
    allow two servos to sweep simultaneously? This is the problem
    Activity 11's non-blocking timing solves.

3.  Implement a servo sequencer: define a sequence of (angle,
    dwell_ms) pairs representing positions and how long to hold
    each one. Write a function that steps through the sequence,
    moving the servo to each angle and waiting the specified time.

    Example sequence for a simple pick-and-place arm:

  sequence = (
    (10, 800),   # Move to pick position
    (60, 1500),  # Move to carry position
    (90, 400),   # Move to place position
    (60, 500),   # Return to carry position
  )

    The following code reads the sequence, sets SERVO1's position,
    and waits for the dwell time:

  for step in sequence:
    beaper.set_servo(beaper.SERVO1, step[0])  # servo position
    time.sleep_ms(step[1])  # delay for servo dwell time

4.  Research the pulse width range for the specific servo you are
    using. Many servos accept a wider range than the standard
    1.0-2.0ms, allowing more than 90 degrees of travel. Look in
    BEAPER_Nano.py for constants that set the servo pulse width
    limits and try adjusting them. What happens if the pulse width
    exceeds the servo's mechanical limits?

"""