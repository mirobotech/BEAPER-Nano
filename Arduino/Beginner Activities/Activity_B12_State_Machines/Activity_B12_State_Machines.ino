/* ================================================================================
Beginner Activity 12: State Machines [Activity_B12_State_Machines]
Version: 1.2
Updated: September 22, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPERNano.h header file

This program uses a state machine to implement a three-button
combination lock, styled after a digital hotel safe lock. SW2, SW3,
and SW4 can be pressed at each step to enter the code. Each press
beeps and lights the next progress LED. After all three presses
have been entered, the program checks whether they matched the
correct combination (SW2, SW3, SW4, in that order). SW5 restarts
code entry from any state except UNLOCKED.

State diagram:
  ENTRY_1 --(any button)--> ENTRY_2
  ENTRY_2 --(any button)--> ENTRY_3
  ENTRY_3 --(any button, correct sequence)--> UNLOCKED
  ENTRY_3 --(any button, wrong sequence)   --> ALARM
  ALARM --(3 alarm beeps complete)--> ENTRY_1
  Any state except UNLOCKED --(SW5)--> ENTRY_1

Outputs per state:
  ENTRY_1:  LED2 on (ready, no digits entered)
  ENTRY_2:  LED2 + LED3 on (one digit entered)
  ENTRY_3:  LED2 + LED3 + LED4 on (two digits entered)
  UNLOCKED: LED5 on, beep (access granted)
  ALARM:    LED2-LED5 flashing, 3 beeps, then returns to ENTRY_1
=================================================================================*/
// IMPORTANT: Make sure that BEAPERNano.h is accessible as a tab in this project.
#include "BEAPERNano.h"

// Explicit prototype: Arduino's automatic prototype generation does not
// handle functions with default parameter values correctly, so this one
// is declared by hand to guarantee enter_state() compiles as intended
// wherever it is called below.
void enter_state(int new_state, unsigned long current_time, const char* reason = "");

// ---- State Constants ------------------
// States are given named integer constants to match the state diagram.
const int STATE_ENTRY_1  = 0;         // Waiting for the first button press
const int STATE_ENTRY_2  = 1;         // One press entered, waiting for the second
const int STATE_ENTRY_3  = 2;         // Two presses entered, waiting for the third
const int STATE_UNLOCKED = 3;         // Correct sequence entered
const int STATE_ALARM    = 4;         // Wrong sequence entered

// State names for diagnostic printing, indexed by state constant - see GE2.
const char* STATE_NAMES[] = {"ENTRY_1", "ENTRY_2", "ENTRY_3", "UNLOCKED", "ALARM"};

// ---- The Correct Combination -----------
// Each correct button is stored in its own named constant, in order.
const int CORRECT_1 = 2;              // First press should be SW2
const int CORRECT_2 = 3;              // Second press should be SW3
const int CORRECT_3 = 4;              // Third press should be SW4

// ---- Program Constants ---------------
const int LOOP_DELAY       = 10;      // Main loop delay (ms)
const int ENTRY_BEEP_FREQ  = 1500;    // Beep frequency for each digit entered (Hz)
const int ENTRY_BEEP_MS    = 80;      // Beep duration for each digit entered (ms)
const int UNLOCK_FREQ      = 2000;    // Access-granted beep frequency (Hz)
const int UNLOCK_BEEP_MS   = 300;     // Access-granted beep duration (ms)
const int ALARM_FREQ       = 2500;    // Alarm beep frequency (Hz)
const int ALARM_BEEP_ON    = 150;     // Alarm beep on duration (ms)
const int ALARM_BEEP_OFF   = 150;     // Alarm beep off duration (ms)
const int ALARM_BEEP_COUNT = 3;       // Number of beeps before returning to entry
const int FLASH_INTERVAL   = 150;     // Alarm LED flash toggle interval (ms)

// ---- Program Variables ---------------
int  state            = STATE_ENTRY_1;
unsigned long state_start      = 0;
int  entered_1        = 0;            // Button pressed first this attempt (0-4)
int  entered_2        = 0;            // Button pressed second this attempt
int  entered_3        = 0;            // Button pressed third this attempt
unsigned long last_flash_time  = 0;   // Alarm: last time LEDs toggled
bool flash_on         = false;        // Alarm: current LED flash state
unsigned long last_beep_time   = 0;   // Alarm: last time the beep toggled
bool beep_on          = false;        // Alarm: current beep on/off state
int  alarm_beep_count = 0;            // Alarm: number of beeps completed so far


// ---- Program Functions ---------------

void all_leds_off()
{
    digitalWrite(LED2, LOW);
    digitalWrite(LED3, LOW);
    digitalWrite(LED4, LOW);
    digitalWrite(LED5, LOW);
}

int read_button()
{
    // Return 2, 3, or 4 if that button is currently pressed, or 0 if
    // none of the three combination buttons are pressed.
    if (digitalRead(SW2) == LOW) return 2;
    else if (digitalRead(SW3) == LOW) return 3;
    else if (digitalRead(SW4) == LOW) return 4;
    else return 0;
}

void wait_for_release()
{
    // Block until SW2, SW3, and SW4 are all released. Called after
    // a button press is detected.
    while (digitalRead(SW2) == LOW || digitalRead(SW3) == LOW || digitalRead(SW4) == LOW) {}
}

void enter_state(int new_state, unsigned long current_time, const char* reason)
{
    // Transition to a new state: clear outputs, update state variable,
    // record transition time, and print a diagnostic message.
    all_leds_off();
    noTone(LS1);                      // Silence speaker
    state = new_state;
    state_start = current_time;
    flash_on = false;
    beep_on = false;
    alarm_beep_count = 0;

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
    pinMode(SW4, INPUT_PULLUP);
    pinMode(SW5, INPUT_PULLUP);

    Serial.begin(9600);
    delay(2000);                      // Give the Serial Monitor time to connect

    all_leds_off();
    state_start = millis();
    last_flash_time = millis();

    Serial.println("Combination Lock");
    Serial.println("Enter combination: SW2, SW3, SW4");
    Serial.println("SW5: restart entry");
    Serial.println();

    // Set initial state outputs
    enter_state(STATE_ENTRY_1, state_start, "startup");
    digitalWrite(LED2, HIGH);
}

void loop()
{
    unsigned long current_time = millis();

    // SW5 restarts entry from any state except UNLOCKED
    if (digitalRead(SW5) == LOW && state != STATE_UNLOCKED)
    {
        while (digitalRead(SW5) == LOW) {}   // Wait for release
        enter_state(STATE_ENTRY_1, current_time, "SW5 reset");
        digitalWrite(LED2, HIGH);
    }

    // ---- State machine ----

    else if (state == STATE_ENTRY_1)
    {
        int pressed = read_button();
        if (pressed != 0)
        {
            entered_1 = pressed;
            tone(LS1, ENTRY_BEEP_FREQ, ENTRY_BEEP_MS);
            wait_for_release();
            enter_state(STATE_ENTRY_2, current_time);
            digitalWrite(LED2, HIGH);
            digitalWrite(LED3, HIGH);
        }
    }

    else if (state == STATE_ENTRY_2)
    {
        int pressed = read_button();
        if (pressed != 0)
        {
            entered_2 = pressed;
            tone(LS1, ENTRY_BEEP_FREQ, ENTRY_BEEP_MS);
            wait_for_release();
            enter_state(STATE_ENTRY_3, current_time);
            digitalWrite(LED2, HIGH);
            digitalWrite(LED3, HIGH);
            digitalWrite(LED4, HIGH);
        }
    }

    else if (state == STATE_ENTRY_3)
    {
        int pressed = read_button();
        if (pressed != 0)
        {
            entered_3 = pressed;
            tone(LS1, ENTRY_BEEP_FREQ, ENTRY_BEEP_MS);
            wait_for_release();
            if (entered_1 == CORRECT_1 && entered_2 == CORRECT_2 && entered_3 == CORRECT_3)
            {
                enter_state(STATE_UNLOCKED, current_time, "correct combination");
                digitalWrite(LED5, HIGH);
                tone(LS1, UNLOCK_FREQ, UNLOCK_BEEP_MS);
            }
            else
            {
                enter_state(STATE_ALARM, current_time, "wrong combination");
            }
        }
    }

    else if (state == STATE_UNLOCKED)
    {
        // Lock is open - LED5 stays on (set on entry). No exit transition
        // yet - see Extension Activity 1 to add a hold-to-relock feature.
    }

    else if (state == STATE_ALARM)
    {
        // Flash all LEDs together at FLASH_INTERVAL - a repeating timer
        if ((current_time - last_flash_time) >= (unsigned long)FLASH_INTERVAL)
        {
            flash_on = !flash_on;
            if (flash_on)
            {
                digitalWrite(LED2, HIGH);
                digitalWrite(LED3, HIGH);
                digitalWrite(LED4, HIGH);
                digitalWrite(LED5, HIGH);
            }
            else
            {
                all_leds_off();
            }
            last_flash_time = current_time;
        }

        // Repeating beep, running independently of the flash timer above.
        // After ALARM_BEEP_COUNT beeps, return to entry automatically.
        if (beep_on)
        {
            if ((current_time - last_beep_time) >= (unsigned long)ALARM_BEEP_ON)
            {
                noTone(LS1);
                beep_on = false;
                last_beep_time = current_time;
                alarm_beep_count++;
                if (alarm_beep_count >= ALARM_BEEP_COUNT)
                {
                    enter_state(STATE_ENTRY_1, current_time, "alarm complete");
                    digitalWrite(LED2, HIGH);
                }
            }
        }
        else
        {
            if ((current_time - last_beep_time) >= (unsigned long)ALARM_BEEP_OFF)
            {
                tone(LS1, ALARM_FREQ);
                beep_on = true;
                last_beep_time = current_time;
            }
        }
    }

    delay(LOOP_DELAY);
}


/* ================================================================================
Guided Exploration
================================================================================

Activities 9 through 11 focused on a single technical problem at a
time: analog input, output, and non-blocking timing. Each activity's
program grew more capable, but the overall structure stayed the
same - a loop that checks conditions and updates outputs directly.
This works well when a program's behaviour depends only on its
current inputs, but breaks down when a program needs to behave
differently depending on what has happened before. For example,
the same button could mean something different depending what part
of the program is currently running.

This activity introduces state machines: a way of organising a
program around a set of named states, with explicit rules for when
to move between them, and what to do while each state is active.
You have actually built a similar combination lock program twice
before - as a step-counter in Activity 6, and refactored with
functions in Activity 8. This activity solves the same problem a
third time as a proper state machine, allowing you to compare all
three approaches directly.

--------------------------------------------------------------------------------
GE 1 - The state diagram
--------------------------------------------------------------------------------

A state machine can be described visually using a state diagram:
circles represent states and arrows represent transitions between
them. Each arrow is labelled with the event that triggers it.

Draw the state diagram for this program. Your diagram should
have five circles (ENTRY_1, ENTRY_2, ENTRY_3, UNLOCKED, ALARM)
and an arrow for every transition described in the header
comment.

Compare your diagram to the state machine section of loop(). Can
you find a direct correspondence between each arrow in your
diagram and a specific 'else if' branch in the code?

--------------------------------------------------------------------------------
GE 2 - Named state constants
--------------------------------------------------------------------------------

States are defined using named integer constants:

Example code:

const int STATE_ENTRY_1  = 0;
const int STATE_ENTRY_2  = 1;
const int STATE_ENTRY_3  = 2;
const int STATE_UNLOCKED = 3;
const int STATE_ALARM    = 4;

The program could instead use raw numbers (0, 1, 2, 3, 4) directly
in the 'if' statements. What would be lost? Consider what happens
if you need to insert a new state between ENTRY_2 and ENTRY_3 and
must renumber the existing states.

Named constants also make the Serial Monitor output meaningful.
'enter_state()' looks up the state name using an array of strings,
indexed by the state constant itself:

Example code:

const char* STATE_NAMES[] = {"ENTRY_1", "ENTRY_2", "ENTRY_3", "UNLOCKED", "ALARM"};
...
Serial.print(STATE_NAMES[new_state]);

This works only because the state constants are sequential integers
starting at 0 - 'STATE_NAMES[2]' is "ENTRY_3" because STATE_ENTRY_3
is defined as 2. What would print if the state constants were not
sequential, or did not start at 0? What would the output look like
if raw numbers were printed instead of names?

--------------------------------------------------------------------------------
GE 3 - enter_state() and centralized transitions
--------------------------------------------------------------------------------

Every state transition goes through 'enter_state()' rather than
setting 'state' directly. This function clears every output
before setting the new state, resetting 'flash_on', 'beep_on',
and 'alarm_beep_count' at the same time. Each caller then turns
on only what the new state needs.

Compare this to an alternative design where every state's
outputs are checked and set fresh on every single loop
iteration, regardless of whether the state just changed. What
would be different about the program's behaviour, readability,
and efficiency?

Why does 'enter_state()' reset 'alarm_beep_count' to 0 even
though it is only used inside STATE_ALARM? What would happen on
the second time the lock enters ALARM if this reset were
missing?

Notice the explicit prototype near the top of the sketch:

Example code:

void enter_state(int new_state, unsigned long current_time, const char* reason = "");

The default value for 'reason' is declared here, not down in the
function's actual definition - C++ only allows a default value to
appear once, and it must be visible to every call site. Since
Arduino normally generates this kind of prototype automatically,
most sketches never need to write one by hand; this one is written
explicitly because Arduino's automatic prototype generation does
not handle functions with default parameter values correctly. The
default lets most calls omit the reason entirely (as in
'enter_state(STATE_ENTRY_2, current_time)') while a few calls
provide one for extra context in the Serial Monitor output. Where
have you seen default parameter values used before, in an earlier
activity?

--------------------------------------------------------------------------------
GE 4 - Reading buttons: read_button() and wait_for_release()
--------------------------------------------------------------------------------

Reading the buttons uses two small functions:

Example code:

int read_button()
{
    if (digitalRead(SW2) == LOW) return 2;
    else if (digitalRead(SW3) == LOW) return 3;
    else if (digitalRead(SW4) == LOW) return 4;
    else return 0;
}

void wait_for_release()
{
    while (digitalRead(SW2) == LOW || digitalRead(SW3) == LOW || digitalRead(SW4) == LOW) {}
}

'read_button()' uses the same 'digitalRead(SWx) == LOW' check you
have used since Activity 3 - nothing new there. The only new idea
is 'wait_for_release()': once a press is detected and recorded, the
program deliberately pauses until the button is physically
released, before continuing.

Why is this necessary? Consider what would happen without
'wait_for_release()' if a press were held down for 300ms: at
LOOP_DELAY = 10ms, how many loop iterations would that span, and
what would 'entered_1' end up containing after all of them?

This pattern - detect a press, then wait for release before
continuing - is a simplified version of 'read_keypad()' from
Activity 8, which did the same thing across all four buttons.
Compare the two: what does 'read_keypad()' do that
'read_button()' plus 'wait_for_release()' does not?

Note that 'wait_for_release()' blocks the program - it is not
the non-blocking style from Activity 11. Why is blocking
acceptable here but not in STATE_ALARM below? Think about what
else the program needs to keep doing while each state is active.

--------------------------------------------------------------------------------
GE 5 - Tracing the happy path
--------------------------------------------------------------------------------

Trace through the "happy path" - the sequence of transitions
when the combination is entered correctly:

Example code:

Start in ENTRY_1
Press SW2 --> ENTRY_2 (entered_1 = 2)
Press SW3 --> ENTRY_3 (entered_2 = 3)
Press SW4 --> UNLOCKED (entered_3 = 4, all three correct)

For each transition, identify: which 'else if' branch handles it,
which LEDs turn on, and what gets printed to the Serial Monitor.
Run the program and verify your trace against the actual output.

Now trace an incorrect attempt: SW3, SW2, SW4. Which state does
each press lead to? Is anything different about how ENTRY_2 and
ENTRY_3 behave for this attempt compared to the correct one, or
do they behave identically until the final check?

--------------------------------------------------------------------------------
GE 6 - Why check the whole combination at once
--------------------------------------------------------------------------------

Notice that pressing a wrong button during ENTRY_1 or ENTRY_2
does not trigger the alarm immediately - it is simply recorded
and the program moves on to the next entry state, exactly as if
it were correct. The combination is only checked once, after
all three presses have been entered, in STATE_ENTRY_3.

Why might this be a better design than checking each button as
it is pressed and triggering the alarm on the first wrong one?
Think about someone trying to guess the combination by trial and
error: what could they learn from a lock that reveals which
specific digit was wrong, that they could not learn from a lock
that only reveals whether the whole sequence was right or wrong?

--------------------------------------------------------------------------------
GE 7 - Independent timers inside the alarm state
--------------------------------------------------------------------------------

The ALARM state contains two independent repeating timers
running simultaneously - the same multi-rate timing pattern
from Activity 11, but now happening inside a single state
rather than across the whole program:

- 'last_flash_time' controls when the LEDs toggle, at
  FLASH_INTERVAL.
- 'last_beep_time' controls when the beep toggles, using two
  different intervals depending on 'beep_on': ALARM_BEEP_ON
  while beeping, ALARM_BEEP_OFF while silent.

Trace through several iterations of loop() while in STATE_ALARM
and verify that the flash and beep timers advance independently -
one does not wait for or reset the other.

'alarm_beep_count' increments each time a beep finishes (when
'beep_on' changes from true to false). Once it reaches
ALARM_BEEP_COUNT, the program calls 'enter_state(STATE_ENTRY_1,
...)' - from inside the alarm-handling code itself, not from a
button press. What does this tell you about what can trigger a
state transition? Must it always be a button press?

--------------------------------------------------------------------------------
GE 8 - Comparing three versions of the same lock
--------------------------------------------------------------------------------

You have now seen three variations of the same combination lock:
a step-counter with 'if (attempts == 1) { ... } else if (attempts
== 2) { ... }' logic in Activity 6, a version refactored to use
functions in Activity 8, and now this state machine version -
which also behaves differently, checking the whole combination at
once rather than rejecting on the first wrong button.

Compare all three versions (open your earlier sketches if you
still have them). What does naming the states explicitly add
that the attempts-counter versions did not have? Is there
anything the earlier versions did more simply? A state machine
is a tool, not always the best tool - when would a simple
counter be preferable to a full state machine?


================================================================================
Extension Activities
================================================================================

--------------------------------------------------------------------------------
EA 1 - Hold-to-relock from UNLOCKED
--------------------------------------------------------------------------------

The UNLOCKED state currently does nothing useful after the
lock opens - LED5 stays on indefinitely. Implement a re-lock
mechanism: SW5 must be held for RESET_HOLD_TIME milliseconds
to re-lock. Use the 'button_is_down' and 'button_down_time'
pattern from Activity 11.

Why require a hold rather than a tap to re-lock? Think about
what would happen in a real access-control system if the door
accidentally re-locked while someone was passing through.

--------------------------------------------------------------------------------
EA 2 - Lockout after failed attempts
--------------------------------------------------------------------------------

Add a lockout after three failed attempts. Declare an
'attempt_count' variable that increments each time the lock
transitions to ALARM (which only happens from STATE_ENTRY_3).
After three failed attempts, enter a LOCKOUT state that ignores
all input for LOCKOUT_TIME milliseconds before returning to
ENTRY_1.

Add LOCKOUT to your state diagram and identify the new
transitions. How does this change the security of the lock
compared to the version with no lockout?

--------------------------------------------------------------------------------
EA 3 - A four-button combination
--------------------------------------------------------------------------------

Extend the lock to a four-button combination. Add a
'CORRECT_4' constant, an 'entered_4' variable, and a new
'STATE_ENTRY_4' state following the same pattern as
ENTRY_1 through ENTRY_3. Update the state diagram, the
'STATE_NAMES' array, and the final check in what is now
STATE_ENTRY_4 to compare all four entered values.

What did you have to change in how many places to add one more
digit? A fully flexible version - supporting any combination
length without adding a new state and a new variable for each
digit - would store the combination in an array and use a loop
with an index variable instead. Arrays and indexing are covered
in the intermediate activities; for now, four independent
variables is a reasonable way to extend this design by one step.

--------------------------------------------------------------------------------
EA 4 - Designing a security alarm capstone
--------------------------------------------------------------------------------

Consider how this combination lock could form the arm/disarm
mechanism for a security alarm capstone project. What would
the full system's state diagram look like, including:
- Disarmed state (lock is open, sensors ignored)
- Arming state (countdown delay while you leave)
- Armed state (sensors active)
- Triggered state (alarm sounding)
- Each combination lock state for disarming

Draw the complete state diagram. How many states does the
full system have? How does the lock's state machine nest
inside the alarm system's state machine?

--------------------------------------------------------------------------------
EA 5 - Traffic Light Controller
--------------------------------------------------------------------------------

Apply what you have learned to a different kind of state
machine - one driven mostly by elapsed time rather than button
presses, with events (a simulated car and pedestrian) setting
flags that are checked later rather than triggering an immediate
transition. Open: B12_Traffic_Light_Controller_Project

This project is a skeleton, not a finished sketch - re-read
GE1 through GE7 before starting, since the traffic light reuses
the same enter_state() and named-constant patterns as the
combination lock above.

*/
