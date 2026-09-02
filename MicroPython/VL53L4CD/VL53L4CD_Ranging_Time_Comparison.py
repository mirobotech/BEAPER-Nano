# ==============================================================================
# VL53L4CD Ranging Time Comparison [VL53L4CD_Ranging_Time_Comparison.py]
# Version: 1.2
# Updated: September 1, 2026
#
# Platform: mirobo.tech BEAPER Nano
# Requires: BEAPER_Nano.py board support module file
#           VL53L4CD.py driver module
#
# Use the controls to select a ranging time:
#   SW3 - select a shorter ranging time
#   SW4 - select a longer ranging time
#
# Keep the sensor and target stationary while comparing settings.
# ==============================================================================

import time

import BEAPER_Nano as beaper
from VL53L4CD import VL53L4CD

# Ranging-time settings use a 1-2-5 sequence.
RANGE_TIMES_MS = (10, 20, 50, 100, 200)
range_time_index = 2           # Start at 50 ms

WINDOW_SIZE = 20               # Number of valid readings retained
DISPLAY_INTERVAL_MS = 250      # Limit REPL output rate

# Set this to the measured target distance to calculate accuracy.
# Leave it as None to display repeatability statistics only.
REFERENCE_DISTANCE_MM = None
# REFERENCE_DISTANCE_MM = 100


def apply_range_time(sensor, range_time_ms):
  # Stop ranging before changing the timing budget.
  sensor.stop_ranging()
  sensor.clear_interrupt()
  sensor.set_range_timing(range_time_ms)
  sensor.start_ranging()


def add_reading(readings, distance_mm):
  # Add a new reading and keep only the newest WINDOW_SIZE readings.
  readings.append(distance_mm)

  if len(readings) > WINDOW_SIZE:
    readings.pop(0)


def calculate_sigma(readings):
  # Return the sample standard deviation of the rolling readings.
  if len(readings) < 2:
    return 0.0

  mean = sum(readings) / len(readings)
  variance = sum((reading - mean) ** 2 for reading in readings) / (len(readings) - 1)
  return variance ** 0.5


def display_results(result, readings, measured_period_ms, invalid_count):
  distance_mm = result["distance_mm"]
  sensor_sigma_mm = result["sigma_mm"]
  number_of_spad = result["number_of_spad"]

  minimum_mm = min(readings)
  maximum_mm = max(readings)
  average_mm = sum(readings) / len(readings)
  spread_mm = maximum_mm - minimum_mm
  measured_sigma_mm = calculate_sigma(readings)

  print(
    f"Timing: {RANGE_TIMES_MS[range_time_index]:3d} ms     | "
    f"Period: {measured_period_ms:6.1f} ms           | "
    f"Samples: {len(readings):2d}/{WINDOW_SIZE:2d}"
  )

  print(
    f"Range: {distance_mm:4d} mm     | "
    f"Min: {minimum_mm:4d}   | "
    f"Max: {maximum_mm:4d}     | "
    f"Spread: {spread_mm:3d} mm"
  )

  print(
    f"Mean: {average_mm:7.1f} mm   | "
    f"Measured +/- sigma: {measured_sigma_mm:4.1f} mm"
  )

  print(
    f"SPADs: {number_of_spad:3d}         | "
    f"Sensor +/- sigma: {sensor_sigma_mm:4d} mm   | "
    f"Invalid: {invalid_count}"
  )

  if REFERENCE_DISTANCE_MM is not None:
    current_error_mm = distance_mm - REFERENCE_DISTANCE_MM
    mean_error_mm = average_mm - REFERENCE_DISTANCE_MM
    suggested_offset_mm = -round(mean_error_mm)

    print(
      f"Reference: {REFERENCE_DISTANCE_MM:4d} mm | "
      f"Current error: {current_error_mm:+5d} mm     | "
      f"Mean error: {mean_error_mm:+6.1f} mm"
    )

    if len(readings) == WINDOW_SIZE:
      print(
        f"Suggested offset correction: {suggested_offset_mm:+d} mm  "
        f"->  tof.set_offset({suggested_offset_mm})"
      )

  print()


# Turn on the Nano status LED.
beaper.nano_led_on()

# Configure the sensor.
tof = VL53L4CD(beaper.QWIIC)
if REFERENCE_DISTANCE_MM is not None:
  tof.set_offset(0)  # Clear the factory offset so raw error can be measured for calibration
apply_range_time(tof, RANGE_TIMES_MS[range_time_index])

# Rolling measurement data.
readings = []
invalid_count = 0

# Button edge-detection variables.
previous_sw3_pressed = False
previous_sw4_pressed = False

# Timing variables.
last_result_time_us = time.ticks_us()
last_display_time_ms = time.ticks_ms()

print("VL53L4CD ranging-time comparison")
print("SW3 = shorter time, SW4 = longer time")
print()

while True:
  # Pushbuttons are active-LOW.
  sw3_pressed = beaper.SW3.value() == 0
  sw4_pressed = beaper.SW4.value() == 0

  # SW3 selects the next shorter ranging time.
  if sw3_pressed and not previous_sw3_pressed:
    if range_time_index > 0:
      range_time_index -= 1
      apply_range_time(tof, RANGE_TIMES_MS[range_time_index])

      readings = []
      invalid_count = 0
      last_result_time_us = time.ticks_us()
      last_display_time_ms = time.ticks_ms()

      print(f"Ranging time changed to {RANGE_TIMES_MS[range_time_index]} ms")
      print()

  # SW4 selects the next longer ranging time.
  if sw4_pressed and not previous_sw4_pressed:
    if range_time_index < len(RANGE_TIMES_MS) - 1:
      range_time_index += 1
      apply_range_time(tof, RANGE_TIMES_MS[range_time_index])

      readings = []
      invalid_count = 0
      last_result_time_us = time.ticks_us()
      last_display_time_ms = time.ticks_ms()

      print(f"Ranging time changed to {RANGE_TIMES_MS[range_time_index]} ms")
      print()

  previous_sw3_pressed = sw3_pressed
  previous_sw4_pressed = sw4_pressed

  # Read each new sensor result without blocking button operation.
  if tof.data_ready():
    result = tof.get_result()
    tof.clear_interrupt()

    now_us = time.ticks_us()
    measured_period_ms = time.ticks_diff(now_us, last_result_time_us) / 1000
    last_result_time_us = now_us

    # Only valid readings are included in the rolling statistics.
    if result["range_status"] == 0:
      add_reading(readings, result["distance_mm"])

      now_ms = time.ticks_ms()
      display_due = (
        len(readings) == 1 or
        time.ticks_diff(now_ms, last_display_time_ms) >= DISPLAY_INTERVAL_MS
      )

      if display_due:
        display_results(result, readings, measured_period_ms, invalid_count)
        last_display_time_ms = now_ms

    else:
      invalid_count += 1

      # Limit invalid-reading messages to the same display interval.
      now_ms = time.ticks_ms()
      if time.ticks_diff(now_ms, last_display_time_ms) >= DISPLAY_INTERVAL_MS:
        print(
          f"Invalid reading | "
          f"status: {result['range_status']} | "
          f"distance: {result['distance_mm']} mm | "
          f"Invalid count: {invalid_count}"
        )
        print()
        last_display_time_ms = now_ms

  time.sleep_ms(1)