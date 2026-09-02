# ================================================================================
# VL53L4CD test program [VL53L4CD_test.py]
# Version: 1.1
# Updated: August 31, 2026
#
# Platform: mirobo.tech BEAPER Nano circuit
# Requires: BEAPER_Nano.py board support module file
#           VL53L4CD.py non-blocking VL53L4CD driver module
#
# Tests VL53L4CD ToF (Time of Flight) module ranging and acqusition time.
# ================================================================================

# MicroPython Modules
from machine import I2C
import time

# BEAPER Nano board support module
import BEAPER_Nano as beaper

beaper.nano_led_on()  # Turn LED on as status indicator

# Program variables
range_mm = 0
start_time_us = 0
tof_time_us = 0

# Configure VL53L4CD module
from VL53L4CD import VL53L4CD
tof = VL53L4CD(beaper.QWIIC)
# tof.set_range_timing(20)  # 10ms (less accurate) -> 200ms, default is 50ms.

start_time_us = time.ticks_us()
tof.start_ranging()

while True:
    if tof.data_ready():
        result = tof.get_result()
        tof.clear_interrupt()
        tof_time_us = time.ticks_diff(time.ticks_us(), start_time_us)
        start_time_us = time.ticks_us()
        
        print(f"Range: {result['distance_mm']:4d}mm  status: {result['range_status']}")
        print(f"Ranging time: {tof_time_us:d}us")
        print()

    # Do other processing here
  
    time.sleep_ms(1)
            


