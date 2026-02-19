"""
BEAPER_Nano.py
February 18, 2026

Board support module for the mirobo.tech BEAPER Nano circuit.

This module configures Arduino Nano ESP32's GPIO pins for BEAPER
Nano's on-board circuits and provides simple helper functions to
enable beginners to focus on programming concepts first.

Before getting started with it you should know:
- nothing here is hidden, or * magic *, or requires special libraries
- the functions are just normal Python code to help you start learning
- you're encouraged to modify the code to make it work better for you!

BEAPER Nano hardware notes:
- Buttons use internal pull-up resistors (so pressed == 0)
- LEDs and motor driver inputs share I/O pins
- Headers H1-H4 and H5-H8 share I/O pins (so much I/O, too few pins!)
- Analog jumpers on BEAPER Nano must be set to connect sensors to pins:
  - Enviro. position selects sensors Q4, U4, and pots RV1 and RV2
  - Robot position selects floor/line phototransistors Q1, Q2, Q3,
    and voltage divider resistor circuit (VDIV)
"""

import machine
from machine import Pin, ADC, PWM, I2C
import time

# ---------------------------------------------------------------------
# Arduino Nano ESP32 Module LEDs
# ---------------------------------------------------------------------

LED_BUILTIN = Pin(48, Pin.OUT)    # Used as GPIO48 and SPI SCK
LED_RGB_RED   = PWM(Pin(46), freq=1000, duty_u16=65535)  # Active LOW
LED_RGB_GREEN = PWM(Pin(0), freq=1000, duty_u16=65535)   # Active LOW
LED_RGB_BLUE  = PWM(Pin(45), freq=1000, duty_u16=65535)  # Active LOW

def nano_led_on():
  # Turn the Arduino Nano ESP32 on-board LED on.
  LED_BUILTIN.value(1)

def nano_led_off():
  # Turn the Arduino Nano ESP32 on-board LED off.
  LED_BUILTIN.value(0)

def nano_led_toggle():
  # Toggle the Arduino Nano ESP32 on-board LED.
  LED_BUILTIN.value(not LED_BUILTIN.value())

def nano_rgb_red(brightness):
  # Set the RGB LED red element to brightness (0 - 65535)
  LED_RGB_RED.duty_u16(65535 - brightness)

def nano_rgb_green(brightness):
  # Set the RGB LED green element to brightness (0 - 65535)
  LED_RGB_GREEN.duty_u16(65535 - brightness)

def nano_rgb_blue(brightness):
  # Set the RGB LED blue element to brightness (0 - 65535)
  LED_RGB_BLUE.duty_u16(65535 - brightness)


# ---------------------------------------------------------------------
# BEAPER Nano Pushbutton Switches
# ---------------------------------------------------------------------

# All pushbutton switches use internal pull-up resistors (active LOW)

SW2_PIN = const(44)  # SW2
SW3_PIN = const(43)  # SW3
SW4_PIN = const(5)   # SW4
SW5_PIN = const(6)   # SW5

SW2 = Pin(SW2_PIN, Pin.IN, Pin.PULL_UP)
SW3 = Pin(SW3_PIN, Pin.IN, Pin.PULL_UP)
SW4 = Pin(SW4_PIN, Pin.IN, Pin.PULL_UP)
SW5 = Pin(SW5_PIN, Pin.IN, Pin.PULL_UP)

def SW2_pressed():
  # Return True if pushbutton 2 is pressed.
  return SW2.value() == 0

def SW3_pressed():
  # Return True if pushbutton 3 is pressed.
  return SW3.value() == 0

def SW4_pressed():
  # Return True if pushbutton 4 is pressed.
  return SW4.value() == 0

def SW5_pressed():
  # Return True if pushbutton 5 is pressed.
  return SW5.value() == 0


# ---------------------------------------------------------------------
# BEAPER Nano LEDS
# ---------------------------------------------------------------------

# IMPORTANT: LED pins are shared with the motor controller. Using the
# LEDs while the the motors are active will affect motor behavior!

LED2_PIN = const(7)  # LED2 and Motor 1A (Motor 1 = left motor)
LED3_PIN = const(8)  # LED3 and Motor 1B
LED4_PIN = const(9)  # LED4 and Motor 2A (Motor 2 = right motor)
LED5_PIN = const(10) # LED5 and Motor 2B

LED2 = Pin(LED2_PIN, Pin.OUT)
LED3 = Pin(LED3_PIN, Pin.OUT)
LED4 = Pin(LED4_PIN, Pin.OUT)
LED5 = Pin(LED5_PIN, Pin.OUT)


# ---------------------------------------------------------------------
# BEAPER Nano Motor Controller
# ---------------------------------------------------------------------

# IMPORTANT: Motor controller is connected to LED pins! Using the
# LEDs while the the motors are active will affect motor behavior!

# NOTE: The forward and reverse directions of each motor are dependent
# on both program code and physical motor wiring connections on CON1.

M1A = LED2
M1B = LED3
M2A = LED4
M2B = LED5

def motors_stop():
  M1A.value(0)
  M1B.value(0)
  M2A.value(0)
  M2B.value(0)

def left_motor_forward():
  M1A.value(1)
  M1B.value(0)

def left_motor_reverse():
  M1A.value(0)
  M1B.value(1)

def left_motor_stop():
    M1A.value(0)
    M1B.value(0)

def right_motor_forward():
  M2A.value(0)
  M2B.value(1)  # Opposite of left_motor_forward()

def right_motor_reverse():
  M2A.value(1)  # Opposite of left_motor_reverse()
  M2B.value(0)

def right_motor_stop():
    M2A.value(0)
    M2B.value(0)


# ---------------------------------------------------------------------
# BEAPER Nano Piezo Buzzer (BEAPER's beeper!)
# ---------------------------------------------------------------------

# Generate tones using PWM (similar to Arduino tone() functions)

LS1_PIN = const(17)

LS1 = PWM(Pin(LS1_PIN), freq = 1000, duty_u16 = 0)

def tone(frequency, duration=None):
  # Start a tone at specified frequency (Hz), and stop the tone after
  # an optional duration (ms). Adding duration causes a blocking delay.
  LS1.freq(frequency)
  LS1.duty_u16(32768)
  if duration is not None:
    time.sleep_ms(duration)
    noTone()

def noTone(duration=None):
  # Stop the tone. Optionally pause (blocking) for the duration (ms). 
  LS1.duty_u16(0)
  if duration is not None:
    time.sleep_ms(duration)


# ---------------------------------------------------------------------
# BEAPER Nano Analog Inputs
# ---------------------------------------------------------------------

# IMPORTANT: On-board analog jumpers must be used to select analog devices.

ADC0_PIN = const(1)  # Ambient light sensor Q4 OR floor sensor Q1
ADC1_PIN = const(2)  # Temperature sensor U4 OR line sensor Q2
ADC2_PIN = const(3)  # Pot RV1 OR floor/line sensor Q3
ADC3_PIN = const(4)  # Pot RV2 OR battery divider circuit VDIV

# IMPORTANT: ADC4-7 are shared with headers H1-H4, H5-H8, I2C, and 
# ESP32-S3 has ADC additional limitations. For more details see:
# https://docs.arduino.cc/tutorials/nano-esp32/cheat-sheet/#pins
# ADC4_PIN = const(11) # Shared with H1, H5, and I2C SDA
# ADC5_PIN = const(12) # Shared with H4, H6, and I2C SCL
# ADC6_PIN = const(13) # Shared with H2 (SONAR TRIG) and H7
# ADC7_PIN = const(14) # Shared with H3 (SONAR ECHO) and H8

ADC0 = ADC(Pin(ADC0_PIN), atten = ADC.ATTN_11DB)
ADC1 = ADC(Pin(ADC1_PIN), atten = ADC.ATTN_11DB)
ADC2 = ADC(Pin(ADC2_PIN), atten = ADC.ATTN_11DB)
ADC3 = ADC(Pin(ADC3_PIN), atten = ADC.ATTN_11DB)
# ADC4 = ADC(Pin(ADC4_PIN), atten = ADC.ATTN_11DB)
# ADC5 = ADC(Pin(ADC5_PIN), atten = ADC.ATTN_11DB)
# ADC6 = ADC(Pin(ADC6_PIN), atten = ADC.ATTN_11DB)
# ADC7 = ADC(Pin(ADC7_PIN), atten = ADC.ATTN_11DB)

def light_level():
  # Read Q4 ambient light sensor value. Set JP1 to Enviro.
  return 65535-ADC0.read_u16() # Brighter -> higher values

def temp_level():
  # Read U4 analog temperature sensor value. Set JP2 to Enviro.
  return ADC1.read_u16()  # Warmer -> higher values

def Q1_level():
  # Read floor sensor Q1. Set JP1 to Robot.
  return 65535-ADC0.read_u16()  # Higher reflectivity -> higher values

def Q2_level():
  # Read line sensor Q2. Set JP2 to Robot.
  return 65535-ADC1.read_u16()  # Higher reflectivity -> higher values

def Q3_level():
  # Read floor/line sensor Q3. Set JP3 to Robot.
  return 65535-ADC2.read_u16()  # Higher reflectivity -> higher values

def RV1_level():
  # Read potentiometer RV1. Set JP3 to Enviro.
  return ADC2.read_u16()  # Clockwise -> higher values

def RV2_level():
  # Read potentiometer RV2. Set JP3 to Enviro.
  return ADC3.read_u16()  # Clockwise -> higher values

def VDIV_level():
  # Read VDIV voltage divider. Set JP3 to Robot.
  return ADC3.read_u16()


# ---------------------------------------------------------------------
# 3.3V I/O Headers H1-H4 (supports I2C and 3.3V HC-SR04P SONAR module)
# ---------------------------------------------------------------------

# Analog/digital I/O header (optional SONAR module shares H2 and H3)
# IMPORTANT: Headers H1-H4, headers H5-H8, and I2C/QWIIC connector J4
# share Arduino Nano ESP32 I/O pins. Plan header I/O carefully!

H1_PIN = const(11)  # H1 (I2C SDA)
H2_PIN = const(13)  # H2 (SONAR TRIG)
H3_PIN = const(14)  # H3 (SONAR ECHO)
H4_PIN = const(12)  # H4 (I2C SCL)


# QWIIC connector I2C bus initialization

I2C_ID = 0
SDA = H1_PIN
SCL = H4_PIN
QWIIC = I2C(id=I2C_ID, sda=SDA, scl=SCL)

# Ultrasonic SONAR distance measurement function

SONAR_TRIG = Pin(H2_PIN, Pin.OUT, value=0)
SONAR_ECHO = Pin(H3_PIN, Pin.IN)

def sonar_distance_cm(max=300):
  # Returns either:
  #  - distance (cm) to the closest target, up to max distance (cm)
  #  - 0 if no target is detected within max distance
  #  - error code (-1, -2) from the time_pulse_us() function
  #  - error code (-3) if a previous ECHO is still in progress

  if SONAR_ECHO.value() == 1:
    # Check if previous ECHO is in progress, return error if so
    return -3   # (wait 10ms after ECHO ends before re-triggering)
  
  # Create a TRIG pulse
  SONAR_TRIG.value(1)
  time.sleep_us(10)
  SONAR_TRIG.value(0)
  
  # Wait 2500us for ECHO pulse to start. Note: HC-SR04P (3.3V-capable
  # modules also labelled as RCWL-9610A 2022) delay for approximately
  # 2300us after the TRIG pulse ends and the ECHO pulse starts.
  
  duration = machine.time_pulse_us(SONAR_ECHO, 0, 2500)

  if duration < 0:
    # ECHO didn't start - return time_pulse_us() error (-2, -1)
    return duration
  
  # Time ECHO pulse. Set time-out value to max range.
  duration = machine.time_pulse_us(SONAR_ECHO, 1, (max + 1) * 58)
  if duration < 0:
    return 0    # Distance > max range
  
  # Calculate target distance in cm
  return duration / 58


# ---------------------------------------------------------------------
# 5V Digital Output Headers H5-H8 (supports up to 4 servos)
# ---------------------------------------------------------------------

# NOTE: Headers H5-H8 are 5V digital output only and share GPIO
# pins with 3.3V I/O headers H1-H4 and I2C/QWIIC connector!

# 5V Digital output headers (output only, designed for servos)
H5_PIN = H1_PIN
H6_PIN = H4_PIN
H7_PIN = H2_PIN
H8_PIN = H3_PIN

# IMPORTANT: Servo outputs are disabled by default. Disable I2C or
# SONAR pin configuration before enabling SERVOx pin configuration.
# SERVO1 = PWM(Pin(H5_PIN), freq=50, duty_u16=4916)
# SERVO2 = PWM(Pin(H6_PIN), freq=50, duty_u16=4916)
# SERVO3 = PWM(Pin(H7_PIN), freq=50, duty_u16=4916)
# SERVO4 = PWM(PIN(H8_PIN), freq=50, duty_u16=4916)

def SERVO1_angle(angle):
  """
  Set servo 1 to angle (0–90 degrees).
  
  90 degree servo pulses range from 1-2 ms. Servo pulse is created
  using PWM, so pulse length is derived from duty cycle of the frame:
  
  1ms pulse / 20ms frame * 65536 (16-bit PWM range) = 3276.8 (use 3277)
  2ms pulse / 20ms frame * 65536 = 6554
  
  Duty cycles from 3277 to 6554 correspond to 0-90 degrees of motion.
  """
  angle = max(0, min(90, 90-angle))
  duty = int(3277 + (angle / 90) * 3277)
  SERVO1.duty_u16(duty)

"""
def SERVO2_angle(angle):
  angle = max(0, min(90, 90-angle))
  duty = int(3277 + (angle / 90) * 3277)
  SERVO2.duty_u16(duty)

def SERVO3_angle(angle):
  angle = max(0, min(90, 90-angle))
  duty = int(3277 + (angle / 90) * 3277)
  SERVO3.duty_u16(duty)

def SERVO4_angle(angle):
  angle = max(0, min(90, 90-angle))
  duty = int(3277 + (angle / 90) * 3277)
  SERVO4.duty_u16(duty)
"""