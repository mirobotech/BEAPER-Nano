"""
================================================================================
SONAR_Timing_Test.py
May 4, 2026

Platform: mirobo.tech BEAPER Nano circuit
Requires: BEAPER_Nano.py board support module file

Shows SONAR range, TRIG -> ECHO delay, and total range time.
================================================================================
"""

# --- MicroPython Modules --------------
from machine import I2C
import time

# BEAPER Nano support module
import BEAPER_Nano as beaper

# --- Program Variables ----------------
sonar_range_mm = 0
sonar_time_us = 0

# --- Start SONAR ranging, time SONAR TRIG -> ECHO delay
def sonar_range_trig():
    # Make a 10us TRIG pulse and measure delay until ECHO starts.
    beaper.SONAR_TRIG.value(1)
    time.sleep_us(10)
    beaper.SONAR_TRIG.value(0)

    trig_start = time.ticks_us()
    while beaper.SONAR_ECHO.value() == 0:
        time.sleep_us(1)
    return time.ticks_diff(time.ticks_us(), trig_start)
    
# ---- Get SONAR range by timing ECHO pulse ---------------
def sonar_range_echo():
    # Measure ECHO pulse duration.
    echo_start = time.ticks_us()
    while beaper.SONAR_ECHO.value() == 1:
        time.sleep_us(1)
    return time.ticks_diff(time.ticks_us(), echo_start)
    
# --- Main program starts here
beaper.nano_led_on()

while True:
    # Measure times to acquire SONAR range and convert range
    trig_time_us = sonar_range_trig()  # Time delay from TRIG -> ECHO
    echo_time_us = sonar_range_echo()  # Time ECHO pulse
    sonar_range = echo_time_us / 58.2  # Range in cm
    sonar_time_us = trig_time_us + echo_time_us
    
    # Print SONAR ranging times and distance
    print(f"SONAR range: {sonar_range:.2f}cm")
    print(f"TRIG delay: {trig_time_us}us")
    print(f"Total time: {sonar_time_us}us")
    print("")

    time.sleep_ms(200)