/* ================================================================================
Capstone Project: Analog Sensor Monitor [BEAPERNano-Capstone-Analog-Monitor]
Version: 1.0
Updated: July 25, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPERNano.h header file

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
    light_level()   - Ambient light sensor Q4 (JP1)
    temp_level()    - Temperature sensor U4 (JP2)
    RV1_level()     - Potentiometer RV1 (JP3) - useful as a threshold knob
    RV2_level()     - Potentiometer RV2 (JP4) - useful as a threshold knob

External analog inputs available (each needs to be enabled/configured
  in the BEAPERNano.h header file):
    H1  - Sensor header with analog input, 3.3V, GND
    H2  - Sensor header with analog input, 3.3V, GND
    H3  - Sensor header with analog input, 3.3V, GND
    H4  - Sensor header with analog input, 3.3V, GND

Digital inputs available:
    SW2 to SW5  - Pushbuttons (active LOW, INPUT_PULLUP)
    H1 to H4    - Expansion headers (for external sensors/switches)

Analog outputs available:
    LS1             - Piezo speaker (tone() / noTone())
    LED2 to LED5    - LEDs (digital on/off or PWM brightness)
    Servo headers H5 to H8 - Servo position (Servo library)

Digital outputs available:
    LED2 to LED5    - LEDs (on/off)
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
=================================================================================*/
// IMPORTANT: Make sure that BEAPERNano.h is accessible as a tab in this project.
#include "BEAPERNano.h"   // Define BEAPER Nano I/O devices

// ==============================================================================
// SENSOR CONFIGURATION
// Name each sensor, its read interval, and its threshold values.
// Add one block per sensor your application requires.
// ==============================================================================

// ---- Sensor 1: Temperature (example) -----------------------------------------
const int TEMP_READ_INTERVAL  = 2000;    // Read every 2000 ms (temperature changes slowly)
const float TEMP_HIGH_THRESHOLD = 28;    // Degrees C: above this, cooling output activates
const float TEMP_LOW_THRESHOLD  = 24;    // Degrees C: below this, cooling output deactivates
                                          // (hysteresis gap prevents rapid on/off cycling)

// ---- Sensor 2: Light (example) -----------------------------------------------
const int LIGHT_READ_INTERVAL  = 500;    // Read every 500 ms (light can change quickly)
const int LIGHT_LOW_THRESHOLD  = 20000;  // Below this (dark): lighting output activates
const int LIGHT_HIGH_THRESHOLD = 30000;  // Above this (bright): lighting output deactivates

// ---- Add your sensors here ----
// const int SENSOR_NAME_READ_INTERVAL = 1000;
// const int SENSOR_NAME_THRESHOLD     = value;

// ==============================================================================
// OUTPUT CONFIGURATION
// Name each output and its behaviour parameters.
// ==============================================================================

// ---- Output 1: Cooling fan (example - right motor driver output) ------------
// Uses right_motor_forward() / right_motor_stop(), which drive the
// H-bridge through the M2A/M2B pins (LED4/LED5). No servo header or H9/H10
// is involved here - those pins do not exist on BEAPER Nano (H1-H8 only).

// ---- Output 2: Status LED (example) ------------------------------------------
// Uses LED2 to indicate whether the system is in a normal or alert condition.

// ---- Add your outputs here ----

// ==============================================================================
// LOOP TIMING
// ==============================================================================
const int LOOP_DELAY     = 10;      // Main loop delay (ms) - keep at 10 or lower
                                     // so timing intervals remain accurate
const int PRINT_INTERVAL = 5000;    // Print sensor summary every 5000 ms

// ==============================================================================
// PROGRAM VARIABLES
// One 'last_read' timestamp per sensor, one 'last_print' for console output.
// One current value variable per sensor.
// One state variable per output that needs to remember its current state.
// ==============================================================================

// Sensor timestamps
unsigned long last_temp_read  = 0;
unsigned long last_light_read = 0;
// unsigned long last_SENSORNAME_read = 0;      // Add one per sensor

// Current sensor values
float temp_c          = 0.0;        // Current temperature in degrees C
int   light_level_val = 0;          // Current light level (raw ADC)
// int sensor_name_val = 0;         // Add one per sensor

// Output states (for outputs that use hysteresis or need to remember state)
bool fan_on       = false;          // True while cooling fan is running
bool alert_active = false;          // True while any alert condition is active

// Console print timestamp
unsigned long last_print = 0;


// ==============================================================================
// SENSOR FUNCTIONS
// One function per sensor, called on its individual interval.
// Each function reads the sensor and updates the corresponding value variable.
// ==============================================================================

void read_temperature()
{
    // Read the analog temperature sensor and convert to degrees Celsius.
    // Formula for MCP9700A: Temp(C) = (Voltage - 0.5V) / 0.01 V/C
    // (See Activity 9 analysis questions for derivation.)
    float voltage = temp_level() * 3.3 / 65535;
    temp_c = (voltage - 0.5) / 0.01;
}

void read_light()
{
    // Read the ambient light sensor and store the raw ADC value.
    light_level_val = light_level();
}

// void read_SENSORNAME()
// {
//     sensor_name_val = SENSORNAME_level();   // or digitalRead / custom logic
// }


// ==============================================================================
// CONDITION EVALUATION
// Called once per loop after all due sensors have been read.
// Evaluates sensor values against thresholds and sets output state variables.
// Write your application logic here.
// ==============================================================================

void check_conditions()
{
    // ---- Temperature control (example: hysteresis) --------------------------
    // Fan turns ON when temperature rises above TEMP_HIGH_THRESHOLD,
    // and turns OFF only when it falls below TEMP_LOW_THRESHOLD.
    // The gap between thresholds prevents rapid cycling at the boundary.
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

    // ---- Alert condition (example: any sensor out of range) -----------------
    // Alert is active if temperature is high OR light is too low.
    // TODO: replace or extend this with your application's alert logic.
    alert_active = (temp_c > TEMP_HIGH_THRESHOLD ||
                     light_level_val < LIGHT_LOW_THRESHOLD);

    // ---- Add your condition logic here ---------------------------------------
    // Follow the pattern above: read from global sensor value variables,
    // write to global output state variables. Use hysteresis (two thresholds)
    // for any output that controls a slow-changing physical process.
}


// ==============================================================================
// OUTPUT CONTROL
// Called once per loop after check_conditions().
// Applies the current output state variables to the physical hardware.
// Keep hardware writes here - check_conditions() only updates variables.
// ==============================================================================

void apply_outputs()
{
    // ---- Cooling fan (example) -----------------------------------------------
    if (fan_on)
        right_motor_forward();       // TODO: replace with your motor/output call
    else
        right_motor_stop();

    // ---- Status LED (example) -------------------------------------------------
    digitalWrite(LED2, alert_active ? HIGH : LOW);

    // ---- Add your output control here ------------------------------------------
    // Each output state variable set in check_conditions() should have a
    // corresponding hardware write here.
}


// ==============================================================================
// SENSOR READ SCHEDULE
// Called once per loop. Checks each sensor's interval timer and calls
// its read function when due. Returns true if any sensor was read this
// iteration (useful for debug output timing).
// ==============================================================================

bool read_sensors(unsigned long current_time)
{
    bool any_read = false;

    // ---- Temperature: read every TEMP_READ_INTERVAL ms -----------------------
    if ((current_time - last_temp_read) >= (unsigned long)TEMP_READ_INTERVAL)
    {
        read_temperature();
        last_temp_read = current_time;
        any_read = true;
    }

    // ---- Light: read every LIGHT_READ_INTERVAL ms -----------------------------
    if ((current_time - last_light_read) >= (unsigned long)LIGHT_READ_INTERVAL)
    {
        read_light();
        last_light_read = current_time;
        any_read = true;
    }

    // ---- Add your sensors here -------------------------------------------------
    // if ((current_time - last_SENSORNAME_read) >= (unsigned long)SENSORNAME_READ_INTERVAL)
    // {
    //     read_SENSORNAME();
    //     last_SENSORNAME_read = current_time;
    //     any_read = true;
    // }

    return any_read;
}


// ==============================================================================
// CONSOLE OUTPUT
// Print a summary of all sensor values and output states periodically.
// Useful during development and for data logging via the serial console.
// ==============================================================================

void print_status()
{
    Serial.print("Temp: "); Serial.print(temp_c, 1); Serial.print(" C");
    Serial.print(" | Light: "); Serial.print(light_level_val);
    Serial.print(" | Fan: "); Serial.print(fan_on ? "ON" : "OFF");
    Serial.print(" | Alert: "); Serial.println(alert_active ? "YES" : "no");
    // Add your sensor values and output states here
}


void setup()
{
    // Configure Arduino Nano ESP32 status LED as output
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, HIGH);

    // Configure the status LED output
    pinMode(LED2, OUTPUT);

    // Configure the ADC for 16-bit readings (0-65535), matching the
    // MicroPython board module's read_u16()-style scaling - see
    // Activity 9, GE1.
    analogReadResolution(16);

    Serial.begin(9600);
    delay(2000);                       // Give Serial Monitor time to
                                        // connect, without blocking
                                        // forever if it's never opened

    Serial.println("Analog Sensor Monitor");
    Serial.print("Temp high: "); Serial.print(TEMP_HIGH_THRESHOLD);
    Serial.print(" C  low: "); Serial.print(TEMP_LOW_THRESHOLD); Serial.println(" C");
    Serial.print("Light low: "); Serial.print(LIGHT_LOW_THRESHOLD);
    Serial.print("  high: "); Serial.println(LIGHT_HIGH_THRESHOLD);
    Serial.println();

    // Take initial readings so variables are not zero on first check_conditions()
    read_temperature();
    read_light();
    // read_SENSORNAME();

    unsigned long startup_time = millis();
    last_temp_read  = startup_time;
    last_light_read = startup_time;
    last_print      = startup_time;
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
    if ((current_time - last_print) >= (unsigned long)PRINT_INTERVAL)
    {
        print_status();
        last_print = current_time;
    }

    delay(LOOP_DELAY);
}


/* ================================================================================
Development Guide
================================================================================

This skeleton is deliberately generic. Your first task is to decide
what your system monitors and what it controls, then fill in the
template section by section.

--------------------------------------------------------------------------------
Step 1 - Define your application
--------------------------------------------------------------------------------

Write two or three sentences describing your system from the user's
perspective. Then answer:
- What physical quantities does it measure? (temperature, light,
  moisture, motion, distance, switch state...)
- What does it control in response? (fan, pump, servo, LEDs, alarm...)
- Under what conditions does each output activate or deactivate?
- How quickly do your inputs change? (This determines read intervals.)

Complete the Capstone Preparation Guide before continuing.

--------------------------------------------------------------------------------
Step 2 - Configure and test one sensor
--------------------------------------------------------------------------------

Add your first sensor to the SENSOR CONFIGURATION section and write
its read function. In loop(), temporarily replace the call to
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

--------------------------------------------------------------------------------
Step 3 - Add condition logic for that sensor
--------------------------------------------------------------------------------

Write the condition for your first sensor in check_conditions() and
its output in apply_outputs(). Test the full sensor-to-output path:
vary the sensor input and verify the output responds correctly at both
threshold values (hysteresis boundaries if applicable).

--------------------------------------------------------------------------------
Step 4 - Add remaining sensors and outputs
--------------------------------------------------------------------------------

Add each additional sensor and its output one at a time, testing each
before adding the next. Use the comment templates (lines beginning with
'// ----') as insertion points. Sensors are independent - a slow
temperature read does not delay a fast moisture check.

--------------------------------------------------------------------------------
Step 5 - Combine conditions
--------------------------------------------------------------------------------

If your application requires combined logic (e.g. "fan runs only when
temperature is high AND humidity is high"), implement this in
check_conditions() after the individual sensor checks. Test the
combined logic by independently varying each input to verify all
combinations produce the correct output.

*/


/* ================================================================================
Extension Activities
================================================================================

--------------------------------------------------------------------------------
EA 1 - Calibration on startup
--------------------------------------------------------------------------------

Read each analog sensor several times at startup, average the
results, and use this as a baseline. Useful for sensors whose raw
values vary with supply voltage or ambient conditions (light
sensors, some moisture sensors).

--------------------------------------------------------------------------------
EA 2 - Data logging
--------------------------------------------------------------------------------

Modify print_status() to print comma-separated values (CSV format)
that can be copied from the Serial Monitor into a spreadsheet.
Include a timestamp using millis().

--------------------------------------------------------------------------------
EA 3 - Manual override
--------------------------------------------------------------------------------

Add a button that temporarily overrides the automatic control of an
output. Hold SW5 to run the fan regardless of temperature, for
example. How does this interact with the hysteresis logic in
check_conditions()?

--------------------------------------------------------------------------------
EA 4 - Trend detection
--------------------------------------------------------------------------------

Store the previous reading of a slowly-changing sensor and compute
the rate of change. Activate an output early if the value is
changing rapidly toward a threshold, rather than waiting until it
crosses it. This is a simplified form of predictive control used in
real building automation systems.

--------------------------------------------------------------------------------
EA 5 - Multiple zones
--------------------------------------------------------------------------------

If your application monitors multiple physical locations (e.g. two
greenhouse beds, or two rooms), extend the sensor configuration to
include one set of variables per zone and generalise
check_conditions() to evaluate each zone independently.

With two or three zones, copying each sensor's block (as this
skeleton does throughout) is still manageable - two temperature
blocks, two fan outputs, and so on. If you find yourself
copy-pasting many nearly-identical blocks for many zones, that
repetition is exactly the situation an array of "zone" records (a
struct per zone, holding that zone's sensor values, thresholds, and
output state) is suited to, iterated with a single generalised check
function instead of one copy per zone. This capstone's skeleton does
not use that structure - Simon Game's capstone introduces arrays for
a similar reason (storing a growing sequence) if you want to see the
pattern applied elsewhere first.

*/
