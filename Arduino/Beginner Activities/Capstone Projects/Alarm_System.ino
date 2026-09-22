/* ================================================================================
Capstone Project: Alarm System [BEAPERNano-Capstone-Alarm-System]
Version: 1.0
Updated: July 25, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPERNano.h header file

A five-state intrusion alarm. Arm and disarm with the same
four-button code, entered the same way as the Activity 12 capstone
combination lock and safe: any button may be pressed at each step,
and correctness is only checked once all four digits are in, so a
wrong attempt reveals nothing about which digit was incorrect.

Hardware used:
  SW2-SW5    - Arm/disarm code entry buttons (all four used as code digits)
  LED2-LED5  - Alarm system state indicators
  LS1        - Piezo speaker (entry beeps, countdown, alarm tone)

Sensor options (choose one, or combine - see EA3):
  Option A - Optical proximity sensor (contactless):
    Two sub-choices, depending on which jumper position you use -
    these share jumpers with other sensors, so only one is
    available at a time:
      - Q4 (ambient light sensor, JP1 set to Enviro.): an object or
        hand passing in front of the sensor changes the light
        reading. Mount the circuit inside the protected space so
        the sensor faces the opening.
      - Q1, Q2, or Q3 (break-away floor/line sensors, matching
        jumper set to Robot): detects a trip by reflectivity, the
        same way these sensors detect a floor or line on the robot
        platforms. More consistent regardless of room lighting.
    Either way, set SENSOR_MODE to SENSOR_OPTICAL and calibrate
    SENSOR_THRESHOLD for your setup - see take_sensor_baseline()
    and Step 1 in the Development Guide below. Change 'light_level()'
    to 'Q1_level()' (or Q2/Q3) in both functions if you use a
    floor/line sensor instead of Q4.

  Option B - Contact switch on an expansion header:
    A magnetic contact switch (reed switch) or a simple mechanical
    switch (lever, roller, or pushbutton-style) both work here -
    wire a normally-closed (NC) switch to a spare header and GND.
    Set SENSOR_MODE to SENSOR_CONTACT. A mechanical switch is more
    likely to be available in a school's parts bin than a reed
    switch, but its contacts can bounce - see Activity 11 EA1's
    debounce pattern if 'check_sensors()' behaves inconsistently
    right at the moment of a trip.

--------------------------------------------------------------------------------
Alarm system behaviour:
  DISARMED  - Safe. Enter the arm code to begin arming. If alarms
              occurred since the last disarm, the count is displayed.
  ARMING    - Exit delay: sensors ignored while you leave. LEDs
              count down. Do NOT enter the code during this phase.
  ARMED     - Sensors active. Circuit goes dark. Do not touch buttons.
  TRIPPED   - Entry delay: sensor tripped, enter the disarm code now
              or the alarm will sound. LEDs flash urgently.
  ALARM     - Alarm sounding. Enter the code to disarm. The alarm
              records itself. Stops after ALARM_DURATION, then re-arms.

Before you begin - complete your capstone plan using the Capstone
Preparation Guide: project description, state diagram, state
details table, constants and variables, and testing plan.
=================================================================================*/
// IMPORTANT: Make sure that BEAPERNano.h is accessible as a tab in this project.
#include "BEAPERNano.h"   // Define BEAPER Nano I/O devices

// ---- State Constants -------------------
const int STATE_DISARMED = 0;        // Safe - waiting for arm code
const int STATE_ARMING   = 1;        // Exit delay - sensors ignored
const int STATE_ARMED    = 2;        // Sensors active - circuit dark
const int STATE_TRIPPED  = 3;        // Entry delay - enter code or alarm sounds
const int STATE_ALARM    = 4;        // Alarm sounding - enter code to disarm

// State names, indexed by the constants above - used for Serial output
const char* STATE_NAMES[] = { "DISARMED", "ARMING", "ARMED", "TRIPPED", "ALARM" };

// ---- Code Entry Result Constants ---------
const int CODE_INCOMPLETE = 0;       // Still entering - no result yet
const int CODE_CORRECT    = 1;       // Correct code entered
const int CODE_WRONG      = 2;       // Wrong code entered - entry reset

// ---- The Arm/Disarm Code -----------------
// 2, 3, 4, and 5 represent SW2, SW3, SW4, and SW5. Change these to
// choose your own code. Default: SW2, SW4, SW3, SW5.
const int CORRECT_1 = 2;
const int CORRECT_2 = 4;
const int CORRECT_3 = 3;
const int CORRECT_4 = 5;

// ---- Sensor Configuration ----------------
const int SENSOR_OPTICAL   = 0;
const int SENSOR_CONTACT   = 1;
const int SENSOR_MODE      = SENSOR_OPTICAL;  // SENSOR_OPTICAL or SENSOR_CONTACT
const int SENSOR_THRESHOLD = 3000;            // Optical: light change that indicates a trip

// Only used if SENSOR_MODE is SENSOR_CONTACT. Change if you wire the
// switch to a different header.
const int SENSOR_SWITCH_PIN = H1;

// ---- Timing Constants ---------------------
const int EXIT_DELAY     = 15000;    // Time to leave before arming (ms)
const int ENTRY_DELAY    = 10000;    // Time to enter code before alarm sounds (ms)
const int ALARM_DURATION = 60000;    // Alarm sounds for this long before re-arming (ms)
const int BEEP_INTERVAL  = 1000;     // Entry-delay countdown beep interval (ms)
const int FLASH_INTERVAL = 250;      // Urgent flash interval in TRIPPED/ALARM (ms)
const int BEEP_SHORT     = 80;       // Short neutral beep for key feedback (ms)
const int LOOP_DELAY     = 10;       // Main loop delay (ms)

// ---- Tone Constants -------------------------
const int TONE_KEY   = 880;          // Neutral key-press beep (Hz)
const int TONE_ALARM = 2000;         // Alarm tone frequency (Hz)

// ---- Program Variables -----------------------
int  state             = STATE_DISARMED;
unsigned long state_start = 0;

int  alarm_count        = 0;         // Number of alarms since last disarm
bool showing_count      = false;     // True while displaying alarm count on entry to DISARMED
unsigned long last_beep_time  = 0;   // Last entry-delay or countdown beep
unsigned long last_flash_time = 0;   // Last urgent flash toggle
bool flash_on           = false;     // Current urgent flash state

int  sensor_baseline    = 0;         // Sensor reading at the moment of arming

// Code entry, reused across DISARMED (arming) and TRIPPED/ALARM (disarming)
int  entry_step         = 0;         // Presses received so far in the current attempt (0-4)
int  entered_1          = 0;         // Digits recorded during the current attempt
int  entered_2          = 0;
int  entered_3          = 0;
int  entered_4          = 0;


// ---- Program Functions -----------------------

void all_leds_off()
{
    digitalWrite(LED2, LOW);
    digitalWrite(LED3, LOW);
    digitalWrite(LED4, LOW);
    digitalWrite(LED5, LOW);
}

void enter_state(int new_state, unsigned long current_time, const char* reason = "")
{
    all_leds_off();
    noTone(LS1);
    state       = new_state;
    state_start = current_time;
    flash_on    = false;
    entry_step  = 0;                 // Always start code entry fresh on a state change
    Serial.print("--> ");
    Serial.print(STATE_NAMES[new_state]);
    if (reason[0] != '\0')
    {
        Serial.print(" (");
        Serial.print(reason);
        Serial.println(")");
    }
    else
    {
        Serial.println();
    }
}

int read_button()
{
    // Return 2, 3, 4, or 5 if that button is currently pressed, or 0 if
    // none of the four code buttons are pressed. Reused from Activity
    // 12's capstone combination lock.
    if (digitalRead(SW2) == LOW)
        return 2;
    else if (digitalRead(SW3) == LOW)
        return 3;
    else if (digitalRead(SW4) == LOW)
        return 4;
    else if (digitalRead(SW5) == LOW)
        return 5;
    else
        return 0;
}

void wait_for_release()
{
    // Block until SW2, SW3, SW4, and SW5 are all released. Called
    // immediately after a press is detected.
    while (digitalRead(SW2) == LOW || digitalRead(SW3) == LOW ||
           digitalRead(SW4) == LOW || digitalRead(SW5) == LOW) {}
}

int check_code_entry()
{
    // Check for a button press and record it as part of the current
    // four-button code entry. Returns CODE_CORRECT once all four
    // digits have been entered and match the stored code, CODE_WRONG
    // once all four have been entered and do not match, or
    // CODE_INCOMPLETE while entry is still in progress.
    //
    // Like the Activity 12 capstone combination lock, correctness is
    // only checked once all four presses have been recorded - not
    // press by press - so a wrong attempt reveals nothing about which
    // digit was incorrect. This same function is used for both arming
    // (called from STATE_DISARMED) and disarming (called from
    // STATE_TRIPPED or STATE_ALARM), since the same code serves both
    // purposes.
    int pressed = read_button();
    if (pressed == 0)
        return CODE_INCOMPLETE;

    entry_step++;
    if (entry_step == 1)      entered_1 = pressed;
    else if (entry_step == 2) entered_2 = pressed;
    else if (entry_step == 3) entered_3 = pressed;
    else if (entry_step == 4) entered_4 = pressed;
    tone(LS1, TONE_KEY, BEEP_SHORT);
    wait_for_release();

    if (entry_step < 4)
        return CODE_INCOMPLETE;

    entry_step = 0;
    if (entered_1 == CORRECT_1 && entered_2 == CORRECT_2 &&
        entered_3 == CORRECT_3 && entered_4 == CORRECT_4)
    {
        return CODE_CORRECT;
    }
    else
    {
        Serial.println("    wrong code - entry reset");
        return CODE_WRONG;
    }
}

bool check_sensors()
{
    // Return true if the sensor detects a trip (door opened,
    // proximity detected). Adjust this function to match your
    // sensor configuration.
    if (SENSOR_MODE == SENSOR_OPTICAL)
    {
        // TODO: compare light_level() to sensor_baseline. Both a
        //       drop in light (an object blocking the sensor) and a
        //       rise (a reflective object approaching the sensor)
        //       can indicate a trip, so compare the absolute
        //       difference: abs(current - sensor_baseline) >
        //       SENSOR_THRESHOLD. Return true or false based on this
        //       comparison. If you are using Q1, Q2, or Q3 instead
        //       of Q4 (see the header comment), call that function
        //       here instead.
        return false;
    }
    else if (SENSOR_MODE == SENSOR_CONTACT)
    {
        // A normally-closed (NC) switch reads LOW when closed (door
        // shut) and HIGH when open (door opened), with the pin
        // configured INPUT_PULLUP.
        return digitalRead(SENSOR_SWITCH_PIN) == HIGH;
    }
    return false;
}

void take_sensor_baseline()
{
    // Read the current sensor level and store it as the armed
    // baseline. Called at the moment of arming so the baseline
    // reflects the closed/undisturbed state of the protected space.
    sensor_baseline = light_level();
    Serial.print("    sensor baseline: ");
    Serial.println(sensor_baseline);
}

void display_alarm_count(int count)
{
    // Show the number of alarms that occurred since last disarm.
    // Called on entry to STATE_DISARMED if count > 0.
    // TODO: implement a clear visual display of your choice - for
    //       example, flash LED2-LED5 together 'count' times with a
    //       pause between flashes, similar to Combination Safe's
    //       flash_attempts().
    Serial.print("*** ALARM COUNT: ");
    Serial.print(count);
    Serial.println(" alarm(s) since last disarm ***");
}


void setup()
{
    // Configure Arduino Nano ESP32 status LED as output
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, HIGH);  // Status LED on

    // Configure BEAPER Nano LEDs as outputs
    pinMode(LED2, OUTPUT);
    pinMode(LED3, OUTPUT);
    pinMode(LED4, OUTPUT);
    pinMode(LED5, OUTPUT);

    // Configure BEAPER Nano pushbuttons as inputs
    pinMode(SW2, INPUT_PULLUP);
    pinMode(SW3, INPUT_PULLUP);
    pinMode(SW4, INPUT_PULLUP);
    pinMode(SW5, INPUT_PULLUP);

    // Configure the sensor switch input, if used
    if (SENSOR_MODE == SENSOR_CONTACT)
        pinMode(SENSOR_SWITCH_PIN, INPUT_PULLUP);

    // Configure the ADC for 16-bit readings (0-65535), matching the
    // MicroPython board module's read_u16()-style scaling - see
    // Activity 9, GE1.
    analogReadResolution(16);

    Serial.begin(9600);
    delay(2000);                       // Give Serial Monitor time to
                                        // connect, without blocking
                                        // forever if it's never opened

    all_leds_off();

    Serial.println("Alarm System");
    Serial.print("Code: SW"); Serial.print(CORRECT_1);
    Serial.print(" SW"); Serial.print(CORRECT_2);
    Serial.print(" SW"); Serial.print(CORRECT_3);
    Serial.print(" SW"); Serial.println(CORRECT_4);
    Serial.println();

    state_start     = millis();
    last_flash_time = state_start;
    last_beep_time  = state_start;

    enter_state(STATE_DISARMED, state_start, "startup");
    digitalWrite(LED2, HIGH);          // LED2 on = disarmed indicator
}

void loop()
{
    unsigned long current_time = millis();
    unsigned long elapsed = current_time - state_start;

    if (state == STATE_DISARMED)
    {
        // Display the alarm count once on entry, if any alarms occurred
        if (alarm_count > 0 && !showing_count)
        {
            showing_count = true;
            display_alarm_count(alarm_count);
        }

        int result = check_code_entry();
        if (result == CODE_CORRECT)
        {
            // TODO: enter_state(STATE_ARMING, current_time, "armed"),
            //       call take_sensor_baseline() just before leaving
            //       this state so the baseline reflects the current
            //       (safe) reading, and reset alarm_count and
            //       showing_count to 0/false.
        }
    }

    else if (state == STATE_ARMING)
    {
        // Sensors are ignored during the exit delay - the user is leaving.
        // TODO: implement a countdown display using 'elapsed' and
        //       EXIT_DELAY. A simple approach: divide EXIT_DELAY into
        //       four equal segments. In the first quarter all four
        //       LEDs are on; by the last quarter only LED2 is on.
        // TODO: once elapsed >= (unsigned long)EXIT_DELAY, confirm
        //       arming with a short beep, turn off all LEDs (circuit
        //       goes dark while armed), and
        //       enter_state(STATE_ARMED, current_time).
    }

    else if (state == STATE_ARMED)
    {
        // Circuit is dark. Check sensors every loop iteration.
        // Buttons are not read here - a press while armed has no
        // effect (code entry only happens in DISARMED, TRIPPED, and
        // ALARM).
        if (check_sensors())
            enter_state(STATE_TRIPPED, current_time, "sensor tripped");
    }

    else if (state == STATE_TRIPPED)
    {
        // TODO: flash LED2-LED5 together at FLASH_INTERVAL using
        //       last_flash_time, the same repeating-timer pattern
        //       from Activity 12's alarm state.
        // TODO: beep briefly every BEEP_INTERVAL using
        //       last_beep_time, as a second independent timer
        //       running alongside the flash.

        int result = check_code_entry();
        if (result == CODE_CORRECT)
        {
            // TODO: disarm silently - no alarm recorded, since the
            //       user responded before the entry delay expired.
            //       enter_state(STATE_DISARMED, current_time, "disarmed")
            //       and turn LED2 on for the disarmed indicator.
        }

        // TODO: if elapsed >= (unsigned long)ENTRY_DELAY without a
        //       correct code, increment alarm_count and
        //       enter_state(STATE_ALARM, current_time, "entry delay expired").
    }

    else if (state == STATE_ALARM)
    {
        // TODO: flash LED2-LED5 at FLASH_INTERVAL using last_flash_time.
        // TODO: sound a continuous alarm tone on LS1. Consider
        //       alternating between two frequencies using a second
        //       independent timer for an attention-getting pattern -
        //       the same two-timers-in-one-state technique used for
        //       the flash and beep in Activity 12's alarm state,
        //       applied here to two different tones instead of a
        //       flash and a beep.

        int result = check_code_entry();
        if (result == CODE_CORRECT)
        {
            // TODO: enter_state(STATE_DISARMED, current_time, "disarmed")
            //       and turn LED2 on. Do not increment alarm_count
            //       again - it was already recorded when the alarm
            //       was triggered.
        }

        // TODO: if elapsed >= (unsigned long)ALARM_DURATION without a
        //       correct code, enter_state(STATE_ARMED, current_time,
        //       "alarm timeout") to re-arm - the intruder has not
        //       disarmed the system.
    }

    delay(LOOP_DELAY);
}


/* ================================================================================
Development Guide
================================================================================

Work through these steps in order. Test each step thoroughly before
continuing - a working partial system is always better than a broken
complete one.

--------------------------------------------------------------------------------
Step 1 - Sensor configuration and baseline
--------------------------------------------------------------------------------

Choose your sensor mode and implement 'check_sensors()'.

For optical mode: mount the sensor facing the door or opening. Run
the program, open the door slowly, and print the sensor reading
every loop iteration to find the typical range of values when
undisturbed vs. disturbed. Set SENSOR_THRESHOLD to a value
comfortably between the two.

For contact mode: wire your NC switch to H1 (or another header -
update SENSOR_SWITCH_PIN if so) and GND. Verify that
'check_sensors()' returns true when the door is open and false when
closed. If using a mechanical switch, watch for bounce right at the
moment of the transition - see the header comment's note on Option B.

--------------------------------------------------------------------------------
Step 2 - Disarmed state and code entry
--------------------------------------------------------------------------------

Implement the arm transition from STATE_DISARMED. Code entry itself
is already handled by 'check_code_entry()' - you only need to act on
the CODE_CORRECT result. Test carefully:
- Correct sequence transitions to ARMING
- Wrong sequence resets silently (stays in DISARMED, no feedback
  beyond the neutral key beeps already heard during entry)
- A partial sequence followed by the correct remaining digits works

--------------------------------------------------------------------------------
Step 3 - Arming (exit delay)
--------------------------------------------------------------------------------

Implement the countdown in STATE_ARMING. Test that sensors are
genuinely ignored during the exit delay by triggering them while the
countdown runs. Verify the circuit goes dark when ARMED.

--------------------------------------------------------------------------------
Step 4 - Armed and tripped
--------------------------------------------------------------------------------

Implement the entry delay in STATE_TRIPPED. Test the full
arm -> trip -> disarm sequence:
- Arm the system
- Trigger the sensor
- Enter the code within ENTRY_DELAY
- Verify STATE_DISARMED is reached with no alarm recorded

--------------------------------------------------------------------------------
Step 5 - Alarm and re-arm
--------------------------------------------------------------------------------

Implement STATE_ALARM. Test the full arm -> trip -> timeout -> alarm
-> re-arm sequence. Verify alarm_count increments correctly and is
displayed on the next successful disarm.

--------------------------------------------------------------------------------
Step 6 - Alarm count display
--------------------------------------------------------------------------------

Implement 'display_alarm_count()' with a visible LED display, not
just the Serial message already provided. Verify the count is
accurate and clears after being shown.

*/


/* ================================================================================
Extension Activities
================================================================================

--------------------------------------------------------------------------------
EA 1 - Acknowledge and clear the alarm count
--------------------------------------------------------------------------------

After the alarm count is displayed on entry to DISARMED, require a
button press to acknowledge it before accepting a new arm code. What
happens currently if the user starts entering a new code while the
count is still displaying?

--------------------------------------------------------------------------------
EA 2 - Tamper protection
--------------------------------------------------------------------------------

If SENSOR_MODE is SENSOR_CONTACT and the sensor trips while in
STATE_ARMED, add a check that the sensor is still tripped a short
time later before transitioning to STATE_TRIPPED - a very brief trip
could indicate a tamper attempt rather than genuine entry. Log tamper
attempts separately from alarm_count.

--------------------------------------------------------------------------------
EA 3 - Multiple sensors
--------------------------------------------------------------------------------

Extend 'check_sensors()' to read both an optical sensor and a
contact switch, returning true if either is triggered. Print which
sensor tripped to the Serial Monitor for debugging.

--------------------------------------------------------------------------------
EA 4 - Changeable code
--------------------------------------------------------------------------------

Add a mode (triggered by a special button sequence from DISARMED)
that lets the user change the arm/disarm code. CORRECT_1-4 are
declared 'const int', which cannot be reassigned while the program
runs - the first step is changing them to plain 'int' variables, the
same way Combination Safe uses DEFAULT_CODE_1-4 (fixed starting
point) alongside code_1-4 (the current, changeable code). Once they
are plain variables, how will the new code persist if the board
loses power? A fully persistent version would write the new code to
EEPROM or flash storage, which is covered in the intermediate
activities.

--------------------------------------------------------------------------------
EA 5 - Panic button
--------------------------------------------------------------------------------

SW5 held for 3 seconds in any state immediately transitions to
STATE_ALARM and increments alarm_count, simulating a manual
panic/duress feature found in real alarm systems. You will need the
button-hold-detection pattern from Activity 11, checked independently
of 'check_code_entry()' since SW5 is also one of the four code
digits. What changes does this require to avoid a held SW5 being
misread as a code digit at the same time?

*/
