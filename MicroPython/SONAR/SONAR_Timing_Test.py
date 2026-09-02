# ==============================================================================
# SONAR_Timing_Test.py
# Version: 1.1
# Updated: September 2, 2026
#
# Platform: mirobo.tech BEAPER Nano circuit
# Requires: BEAPER_Nano.py board support module file
#
# Shows SONAR range, TRIG -> ECHO delay, ECHO time, and total ranging time.
# ==============================================================================

from machine import I2C
import time

# BEAPER Nano support module
import BEAPER_Nano as beaper

# Program Variables
sonar_range_mm = 0
sonar_time_us = 0

# Start SONAR ranging and time both the TRIG -> ECHO delay and the
# ECHO pulse width separately for display.
def sonar_range_timing(_timeout_us=35000):
    # Returns (trig_time_us, echo_time_us), or (-1, 0) if ECHO never
    # starts, or (trig_time_us, -1) if ECHO never ends
    beaper.SONAR_TRIG.value(1)
    time.sleep_us(10)
    beaper.SONAR_TRIG.value(0)

    trig_start = time.ticks_us()
    while beaper.SONAR_ECHO.value() == 0:
        if time.ticks_diff(time.ticks_us(), trig_start) > _timeout_us:
            return -1, 0
    echo_start = time.ticks_us()
    trig_time_us = time.ticks_diff(echo_start, trig_start)

    while beaper.SONAR_ECHO.value() == 1:
        if time.ticks_diff(time.ticks_us(), echo_start) > _timeout_us:
            return trig_time_us, -1
    echo_end = time.ticks_us()
    echo_time_us = time.ticks_diff(echo_end, echo_start)

    return trig_time_us, echo_time_us
    
    
# Main program start
beaper.nano_led_on()

while True:
    # Measure time to acquire SONAR range and convert range
    trig_time_us, echo_time_us = sonar_range_timing()
    if trig_time_us < 0 or echo_time_us < 0:
        # ECHO never started, or never ended - skip this update
        time.sleep_ms(50)
        continue
    sonar_range_mm = int(echo_time_us / 5.82)    # Calculate distance in mm
    sonar_time_us = trig_time_us + echo_time_us  # Total ranging time
    
    # Print SONAR distance and timing
    print(f"SONAR range: {sonar_range_mm:4d}mm")
    print(f"TRIG delay: {trig_time_us/1000:.3f}ms")
    print(f"ECHO pulse: {echo_time_us/1000:.3f}ms")
    print(f"Total time: {sonar_time_us/1000:.3f}ms")
    print("")

    time.sleep_ms(200)