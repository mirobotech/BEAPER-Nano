/* ================================================================================
Beginner Activity 12: State Machines [BEAPERNano-Activity-B12-State-Machines]
April 14, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPERNano.h header file

This program implements a traffic light controller as a state machine.
The traffic light cycles through green, yellow, and red states. A car
sensor (SW2) can register a waiting vehicle during red, triggering an
advanced green turn signal before the regular green phase. A walk
request (SW5) registered during red extends the subsequent green phase
and lights the on-board LED as a walk signal.

Traffic light LED assignments:
  LED2        - Left turn signal (advanced green, flashing)
  LED3        - Straight through / regular green
  LED4        - Yellow
  LED5        - Red (stays lit during advanced green phase)
  LED_BUILTIN - Walk signal (active during extended green)
================================================================================*/
// IMPORTANT: Make sure that BEAPERNano.h is accessible as a tab in this project.
#include "BEAPERNano.h"

// ---- State Constants -----------------
const int STATE_ADV_GREEN = 0;        // Advanced green: left turn flashing
const int STATE_GREEN     = 1;        // Regular green: straight through
const int STATE_YELLOW    = 2;        // Yellow: prepare to stop
const int STATE_RED       = 3;        // Red: all stopped

const char* STATE_NAMES[] = { "ADV_GREEN", "GREEN", "YELLOW", "RED" };

// ---- Program Constants ---------------
const int LOOP_DELAY      = 1;        // Main loop delay (ms)
const int ADV_GREEN_TIME  = 5000;     // Advanced green phase duration (ms)
const int GREEN_TIME      = 6000;     // Regular green phase duration (ms)
const int YELLOW_TIME     = 2000;     // Yellow phase duration (ms)
const int RED_TIME        = 5000;     // Red phase duration (ms)
const int FLASH_INTERVAL  = 400;      // Advanced green flash toggle interval (ms)
const int WALK_EXTENSION  = 4000;     // Extra green time for pedestrian crossing (ms)

// ---- Program Variables ---------------
int           state           = STATE_RED;
unsigned long state_start     = 0;
unsigned long last_flash_time = 0;
bool          flash_on        = false;
bool          car_waiting     = false;
bool          walk_requested  = false;
int           effective_green = GREEN_TIME;


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
    // Transition to a new state: clear all outputs, update state variable,
    // record transition time, and print a diagnostic message.
    all_leds_off();
    digitalWrite(LED_BUILTIN, HIGH);   // Off (active-LOW) - clears walk signal
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


void setup()
{
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, HIGH);   // Off initially - reserved for walk signal

    pinMode(LED2, OUTPUT);
    pinMode(LED3, OUTPUT);
    pinMode(LED4, OUTPUT);
    pinMode(LED5, OUTPUT);
    all_leds_off();

    pinMode(SW2, INPUT_PULLUP);
    pinMode(SW5, INPUT_PULLUP);

    Serial.begin(9600);
    while (!Serial);

    Serial.println("Activity 12: State Machines - Traffic Light Controller");
    Serial.println("SW2: car sensor (advanced green request during red)");
    Serial.println("SW5: walk signal request (during red)");
    Serial.println();

    // Enter initial state
    state_start     = millis();
    last_flash_time = millis();
    Serial.println("--> RED (initial)");
    digitalWrite(LED5, HIGH);
}

void loop()
{
    unsigned long current_time = millis();
    unsigned long elapsed      = current_time - state_start;

    // ---- State: Advanced Green ----
    if (state == STATE_ADV_GREEN)
    {
        // Red stays lit during advanced green (cross traffic still stopped)
        // Flash LED2 at FLASH_INTERVAL while state persists
        if ((current_time - last_flash_time) >= (unsigned long)FLASH_INTERVAL)
        {
            flash_on = !flash_on;
            digitalWrite(LED2, flash_on);
            last_flash_time = current_time;
        }

        if (elapsed >= (unsigned long)ADV_GREEN_TIME)
        {
            effective_green = walk_requested ? GREEN_TIME + WALK_EXTENSION : GREEN_TIME;
            enter_state(STATE_GREEN, current_time, "advanced green complete");
            digitalWrite(LED3, HIGH);
            if (walk_requested)
            {
                digitalWrite(LED_BUILTIN, LOW);   // Walk signal on (active-LOW)
                Serial.print("    walk signal active (+");
                Serial.print(WALK_EXTENSION / 1000);
                Serial.println("s extension)");
            }
        }
    }

    // ---- State: Green ----
    else if (state == STATE_GREEN)
    {
        if (elapsed >= (unsigned long)effective_green)
        {
            walk_requested = false;
            enter_state(STATE_YELLOW, current_time, "timed out");
            digitalWrite(LED4, HIGH);
        }
    }

    // ---- State: Yellow ----
    else if (state == STATE_YELLOW)
    {
        if (elapsed >= (unsigned long)YELLOW_TIME)
        {
            enter_state(STATE_RED, current_time, "timed out");
            digitalWrite(LED5, HIGH);
        }
    }

    // ---- State: Red ----
    else if (state == STATE_RED)
    {
        if (digitalRead(SW2) == LOW && !car_waiting)
        {
            car_waiting = true;
            Serial.println("    car sensor: advanced green requested");
        }

        if (digitalRead(SW5) == LOW && !walk_requested)
        {
            walk_requested = true;
            Serial.println("    walk button: extended green requested");
        }

        if (elapsed >= (unsigned long)RED_TIME)
        {
            if (car_waiting)
            {
                car_waiting = false;
                enter_state(STATE_ADV_GREEN, current_time, "car waiting");
                digitalWrite(LED5, HIGH);          // Red stays on during advanced green
                last_flash_time = current_time;
            }
            else
            {
                effective_green = walk_requested ? GREEN_TIME + WALK_EXTENSION : GREEN_TIME;
                enter_state(STATE_GREEN, current_time, "timed out");
                digitalWrite(LED3, HIGH);
                if (walk_requested)
                {
                    digitalWrite(LED_BUILTIN, LOW);
                    Serial.print("    walk signal active (+");
                    Serial.print(WALK_EXTENSION / 1000);
                    Serial.println("s extension)");
                }
            }
        }
    }

    delay(LOOP_DELAY);
}


/*
Guided Exploration

Activities 9 through 11 built programs that respond to inputs and
manage outputs using variables, functions, and timing patterns. Each
program was essentially one continuous process: a single loop checking
conditions and updating outputs on every iteration. This works well for
simple programs, but as behaviour becomes more complex it gets harder
to reason about - which outputs should be on right now depends on a
growing tangle of flags and conditions spread throughout the loop.

A state machine solves this by organising behaviour into distinct named
states, where each state has a clearly defined set of outputs and a
small set of conditions that cause a transition to another state. At
any moment the program is in exactly one state, and the logic for that
state is self-contained. This activity implements a traffic light
controller as a state machine. By the end you will understand how the
patterns from Activities 10 and 11 - output control, timed transitions,
and multi-rate timing - compose naturally inside a state machine, and
why this structure scales to systems that would be unmanageable as a
flat loop.

1.  A state machine can be described visually as a state diagram:
    circles represent states and arrows represent transitions between
    them. Each arrow is labelled with the event or condition that
    triggers the transition.

    Draw the state diagram for this traffic light program. Your
    diagram should have four circles (one per state) and arrows
    showing every possible transition. Label each arrow with its
    trigger - either a timing condition (e.g. "elapsed >= GREEN_TIME")
    or an event (e.g. "car_waiting == true").

    Compare your diagram to the program's 'loop()' function. Can
    you find a direct correspondence between each arrow in your
    diagram and a specific 'if' statement in the code?

    Notice that the outputs of each state - which LEDs are on -
    are set when entering each state via 'enter_state()', not
    checked continuously on every loop iteration. Why is this
    cleaner? What would happen if a noisy connection briefly
    triggered 'enter_state()' a second time while already in a
    state?

    The red LED (LED5) stays on during the advanced green phase
    even though the state has changed. Where in the code is this
    handled, and why is it correct for cross-traffic safety?

2.  States are defined using named integer constants:

  const int STATE_ADV_GREEN = 0;
  const int STATE_GREEN     = 1;
  const int STATE_YELLOW    = 2;
  const int STATE_RED       = 3;

    The program could instead use raw numbers (0, 1, 2, 3)
    directly in the 'if' statements. What would be lost?
    Consider what happens if you need to add a new state between
    GREEN and YELLOW and must renumber the existing states.

    The 'STATE_NAMES' array allows the state number to be used
    as an index to retrieve a human-readable name for printing:

  const char* STATE_NAMES[] = { "ADV_GREEN", "GREEN", "YELLOW", "RED" };
  Serial.println(STATE_NAMES[STATE_GREEN]);   // Prints: GREEN

    What is the relationship between the order of names in this
    array and the values of the state constants? What would the
    output be if STATE_GREEN were changed from 1 to 2 without
    updating the array?

    This naming principle applies beyond state machines. Any
    number in your program that represents a meaningful concept -
    a pin, a threshold, a mode - should have a name. Where else
    in this curriculum have you seen this principle applied?

3.  The program uses two flag variables to record sensor events
    during red: 'car_waiting' and 'walk_requested'. Both are set
    when their respective buttons are pressed during red, but
    neither triggers an immediate transition - they are checked
    only when the red duration elapses.

    Why is this design correct for 'car_waiting'? What would
    happen if the program transitioned to advanced green
    immediately when SW2 was pressed, regardless of how much
    red time remained?

    The walk request is treated differently from the car request:
    it does not change which state follows red, only how long
    green lasts and whether the walk signal lights. Trace through
    the program for this sequence of events and identify exactly
    where 'walk_requested' affects the program's behaviour:

    - Red phase begins
    - SW5 pressed at t=2000ms into red
    - SW2 pressed at t=3000ms into red
    - Red elapses at t=5000ms

    Both flags are separate variables with separate
    responsibilities, even though both are set during red and
    each cleared when the phase it governs ends. Why is it important
    that they are separate rather than combined into a single variable
    or checked in a single 'if' statement?

4.  The advanced green state contains two independent timers
    running simultaneously:

    - 'state_start' tracks how long the state has been active,
      used to determine when to leave the state.
    - 'last_flash_time' tracks when LED2 last toggled, used
      to control the flash rate.

    These two timers are completely independent - the flash rate
    does not affect the state duration and vice versa. Trace
    through several iterations of 'loop()' while in
    STATE_ADV_GREEN and verify that both timers advance
    independently.

    This is the multi-rate timing pattern from Activity 11, now
    applied inside a single state of a state machine: the state-
    duration timer is a one-shot elapsed timer (set once on entry,
    never reset), while the flash timer is a repeating interval
    timer (reset each time LED2 toggles). What would happen to
    the flash rate if 'state_start' were reset each time LED2
    toggled? What would happen to the state duration?

5.  The 'enter_state()' function prints a diagnostic message
    every time a state transition occurs:

  --> GREEN (timed out)
  --> YELLOW (timed out)
  --> RED (timed out)
  --> ADV_GREEN (car waiting)
  --> GREEN (advanced green complete)

    This is serial output used as an engineering tool rather than
    as a user interface. By printing on transitions rather than
    every loop iteration, the output is concise and meaningful -
    each line tells you exactly what happened and why.

    Compare this to printing every loop iteration as earlier
    activities did. How many lines per second would be printed at
    LOOP_DELAY = 1ms if every iteration printed a status message?
    Why would that be less useful than transition-only printing?

    Add a print statement inside the STATE_RED block that prints
    the elapsed time every 1000ms while waiting. How does this
    feel different from the transition prints? When would
    continuous printing be useful versus transition-only printing?


Extension Activities

    The following activities each extend the traffic light controller
    in a different direction. Read each one fully before starting,
    and draw an updated state diagram before writing any code - the
    diagram will reveal how many new states and transitions are needed
    before you have to think about implementation. EA3 opens a
    separate project sketch that implements a different state machine
    from scratch.

1.  Train crossing mode: add a train crossing sensor (SW3) that
    forces the signal to yellow then red from any active green
    state, and holds red until the train has cleared.

    A real signal must transition through yellow before red so
    that drivers already committed to crossing have time to clear
    the intersection safely. Jumping directly to red could cause
    collisions.

    Draw the updated state diagram before writing any code. Then
    implement the following behaviour:

    - If currently in STATE_ADV_GREEN or STATE_GREEN, immediately
      transition to STATE_YELLOW (interrupting the normal cycle)
    - Yellow then transitions normally to red after YELLOW_TIME
    - A 'train_crossing' bool flag distinguishes train-forced red
      from normal red, preventing the cycle from resuming while
      SW3 is held
    - After SW3 is released, a CLEARANCE_TIME delay elapses
      before returning to normal red and resuming the cycle

    You will need:
    - A 'train_crossing' boolean flag
    - A 'clearance_start' unsigned long for the post-release delay
    - A check for SW3 at the top of 'loop()', before the state
      logic, to catch it in any green state
    - Modified red state logic that checks 'train_crossing'
      before deciding whether to resume the normal cycle

    How many new transitions does train crossing add to your
    diagram? Does the yellow-first requirement change how you
    structure the SW3 check relative to the existing yellow state
    logic?

2.  Crosswalk extension: the main program already processes a
    walk request (SW5) registered during red, extending the green
    phase and lighting LED_BUILTIN as a walk signal. Extend this
    behaviour in two ways:

    a) Walk signal timeout: LED_BUILTIN should turn off partway
       through the extended green phase (after WALK_TIME
       milliseconds) to indicate that the safe crossing window
       has closed, even though the light remains green. Add a
       'walk_start_time' unsigned long set when entering extended
       green, and turn off LED_BUILTIN when WALK_TIME elapses.

    b) Walk request during green: currently a walk request pressed
       during green is ignored. Add handling so that SW5 pressed
       during green sets 'walk_requested' and extends the current
       green phase by WALK_EXTENSION, starting the walk signal
       immediately. Guard against extending an already-extended
       phase.

    For part (b), how do you extend the current green phase
    without restarting the state timer? Consider using
    'effective_green' and 'walk_requested' together to calculate
    the remaining time correctly.

3.  Combination lock: implement a three-button combination lock
    as a standalone state machine.
    Open: BEAPERNano-Project-Combination-Lock

    The correct combination is SW2, SW3, SW4 pressed in sequence.
    The lock has states for each step of the sequence, an unlocked
    state, and an alarm state triggered by any wrong button press.
    SW5 resets from any state.

    This state machine is event-driven rather than time-driven -
    transitions occur when buttons are pressed, not when timers
    elapse. Compare its structure to the traffic light's structure:
    what is the same and what is different?

*/
