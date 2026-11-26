/* ================================================================================
Capstone Project: Reaction Time Game [BEAPERNano-Capstone-Reaction-Game]
Version: 1.2
Updated: November 24, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPERNano_v1_2.h header file

Two reaction-testing games in one, selected with SW2/SW3:

  SIMPLE   - React as fast as possible to an unpredictable stimulus.
             LED1 lights up after a random delay - press SW1 the
             instant it does. Pressing too early ends the trial
             immediately as a false start, the same way real
             reaction-time testing works.

  TIMING   - React at the RIGHT MOMENT to a predictable, repeating
             pattern instead. LED1-LED4 chase continuously in a
             loop; press SW1 exactly when the chase reaches the
             target LED (LED3). Unlike SIMPLE, the pattern's timing
             is known in advance - this tests anticipation and
             rhythm judgement rather than raw speed.

Both modes measure the same underlying thing - how close your
press was to a reference moment in time - but the character of
that reference moment (unpredictable vs. predictable) is what
makes them test genuinely different skills.

Hardware used:
  SW1          - Start a round / react during a round
  SW2 / SW3    - Cycle game mode (only while at the menu)
  SW4          - Cancel the current round, return to the menu
  LS1          - Piezo speaker (stimulus/target beep, result tones)
  On-board LED - On during an active round

Compatible with all BEAPER Nano configurations. No additional
hardware or jumper changes required.

--------------------------------------------------------------------------------
Before you begin - complete your capstone plan using the Capstone
Preparation Guide: a plain-English description of each mode from
the player's perspective, a state diagram for each, your constants
and variables, and your testing plan.
=================================================================================*/
// IMPORTANT: Make sure that BEAPERNano_v1_2.h is accessible as a tab in this project.
#include "BEAPERNano_v1_2.h"   // Define BEAPER Nano I/O devices

// ---- State Constants -------------------
const int STATE_MENU    = 0;         // Selecting a mode, waiting to start
const int STATE_WAITING = 1;         // SIMPLE only: waiting out the random delay
const int STATE_REACT   = 2;         // SIMPLE only: stimulus is showing, timing the press
const int STATE_CHASING = 3;         // TIMING only: chase pattern running
const int STATE_RESULT  = 4;         // Showing the result of the last round

const char* STATE_NAMES[] = { "MENU", "WAITING", "REACT", "CHASING", "RESULT" };

// ---- Mode Constants -----------------------
const int MODE_SIMPLE = 0;           // Simple reaction time
const int MODE_TIMING = 1;           // Timing / anticipation
const int NUM_MODES   = 2;

const char* MODE_NAMES[] = { "SIMPLE", "TIMING" };

// ---- Simple Reaction Time Configuration ---
const int REACT_LED   = LED1;        // The single stimulus LED for SIMPLE mode
const int MIN_WAIT_MS = 1500;        // Shortest possible random delay before the stimulus
const int MAX_WAIT_MS = 4000;        // Longest possible random delay before the stimulus

// ---- Timing/Anticipation Configuration -----
const int CHASE_LEDS[]      = { LED1, LED2, LED3, LED4 };
const int CHASE_INTERVAL_MS = 300;   // Time the chase spends on each LED
const int TARGET_POSITION   = 2;     // Index into CHASE_LEDS - 2 = LED3

// ---- Timing Constants -----------------------
const int RESULT_DISPLAY_MS = 2000;  // How long a result is shown before returning to MENU
const int LOOP_DELAY        = 1;     // Main loop delay (ms) - kept short for timing precision

// ---- Program Variables -----------------------
int  state             = STATE_MENU;
unsigned long state_start = 0;

int  current_mode      = MODE_SIMPLE;

// ---- SIMPLE mode variables ----
unsigned long wait_duration      = 0;      // This round's random delay (ms)
unsigned long stimulus_time      = 0;      // When the stimulus actually lit
unsigned long reaction_time      = 0;      // Most recent trial's reaction time (ms)
unsigned long best_reaction_time = 999999; // Best (lowest) reaction time this session
bool false_start = false;                  // True if the most recent trial was a false start

// ---- TIMING mode variables ----
int  chase_position          = 0;          // Which of the 4 CHASE_LEDS is currently lit
unsigned long last_chase_step      = 0;    // Time the chase last advanced
unsigned long last_target_lit_time = 0;    // Time the chase most recently lit the target LED
unsigned long timing_error         = 0;    // Most recent trial's timing error (ms)
unsigned long best_timing_error    = 999999; // Best (lowest) timing error this session

// ---- SW2/SW3 edge detection (menu mode cycling) ----
int sw2_last = 1;
int sw3_last = 1;


// ---- Program Functions -----------------------

void all_leds_off()
{
    for (int i = 0; i < 4; i++)
        digitalWrite(CHASE_LEDS[i], LOW);   // CHASE_LEDS[0] is REACT_LED (LED1)
    digitalWrite(LED_BUILTIN, LOW);
}

void enter_state(int new_state, unsigned long current_time, const char* reason = "")
{
    state       = new_state;
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

void start_round(unsigned long current_time)
{
    // Begin a new round in the currently selected mode.
    digitalWrite(LED_BUILTIN, HIGH);
    all_leds_off();
    if (current_mode == MODE_SIMPLE)
    {
        wait_duration = random(MIN_WAIT_MS, MAX_WAIT_MS + 1);   // +1: random() excludes its upper bound
        false_start   = false;
        enter_state(STATE_WAITING, current_time, "round start");
    }
    else if (current_mode == MODE_TIMING)
    {
        chase_position  = 0;
        last_chase_step = current_time;
        digitalWrite(CHASE_LEDS[0], HIGH);
        if (TARGET_POSITION == 0)
            last_target_lit_time = current_time;
        enter_state(STATE_CHASING, current_time, "round start");
    }
}


void setup()
{
    // Configure Arduino Nano ESP32 status LED as output
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, LOW);

    // Configure BEAPER Nano LEDs as outputs
    for (int i = 0; i < 4; i++)
        pinMode(CHASE_LEDS[i], OUTPUT);

    // Configure BEAPER Nano pushbuttons as inputs
    pinMode(SW1, INPUT_PULLUP);
    pinMode(SW2, INPUT_PULLUP);
    pinMode(SW3, INPUT_PULLUP);
    pinMode(SW4, INPUT_PULLUP);

    Serial.begin(9600);
    delay(2000);                       // Give Serial Monitor time to
                                        // connect, without blocking
                                        // forever if it's never opened

    randomSeed(millis());              // Seed the random number generator

    all_leds_off();
    Serial.println("Reaction Time Game");
    Serial.println("SW2/SW3: change mode   SW1: start / react   SW4: cancel");
    Serial.println();

    state_start = millis();
    enter_state(STATE_MENU, state_start, "startup");
    Serial.print("Mode: "); Serial.println(MODE_NAMES[current_mode]);
}

void loop()
{
    unsigned long current_time = millis();
    unsigned long elapsed      = current_time - state_start;

    // ---- Cancel (SW4) - checked before all state logic, except at the menu ----
    if (digitalRead(SW4) == LOW && state != STATE_MENU && state != STATE_RESULT)
    {
        all_leds_off();
        enter_state(STATE_MENU, current_time, "cancelled");
    }

    // ---- State: Menu ----
    else if (state == STATE_MENU)
    {
        int sw2_current = digitalRead(SW2);
        int sw3_current = digitalRead(SW3);
        if ((sw2_current == LOW && sw2_last == HIGH) || (sw3_current == LOW && sw3_last == HIGH))
        {
            current_mode = (current_mode + 1) % NUM_MODES;
            Serial.print("Mode: "); Serial.println(MODE_NAMES[current_mode]);
        }
        sw2_last = sw2_current;
        sw3_last = sw3_current;

        if (digitalRead(SW1) == LOW)
            start_round(current_time);
    }

    // ---- State: Waiting (SIMPLE mode - random delay before stimulus) ----
    else if (state == STATE_WAITING)
    {
        // TODO: if SW1 is pressed here, it is a false start - the player
        //       reacted before the stimulus appeared. Set false_start =
        //       true and enter_state(STATE_RESULT, current_time,
        //       "false start").
        //
        // TODO: once elapsed >= (unsigned long)wait_duration, light REACT_LED,
        //       sound a short beep, record stimulus_time = current_time,
        //       and enter_state(STATE_REACT, current_time).
    }

    // ---- State: React (SIMPLE mode - stimulus is showing) ----
    else if (state == STATE_REACT)
    {
        // TODO: if SW1 is pressed, compute reaction_time =
        //       current_time - stimulus_time. Update
        //       best_reaction_time if this is an improvement. Turn off
        //       REACT_LED and enter_state(STATE_RESULT, current_time).
    }

    // ---- State: Chasing (TIMING mode) ----
    else if (state == STATE_CHASING)
    {
        // TODO: non-blocking chase animation - if elapsed since
        //       last_chase_step >= (unsigned long)CHASE_INTERVAL_MS: turn off
        //       the current CHASE_LEDS[chase_position], advance
        //       chase_position by 1 (wrapping with % 4), turn on the new
        //       CHASE_LEDS[chase_position], and reset last_chase_step =
        //       current_time. If the new chase_position == TARGET_POSITION,
        //       also record last_target_lit_time = current_time and sound
        //       a short beep - this is the moment a well-timed press
        //       should land on.
        //
        // TODO: if SW1 is pressed, compute timing_error =
        //       abs((long)(current_time - last_target_lit_time)).
        //       Note this only measures distance from the MOST RECENT
        //       time the target lit, not the nearest occurrence in either
        //       direction - see Development Guide Step 5 for the
        //       limitation this creates and how to improve it. Update
        //       best_timing_error if this is an improvement. Turn off all
        //       CHASE_LEDS and enter_state(STATE_RESULT, current_time).
    }

    // ---- State: Result ----
    else if (state == STATE_RESULT)
    {
        // TODO: on entry to this state (elapsed == 0, or track a
        //       'result_shown' flag to only do this once), print the
        //       result:
        //       - SIMPLE, false start: print "Too soon!"
        //       - SIMPLE, normal: print reaction_time and whether it is
        //         a new best
        //       - TIMING: print timing_error and whether it is a new best
        //       Consider a distinct confirmation tone for a new best.
        //
        // TODO: once elapsed >= (unsigned long)RESULT_DISPLAY_MS,
        //       enter_state(STATE_MENU, current_time) to return to mode
        //       selection.
    }

    delay(LOOP_DELAY);
}


/* ================================================================================
Development Guide
================================================================================

Work through these steps in order. Test SIMPLE mode completely
before starting TIMING mode - they share very little code, but the
overall program structure (state transitions, result display) is
easiest to get right once with one working mode as a reference.

--------------------------------------------------------------------------------
Step 1 - Menu and mode selection
--------------------------------------------------------------------------------

The menu and mode-cycling logic (SW2/SW3 in STATE_MENU) is already
complete. Run the program and confirm pressing SW2 or SW3 toggles
between SIMPLE and TIMING, printing the mode name each time.
Confirm SW1 calls start_round() and transitions to the correct
first state for whichever mode is selected (STATE_WAITING for
SIMPLE, STATE_CHASING for TIMING).

--------------------------------------------------------------------------------
Step 2 - False start detection
--------------------------------------------------------------------------------

Implement the false-start TODO in STATE_WAITING. Test by starting a
SIMPLE round and immediately pressing SW1 before the LED lights.
Confirm this transitions straight to STATE_RESULT without ever
lighting REACT_LED.

--------------------------------------------------------------------------------
Step 3 - Stimulus and reaction timing
--------------------------------------------------------------------------------

Implement the remaining TODO in STATE_WAITING (lighting the
stimulus) and the TODO in STATE_REACT (measuring the press).
Test several rounds and confirm reaction_time values look
reasonable (human simple reaction time is typically 150-300ms) and
that best_reaction_time only updates when a round is genuinely
faster than the previous best.

--------------------------------------------------------------------------------
Step 4 - Chase animation
--------------------------------------------------------------------------------

Implement the chase animation portion of the TODO in STATE_CHASING,
without the press-handling yet. Confirm the four LEDs light in
sequence, looping continuously, at the rate set by
CHASE_INTERVAL_MS, and that a beep sounds each time the chase
passes over the target LED (LED3).

--------------------------------------------------------------------------------
Step 5 - Timing measurement and its limitation
--------------------------------------------------------------------------------

Implement the press-handling portion of the TODO in STATE_CHASING.
Test by pressing SW1 at different points in the chase cycle and
confirming timing_error is small when you press near the target
LED and large otherwise.

This measurement has a known limitation worth understanding: it is
calculated only against the MOST RECENT time the target lit, not
whichever occurrence (past or upcoming) is actually closer. Press
SW1 just before the chase is about to reach the target again - you
should genuinely be very close in time, but timing_error will
report a value close to a full chase cycle instead of close to
zero, because it is measuring backward to the previous lit moment
rather than forward to the upcoming one. Confirm you can observe
this for yourself before moving on - EA 'improved timing
measurement' below addresses it properly.

--------------------------------------------------------------------------------
Step 6 - Result display
--------------------------------------------------------------------------------

Implement STATE_RESULT. Test that each of the three result types
(SIMPLE false start, SIMPLE normal, TIMING) prints a clear,
distinguishable message, and that the program correctly returns to
STATE_MENU after RESULT_DISPLAY_MS with the previously selected
mode still active.

*/


/* ================================================================================
Extension Activities
================================================================================

--------------------------------------------------------------------------------
EA 1 - Improved timing measurement
--------------------------------------------------------------------------------

Fix the limitation identified in Development Guide Step 5: rather
than measuring only backward to the most recent time the target
lit, compute the shortest distance to either the most recent OR
the next upcoming occurrence, whichever is closer. This is the
same "shortest distance around a repeating cycle" problem Stepper
Controller's EA1 (bidirectional movement) solves for a rotating
position - the chase's position within its 4-step cycle is directly
analogous to the stepper's position within a full revolution.

--------------------------------------------------------------------------------
EA 2 - Running average
--------------------------------------------------------------------------------

Beyond tracking only the single best result, keep a running sum
and count of every trial's result (in either mode) and display the
average alongside the best. How does the average compare to the
best across many trials - does it reveal anything the best score
alone does not?

--------------------------------------------------------------------------------
EA 3 - Choice reaction time
--------------------------------------------------------------------------------

Add a third mode where, instead of always lighting REACT_LED, the
stimulus randomly lights ONE of LED1-LED4 (reusing the read_button()
style pattern from Simon Game or Combination Safe), and the player
must press the MATCHING button (SW1-SW4) as quickly as possible.
This tests both reaction speed and discrimination together - a
real, named distinction in human factors research called "choice
reaction time," typically measurably slower than simple reaction
time even though it uses the same LEDs and buttons.

--------------------------------------------------------------------------------
EA 4 - Rhythm matching
--------------------------------------------------------------------------------

Add a fourth mode with a steady metronome beep and flash at a
fixed tempo (reuse Activity 11's repeating-timer pattern
directly). The player tries to press SW1 in sync with each beat,
and each press is scored by how close it lands to the nearest
beat - similar in spirit to TIMING mode, but matching a continuous
rhythm rather than a single target point in a longer cycle. Track
and display a running average timing error across several beats
rather than just one round's result.

--------------------------------------------------------------------------------
EA 5 - Head-to-head
--------------------------------------------------------------------------------

Add a two-player mode: both players' buttons (for example SW1 and
SW4, freeing SW4 from its cancel role while this mode is active)
watch the same SIMPLE-style unpredictable stimulus, and whichever
player presses first wins the round. This reuses SIMPLE mode's
false-start and stimulus-timing logic almost entirely - the main
difference is in STATE_REACT, which now needs to check two buttons
and determine which was pressed first, rather than measuring one
button's absolute reaction time.

*/
