"""
BEAPER Nano I/O Test project
January 15, 2025

Functional test of all on-board BEAPER Nano I/O devices.

This program includes a SONAR range function designed to test an
optional 3.3V HC-SR04P ultrasonic distance sensor module plugged
into headers H1-H4, as well as servo position functions to control
two servos connected to H5 and H6 from potentiometers RV1 and RV2.

The program displays the SONAR range and analog input values from
the ambient light sensor, temperature sensor and both on-board
potentiometers. Set the jumpers to select the environmental inputs
(labelled Enviro.) on the BEAPER Nano PCB.

See the https://mirobo.tech/beaper webpage for additional BEAPER
Nano starter progams and beginner programming activities.
"""

# Import machine and time functions
from machine import Pin, PWM, ADC
import time

# Built-in Arduino Nano ESP32 LEDs
LED_BUILTIN = Pin(48, Pin.OUT, value = 0)   # Active High
LED_BLUE = Pin(45, Pin.OUT, value = 1)      # Active Low
LED_GREEN = Pin(0, Pin.OUT, value = 1)      # Active Low
LED_RED = Pin(46, Pin.OUT, value = 0)       # Active Low

# BEAPER Nano Educational Starter I/O devices
SW2 = Pin(44, Pin.IN, Pin.PULL_UP)
SW3 = Pin(43, Pin.IN, Pin.PULL_UP)
SW4 = Pin(5, Pin.IN, Pin.PULL_UP)
SW5 = Pin(6, Pin.IN, Pin.PULL_UP)
LED2 = M1A = Pin(7, Pin.OUT)
LED3 = M1B = Pin(8, Pin.OUT)
LED4 = Pin(9, Pin.OUT)
LED5 = Pin(10, Pin.OUT)
BEEPER = PWM(Pin(17), freq = 1000, duty_u16 = 0)

# BEAPER Nano analog input devices
Q1 = Q4 = ADC(1, atten = ADC.ATTN_11DB)
Q2 = U4 = ADC(2, atten = ADC.ATTN_11DB)
Q3 = RV1 = ADC(3, atten = ADC.ATTN_11DB)
VDIV = RV2 = ADC(4, atten = ADC.ATTN_11DB)

# BEAPER Nano 3.3V analog/digital I/O (shared with 5V digital outputs)
# H1IN = Pin(11, Pin.IN, Pin.PULL_UP)
# H1OUT = H5OUT = Pin(11, Pin.OUT)
SERVO1 = PWM(Pin(11), freq=50, duty_u16=4916)
# H2IN = Pin(13, Pin.IN, Pin.PULL_UP)
H2OUT = TRIG = H7OUT = Pin(13, Pin.OUT)
H3IN = ECHO = Pin(14 , Pin.IN, Pin.PULL_UP)
# H3OUT = H8OUT = Pin(14, Pin.OUT)
# H4IN = Pin(12 , Pin.IN, Pin.PULL_UP)
# H4OUT = H6OUT = Pin(12 , Pin.OUT)
SERVO2 = PWM(Pin(12), freq=50, duty_u16=4916)

# Tone functions. The tone() function creates a tone using a PWM output. The
# tone plays until stopped using the noTone() function, or for the duration of
# time specified (optional, in seconds, other operations are blockd for duration). 
def tone(frequency, duration=None):
    BEEPER.freq(frequency)
    BEEPER.duty_u16(32768)
    if duration is not None:
        time.sleep(duration)
        noTone()

# Stops the tone. Specifying an optional duration pauses for the duration of
# time specified (in seconds, other operations for duration).
def noTone(duration=None):
    BEEPER.duty_u16(0)
    if duration is not None:
        time.sleep(duration)

# Map function. Map value in input range to output range.
def map(value, in_min, in_max, out_min, out_max):
    return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

# Servo position functions. Creates servo pulses my mapping degree to PWM pulsewidth.
# Un-comment appropriate duty_u16 line to map input values between 0-180 degrees to pulse length
def servo1_position(deg):
    SERVO1.duty_u16(map(deg, 0, 90, 3277, 6554))  # 1-2ms pulses for a 90 deg. servo
    # SERVO1.duty_u16(map(deg, 0, 180, 3277, 6554))  # 1-2ms pulses for 180 deg. input to a 90 deg. servo
    # SERVO1.duty_u16(map(deg, 0, 180, 1782, 8192))  # 544us-2500us pulses for a 180 deg. servo
    # SERVO1.duty_u16(map(deg, 0, 180, 1638, 8192))  # 500us-2500us pulses for a 180 deg. servo

def servo2_position(deg):
    SERVO2.duty_u16(map(deg, 0, 90, 3277, 6554))  # 1-2ms pulses for a 90 deg. servo
    # SERVO2.duty_u16(map(deg, 0, 180, 3277, 6554))  # 1-2ms pulses for 180 deg. input to a 90 deg. servo
    # SERVO2.duty_u16(map(deg, 0, 180, 1782, 8192))  # 544us-2500us pulses for a 180 deg. servo
    # SERVO2.duty_u16(map(deg, 0, 180, 1638, 8192))  # 500us-2500us pulses for a 180 deg. servo

# SONAR range function with maximum range limit and error checking.
# Returns the range of the closest target in cm. The 'max' parameter limits
# the search range to objects no farther than 'max' (cm). The function returns
# -1  if previous ranging operation is still in progress, 0 if no target is
# found within the specified max range, or the range of the closest target in cm.
# Example application:
# range_cm = sonar_range(100)   # Find closest target within 100 cm
def sonar_range(max):
    # Check if previous ECHO has finished
    if ECHO.value() == 1:
        return -1   # ECHO in progress, can't trigger until 10ms after ECHO ends
    # Create TRIG pulse
    TRIG.value(1)
    time.sleep_us(10)
    TRIG.value(0)
    # HC-SR04P (3.3V-capable module, also labelled as RCWL-9610A 2022) delays for 
    # 2320us after TRIG pulse and before ECHO starts. Uncomment the lines below to
    # enable max measurement range of less than 40cm
    # pulse_duration = time_pulse_us(ECHO, 0, 2500)
    # if pulse_duration < 0:
    #     return pulse_duration
    
    # Wait for ECHO and time ECHO pulse. Set time-out to max range (min. 40 cm)
    pulse_duration = time_pulse_us(ECHO, 1, (max + 1) * 58)
    if pulse_duration < 0:
        return 0                        # Out of range - return 0
    else:
        return pulse_duration / 58    # Return range in cm 

# LED on
LED_BUILTIN.value(1)

# Start-up sound
tone(1000,0.1)

print("Starting BEAPER Nano")
print("SW2 - LED sequence and tones")
print("SW3 - light Arduino Nano ESP32 red LED")
print("SW4 - light Arduino Nano ESP32 green LED")
print("SW5 - light Arduino Nano ESP32 blue LED")
time.sleep(1)

servo_timer = time.ticks_ms()
sonar_timer = time.ticks_ms()

while True:
    # Chase LEDs
    if SW2.value() == 0:
        LED2.value(1)
        tone(523)
        time.sleep(0.1)
        LED3.value(1)
        tone(659)
        time.sleep(0.1)
        LED4.value(1)
        tone(784)
        time.sleep(0.1)
        LED5.value(1)
        tone(1047)
        time.sleep(0.1)
        
        LED2.value(0)
        tone(2093)
        time.sleep(0.1)
        LED3.value(0)
        tone(4186)
        time.sleep(0.1)
        LED4.value(0)
        tone(8372)
        time.sleep(0.1)
        LED5.value(0)
        noTone()
        time.sleep(0.1)

    if SW3.value() == 0:
        LED_RED.value(0)
    else:
        LED_RED.value(1)
    
    if SW4.value() == 0:
        LED_GREEN.value(0)
    else:
        LED_GREEN.value(1)
    
    if SW5.value() == 0:
        LED_BLUE.value(0)
    else:
        LED_BLUE.value(1)
    
    if time.ticks_diff(time.ticks_ms(), servo_timer) > 20:
        servo_timer = time.ticks_ms()
        # Update servos
        rv1_pos = RV1.read_u16()
        rv1_angle = map(rv1_pos, 0, 65535, 0, 90)
        servo1_position(rv1_angle)
        rv2_pos = RV2.read_u16()
        rv2_angle = map(rv2_pos, 0, 65535, 0, 90)
        servo2_position(rv2_angle)

    if time.ticks_diff(time.ticks_ms(), sonar_timer) > 500:
        sonar_timer = time.ticks_ms()
        # Get and print SONAR range
        range_cm = sonar_range(100)
        print("Range:", int(range_cm), "cm")
        # Read and print analog input levels
        lightLevel = Q4.read_u16()
        rawTemp = U4.read_u16()
        print("Light level: ", lightLevel)
        print("Temp level: ", rawTemp)
        print("RV1 position: ", rv1_pos)
        print("RV2 position: ", rv2_pos)
        print("")

