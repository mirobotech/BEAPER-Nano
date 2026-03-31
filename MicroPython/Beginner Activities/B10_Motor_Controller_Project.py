"""
================================================================================
Project: Motor Controller [B10_Motor_Controller_Project.py]
March 31, 2026

Platform: mirobo.tech BEAPER Nano circuit (robot configuration)
Requires: BEAPER_Nano.py board module file.

Before starting this project, re-read GE1, GE2, GE3,
and GE4 from Activity 10: Analog Output.

IMPORTANT HARDWARE NOTES:
  The H-bridge motor driver outputs share pins with LED2-LED5.
  Using this skeleton will prevent LED2-LED5 from being used as
  status indicators - the PWM objects created here replace the
  LED Pin objects from the board module on those pins.

  Motor wiring (standard robot configuration):
    M1A / M1B - Left motor
    M2A / M2B - Right motor

  The H-bridge driver requires motor power to be connected
  separately from the logic supply. Ensure motor power is
  connected before running motors. Never exceed the driver
  chip's rated current per channel.

  Always test motor direction at low speed (25%) before
  increasing to full speed. If a motor runs the wrong direction,
  swap its two wires at the motor terminal.

This project configures both H-bridge channels as PWM outputs
and provides a left_motor() speed control function and right_motor()
and motors() function skeletons for you to finish implementing.
Speed is given as a percentage from -100 (full reverse) to 100
(full forward), with 0 as stopped.

Controls:
  RV1 - left motor speed  (clockwise = reverse, anti-clockwise = forward)
  RV2 - right motor speed (anti-clockwise = reverse, clockwise = forward)
  SW5 - enable/disable drive (safety enable switch)
================================================================================
"""
# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32
import BEAPER_Nano as beaper

from machine import Pin, PWM
import time

# --- Program Constants ----------------
STEP_DELAY = 20                  # Main loop delay (ms)
MOTOR_FREQ = 1000                # PWM frequency for motors (Hz)
DEADBAND   = 5                   # Speed % below which motor is stopped
MAX_SPEED  = 100                 # Maximum speed percentage

# --- Motor PWM objects ----------------
# These replace LED2-LED5 Pin objects with PWM-capable motor drive outputs.
# A higher PWM frequency is used for motors than for LEDs - see Analysis Q3.
M1A_PWM = PWM(Pin(beaper.LED2_PIN), freq=MOTOR_FREQ, duty_u16=0)
M1B_PWM = PWM(Pin(beaper.LED3_PIN), freq=MOTOR_FREQ, duty_u16=0)
M2A_PWM = PWM(Pin(beaper.LED4_PIN), freq=MOTOR_FREQ, duty_u16=0)
M2B_PWM = PWM(Pin(beaper.LED5_PIN), freq=MOTOR_FREQ, duty_u16=0)

# --- Program Variables ----------------
drive_enabled = False                 # Safety enable flag


# --- Program Functions ----------------

def left_motor(speed):
  # Drive the left motor at the given speed (-100 to 100 percent).
  # Positive speed drives forward (M1A active, M1B LOW).
  # Negative speed drives reverse (M1B active, M1A LOW).
  # Zero or within deadband stops the motor (both outputs LOW).
  speed = max(-MAX_SPEED, min(MAX_SPEED, speed))
  if abs(speed) < DEADBAND:
    M1A_PWM.duty_u16(0)
    M1B_PWM.duty_u16(0)
    return
  duty = int(abs(speed) * 65535 / 100)
  if speed > 0:
    M1A_PWM.duty_u16(duty)
    M1B_PWM.duty_u16(0)
  else:
    M1A_PWM.duty_u16(0)
    M1B_PWM.duty_u16(duty)

def right_motor(speed):
  # Drive the right motor at the given speed (-100 to 100 percent).
  # Positive speed drives forward (M2B active, M2A LOW).
  # Negative speed drives reverse (M2A active, M2B LOW).
  # TODO: implement using M2A_PWM and M2B_PWM, following left_motor() above
  pass

def motors(left_speed, right_speed):
  # Drive both motors at the given speeds.
  # TODO: call left_motor() and right_motor() with their respective speeds
  pass

def pot_to_speed(pot_value):
  # Convert a potentiometer reading (0-65535) to a motor speed (-100 to 100).
  # The centre of the pot range maps to 0 (stopped).
  # Values within DEADBAND percent of centre return 0.
  speed = int((pot_value - 32767) * 100 / 32767)
  speed = max(-MAX_SPEED, min(MAX_SPEED, speed))
  if abs(speed) < DEADBAND:
    return 0
  return speed


# --- Main Program ---------------------

beaper.nano_led_on()
motors(0, 0)
print("Motor Controller")
print("SW5: enable/disable drive   RV1: left speed   RV2: right speed")
print("Drive DISABLED - press SW5 to enable")

while True:
  # SW5 toggles drive enable (press and release to toggle)
  if beaper.SW5.value() == 0:
    drive_enabled = not drive_enabled
    if drive_enabled:
      beaper.nano_led_on()
      print("Drive ENABLED")
    else:
      motors(0, 0)
      beaper.nano_led_off()
      print("Drive DISABLED")
    while beaper.SW5.value() == 0:     # Wait for SW5 release
      pass

  if drive_enabled:
    left_speed  = pot_to_speed(beaper.RV1_level())
    # TODO: read RV2 and convert to right_speed using pot_to_speed()
    right_speed = 0
    motors(left_speed, right_speed)
    print("L:", left_speed, "  R:", right_speed, end="\r")
  else:
    motors(0, 0)

  time.sleep_ms(STEP_DELAY)


"""
Extension Activities

1.  Note: BEAPER Nano will need to be powered using either a power
    supply or a battery pack connected to the CON1 screw terminal
    strip to run the motors. Test the program with one motor
    connected to the left motor terminals. Finish the right_motor()
    and motors() functions in the program and test them to make
    sure they work.

2.  Add acceleration limiting so that motor speed changes gradually
    rather than jumping to the target immediately. Store the current
    speed for each motor in a variable and move it toward the target
    by a fixed step per loop iteration. What step size gives a
    natural-feeling acceleration without making the robot feel
    sluggish?

3.  Implement a 'drive_timed(left_speed, right_speed, duration_ms)'
    function that drives both motors at the given speeds for a set
    duration, then stops. Use it to create a simple repeatable
    movement sequence - forward, turn, forward, stop.

    Note that 'drive_timed()' blocks the main loop for its full
    duration using 'time.sleep_ms()'. Activity 11 introduces
    non-blocking timing that allows other actions to continue
    during a timed movement.

4.  Four-pump or four-fan controller: the H-bridge driver can
    control four independent single-direction loads (pumps, fans)
    by wiring each load between one motor output pin and ground.
    Reconfigure the motor PWM objects for the type of load that
    will be controlled:

  PUMP1_PWM = PWM(Pin(beaper.LED2_PIN), freq=1000, duty_u16=0)
  PUMP2_PWM = PWM(Pin(beaper.LED3_PIN), freq=1000, duty_u16=0)
  PUMP3_PWM = PWM(Pin(beaper.LED4_PIN), freq=1000, duty_u16=0)
  PUMP4_PWM = PWM(Pin(beaper.LED5_PIN), freq=1000, duty_u16=0)

    Use SW2-SW5 to enable each pump independently and RV1 to set
    a shared duty cycle (flow rate). Add a maximum run time per
    pump to prevent overheating or as a safety measure to prevent
    a storage tank overflow.

"""