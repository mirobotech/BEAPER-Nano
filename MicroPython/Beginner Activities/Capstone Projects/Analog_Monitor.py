"""
================================================================================
Capstone Project: Analog Sensor Monitor [BEAPER_Nano-Capstone_Analog_Monitor.py]
April 22, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPER_Nano.py board module file.

This skeleton provides a multi-sensor monitoring and control structure.
Adapt it to your application by:
  1. Configuring your analog and digital inputs in the SENSOR CONFIGURATION
     section and the read_sensors() function.
  2. Writing your condition logic in check_conditions().
  3. Configuring your outputs in the OUTPUT CONFIGURATION section and
     the apply_outputs() function.

Suggested applications:
  Greenhouse controller   - temperature, light, soil moisture sensors;
                            servo vent, motor fan, motor pump outputs
  Climate monitor         - temperature and humidity sensors;
                            LED indicators, alarm tone outputs
  Plant watering system   - soil moisture sensor, timer;
                            motor pump output, LED status indicators
  Environmental logger    - multiple analog sensors;
                            LED bar graph display, serial data output

On-board analog inputs available (set jumpers to Enviro. mode):
    beaper.light_level()   - Ambient light sensor Q4 (JP1)
    beaper.temp_level()    - Temperature sensor U4 (JP2)
    beaper.RV1_level()     - Potentiometer RV1 (JP3) - useful as a threshold knob
    beaper.RV2_level()     - Potentiometer RV2 (JP4) - useful as a threshold knob

External analog inputs available (each needs to be enabled/configured
  in the BEAPER_Nano.py board module):
    H1  - Sensor header with analog input, 3.3V, GND
    H2  - Sensor header with analog input, 3.3V, GND
    H3  - Sensor header with analog input, 3.3V, GND
    H4  - Sensor header with analog input, 3.3V, GND

Digital inputs available:
    beaper.SW2 to beaper.SW5  - Pushbuttons (active LOW, INPUT_PULLUP)
    beaper.H1 to beaper.H4    - Expansion headers (for external sensors/switches)

Analog outputs available:
    beaper.LS1             - Piezo speaker (tone() / noTone())
    beaper.LED2 to LED5    - LEDs (digital on/off or PWM brightness)
    Servo headers H5 to H8 - Servo position (set_servo())

Digital outputs available:
    beaper.LED2 to LED5    - LEDs (on/off)
    Headers H1 to H4       - 3.3V output headers
    Headers H5 to H8       - 5V output headers (shared with H1 - H4)

--------------------------------------------------------------------------------
Before you begin - complete your capstone plan using the preparation guide:
  1. Write a plain-English description of what your system monitors and
     what it controls, and under what conditions.
  2. List all inputs: sensor type, what it measures, acceptable range,
     and how often it needs to be read.
  3. List all outputs: what it drives, how it responds to sensor values,
     and whether it uses analog (PWM) or digital (on/off) control.
  4. Write your condition logic in plain language before coding it:
     e.g. "if temperature > HIGH_TEMP and fan is off: turn fan on"
  5. Write your testing plan: one test case per condition.
================================================================================
"""
# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32
import BEAPER_Nano as beaper

import time

# ==============================================================================
# SENSOR CONFIGURATION
# Name each sensor, its read interval, and its threshold values.
# Add one block per sensor your application requires.
# ==============================================================================

# --- Sensor 1: Temperature (example) -----------------------------------------
TEMP_READ_INTERVAL  = const(2000)   # Read every 2000 ms (temperature changes slowly)
TEMP_HIGH_THRESHOLD = 28            # Degrees C: above this, cooling output activates
TEMP_LOW_THRESHOLD  = 24            # Degrees C: below this, cooling output deactivates
                                    # (hysteresis gap prevents rapid on/off cycling)

# --- Sensor 2: Light (example) -----------------------------------------------
LIGHT_READ_INTERVAL  = const(500)   # Read every 500 ms (light can change quickly)
LIGHT_LOW_THRESHOLD  = 20000        # Below this (dark): lighting output activates
LIGHT_HIGH_THRESHOLD = 30000        # Above this (bright): lighting output deactivates

# --- Add your sensors here ---
# SENSOR_NAME_READ_INTERVAL  = const(1000)
# SENSOR_NAME_THRESHOLD      = value

# ==============================================================================
# OUTPUT CONFIGURATION
# Name each output and its behavior parameters.
# ==============================================================================

# --- Output 1: Cooling fan (example - motor on H9/H10) -----------------------
FAN_ON  = 1   # Motor output value when fan is running
FAN_OFF = 0   # Motor output value when fan is stopped

# --- Output 2: Status LED (example) ------------------------------------------
# Uses LED2 to indicate whether the system is in a normal or alert condition.

# --- Add your outputs here ---

# ==============================================================================
# LOOP TIMING
# ==============================================================================
LOOP_DELAY      = const(10)    # Main loop delay (ms) - keep at 10 or lower
                                # so timing intervals remain accurate
PRINT_INTERVAL  = const(5000)  # Print sensor summary every 5000 ms

# ==============================================================================
# PROGRAM VARIABLES
# One 'last_read' timestamp per sensor, one 'last_print' for console output.
# One current value variable per sensor.
# One state variable per output that needs to remember its current state.
# ==============================================================================

# Sensor timestamps
last_temp_read   = 0
last_light_read  = 0
# last_SENSORNAME_read = 0         # Add one per sensor

# Current sensor values
temp_c           = 0.0            # Current temperature in degrees C
light_level_val  = 0              # Current light level (raw ADC)
# sensor_name_val  = 0            # Add one per sensor

# Output states (for outputs that use hysteresis or need to remember state)
fan_on           = False          # True while cooling fan is running
alert_active     = False          # True while any alert condition is active

# Console print timestamp
last_print       = 0


# ==============================================================================
# SENSOR FUNCTIONS
# One function per sensor, called on its individual interval.
# Each function reads the sensor and updates the corresponding value variable.
# ==============================================================================

def read_temperature():
  # Read the analog temperature sensor and convert to degrees Celsius.
  # Formula for MCP9700A: Temp(C) = (Voltage - 0.5V) / 0.01 V/C
  # (See Activity 9 analysis questions for derivation.)
  global temp_c
  voltage = beaper.temp_level() * 3.3 / 65535
  temp_c  = (voltage - 0.5) / 0.01

def read_light():
  # Read the ambient light sensor and store the raw ADC value.
  global light_level_val
  light_level_val = beaper.light_level()

# def read_SENSORNAME():
#   global sensor_name_val
#   sensor_name_val = beaper.SENSORNAME_level()   # or digitalRead / custom logic


# ==============================================================================
# CONDITION EVALUATION
# Called once per loop after all due sensors have been read.
# Evaluates sensor values against thresholds and sets output state variables.
# Write your application logic here.
# ==============================================================================

def check_conditions():
  global fan_on, alert_active

  # --- Temperature control (example: hysteresis) ----------------------------
  # Fan turns ON when temperature rises above TEMP_HIGH_THRESHOLD,
  # and turns OFF only when it falls below TEMP_LOW_THRESHOLD.
  # The gap between thresholds prevents rapid cycling at the boundary.
  if fan_on:
    if temp_c < TEMP_LOW_THRESHOLD:
      fan_on = False
  else:
    if temp_c > TEMP_HIGH_THRESHOLD:
      fan_on = True

  # --- Alert condition (example: any sensor out of range) -------------------
  # Alert is active if temperature is high OR light is too low.
  # TODO: replace or extend this with your application's alert logic.
  alert_active = (temp_c > TEMP_HIGH_THRESHOLD or
                  light_level_val < LIGHT_LOW_THRESHOLD)

  # --- Add your condition logic here ----------------------------------------
  # Follow the pattern above: read from global sensor value variables,
  # write to global output state variables. Use hysteresis (two thresholds)
  # for any output that controls a slow-changing physical process.


# ==============================================================================
# OUTPUT CONTROL
# Called once per loop after check_conditions().
# Applies the current output state variables to the physical hardware.
# Keep hardware writes here - check_conditions() only updates variables.
# ==============================================================================

def apply_outputs():
  # --- Cooling fan (example) ------------------------------------------------
  if fan_on:
    beaper.right_motor_forward()    # TODO: replace with your motor/output call
  else:
    beaper.right_motor_stop()

  # --- Status LED (example) -------------------------------------------------
  beaper.LED2.value(1 if alert_active else 0)

  # --- Add your output control here -----------------------------------------
  # Each output state variable set in check_conditions() should have a
  # corresponding hardware write here.


# ==============================================================================
# SENSOR READ SCHEDULE
# Called once per loop. Checks each sensor's interval timer and calls
# its read function when due. Returns True if any sensor was read this
# iteration (useful for debug output timing).
# ==============================================================================

def read_sensors(current_time):
  global last_temp_read, last_light_read

  any_read = False

  # --- Temperature: read every TEMP_READ_INTERVAL ms -----------------------
  if time.ticks_diff(current_time, last_temp_read) >= TEMP_READ_INTERVAL:
    read_temperature()
    last_temp_read = current_time
    any_read = True

  # --- Light: read every LIGHT_READ_INTERVAL ms ----------------------------
  if time.ticks_diff(current_time, last_light_read) >= LIGHT_READ_INTERVAL:
    read_light()
    last_light_read = current_time
    any_read = True

  # --- Add your sensors here -----------------------------------------------
  # if time.ticks_diff(current_time, last_SENSORNAME_read) >= SENSORNAME_READ_INTERVAL:
  #   read_SENSORNAME()
  #   last_SENSORNAME_read = current_time
  #   any_read = True

  return any_read


# ==============================================================================
# CONSOLE OUTPUT
# Print a summary of all sensor values and output states periodically.
# Useful during development and for data logging via the serial console.
# ==============================================================================

def print_status():
  print("Temp:", round(temp_c, 1), "C",
        "| Light:", light_level_val,
        "| Fan:", "ON" if fan_on else "OFF",
        "| Alert:", "YES" if alert_active else "no")
  # Add your sensor values and output states here


# ==============================================================================
# MAIN PROGRAM
# ==============================================================================

beaper.nano_led_on()
print("Analog Sensor Monitor")
print("Temp high:", TEMP_HIGH_THRESHOLD, "C  low:", TEMP_LOW_THRESHOLD, "C")
print("Light low:", LIGHT_LOW_THRESHOLD, "  high:", LIGHT_HIGH_THRESHOLD)
print()

# Take initial readings so variables are not zero on first check_conditions()
read_temperature()
read_light()
# read_SENSORNAME()

state_start   = time.ticks_ms()
last_temp_read  = state_start
last_light_read = state_start
last_print      = state_start

while True:
  current_time = time.ticks_ms()

  # 1. Read any sensors that are due
  read_sensors(current_time)

  # 2. Evaluate conditions and update output state variables
  check_conditions()

  # 3. Apply output states to hardware
  apply_outputs()

  # 4. Print periodic status summary
  if time.ticks_diff(current_time, last_print) >= PRINT_INTERVAL:
    print_status()
    last_print = current_time

  time.sleep_ms(LOOP_DELAY)


"""
Capstone Development Guide

This skeleton is deliberately generic. Your first task is to decide
what your system monitors and what it controls, then fill in the
template section by section.

Step 1 - Define your application
  Write two or three sentences describing your system from the user's
  perspective. Then answer:
  - What physical quantities does it measure? (temperature, light,
    moisture, motion, distance, switch state...)
  - What does it control in response? (fan, pump, servo, LEDs, alarm...)
  - Under what conditions does each output activate or deactivate?
  - How quickly do your inputs change? (This determines read intervals.)

  Complete the capstone preparation guide before continuing.

Step 2 - Configure and test one sensor
  Add your first sensor to the SENSOR CONFIGURATION section and write
  its read function. In the main loop, temporarily replace the call to
  check_conditions() and apply_outputs() with just a print statement
  showing the raw sensor value. Verify the reading looks correct before
  adding any control logic.

  For analog sensors:
  - Print the raw ADC value while varying the physical quantity.
  - Record the values at your intended threshold levels.
  - Set your threshold constants from these measurements, not guesses.

  For digital inputs (buttons or contact switches):
  - Verify the pin reads LOW when active and HIGH when not (INPUT_PULLUP).
  - Test both states explicitly before using the value in conditions.

Step 3 - Add condition logic for that sensor
  Write the condition for your first sensor in check_conditions() and
  its output in apply_outputs(). Test the full sensor-to-output path:
  vary the sensor input and verify the output responds correctly at both
  threshold values (hysteresis boundaries if applicable).

Step 4 - Add remaining sensors and outputs
  Add each additional sensor and its output one at a time, testing each
  before adding the next. Use the comment templates (lines beginning with
  '# ---') as insertion points. Sensors are independent - a slow
  temperature read does not delay a fast moisture check.

Step 5 - Combine conditions
  If your application requires combined logic (e.g. "fan runs only when
  temperature is high AND humidity is high"), implement this in
  check_conditions() after the individual sensor checks. Test the
  combined logic by independently varying each input to verify all
  combinations produce the correct output.

Step 6 - Refinements and extensions

  a) Calibration on startup: read each analog sensor several times at
     startup, average the results, and use this as a baseline. Useful
     for sensors whose raw values vary with supply voltage or ambient
     conditions (light sensors, some moisture sensors).

  b) Data logging: modify print_status() to print comma-separated values
     (CSV format) that can be copied from the serial console into a
     spreadsheet. Include a timestamp using time.ticks_ms().

  c) Manual override: add a button that temporarily overrides the
     automatic control of an output. Hold SW5 to run the fan regardless
     of temperature, for example. How does this interact with the
     hysteresis logic in check_conditions()?

  d) Trend detection: store the previous reading of a slowly-changing
     sensor and compute the rate of change. Activate an output early
     if the value is changing rapidly toward a threshold, rather than
     waiting until it crosses it. This is a simplified form of
     predictive control used in real building automation systems.

  e) Multiple zones: if your application monitors multiple physical
     locations (e.g. two greenhouse beds, or two rooms), extend the
     sensor configuration to include one set of variables per zone
     and generalise check_conditions() to evaluate each zone
     independently.

"""
