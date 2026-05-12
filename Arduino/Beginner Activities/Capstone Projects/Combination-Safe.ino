/* ================================================================================
Capstone Project: Combination Safe [BEAPERNano-Capstone-Combination-Safe]
May 11, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPERNano.h header file

Hardware used:
  SW2-SW5    - Code entry buttons (all four used as code digits)
  LED2       - Code-setting mode indicator (on while setting code)
  LED5       - Attempt counter indicator (flashes on unlock if attempts > 0)
  LS1        - Piezo speaker (key feedback, code set, unlock, wrong code tones)
  Servo on H9 or H10 - Locking mechanism (LOCKED_ANGLE / UNLOCKED_ANGLE)

Door sensor options (choose one):
  Option A - Optical proximity sensor (contactless):
    Set JP1 to Enviro. to use Q4 (ambient light sensor). Mount so the
    sensor detects the door closing. Set SENSOR_MODE = OPTICAL.
    Calibrate SENSOR_THRESHOLD for your setup.

  Option B - Hard-wired contact switch on expansion header:
    Wire a normally-closed (NC) or normally-open (NO) magnetic contact
    to H1 (or H2, H3, H4) and GND. Set SENSOR_MODE = CONTACT and
    SENSOR_CLOSED_VALUE to match your switch type (LOW for NC, HIGH for NO).

Compatible with all BEAPER Nano configurations.
--------------------------------------------------------------------------------
Safe behaviour:
  UNLOCKED  - Servo open. Any number of failed unlock attempts are logged
              silently. Hold SW2 for 2 seconds to enter code-setting mode.
              Door closing (sensor) automatically locks if a code is set.

  SETTING   - LED2 on. Enter any four button presses to set the new code.
              Each press beeps for confirmation. After four presses the code
              is saved, LED2 turns off, and the safe returns to UNLOCKED.
              The safe remains physically unlocked throughout.

  LOCKED    - Each button press beeps neutrally. After four presses:
              correct code -> unlock tone, servo opens, attempt flash if any.
              wrong code   -> silence, counter increments, entry resets.
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
#include <Servo.h>

// ---- State Constants -----------------
const int STATE_UNLOCKED = 0;  // Servo open - safe accessible
const int STATE_SETTING  = 1;  // Memorizing new 4-digit code (stays unlocked)
const int STATE_LOCKED   = 2;  // Servo closed - awaiting correct code

const char* STATE_NAMES[] = { "UNLOCKED", "SETTING", "LOCKED" };

// ---- Sensor Configuration ------------
const int OPTICAL = 0;
const int CONTACT = 1;
const int SENSOR_MODE         = OPTICAL;  // Change to CONTACT for hard-wired switch
const int SENSOR_PIN          = H1;       // Header pin for contact switch (Option B)
const int SENSOR_THRESHOLD    = 30;       // Optical: ADC change indicating door closed
const int SENSOR_CLOSED_VALUE = LOW;      // Contact: pin value when door CLOSED

// ---- Servo Configuration -------------
// Adjust these angles to match your servo mounting and locking mechanism.
// Test with the servo disconnected from the locking bar first.
const int LOCKED_ANGLE   = 0;    // Servo angle (degrees) when locked
const int UNLOCKED_ANGLE = 90;   // Servo angle (degrees) when unlocked

Servo safe_servo;                 // Servo object - attach in setup()
const int SERVO_PIN = H9;        // Change to H10 if using that header

// ---- Code Constants ------------------
const int CODE_LENGTH = 4;        // Fixed code length

// ---- Timing Constants ----------------
const unsigned long HOLD_TIME  = 2000;  // SW2 hold to enter code-setting (ms)
const int           BEEP_SHORT = 80;    // Short neutral key beep (ms)
const int           LOOP_DELAY = 10;    // Main loop delay (ms)

// ---- Tone Constants ------------------
const int TONE_KEY     = 880;   // Neutral key-press beep (Hz)
const int TONE_SETTING = 1200;  // Code-setting mode entry confirmation (Hz)
const int TONE_UNLOCK  = 1047;  // Correct code / unlock tone (Hz) - C6
const int TONE_WRONG   = 220;   // Wrong code tone (Hz)

// ---- Hardware Maps -------------------
const int BUTTONS[] = { SW2, SW3, SW4, SW5 };
const int LEDS[]    = { LED2, LED3, LED4, LED5 };

// ---- Program Variables ---------------
int           state          = STATE_UNLOCKED;
unsigned long state_start    = 0;

int           code[CODE_LENGTH];          // Current stored code (button indices 0-3)
bool          code_set       = false;     // True once a code has been set
int           entry[CODE_LENGTH];         // Current button presses being entered
int           entry_index    = 0;         // Presses received in current entry
int           attempt_count  = 0;         // Wrong attempts since last unlock

// SW2 hold detection
bool          sw2_down       = false;
unsigned long sw2_down_time  = 0;
bool          hold_fired     = false;

// Edge detection
int           last_buttons[] = { HIGH, HIGH, HIGH, HIGH };

// Sensor baseline
int           sensor_baseline = 0;


// ---- Program Functions ---------------

void all_leds_off()
{
    digitalWrite(LED2, LOW);
    digitalWrite(LED5, LOW);
}

void enter_state(int new_state, unsigned long current_time, const char* reason = "")
{
    state       = new_state;
    state_start = current_time;
    entry_index = 0;
    hold_fired  = false;
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

int read_any_press()
{
    // Return index (0-3) of a button that just transitioned to pressed,
    // or -1 if no new press. Updates last_buttons for edge detection.
    for (int i = 0; i < 4; i++)
    {
        int current = digitalRead(BUTTONS[i]);
        if (current == LOW && last_buttons[i] == HIGH)
        {
            last_buttons[i] = LOW;
            return i;
        }
        if (current == HIGH)
            last_buttons[i] = HIGH;
    }
    return -1;
}

bool door_is_closed()
{
    if (SENSOR_MODE == OPTICAL)
    {
        // TODO: compare current light_level() to sensor_baseline.
        //       Return true if the difference exceeds SENSOR_THRESHOLD.
        return false;  // Replace with threshold comparison
    }
    else if (SENSOR_MODE == CONTACT)
    {
        return (digitalRead(SENSOR_PIN) == SENSOR_CLOSED_VALUE);
    }
    return false;
}

void take_sensor_baseline()
{
    sensor_baseline = light_level();
    Serial.print("    sensor baseline: ");
    Serial.println(sensor_baseline);
}

void flash_attempts(int count)
{
    // Flash LED5 'count' times, then clear. Called after unlocking.
    // TODO: implement the flash sequence.
    // Each flash: LED5 on for 200ms, off for 200ms.
    // After all flashes, a longer pause, then LED5 off.
    Serial.print("    attempts since last unlock: ");
    Serial.println(count);
}

bool code_matches(int entered[])
{
    for (int i = 0; i < CODE_LENGTH; i++)
    {
        if (entered[i] != code[i])
            return false;
    }
    return true;
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

    safe_servo.attach(SERVO_PIN);
    safe_servo.write(UNLOCKED_ANGLE);

    Serial.begin(9600);
    while (!Serial);

    take_sensor_baseline();

    Serial.println("Combination Safe");
    Serial.println("Hold SW2 for 2s to set code");
    Serial.println("No code set - door will not lock until code is set");
    Serial.println();

    state_start = millis();
    enter_state(STATE_UNLOCKED, state_start, "startup");
}

void loop()
{
    unsigned long current_time = millis();
    unsigned long elapsed      = current_time - state_start;
    int           pressed      = read_any_press();

    // ---- SW2 hold detection (active in UNLOCKED only) ----
    if (state == STATE_UNLOCKED)
    {
        int sw2_current = digitalRead(SW2);
        if (sw2_current == LOW && !sw2_down)
        {
            sw2_down      = true;
            sw2_down_time = current_time;
            hold_fired    = false;
        }
        else if (sw2_current == HIGH)
        {
            sw2_down   = false;
            hold_fired = false;
        }
        if (sw2_down && !hold_fired &&
            (current_time - sw2_down_time) >= HOLD_TIME)
        {
            hold_fired = true;
            tone(LS1, TONE_SETTING, 300);
            digitalWrite(LED2, HIGH);
            enter_state(STATE_SETTING, current_time, "SW2 held - setting code");
        }
    }

    // ---- State: Unlocked ----
    if (state == STATE_UNLOCKED)
    {
        if (code_set && door_is_closed())
        {
            safe_servo.write(LOCKED_ANGLE);
            enter_state(STATE_LOCKED, current_time, "door closed");
        }
    }

    // ---- State: Setting new code ----
    else if (state == STATE_SETTING)
    {
        if (pressed != -1)
        {
            entry[entry_index] = pressed;
            entry_index++;
            tone(LS1, TONE_KEY, BEEP_SHORT);
            Serial.print("    code digit ");
            Serial.print(entry_index);
            Serial.println(" set");

            if (entry_index == CODE_LENGTH)
            {
                // TODO: copy entry[] into code[] and set code_set = true.
                // TODO: sound the code-set confirmation tone (TONE_SETTING).
                // TODO: turn off LED2 and enter STATE_UNLOCKED.
            }
        }
    }

    // ---- State: Locked ----
    else if (state == STATE_LOCKED)
    {
        if (pressed != -1)
        {
            entry[entry_index] = pressed;
            entry_index++;
            tone(LS1, TONE_KEY, BEEP_SHORT);

            if (entry_index == CODE_LENGTH)
            {
                entry_index = 0;
                if (code_matches(entry))
                {
                    // TODO: sound TONE_UNLOCK, write UNLOCKED_ANGLE to servo,
                    //       and enter STATE_UNLOCKED. Call flash_attempts() if
                    //       attempt_count > 0 and reset attempt_count to 0.
                }
                else
                {
                    // TODO: increment attempt_count and sound a brief TONE_WRONG.
                    //       Do NOT give any visible feedback - silent reset only.
                }
            }
        }
    }

    delay(LOOP_DELAY);
}


/*
Capstone Development Guide

Work through these steps in order. Fully test each step before
proceeding to the next.

Step 1 - Servo setup and angles
  Before any state logic, verify your servo moves correctly.
  Temporarily add these lines at the end of setup() and run:

    delay(2000);
    safe_servo.write(LOCKED_ANGLE);
    delay(2000);
    safe_servo.write(UNLOCKED_ANGLE);

  Adjust LOCKED_ANGLE and UNLOCKED_ANGLE until the servo moves your
  locking bar or bolt to the correct positions. Remove the test lines
  when satisfied.

Step 2 - Button edge detection
  Verify that read_any_press() returns the correct index (0-3) exactly
  once per physical press, not repeatedly while held. Add a temporary
  Serial.println() inside the function to confirm each button maps to
  the expected index.

Step 3 - Door sensor calibration
  Choose your sensor mode and implement door_is_closed(). For optical
  mode, print light_level() while opening and closing the door to find
  the right threshold. For contact mode, verify the pin value is correct
  for both door states. Confirm door_is_closed() returns true only when
  the door is physically closed.

Step 4 - Code setting
  Implement the code commit block in STATE_SETTING. Test:
  - LED2 lights on SW2 hold and turns off after four presses
  - Each press produces a short beep
  - A new code can be set by repeating the hold process
  - The servo remains in UNLOCKED_ANGLE throughout

Step 5 - Locking
  With a code set, close the door (or simulate the sensor) and verify
  the servo moves to LOCKED_ANGLE and the state changes to LOCKED.
  Print sensor readings to confirm the threshold is working.

Step 6 - Code entry and unlock
  Implement the correct and wrong branches in STATE_LOCKED. Test:
  - Correct code: servo opens, state returns to UNLOCKED
  - Wrong code: silence, no visible feedback, entry resets
  - Correct code after wrong attempts: flash_attempts() fires
    and attempt_count resets to 0

Step 7 - Attempt display
  Implement flash_attempts(). Three slow flashes of LED5 is a natural
  choice. Verify the count is accurate and clears after display.

Step 8 - Extensions

  a) Auto-relock after timeout: after unlocking, if the door sensor
     shows the door has been open for RELOCK_TIMEOUT milliseconds,
     sound a warning beep and re-lock automatically.

  b) Lockout after repeated failures: after LOCKOUT_ATTEMPTS wrong
     codes in a row, ignore all button presses for LOCKOUT_TIME
     milliseconds. Flash LED5 continuously during lockout.

  c) Variable code length (up to 8 digits): replace the fixed
     CODE_LENGTH with a variable. In code-setting mode, accept presses
     until SW2 is held briefly to commit rather than a fixed count.
     Resize the entry[] and code[] arrays to 8 elements.

  d) Code change confirmation: require the existing code before
     allowing a new one to be set. Add a verification step between
     the SW2 hold and STATE_SETTING.

*/
