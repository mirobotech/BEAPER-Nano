# ================================================================================
# VL53L4CD simple ranging program [VL53L4CD_simple.py]
# Version: 1.2
# Updated: September 2, 2026
#
# Platform: mirobo.tech BEAPER Nano circuit
# Requires: BEAPER_Nano.py board support module file
#           VL53L4CD.py non-blocking VL53L4CD driver module
#
# Tests VL53L4CD ToF (Time of Flight) module ranging and reading time using
# the simple get_range() function.
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
# tof.set_range_timing(35)  # 10ms (less accurate) -> 200ms, default is 50ms.

tof.start_ranging()

while True:
  start_time_us = time.ticks_us()
  dist = tof.get_range()
  tof_time_us = time.ticks_diff(time.ticks_us(), start_time_us)
        
  if dist >= 0:
    print(f"Distance: {dist}mm")
  elif dist == VL53L4CD.ERR_NO_TARGET:
    print("No target detected")
  elif dist == VL53L4CD.ERR_SIGMA_HIGH:
    print("Noisy measurement - try a longer timing budget")
  elif dist == VL53L4CD.ERR_WRAP_AROUND:
    print("Target may be beyond sensor range")
  else:   # ERR_HARDWARE
    print("VL53L4CD sensor fault")

  print(f"Ranging time: {tof.get_range_timing()[0]}ms")
  print(f"Read time: {tof_time_us:4d}us")
  print()

  time.sleep_ms(100)
            


