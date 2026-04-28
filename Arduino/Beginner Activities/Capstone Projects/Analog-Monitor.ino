/* ================================================================================
Capstone Project: Analog Sensor Monitor [BEAPERNano-Capstone-Analog-Monitor]
April 22, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPERNano.h header file

This sketch provides a multi-sensor monitoring and control structure.
Adapt it to your application by:
  1. Configuring your inputs in the SENSOR CONFIGURATION section
     and the read_sensors() function.
  2. Writing your condition logic in check_conditions().
  3. Configuring your outputs in the OUTPUT CONFIGURATION section
     and the apply_outputs() function.

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
    light_level()   - Ambient light sensor Q4 (JP1)
    temp_level()    - Temperature sensor U4 (JP2)
    RV1_level()     - Potentiometer RV1 (JP3) - useful as a threshold knob
    RV2_level()     - Potentiometer RV2 (JP4) - useful as a threshold knob

External analog inputs available (each needs to be enabled/configured
  in the BEAPERNano.h header file - see ADC4-7 notes):
    H1  - Sensor header with analog input, 3.3V, GND
    H2  - Sensor header with analog input, 3.3V, GND
    H3  - Sensor header with analog input, 3.3V, GND
    H4  - Sensor header with analog input, 3.3V, GND

Digital inputs available:
    SW2-SW5         - Pushbuttons (active LOW, INPUT_PULLUP)
    H1-H4           - Expansion headers (for external sensors/switches)

Analog outputs available:
    LED2-LED5       - LEDs (on/off or PWM brightness via analogWrite)
    LS1             - Piezo speaker (tone() / noTone())
    Servo headers H5 to H8 - Servo position (Servo library)

Digital outputs available:
    LED2-LED5       - LEDs (on/off)
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
================================================================================*/
// IMPORTANT: Make sure that BEAPERNano.h is accessible as a tab in this project.
#include "BEAPERNano.h"

// ==============================================================================
// SENSOR CONFIGURATION
// Name each sensor, its read interval, and its threshold values.
// Add one block per sensor your application requires.
// ==============================================================================

// ---- Sensor 1: Temperature (example) ----------------------------------------
const unsigned long TEMP_READ_INTERVAL  = 2000;  // Read every 2000 ms
const float         TEMP_HIGH_THRESHOLD = 28.0;  // Degrees C: cooling activates
const float         TEMP_LOW_THRESHOLD  = 24.0;  // Degrees C: cooling deactivates

// ---- Sensor 2: Light (example) ----------------------------------------------
const unsigned long LIGHT_READ_INTERVAL  = 500;   // Read every 500 ms
const int           LIGHT_LOW_THRESHOLD  = 200;   // Below this (dark): light activates
const int           LIGHT_HIGH_THRESHOLD = 300;   // Above this (bright): light deactivates

// ---- Add your sensors here --------------------------------------------------
// const unsigned long SENSOR_NAME_READ_INTERVAL = 1000;
// const int           SENSOR_NAME_THRESHOLD      = value;

// ==============================================================================
// OUTPUT CONFIGURATION
// ==============================================================================

// ---- Output 1: Cooling fan (example - motor on H9/H10) ----------------------
// Uses right_motor_forward() / right_motor_stop() from BEAPERNano.h motor functions.

// ---- Output 2: Status LED (example) -----------------------------------------
// LED2 indicates alert condition.

// ---- Add your outputs here --------------------------------------------------

// ==============================================================================
// LOOP TIMING
// ==============================================================================
const int           LOOP_DELAY    = 10;    // Main loop delay (ms)
const unsigned long PRINT_INTERVAL = 5000; // Serial summary interval (ms)

// ==============================================================================
// PROGRAM VARIABLES
// ==============================================================================

// Sensor read timestamps
unsigned long last_temp_read  = 0;
unsigned long last_light_read = 0;
// unsigned long last_SENSORNAME_read = 0;

// Current sensor values
float temp_c          = 0.0;
int   light_level_val = 0;
// int   sensor_name_val = 0;

// Output states
bool  fan_on          = false;
bool  alert_active    = false;

// Console print timestamp
unsigned long last_print = 0;


// ==============================================================================
// SENSOR FUNCTIONS
// ==============================================================================

void read_temperature()
{
    // Read the analog temperature sensor and convert to degrees Celsius.
    // Formula for MCP9700A: Temp(C) = (Voltage - 0.5V) / 0.01 V/C
    float voltage = temp_level() * (3.3 / 1023.0);
    temp_c = (voltage - 0.5) / 0.01;
}

void read_light()
{
    light_level_val = light_level();
}

// void read_SENSORNAME()
// {
//     sensor_name_val = analogRead(SENSOR_PIN);   // or digitalRead
// }


// ==============================================================================
// CONDITION EVALUATION
// Called once per loop after sensors have been read.
// Evaluates values against thresholds and sets output state variables.
// ==============================================================================

void check_conditions()
{
    // ---- Temperature control (hysteresis) ------------------------------------
    if (fan_on)
    {
        if (temp_c < TEMP_LOW_THRESHOLD)
            fan_on = false;
    }
    else
    {
        if (temp_c > TEMP_HIGH_THRESHOLD)
            fan_on = true;
    }

    // ---- Alert condition (any sensor out of range) ---------------------------
    // TODO: replace or extend with your application's alert logic.
    alert_active = (temp_c > TEMP_HIGH_THRESHOLD ||
                    light_level_val < LIGHT_LOW_THRESHOLD);

    // ---- Add your condition logic here ---------------------------------------
    // Read from sensor value variables; write to output state variables.
    // Use hysteresis for any output controlling a slow-changing process.
}


// ==============================================================================
// OUTPUT CONTROL
// Called once per loop after check_conditions().
// Applies output state variables to hardware.
// ==============================================================================

void apply_outputs()
{
    // ---- Cooling fan ---------------------------------------------------------
    if (fan_on)
        right_motor_forward();    // TODO: replace with your motor/output call
    else
        right_motor_stop();

    // ---- Status LED ----------------------------------------------------------
    digitalWrite(LED2, alert_active ? HIGH : LOW);

    // ---- Add your output control here ----------------------------------------
}


// ==============================================================================
// SENSOR READ SCHEDULE
// Checks each sensor's interval and calls its read function when due.
// ==============================================================================

void read_sensors(unsigned long current_time)
{
    if ((current_time - last_temp_read) >= TEMP_READ_INTERVAL)
    {
        read_temperature();
        last_temp_read = current_time;
    }

    if ((current_time - last_light_read) >= LIGHT_READ_INTERVAL)
    {
        read_light();
        last_light_read = current_time;
    }

    // if ((current_time - last_SENSORNAME_read) >= SENSORNAME_READ_INTERVAL)
    // {
    //     read_SENSORNAME();
    //     last_SENSORNAME_read = current_time;
    // }
}


// ==============================================================================
// CONSOLE OUTPUT
// ==============================================================================

void print_status()
{
    Serial.print("Temp: ");   Serial.print(temp_c, 1);
    Serial.print(" C | Light: "); Serial.print(light_level_val);
    Serial.print(" | Fan: ");     Serial.print(fan_on ? "ON" : "OFF");
    Serial.print(" | Alert: ");   Serial.println(alert_active ? "YES" : "no");
    // Add your sensor values and output states here
}


// ==============================================================================
// SETUP AND LOOP
// ==============================================================================

void setup()
{
    pinMode(LED2, OUTPUT);
    pinMode(LED3, OUTPUT);
    pinMode(LED4, OUTPUT);
    pinMode(LED5, OUTPUT);
    digitalWrite(LED2, LOW);
    digitalWrite(LED3, LOW);
    digitalWrite(LED4, LOW);
    digitalWrite(LED5, LOW);

    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, HIGH);

    Serial.begin(9600);
    while (!Serial);

    // Take initial readings so variables are not zero on first check_conditions()
    read_temperature();
    read_light();
    // read_SENSORNAME();

    unsigned long now = millis();
    last_temp_read  = now;
    last_light_read = now;
    last_print      = now;

    Serial.println("Analog Sensor Monitor");
    Serial.print("Temp high: "); Serial.print(TEMP_HIGH_THRESHOLD);
    Serial.print(" C  low: ");   Serial.println(TEMP_LOW_THRESHOLD);
    Serial.print("Light low: "); Serial.print(LIGHT_LOW_THRESHOLD);
    Serial.print("  high: ");    Serial.println(LIGHT_HIGH_THRESHOLD);
    Serial.println();
}

void loop()
{
    unsigned long current_time = millis();

    // 1. Read any sensors that are due
    read_sensors(current_time);

    // 2. Evaluate conditions and update output state variables
    check_conditions();

    // 3. Apply output states to hardware
    apply_outputs();

    // 4. Print periodic status summary
    if ((current_time - last_print) >= PRINT_INTERVAL)
    {
        print_status();
        last_print = current_time;
    }

    delay(LOOP_DELAY);
}


/*
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
  Add your first sensor to SENSOR CONFIGURATION and write its read
  function. Temporarily comment out check_conditions() and apply_outputs()
  in loop() and replace them with a Serial.print() of the raw sensor
  value. Verify the reading looks correct before adding control logic.

  For analog sensors:
  - Print the raw value while varying the physical quantity.
  - Record values at your intended threshold levels.
  - Set threshold constants from measurements, not guesses.

  For digital inputs (buttons or contact switches):
  - Verify the pin reads LOW when active and HIGH when not (INPUT_PULLUP).
  - Test both states explicitly before using the value in conditions.

Step 3 - Add condition logic for that sensor
  Write the condition for your first sensor in check_conditions() and
  its output in apply_outputs(). Test the full sensor-to-output path:
  vary the sensor and verify the output responds correctly at both
  threshold values (hysteresis boundaries if applicable).

Step 4 - Add remaining sensors and outputs
  Add each additional sensor and output one at a time, testing each
  before adding the next. Use the comment templates as insertion points.
  Sensors are independent - a slow temperature read does not delay a
  fast moisture check.

Step 5 - Combine conditions
  If your application requires combined logic (e.g. fan runs only when
  temperature is high AND humidity is high), implement this in
  check_conditions() after the individual sensor checks. Test all
  combinations by independently varying each input.

Step 6 - Refinements and extensions

  a) Calibration on startup: read each analog sensor several times,
     average the results, and use this as a baseline. Useful for sensors
     whose raw values vary with ambient conditions.

  b) Data logging: modify print_status() to print comma-separated values
     (CSV format) for copying into a spreadsheet. Include millis() as a
     timestamp column.

  c) Manual override: add a button that temporarily overrides automatic
     control of an output. Hold SW5 to run the fan regardless of
     temperature. How does this interact with the hysteresis logic?

  d) Trend detection: store the previous reading of a slowly-changing
     sensor and compute the rate of change. Activate an output early
     if the value is approaching a threshold rapidly. This is a
     simplified form of predictive control used in real building
     automation systems.

  e) Multiple zones: extend the sensor configuration to include one
     set of variables per zone (e.g. two greenhouse beds). Generalise
     check_conditions() to evaluate each zone independently.

*/
