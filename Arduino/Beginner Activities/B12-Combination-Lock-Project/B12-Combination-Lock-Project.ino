/* ================================================================================
Project: Combination Lock [B12-Combination-Lock-Project]
April 14, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPERNano.h header file

Before starting, re-read GE1, GE2, and GE3 from
Activity 12: State Machines.

This sketch implements a three-button combination lock as a state
machine. The correct combination is SW2, SW3, SW4 pressed in
sequence. Any wrong button press triggers the alarm state.
SW5 resets from any state.

State diagram:
  LOCKED   --> (SW2 correct) --> STEP_1
  STEP_1   --> (SW3 correct) --> STEP_2
  STEP_2   --> (SW4 correct) --> UNLOCKED
  Any state --> (wrong button) --> ALARM
  Any state --> (SW5)          --> LOCKED

Outputs per state:
  LOCKED:   LED2 on (locked indicator)
  STEP_1:   LED2 + LED3 on (one correct press)
  STEP_2:   LED2 + LED3 + LED4 on (two correct presses)
  UNLOCKED: LED5 on, short beep (access granted)
  ALARM:    LED2-LED5 flashing rapidly, repeated beeps (alarm)
================================================================================*/
// IMPORTANT: Make sure that BEAPERNano.h is accessible as a tab in this project.
#include "BEAPERNano.h"

// ---- State Constants -----------------
const int STATE_LOCKED   = 0;
const int STATE_STEP_1   = 1;
const int STATE_STEP_2   = 2;
const int STATE_UNLOCKED = 3;
const int STATE_ALARM    = 4;

const char* STATE_NAMES[] = { "LOCKED", "STEP_1", "STEP_2", "UNLOCKED", "ALARM" };

// ---- Program Constants ---------------
const int LOOP_DELAY      = 10;       // Main loop delay (ms)
const int FLASH_INTERVAL  = 150;      // Alarm flash toggle interval (ms)
const int ALARM_BEEP_ON   = 100;      // Alarm beep on duration (ms)
const int ALARM_BEEP_OFF  = 200;      // Alarm beep off duration (ms)
const int RESET_HOLD_TIME = 1000;     // Time to hold SW5 to reset from UNLOCKED (ms)

// ---- Program Variables ---------------
int           state           = STATE_LOCKED;
unsigned long state_start     = 0;
unsigned long last_flash_time = 0;
bool          flash_on        = false;

// Edge detection - track previous button states to detect fresh presses
int last_sw2_state = HIGH;
int last_sw3_state = HIGH;
int last_sw4_state = HIGH;
int last_sw5_state = HIGH;


// ---- Program Functions ---------------

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

bool button_just_pressed(int current_val, int last_val)
{
    // Return true if button transitioned from not-pressed (HIGH) to pressed (LOW).
    return (current_val == LOW && last_val == HIGH);
}


void setup()
{
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, HIGH);

    pinMode(LED2, OUTPUT);
    pinMode(LED3, OUTPUT);
    pinMode(LED4, OUTPUT);
    pinMode(LED5, OUTPUT);
    all_leds_off();

    pinMode(SW2, INPUT_PULLUP);
    pinMode(SW3, INPUT_PULLUP);
    pinMode(SW4, INPUT_PULLUP);
    pinMode(SW5, INPUT_PULLUP);

    Serial.begin(9600);
    while (!Serial);

    state_start     = millis();
    last_flash_time = millis();

    Serial.println("Combination Lock");
    Serial.println("Enter combination: SW2, SW3, SW4");
    Serial.println("SW5: reset");
    Serial.println();

    enter_state(STATE_LOCKED, state_start, "startup");
    digitalWrite(LED2, HIGH);
}

void loop()
{
    unsigned long current_time = millis();

    // Read all buttons
    int sw2 = digitalRead(SW2);
    int sw3 = digitalRead(SW3);
    int sw4 = digitalRead(SW4);
    int sw5 = digitalRead(SW5);

    // Detect fresh button presses
    bool sw2_pressed = button_just_pressed(sw2, last_sw2_state);
    bool sw3_pressed = button_just_pressed(sw3, last_sw3_state);
    bool sw4_pressed = button_just_pressed(sw4, last_sw4_state);
    bool sw5_pressed = button_just_pressed(sw5, last_sw5_state);

    // SW5 resets to LOCKED from any state except UNLOCKED
    // (UNLOCKED requires a hold - see EA1)
    if (sw5_pressed && state != STATE_UNLOCKED)
    {
        enter_state(STATE_LOCKED, current_time, "SW5 reset");
        digitalWrite(LED2, HIGH);
    }

    // ---- State machine ----

    else if (state == STATE_LOCKED)
    {
        // TODO: if SW2 pressed, transition to STEP_1 and update LEDs
        // TODO: if SW3 or SW4 pressed, transition to ALARM
    }

    else if (state == STATE_STEP_1)
    {
        // TODO: if SW3 pressed, transition to STEP_2 and update LEDs
        // TODO: if SW2 or SW4 pressed, transition to ALARM
    }

    else if (state == STATE_STEP_2)
    {
        // TODO: if SW4 pressed, transition to UNLOCKED and update LEDs
        // TODO: if SW2 or SW3 pressed, transition to ALARM
    }

    else if (state == STATE_UNLOCKED)
    {
        // Lock is open - LED5 on (set on entry, maintained here)
        // SW5 held for RESET_HOLD_TIME re-locks
        // TODO: check if SW5 is held for RESET_HOLD_TIME using the
        //       button_is_down / button_down_time pattern from Activity 11,
        //       then transition to LOCKED
    }

    else if (state == STATE_ALARM)
    {
        // Flash all LEDs and sound repeated beeps while in alarm state
        // TODO: flash LED2-LED5 together at FLASH_INTERVAL using last_flash_time
        // TODO: produce a repeating beep pattern using tone()/noTone():
        //       on for ALARM_BEEP_ON ms, off for ALARM_BEEP_OFF ms
        //       Hint: use elapsed time within the flash cycle to determine
        //       beep on/off, so beep timing stays aligned with the flash
    }

    // Update last button states for next iteration
    last_sw2_state = sw2;
    last_sw3_state = sw3;
    last_sw4_state = sw4;
    last_sw5_state = sw5;

    delay(LOOP_DELAY);
}


/*
Extension Activities

1.  The UNLOCKED state currently does nothing useful after the lock
    opens. Implement a re-lock mechanism: SW5 must be held for
    RESET_HOLD_TIME milliseconds to re-lock. Use the 'button_is_down'
    and 'button_down_time' pattern from Activity 11.

    Why require a hold rather than a tap to re-lock? Think about
    what would happen in a real access-control system if the door
    accidentally re-locked while someone was passing through.

2.  Add a lockout after three failed attempts. Declare an
    'attempt_count' variable that increments each time the lock
    transitions to ALARM from any step state. After three failed
    attempts, enter a LOCKOUT state that ignores all input for
    LOCKOUT_TIME milliseconds before returning to LOCKED.

    Add LOCKOUT to your state diagram and identify the new
    transitions. How does this change the security of the lock
    compared to the version with no lockout?

3.  Make the combination configurable. Store the correct sequence
    as an array:

  const int COMBINATION[] = { SW2, SW3, SW4 };
  const int COMBO_LENGTH  = 3;

    Rewrite the state machine to work with any length combination
    stored in this array, using a 'step' index variable instead of
    separate STEP_1 and STEP_2 states. How does the number of
    states in the new design compare to the original? What are
    the tradeoffs of the two approaches?

4.  Consider how this combination lock could form the arm/disarm
    mechanism for a security alarm capstone project. What would
    the full system's state diagram look like, including:
    - Disarmed state (lock open, sensors ignored)
    - Arming state (countdown delay while you leave)
    - Armed state (sensors active)
    - Triggered state (alarm sounding)
    - Each combination lock state for disarming

    Draw the complete state diagram. How many states does the
    full system have? How does the lock's state machine nest
    inside the alarm system's state machine?

*/
