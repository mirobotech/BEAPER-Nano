/* ================================================================================
Project: Traffic Light Controller [B12_Traffic_Light_Controller_Project]
Version: 1.2
Updated: September 22, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPERNano.h header file

Before starting this project, re-read GE 1 through GE 7 from
Activity 12: State Machines. This skeleton reuses the same
enter_state() and named-constant patterns as the combination lock,
now applied to a four-state traffic light.

State diagram:
  RED --(RED_TIME elapsed, car_waiting)     --> ADV_GREEN
  RED --(RED_TIME elapsed, not car_waiting) --> GREEN
  ADV_GREEN --(ADV_GREEN_TIME elapsed)      --> GREEN
  GREEN     --(effective green time elapsed)--> YELLOW
  YELLOW    --(YELLOW_TIME elapsed)         --> RED

Outputs per state:
  RED:        LED5 on
  ADV_GREEN:  LED5 on (cross traffic still stopped) + LED2 flashing
              (protected left-turn arrow)
  GREEN:      LED3 on
  YELLOW:     LED4 on

Simulated inputs (SW2/SW3 are only read during RED):
  SW2: simulates a car waiting for the protected left turn -
       sets 'car_waiting', which is checked once, when RED_TIME
       elapses, to decide whether to enter ADV_GREEN or GREEN
  SW3: simulates a pedestrian crossing request - sets
       'walk_requested', which extends the following GREEN phase
       by WALK_EXTENSION milliseconds

Unlike the combination lock, where each button press needed to be
counted individually, SW2 and SW3 here just need to be noticed at
any point during RED - so this project checks them with the same
plain 'digitalRead(SW2) == LOW' comparison used since Activity 3,
with no release-waiting required. A flag, once set, stays set until
the state machine resets it on the next entry to RED.
=================================================================================*/
// IMPORTANT: Make sure that BEAPERNano.h is accessible as a tab in this project.
#include "BEAPERNano.h"

// Explicit prototype: Arduino's automatic prototype generation does not
// handle functions with default parameter values correctly, so this one
// is declared by hand to guarantee enter_state() compiles as intended
// wherever it is called below.
void enter_state(int new_state, unsigned long current_time, const char* reason = "");

// ---- State Constants ------------------
const int STATE_RED       = 0;
const int STATE_ADV_GREEN = 1;        // Protected left-turn arrow phase
const int STATE_GREEN     = 2;
const int STATE_YELLOW    = 3;

const char* STATE_NAMES[] = {"RED", "ADV_GREEN", "GREEN", "YELLOW"};

// ---- Program Constants ---------------
const int LOOP_DELAY           = 10;  // Main loop delay (ms)
const int RED_TIME             = 3000;  // Minimum time spent in RED (ms)
const int ADV_GREEN_TIME       = 2000;  // Protected left-turn arrow duration (ms)
const int GREEN_TIME           = 4000;  // Base GREEN duration (ms)
const int YELLOW_TIME          = 1500;  // YELLOW duration (ms)
const int WALK_EXTENSION       = 2000;  // Extra GREEN time if a walk was requested (ms)
const int ARROW_FLASH_INTERVAL = 200;   // Left-turn arrow flash toggle interval (ms)

// ---- Program Variables ---------------
int  state           = STATE_RED;
unsigned long state_start     = 0;
bool car_waiting     = false;         // Set by SW2 during RED
bool walk_requested  = false;         // Set by SW3 during RED
unsigned long last_flash_time = 0;    // ADV_GREEN: last time the arrow toggled
bool arrow_on        = false;         // ADV_GREEN: current arrow flash state


// ---- Program Functions ---------------

void all_leds_off()
{
    digitalWrite(LED2, LOW);
    digitalWrite(LED3, LOW);
    digitalWrite(LED4, LOW);
    digitalWrite(LED5, LOW);
}

unsigned long calculate_green_time()
{
    // Return the GREEN duration for this cycle: the base GREEN_TIME,
    // extended by WALK_EXTENSION if a pedestrian requested a crossing
    // during the preceding RED phase. Written as its own function so
    // both places that need this value - entering GREEN, and checking
    // whether GREEN's time is up - always agree, rather than
    // recalculating the same expression twice and risking the two
    // copies drifting out of sync.
    if (walk_requested)
        return (unsigned long)GREEN_TIME + WALK_EXTENSION;
    else
        return (unsigned long)GREEN_TIME;
}

void enter_state(int new_state, unsigned long current_time, const char* reason)
{
    // Transition to a new state: clear outputs, update state variable,
    // record transition time, and print a diagnostic message.
    all_leds_off();
    state = new_state;
    state_start = current_time;
    arrow_on = false;

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

    pinMode(SW2, INPUT_PULLUP);
    pinMode(SW3, INPUT_PULLUP);

    Serial.begin(9600);
    delay(2000);                      // Give the Serial Monitor time to connect

    all_leds_off();
    state_start = millis();

    Serial.println("Traffic Light Controller");
    Serial.println("SW2 (during RED): car waiting for left turn");
    Serial.println("SW3 (during RED): pedestrian walk request");
    Serial.println();

    enter_state(STATE_RED, state_start, "startup");
    digitalWrite(LED5, HIGH);
}

void loop()
{
    unsigned long current_time = millis();
    unsigned long elapsed = current_time - state_start;

    if (state == STATE_RED)
    {
        // TODO: if SW2 is pressed, set car_waiting = true
        // TODO: if SW3 is pressed, set walk_requested = true
        // TODO: once elapsed >= (unsigned long)RED_TIME:
        //         if (car_waiting) { enter_state(STATE_ADV_GREEN, current_time);
        //                             turn on LED5 (still red for cross traffic)
        //                             reset car_waiting = false for the next cycle }
        //         else             { enter_state(STATE_GREEN, current_time);
        //                             turn on LED3 }
    }

    else if (state == STATE_ADV_GREEN)
    {
        // TODO: flash LED2 (the left-turn arrow) at ARROW_FLASH_INTERVAL,
        //       using last_flash_time and arrow_on the same way GE7's
        //       alarm flash timer works - remember LED5 needs to be lit
        //       again after each all_leds_off() inside enter_state(),
        //       since cross traffic is still stopped during this phase
        // TODO: once elapsed >= (unsigned long)ADV_GREEN_TIME:
        //         enter_state(STATE_GREEN, current_time)
        //         turn on LED3
    }

    else if (state == STATE_GREEN)
    {
        // TODO: once elapsed >= calculate_green_time():
        //         enter_state(STATE_YELLOW, current_time)
        //         turn on LED4
    }

    else if (state == STATE_YELLOW)
    {
        // TODO: once elapsed >= (unsigned long)YELLOW_TIME:
        //         enter_state(STATE_RED, current_time)
        //         turn on LED5
        //         reset walk_requested = false for the next cycle
    }

    delay(LOOP_DELAY);
}


/* ================================================================================
Extension Activities
================================================================================

--------------------------------------------------------------------------------
EA 1 - Complete the skeleton
--------------------------------------------------------------------------------

Complete the four TODO sections above so the traffic light
cycles correctly. Test each transition by watching the Serial
Monitor and LEDs: does RED always last at least RED_TIME? Does
holding SW2 during RED correctly route through ADV_GREEN? Does
a walk request measurably lengthen the following GREEN phase?

--------------------------------------------------------------------------------
EA 2 - A second pedestrian button
--------------------------------------------------------------------------------

Add a second walk request button, SW4, for pedestrians crossing
in the opposite direction, with its own 'walk_requested_2' flag.
Either request should extend GREEN - but pressing both should
not extend it twice. How will your condition check for "at
least one of the two flags is set" without double-counting?

--------------------------------------------------------------------------------
EA 3 - All-red clearance interval
--------------------------------------------------------------------------------

Real traffic lights often include an all-red clearance interval
- a brief period where every direction shows red, after YELLOW
and before the next phase begins, to let the intersection fully
clear before cross traffic gets a green light. Add a new
ALL_RED state between YELLOW and RED, lasting ALL_RED_TIME
milliseconds, with every LED off except LED5.

Update your state diagram, the STATE_NAMES array, and the
transitions to include this new state.

--------------------------------------------------------------------------------
EA 4 - Pedestrian countdown warning
--------------------------------------------------------------------------------

Add a pedestrian countdown warning: when GREEN has less than
3000ms of its calculated duration remaining, flash LED3 instead
of holding it steady, to warn that the light is about to change.
You will need to compare 'elapsed' against
'calculate_green_time() - 3000' rather than a fixed constant.

--------------------------------------------------------------------------------
EA 5 - Time-driven vs. event-driven transitions
--------------------------------------------------------------------------------

This traffic light and the combination lock both use
'enter_state()', named state constants, and millisecond timing -
but they differ in one significant way: the combination lock's
transitions all depend on button presses, while most of this
traffic light's transitions depend on elapsed time instead, with
button presses only setting flags checked later.

Look back at your state diagrams for both programs. Which
transitions in each diagram are triggered by time, and which by
an event? Is there a state in either program with more than one
way to leave it?

*/
