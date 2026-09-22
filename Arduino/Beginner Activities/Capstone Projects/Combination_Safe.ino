/* ================================================================================
Capstone Project: Combination Safe [BEAPERNano-Capstone-Combination-Safe]
Version: 1.0
Updated: July 25, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPERNano.h header file

A four-digit digital safe. SW2, SW3, SW4, and SW5 are the code
buttons - any of the four can appear at any position in the code,
and digits may repeat. Enter the correct four-button sequence to
unlock; a wrong sequence resets silently with no visible feedback,
so a would-be intruder learns nothing about which digit was wrong.
The number of wrong attempts since the last successful unlock is
logged silently and shown briefly the next time the safe opens.

Hardware used:
  SW2-SW5    - Code entry buttons (all four used as code digits)
  LED2       - Code-setting mode indicator (on while setting a new code)
  LED5       - Attempt counter indicator (flashes after unlock if
               any wrong attempts were logged)
  LS1        - Piezo speaker (key feedback, code-set, unlock, wrong-code tones)
  Servo on H5 - Locking mechanism, using the Arduino Servo library

IMPORTANT - Header pin sharing: H5-H8 are electrically the same
pins as H1-H4 (H5=H1, H6=H4, H7=H2, H8=H3 - see BEAPERNano.h). If
you choose the door-sensor Option B (contact switch) below, wire it
to a header that is NOT aliased to whichever servo header you use,
or the two will conflict. With the default servo on H5, use H2, H3,
or H4 for the contact switch, not H1.

Door sensor options (choose one):
  Option A - Optical proximity sensor (contactless):
    Two sub-choices, depending on which jumper position you use -
    these share jumpers with other sensors, so only one is
    available at a time:
      - Q4 (ambient light sensor, JP1 set to Enviro.): detects the
        door by the change in ambient room light as it swings shut.
        Simple to mount, but the threshold depends on your room's
        lighting and may need recalibrating if that changes.
      - Q1, Q2, or Q3 (break-away floor/line sensors, matching
        jumper set to Robot): detects the door by reflectivity as
        a surface on the door approaches the sensor, the same way
        these sensors detect a floor or line on the robot
        platforms. More consistent regardless of room lighting,
        but needs the sensor mounted close enough to the door to
        pick up a clear reflectivity change as it closes.
    Either way, set SENSOR_MODE to SENSOR_OPTICAL and calibrate
    SENSOR_THRESHOLD for your setup - see take_sensor_baseline()
    and Step 3 in the Development Guide below. Change
    'light_level()' to 'Q1_level()' (or Q2/Q3) in both functions if
    you use a floor/line sensor instead of Q4.

  Option B - Contact switch on an expansion header:
    A magnetic contact switch (reed switch) or a simple mechanical
    switch (lever, roller, or pushbutton-style) both work here -
    wire it to a spare header (see the pin-sharing note above) and
    GND. Set SENSOR_MODE to SENSOR_CONTACT and SENSOR_CLOSED_VALUE
    to match your switch type (LOW for NC, HIGH for NO).

    Mechanical switches are more likely to be available in a
    school's parts bins than magnetic reed switches, but their
    contacts can bounce - producing several rapid open/close
    readings over a few milliseconds as the contact settles, rather
    than one clean transition. Reed switches usually bounce less,
    but are not guaranteed to be bounce-free either. If
    'door_is_closed()' behaves inconsistently right at the moment
    the door closes, this is the likely cause - Activity 11 EA1's
    debounce pattern is the tool for this, applied to
    'digitalRead(DOOR_SWITCH_PIN)' instead of a pushbutton.

Safe behaviour:
  UNLOCKED  - Servo open. Hold SW2 for HOLD_TIME to enter
              code-setting mode. If a code has been set, the door
              sensor closing locks the safe automatically.

  SETTING   - LED2 on. Any four button presses set the new code -
              correctness does not apply while setting a code, only
              while verifying one. Each press beeps for
              confirmation. After the fourth press the new code is
              saved and the safe returns to UNLOCKED, still open.

  ENTRY_1-4 - Door is locked. Each press beeps neutrally with no
              indication of correctness. After the fourth press:
              correct code -> unlock tone, servo opens, any logged
              attempts flash on LED5, attempt count resets to 0.
              wrong code   -> silence, attempt count increments,
              entry silently restarts at ENTRY_1.

Before you begin - complete your capstone plan using the Capstone
Preparation Guide: project description, state diagram, state
details table, constants and variables, and testing plan.
=================================================================================*/
// IMPORTANT: Make sure that BEAPERNano.h is accessible as a tab in this project.
#include "BEAPERNano.h"   // Define BEAPER Nano I/O devices
#include <Servo.h>

// ---- State Constants -------------------
const int STATE_UNLOCKED = 0;        // Servo open - safe accessible
const int STATE_SETTING  = 1;        // Recording a new code (stays unlocked)
const int STATE_ENTRY_1  = 2;        // Locked, awaiting the first digit
const int STATE_ENTRY_2  = 3;        // Locked, awaiting the second digit
const int STATE_ENTRY_3  = 4;        // Locked, awaiting the third digit
const int STATE_ENTRY_4  = 5;        // Locked, awaiting the fourth digit

// State names, indexed by the constants above - used for Serial output
const char* STATE_NAMES[] = { "UNLOCKED", "SETTING", "ENTRY_1", "ENTRY_2", "ENTRY_3", "ENTRY_4" };

// ---- Sensor Configuration ---------------
const int SENSOR_OPTICAL       = 0;
const int SENSOR_CONTACT       = 1;
const int SENSOR_MODE          = SENSOR_OPTICAL;   // SENSOR_OPTICAL or SENSOR_CONTACT
const int SENSOR_THRESHOLD     = 3000;             // Optical: light drop that indicates door closed
const int SENSOR_CLOSED_VALUE  = LOW;              // Contact: pin value when door is CLOSED (LOW=NC, HIGH=NO)

// Only used if SENSOR_MODE is SENSOR_CONTACT. Change to whichever
// header you wired the switch to (see the pin-sharing note above).
const int DOOR_SWITCH_PIN = H2;

// ---- Servo Configuration -----------------
// Adjust these angles to match your servo mounting and locking
// mechanism. Test with the servo disconnected from the locking bar
// first - see Step 1 in the Development Guide below.
const int LOCKED_ANGLE   = 0;        // Servo angle (degrees) when locked
const int UNLOCKED_ANGLE = 90;       // Servo angle (degrees) when unlocked

Servo lockServo;                     // Attached to H5 in setup() - change if needed

// ---- Code Constants -----------------------
// The starting code, used until a new one is set via STATE_SETTING.
// 2, 3, 4, and 5 represent SW2, SW3, SW4, and SW5 - change these to
// choose your own starting combination. Digits may repeat.
const int DEFAULT_CODE_1 = 2;
const int DEFAULT_CODE_2 = 3;
const int DEFAULT_CODE_3 = 4;
const int DEFAULT_CODE_4 = 5;

// ---- Timing Constants ---------------------
const int LOOP_DELAY  = 10;          // Main loop delay (ms)
const int HOLD_TIME   = 2000;        // SW2 hold duration to enter code-setting mode (ms)
const int BEEP_SHORT  = 80;          // Short neutral beep duration for key feedback (ms)

// ---- Tone Constants ------------------------
const int TONE_KEY      = 880;       // Neutral key-press beep (Hz)
const int TONE_SETTING  = 1200;      // Code-setting mode entry/confirmation tone (Hz)
const int TONE_UNLOCK   = 1047;      // Correct code / unlock tone (Hz) - C6
const int TONE_WRONG    = 220;       // Wrong code tone (Hz) - brief, then silence

// ---- Program Variables ---------------------
int  state            = STATE_UNLOCKED;
unsigned long state_start = 0;

// The currently stored code. Starts at the DEFAULT_CODE values above,
// and is overwritten when a new code is set in STATE_SETTING.
int  code_1            = DEFAULT_CODE_1;
int  code_2            = DEFAULT_CODE_2;
int  code_3            = DEFAULT_CODE_3;
int  code_4            = DEFAULT_CODE_4;
bool code_set          = false;      // True once a code has been set at least once

int  entered_1          = 0;         // Digits recorded during the current attempt
int  entered_2          = 0;
int  entered_3          = 0;
int  entered_4          = 0;

int  entry_step         = 0;         // Presses received so far in STATE_SETTING (0-4)
int  attempt_count      = 0;         // Wrong attempts since the last unlock

// SW2 hold detection (active only in STATE_UNLOCKED) - the same
// three-variable pattern used for tap/hold detection in Activity 11.
bool sw2_down           = false;
unsigned long sw2_down_time = 0;

int  sensor_baseline    = 0;         // Optical mode: light level with the door open


// ---- Program Functions -----------------------

void all_leds_off()
{
    digitalWrite(LED2, LOW);
    digitalWrite(LED5, LOW);
}

void enter_state(int new_state, unsigned long current_time, const char* reason = "")
{
    state = new_state;
    state_start = current_time;
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
    // none of the four code buttons are pressed.
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
    // immediately after a press is detected - see Activity 12, GE4.
    while (digitalRead(SW2) == LOW || digitalRead(SW3) == LOW ||
           digitalRead(SW4) == LOW || digitalRead(SW5) == LOW) {}
}

void take_sensor_baseline()
{
    // Records the optical sensor's reading with the door open, as a
    // reference point for door_is_closed()'s threshold comparison.
    // Change light_level() to Q1_level() (or Q2/Q3) here too if you
    // are using a floor/line sensor instead of Q4.
    sensor_baseline = light_level();
    Serial.print("    sensor baseline: ");
    Serial.println(sensor_baseline);
}

bool door_is_closed()
{
    // Return true if the door sensor indicates the door is closed.
    if (SENSOR_MODE == SENSOR_OPTICAL)
    {
        // TODO: compare light_level() to sensor_baseline. A drop in
        //       light large enough to exceed SENSOR_THRESHOLD means
        //       the door has closed and is now blocking the sensor.
        //       Return true or false based on this comparison. If
        //       you are using Q1, Q2, or Q3 instead of Q4 (see the
        //       header comment), call that function here instead -
        //       the rest of the comparison works the same way.
        return false;
    }
    else if (SENSOR_MODE == SENSOR_CONTACT)
    {
        return digitalRead(DOOR_SWITCH_PIN) == SENSOR_CLOSED_VALUE;
    }
    return false;
}

void flash_attempts(int count)
{
    // Flash LED5 'count' times to show logged wrong attempts, then
    // clear it. Called immediately after a successful unlock.
    // TODO: implement the flash sequence - for example, LED5 on for
    //       200ms, off for 200ms, repeated 'count' times, then off.
    Serial.print("    attempts since last unlock: ");
    Serial.println(count);
}


void setup()
{
    // Configure Arduino Nano ESP32 status LED as output
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, HIGH);  // Status LED on

    // Configure BEAPER Nano LEDs as outputs
    pinMode(LED2, OUTPUT);
    pinMode(LED5, OUTPUT);

    // Configure BEAPER Nano pushbuttons as inputs
    pinMode(SW2, INPUT_PULLUP);
    pinMode(SW3, INPUT_PULLUP);
    pinMode(SW4, INPUT_PULLUP);
    pinMode(SW5, INPUT_PULLUP);

    // Configure the door switch input, if used
    if (SENSOR_MODE == SENSOR_CONTACT)
        pinMode(DOOR_SWITCH_PIN, INPUT_PULLUP);

    Serial.begin(9600);
    delay(2000);                       // Give Serial Monitor time to
                                        // connect, without blocking
                                        // forever if it's never opened

    all_leds_off();
    lockServo.attach(H5);               // Change to another header if needed
    lockServo.write(UNLOCKED_ANGLE);    // Start unlocked - see Development Guide Step 1
    take_sensor_baseline();

    Serial.println("Combination Safe");
    Serial.print("Hold SW2 for ");
    Serial.print(HOLD_TIME);
    Serial.println(" ms to set a new code");
    if (!code_set)
        Serial.println("No code set yet - safe will not lock until a code is set");
    Serial.println();

    state_start = millis();
    enter_state(STATE_UNLOCKED, state_start, "startup");
}

void loop()
{
    unsigned long current_time = millis();

    if (state == STATE_UNLOCKED)
    {
        // SW2 hold detection - reused from Activity 11's tap/hold pattern
        int sw2_current = digitalRead(SW2);
        if (sw2_current == LOW && !sw2_down)
        {
            sw2_down = true;
            sw2_down_time = current_time;
        }
        else if (sw2_current == HIGH)
        {
            sw2_down = false;
        }

        if (sw2_down && (current_time - sw2_down_time) >= (unsigned long)HOLD_TIME)
        {
            sw2_down = false;
            entry_step = 0;
            tone(LS1, TONE_SETTING, 300);
            enter_state(STATE_SETTING, current_time, "SW2 held");
            digitalWrite(LED2, HIGH);
        }

        // TODO: if the program is still in STATE_UNLOCKED at this
        //       point (the hold above may have just changed it -
        //       check state again) and code_set is true, call
        //       door_is_closed(). If it returns true, call
        //       lockServo.write(LOCKED_ANGLE) and
        //       enter_state(STATE_ENTRY_1, current_time, "door closed").
    }

    else if (state == STATE_SETTING)
    {
        int pressed = read_button();
        if (pressed != 0)
        {
            entry_step++;
            if (entry_step == 1)      entered_1 = pressed;
            else if (entry_step == 2) entered_2 = pressed;
            else if (entry_step == 3) entered_3 = pressed;
            else if (entry_step == 4) entered_4 = pressed;
            tone(LS1, TONE_KEY, BEEP_SHORT);
            wait_for_release();

            // TODO: once entry_step reaches 4, copy entered_1-4 into
            //       code_1-4, set code_set = true, sound TONE_SETTING
            //       briefly to confirm the new code, turn LED2 off,
            //       and enter_state(STATE_UNLOCKED, current_time, "code set").
        }
    }

    else if (state == STATE_ENTRY_1)
    {
        // This state is fully implemented as a model. ENTRY_2 and
        // ENTRY_3 below follow exactly the same pattern - write
        // those yourself before attempting ENTRY_4, which is
        // different.
        int pressed = read_button();
        if (pressed != 0)
        {
            entered_1 = pressed;
            tone(LS1, TONE_KEY, BEEP_SHORT);
            wait_for_release();
            enter_state(STATE_ENTRY_2, current_time);
        }
    }

    else if (state == STATE_ENTRY_2)
    {
        // TODO: follow the same pattern as STATE_ENTRY_1 above -
        //       read a button, record it as entered_2, beep, wait
        //       for release, then enter_state(STATE_ENTRY_3, current_time).
    }

    else if (state == STATE_ENTRY_3)
    {
        // TODO: follow the same pattern again - record entered_3,
        //       beep, wait for release, then
        //       enter_state(STATE_ENTRY_4, current_time).
    }

    else if (state == STATE_ENTRY_4)
    {
        // TODO: read a button and record it as entered_4, beep, and
        //       wait for release, following the same pattern as the
        //       states above. Then compare entered_1, entered_2,
        //       entered_3, and entered_4 against code_1, code_2,
        //       code_3, and code_4:
        //
        //       If all four match:
        //         - sound TONE_UNLOCK
        //         - call lockServo.write(UNLOCKED_ANGLE)
        //         - enter_state(STATE_UNLOCKED, current_time, "unlocked")
        //         - if attempt_count > 0, call flash_attempts(attempt_count)
        //         - reset attempt_count to 0
        //
        //       If any digit does not match:
        //         - increment attempt_count
        //         - sound TONE_WRONG briefly - no LEDs, no other feedback
        //         - enter_state(STATE_ENTRY_1, current_time, "wrong code")
    }

    delay(LOOP_DELAY);
}


/* ================================================================================
Development Guide
================================================================================

Work through these steps in order. Fully test each step before
moving to the next - a capstone this size is much easier to debug
in small pieces than all at once at the end.

--------------------------------------------------------------------------------
Step 1 - Servo setup and angles
--------------------------------------------------------------------------------

Before any state logic, verify your servo moves correctly. The
program already attaches the servo and moves it to UNLOCKED_ANGLE at
startup, using the Arduino Servo library from Activity 10's Servo
Controller project. Temporarily add these lines right after that,
and run the program:

Example code:

delay(2000);
lockServo.write(LOCKED_ANGLE);
delay(2000);
lockServo.write(UNLOCKED_ANGLE);

Adjust LOCKED_ANGLE and UNLOCKED_ANGLE until the servo moves your
locking bar or bolt to the correct positions. Remove the test lines
above once you are satisfied, and use 'lockServo.write(angle)'
everywhere the TODOs mention moving the servo.

--------------------------------------------------------------------------------
Step 2 - Button reading
--------------------------------------------------------------------------------

Verify that 'read_button()' returns the correct number (2-5) for
each of SW2-SW5, and 0 when nothing is pressed. Add a temporary
Serial.println() after the STATE_ENTRY_1 block's
'int pressed = read_button();' line to confirm this before relying
on it elsewhere.

--------------------------------------------------------------------------------
Step 3 - Door sensor calibration
--------------------------------------------------------------------------------

Choose your sensor mode and implement 'door_is_closed()'. For
optical mode, print 'light_level()' (or Q1/Q2/Q3, whichever you
chose) while opening and closing the door to find a
SENSOR_THRESHOLD that reliably distinguishes the two. For contact
mode, test that 'digitalRead(DOOR_SWITCH_PIN)' returns the expected
reading for both open and closed. Verify 'door_is_closed()' returns
true only when the door is actually closed, in both directions of
travel.

If you are using a mechanical contact switch, watch closely for
bounce right at the moment the door closes - print
'digitalRead(DOOR_SWITCH_PIN)' on every loop iteration for a second
or two around the transition and look for rapid flickering rather
than one clean change. See the header comment's note on Option B
for what to do if you find it.

--------------------------------------------------------------------------------
Step 4 - Code setting
--------------------------------------------------------------------------------

Implement the code-commit TODO in STATE_SETTING. Test:
- LED2 lights when SW2 is held for HOLD_TIME, and turns off after
  the fourth press
- Each of the four presses produces a short beep
- A different code can be set by repeating the hold process
- The safe remains physically unlocked throughout code-setting

--------------------------------------------------------------------------------
Step 5 - Entry states and locking
--------------------------------------------------------------------------------

Complete STATE_ENTRY_2 and STATE_ENTRY_3 by following
STATE_ENTRY_1's pattern. With a code set, close the door (or
simulate the sensor) and verify the servo moves to LOCKED_ANGLE and
the state transitions to ENTRY_1. Print the sensor reading and the
result of 'door_is_closed()' during this test if the threshold
needs adjusting.

--------------------------------------------------------------------------------
Step 6 - Code entry and unlock
--------------------------------------------------------------------------------

Implement the correct and wrong-code branches in STATE_ENTRY_4.
Test the complete lock/unlock cycle:
- Set a code from UNLOCKED
- Close the door (auto-locks)
- Enter the correct code - servo should open
- Enter a wrong code - silence, no visible feedback, entry restarts
- Enter the correct code again after one or more wrong attempts -
  verify flash_attempts() fires and attempt_count resets to 0

--------------------------------------------------------------------------------
Step 7 - Attempt display
--------------------------------------------------------------------------------

Implement 'flash_attempts()'. The flash should be noticeable but
not alarming - a few slow flashes of LED5, for example. Verify the
count is accurate and LED5 clears after the display finishes.

*/


/* ================================================================================
Extension Activities
================================================================================

--------------------------------------------------------------------------------
EA 1 - Auto-relock after timeout
--------------------------------------------------------------------------------

After unlocking, if the door sensor shows the door has been open
for RELOCK_TIMEOUT milliseconds, sound a warning beep and re-lock
automatically. This prevents leaving the safe open accidentally.

--------------------------------------------------------------------------------
EA 2 - Lockout after repeated failures
--------------------------------------------------------------------------------

After LOCKOUT_ATTEMPTS wrong codes in a row, freeze the keypad for
LOCKOUT_TIME milliseconds. Flash LED5 continuously during lockout.
No button presses accepted. This slows brute-force attempts
significantly. Add a STATE_LOCKOUT and update your state diagram
and STATE_NAMES[] array.

--------------------------------------------------------------------------------
EA 3 - Progress indicator during entry
--------------------------------------------------------------------------------

LED3 and LED4 are not used anywhere in the base program. Light one
additional LED per digit entered during ENTRY_1-4, the same
cumulative bar-graph pattern used in Activity 12's combination
lock, so someone entering the code can see their progress without
counting beeps. Should this progress indicator also appear during
STATE_SETTING? Consider whether showing progress while setting a
new code makes the safe easier to use, or easier to observe by
someone who should not see the new code being set.

--------------------------------------------------------------------------------
EA 4 - Code change confirmation
--------------------------------------------------------------------------------

Require the existing code to be entered correctly before a new one
can be set. Add a STATE_VERIFY between the SW2 hold and
STATE_SETTING - only proceed to SETTING if the current code is
entered correctly first. This prevents someone from changing the
code without knowing the original, even while the safe is unlocked.

--------------------------------------------------------------------------------
EA 5 - Variable code length
--------------------------------------------------------------------------------

Extend the code to five or six digits, following the same pattern
used to go from Activity 12's three-digit lock to this capstone's
four digits: one more STATE_ENTRY_n, one more entered_n variable,
and one more code_n variable per additional digit. At what code
length does adding states and variables one at a time start to
feel unwieldy? This is the same tradeoff Activity 12 EA3 raised -
a fully flexible length would use an array and a loop with an index
variable, which you will meet in the intermediate activities.

*/
