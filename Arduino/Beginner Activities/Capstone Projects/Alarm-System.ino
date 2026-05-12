/* ================================================================================
Capstone Project: Alarm System [BEAPERNano-Capstone-Alarm-System]
May 11, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPERNano.h header file

Hardware used:
  SW2-SW5    - Arm/disarm code entry buttons
  LED2-LED5  - Alarm system state indicators
  LS1        - Piezo speaker (entry countdown beeps, alarm tone)

Sensor options (choose one or combine):
  Option A - Optical proximity sensor (contactless, no wiring needed):
    Set JP1 to Enviro. to use Q4 (ambient light sensor) as a proximity
    sensor. An object or hand passing in front of the sensor changes
    the light reading. Mount the circuit inside the locker or room so
    the sensor faces the opening. Set SENSOR_MODE = OPTICAL.

  Option B - Hard-wired contact switch on expansion header:
    Wire a normally-closed (NC) magnetic door/drawer contact switch
    between H1 (or H2, H3, H4) and GND. When the door opens the
    circuit breaks, pulling H1 HIGH. Set SENSOR_MODE = CONTACT and
    set SENSOR_PIN to match your header choice.

  You can combine both: check_sensors() can read both and return true
  if either is triggered. See check_sensors() below.

Compatible with all BEAPER Nano configurations.
Optical sensor: set JP1 to Enviro. (selects ambient light sensor Q4).
Contact sensor: no jumper changes required, wire to H1-H4.

--------------------------------------------------------------------------------
Alarm system behaviour:
  DISARMED  - Safe. Enter the arm code to begin arming.
              If alarms occurred since last disarm, count is displayed.
  ARMING    - Exit delay: sensors ignored while you leave. LEDs count
              down. Do NOT enter the code during this phase.
  ARMED     - Sensors active. Circuit goes dark. Do not touch buttons.
  TRIPPED   - Entry delay: sensors tripped, enter disarm code now or
              alarm will sound. LEDs flash urgently.
  ALARM     - Alarm sounding. Enter code to disarm. Alarm records
              itself. Stops after ALARM_DURATION, then re-arms.
--------------------------------------------------------------------------------
Before you begin - complete your capstone plan:
  1. Write a plain-English description from the user's perspective.
  2. List all states and draw your state diagram with transitions.
  3. Complete the state details table (outputs, transitions, next states).
  4. List all constants and variables you will need.
  5. Write your testing plan before writing any code.
================================================================================*/
// IMPORTANT: Make sure that BEAPERNano.h is accessible as a tab in this project.
#include "BEAPERNano.h"

// ---- State Constants -----------------
const int STATE_DISARMED = 0;  // Safe - waiting for arm code
const int STATE_ARMING   = 1;  // Exit delay - sensors ignored
const int STATE_ARMED    = 2;  // Sensors active - circuit dark
const int STATE_TRIPPED  = 3;  // Entry delay - enter code or alarm sounds
const int STATE_ALARM    = 4;  // Alarm sounding - enter code to disarm

const char* STATE_NAMES[] = {
  "DISARMED", "ARMING", "ARMED", "TRIPPED", "ALARM"
};

// ---- Code Entry Result Constants -----
const int CODE_INCOMPLETE = 0;   // Still entering - no result yet
const int CODE_CORRECT    = 1;   // Correct code entered
const int CODE_WRONG      = 2;   // Wrong button pressed - entry reset

// ---- Sensor Configuration ------------
const int OPTICAL = 0;
const int CONTACT = 1;
const int SENSOR_MODE = OPTICAL;   // Change to CONTACT for hard-wired switch
const int SENSOR_PIN  = H1;        // Header pin for contact switch (Option B)

// ---- Timing Constants ----------------
const unsigned long EXIT_DELAY     = 15000; // Time to leave before arming (ms)
const unsigned long ENTRY_DELAY    = 10000; // Time to enter code before alarm (ms)
const unsigned long ALARM_DURATION = 60000; // Alarm sounds for this long (ms)
const unsigned long BEEP_INTERVAL  = 1000;  // Entry countdown beep interval (ms)
const unsigned long FLASH_INTERVAL = 250;   // Urgent flash in TRIPPED/ALARM (ms)

// ---- Code Constants ------------------
// The arm/disarm code as an array of button indices (0=SW2, 1=SW3, 2=SW4, 3=SW5).
// Change this to set your code. Default: SW2, SW4, SW3, SW5.
const int ARM_CODE[]    = { 0, 2, 1, 3 };
const int CODE_LENGTH   = 4;

// ---- Loop Constant -------------------
const int LOOP_DELAY = 10;         // Main loop delay (ms)

// ---- Hardware Maps -------------------
const int BUTTONS[] = { SW2, SW3, SW4, SW5 };
const int LEDS[]    = { LED2, LED3, LED4, LED5 };

// ---- Program Variables ---------------
int           state            = STATE_DISARMED;
unsigned long state_start      = 0;

int           alarm_count      = 0;      // Alarms since last disarm
bool          showing_count    = false;  // True while displaying alarm count
unsigned long last_beep_time   = 0;
unsigned long last_flash_time  = 0;
bool          flash_on         = false;

int           sensor_baseline  = 0;      // Light level at time of arming

int           code_step        = 0;      // Steps correct so far
int           last_button      = -1;     // For edge detection


// ---- Program Functions ---------------

void all_leds_off()
{
    for (int i = 0; i < 4; i++)
        digitalWrite(LEDS[i], LOW);
}

void enter_state(int new_state, unsigned long current_time, const char* reason = "")
{
    all_leds_off();
    noTone(LS1);
    state       = new_state;
    state_start = current_time;
    flash_on    = false;
    code_step   = 0;
    last_button = -1;
    Serial.print("--> ");
    Serial.print(STATE_NAMES[new_state]);
    if (strlen(reason) > 0)
    {
        Serial.print(" (");
        Serial.print(reason);
        Serial.print(")");
    }
    Serial.println();
}

int read_button_press()
{
    // Return the index (0-3) of a button that has JUST been pressed,
    // or -1 if no new press. Uses last_button for edge detection.
    for (int i = 0; i < 4; i++)
    {
        if (digitalRead(BUTTONS[i]) == LOW)
        {
            if (last_button != i)
            {
                last_button = i;
                return i;
            }
            return -1;     // Already held - not a new press
        }
    }
    last_button = -1;
    return -1;
}

int check_code_entry(unsigned long current_time)
{
    // Check for a button press and match against the next ARM_CODE step.
    // Returns CODE_CORRECT, CODE_WRONG, or CODE_INCOMPLETE.
    int pressed = read_button_press();
    if (pressed == -1)
        return CODE_INCOMPLETE;

    if (pressed == ARM_CODE[code_step])
    {
        code_step++;
        tone(LS1, 800 + code_step * 100, 80);   // Rising confirmation tone
        if (code_step == CODE_LENGTH)
        {
            code_step = 0;
            return CODE_CORRECT;
        }
        return CODE_INCOMPLETE;
    }
    else
    {
        code_step = 0;
        tone(LS1, 200, 150);                     // Low rejection tone
        Serial.println("    wrong button - code reset");
        return CODE_WRONG;
    }
}

bool check_sensors()
{
    // Return true if any sensor detects a trip (door opened / proximity).
    if (SENSOR_MODE == OPTICAL)
    {
        // Optical proximity: trip if light level deviates from baseline.
        // TODO: define SENSOR_THRESHOLD and compare to sensor_baseline.
        //       Return true if abs(light_level() - sensor_baseline) > SENSOR_THRESHOLD.
        //       Start with SENSOR_THRESHOLD = 30 (10-bit range) and adjust.
        return false;  // Replace with threshold comparison
    }
    else if (SENSOR_MODE == CONTACT)
    {
        // Contact switch (NC): trip if header pin reads HIGH (circuit broken).
        return (digitalRead(SENSOR_PIN) == HIGH);
    }
    return false;
}

void take_sensor_baseline()
{
    sensor_baseline = light_level();
    Serial.print("    sensor baseline: ");
    Serial.println(sensor_baseline);
}

void display_alarm_count(int count)
{
    // TODO: implement a clear visual display of your choice.
    // Ideas: flash LED2-LED5 together 'count' times with pauses,
    //        print to the Serial Monitor, or both.
    Serial.print("*** ALARM COUNT: ");
    Serial.print(count);
    Serial.println(" alarm(s) since last disarm ***");
}


void setup()
{
    for (int i = 0; i < 4; i++)
    {
        pinMode(LEDS[i],    OUTPUT);
        pinMode(BUTTONS[i], INPUT_PULLUP);
        digitalWrite(LEDS[i], LOW);
    }
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, HIGH);

    if (SENSOR_MODE == CONTACT)
        pinMode(SENSOR_PIN, INPUT_PULLUP);

    Serial.begin(9600);
    while (!Serial);

    Serial.println("Alarm System");
    Serial.print("Code: SW");
    for (int i = 0; i < CODE_LENGTH; i++)
    {
        Serial.print(ARM_CODE[i] + 2);
        if (i < CODE_LENGTH - 1) Serial.print(", SW");
    }
    Serial.println();
    Serial.println();

    state_start    = millis();
    last_flash_time = millis();
    last_beep_time  = millis();

    enter_state(STATE_DISARMED, state_start, "startup");
    digitalWrite(LEDS[0], HIGH);   // LED2 on = disarmed indicator
}

void loop()
{
    unsigned long current_time = millis();
    unsigned long elapsed      = current_time - state_start;

    // ---- State: Disarmed ----
    if (state == STATE_DISARMED)
    {
        if (alarm_count > 0 && !showing_count)
        {
            showing_count = true;
            display_alarm_count(alarm_count);
        }

        int result = check_code_entry(current_time);
        if (result == CODE_CORRECT)
        {
            // TODO: transition to STATE_ARMING and take sensor baseline.
            //       Call take_sensor_baseline() before entering the new
            //       state so the baseline reflects the current safe light
            //       level. Reset alarm_count and showing_count here.
        }
    }

    // ---- State: Arming (exit delay) ----
    else if (state == STATE_ARMING)
    {
        // Sensors are ignored during exit delay.
        // TODO: implement a countdown display using elapsed and EXIT_DELAY.
        //       Divide EXIT_DELAY into four segments; step LEDs off one by
        //       one as time passes. When EXIT_DELAY elapses, confirm arming
        //       with a short beep pattern and transition to STATE_ARMED.
    }

    // ---- State: Armed ----
    else if (state == STATE_ARMED)
    {
        if (check_sensors())
        {
            enter_state(STATE_TRIPPED, current_time, "sensor tripped");
            // TODO: start urgent LED flashing and beeping.
        }
    }

    // ---- State: Tripped (entry delay) ----
    else if (state == STATE_TRIPPED)
    {
        // TODO: flash LED2-LED5 at FLASH_INTERVAL using last_flash_time.
        // TODO: beep briefly every BEEP_INTERVAL using last_beep_time.

        int result = check_code_entry(current_time);
        if (result == CODE_CORRECT)
        {
            // TODO: disarm silently (no alarm recorded).
            //       Transition to STATE_DISARMED and restore LED2 indicator.
        }

        // TODO: if ENTRY_DELAY elapses without correct code, increment
        //       alarm_count and transition to STATE_ALARM.
    }

    // ---- State: Alarm ----
    else if (state == STATE_ALARM)
    {
        // TODO: flash LED2-LED5 at FLASH_INTERVAL using last_flash_time.
        // TODO: sound a continuous alarm tone, alternating frequencies
        //       for an attention-getting pattern.

        int result = check_code_entry(current_time);
        if (result == CODE_CORRECT)
        {
            // TODO: transition to STATE_DISARMED. Alarm was already counted
            //       on entry to this state - do not increment again.
        }

        // TODO: if ALARM_DURATION elapses, transition back to STATE_ARMED
        //       (re-arm - the intruder has not entered the correct code).
    }

    delay(LOOP_DELAY);
}


/*
Capstone Development Guide

Work through these steps in order. Test each step thoroughly before
continuing - a working partial system is always better than a broken
complete one.

Step 1 - Sensor configuration and baseline
  Choose your sensor mode (OPTICAL or CONTACT) and configure
  check_sensors() to return true when the sensor is triggered.

  For optical mode: set JP1 to Enviro. Mount the circuit with Q4
  facing the door or opening. Run the program and print light_level()
  every loop iteration. Open the door slowly and record the range of
  values when undisturbed vs disturbed. Set SENSOR_THRESHOLD to a
  value comfortably between the two ranges.

  For contact mode: wire your NC switch between H1 and GND. Verify
  that check_sensors() returns true when the door is open and false
  when closed before implementing any state logic.

Step 2 - Disarmed state and code entry
  Implement the arm code transition from STATE_DISARMED. check_code_entry()
  handles the matching - you only need to act on the CODE_CORRECT result.
  Test carefully:
  - Correct sequence transitions to ARMING
  - Wrong button resets silently (stays DISARMED)
  - Partial sequence followed by correct completion works

Step 3 - Arming (exit delay)
  Implement the countdown in STATE_ARMING. Test that check_sensors()
  is genuinely not called during the exit delay. Verify the circuit
  goes dark and silent when ARMED.

Step 4 - Armed and tripped
  Implement sensor checking in STATE_ARMED and the entry delay in
  STATE_TRIPPED. Test the full arm -> trip -> disarm sequence:
  - Arm the system and trigger the sensor
  - Enter the code within ENTRY_DELAY
  - Verify STATE_DISARMED with no alarm recorded

Step 5 - Alarm and re-arm
  Implement STATE_ALARM. Test arm -> trip -> timeout -> alarm -> re-arm.
  Verify alarm_count increments and is displayed on next successful
  disarm. Test that code entry during ALARM also disarms correctly.

Step 6 - Refinements and extensions

  a) Display improvements: implement display_alarm_count() to show the
     count visually (e.g. flash LEDs 'count' times). Add a button press
     in DISARMED to acknowledge and clear the count after it is shown.

  b) Tamper protection: log a tamper event if check_sensors() returns
     true immediately on entry to STATE_ARMED (sensor was not closed
     when arming completed). Print a warning and increment alarm_count.

  c) Multiple sensors: extend check_sensors() to read both an optical
     sensor and a contact switch. Return true if either is triggered.
     Print which sensor tripped to the Serial Monitor for debugging.

  d) Code change: add a mode triggered by a special button sequence from
     DISARMED that allows the arm code to be changed. Store the new code
     in a global array. How would you prevent someone from changing the
     code without knowing the current one?

  e) Panic button: SW5 held for 3 seconds in any state immediately
     triggers STATE_ALARM and increments alarm_count. This simulates a
     manual panic/duress feature. What changes does the state machine
     need? Where in loop() should the hold check go?

*/
