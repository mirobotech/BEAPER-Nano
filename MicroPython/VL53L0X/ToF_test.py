"""
================================================================================
ToF_test.py
June 17, 2026

Platform: mirobo.tech BEAPER Nano circuit
Requires: BEAPER_Nano.py board support module file
          vl53l0x_nb.py non-blocking VL53L0X driver module

Tests VL53L0X ToF (Time of Flight) module ranging and acqusition time.
================================================================================
"""

# MicroPython Modules
from machine import I2C
import time

# BEAPER Nano support module
import BEAPER_Nano as beaper

range_mm = 0
start_time_us = 0
tof_time_us = 0

beaper.nano_led_on()

# Configure VL53LL0X module
from vl53l0x_nb import VL53L0X
tof = VL53L0X(beaper.QWIIC)

start_time_us = time.ticks_us()
tof.start_range_request()

while True:
  if tof.reading_available():
    range_mm = tof.get_range_value()
    tof_time_us = time.ticks_diff(time.ticks_us(), start_time_us)
    start_time_us = time.ticks_us()
    tof.start_range_request()
    
    print(f"{range_mm:d}mm")
    print(f"Ranging time: {tof_time_us:d}us")

  time.sleep_ms(1)

