/* ================================================================================
Beginner Activity 11: Non-Blocking Timing [Activity_B11_Non_Blocking_Timing]
Version: 1.2
Updated: September 16, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPERNano.h header file
=================================================================================*/
// IMPORTANT: Make sure that BEAPERNano.h is accessible as a tab in this project.
#include "BEAPERNano.h"   // Define BEAPER Nano I/O devices

// ---- Program Constants ---------------
const int LOOP_DELAY      = 1;        // Main loop delay (ms) - see GE1
const int HOLD_TIME       = 500;      // Button hold threshold (ms)
const int BLINK4_INTERVAL = 200;      // LED4 blink toggle interval (ms)
const int BLINK5_INTERVAL = 350;      // LED5 blink toggle interval (ms)

// ---- Program Variables ---------------

// Part 1: Button hold detection
bool          button_is_down   = false; // True while SW2 is held
unsigned long button_down_time = 0;     // Time SW2 was pressed (valid when button_is_down)
bool          hold_fired       = false; // True after hold action fires this press

// Part 2: Multi-rate LED blinking
unsigned long last_blink4_time = 0;    // Last time LED4 state was toggled
unsigned long last_blink5_time = 0;    // Last time LED5 state was toggled
bool          led4_state       = false;
bool          led5_state       = false;


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

    digitalWrite(LED2, LOW);
    digitalWrite(LED3, LOW);
    digitalWrite(LED4, LOW);
    digitalWrite(LED5, LOW);

    // Configure BEAPER Nano pushbutton as input
    pinMode(SW2, INPUT_PULLUP);

    Serial.begin(9600);             // Initialize serial output for debugging
    delay(2000);                    // Give the Serial Monitor time to connect

    Serial.println("Activity 11: Non-Blocking Timing");
    Serial.println("SW2 tap: toggle LED2   SW2 hold: toggle LED3");
    Serial.print("LED4 toggles every "); Serial.print(BLINK4_INTERVAL); Serial.println(" ms");
    Serial.print("LED5 toggles every "); Serial.print(BLINK5_INTERVAL); Serial.println(" ms");
    Serial.println();

    // Initialise blink timestamps to current time
    last_blink4_time = millis();
    last_blink5_time = millis();
}

void loop()
{
    unsigned long current_time = millis();
    bool SW2_pressed = (digitalRead(SW2) == LOW);

    // ---- Part 1: Button hold detection ----

    if (SW2_pressed)
    {
        // Button is currently pressed
        if (!button_is_down)
        {
            // Button just went down - record the time and set flag
            button_is_down   = true;
            button_down_time = current_time;
            hold_fired       = false;
        }
        else if (!hold_fired &&
                 (current_time - button_down_time) >= (unsigned long)HOLD_TIME)
        {
            // Hold threshold reached - fire hold action once
            digitalWrite(LED3, !digitalRead(LED3));
            hold_fired = true;
            Serial.println("Hold: LED3 toggled");
        }
    }
    else
    {
        // Button is not pressed
        if (button_is_down)
        {
            // Button just released
            if (!hold_fired)
            {
                // No hold fired this press - treat as a tap
                digitalWrite(LED2, !digitalRead(LED2));
                Serial.println("Tap: LED2 toggled");
            }
            button_is_down = false;
            hold_fired     = false;
        }
    }

    // ---- Part 2: Multi-rate LED blinking ----

    if ((current_time - last_blink4_time) >= (unsigned long)BLINK4_INTERVAL)
    {
        led4_state = !led4_state;
        digitalWrite(LED4, led4_state);
        last_blink4_time = current_time;
    }

    if ((current_time - last_blink5_time) >= (unsigned long)BLINK5_INTERVAL)
    {
        led5_state = !led5_state;
        digitalWrite(LED5, led5_state);
        last_blink5_time = current_time;
    }

    delay(LOOP_DELAY);
}


/* =============================================================================
Guided Exploration
================================================================================

Activities 9 and 10 used a fixed 'STEP_DELAY' to control the main
loop rate, and all outputs - LED dimming, fading, pot reads - were
tied to the same delay. While this works well for simple programs,
Activity 10 GE5 and GE7 identified a fundamental problem: if any
action within the loop slows down, every other part also slows down.

This activity introduces non-blocking timing: rather than pausing
the whole program with 'delay()', the loop continuously checks
and sets timestamps to decide when each action is due. The first
part detects tap-versus hold on a single button, and the second
part blinks two LEDs simultaneously at different rates - both tasks
that would be impossible using fixed time delays. All responsive
programs implement similar techniques.

--------------------------------------------------------------------------------
GE 1 - Why this activity needs a faster loop
--------------------------------------------------------------------------------

Every program since Activity 2 has used 'delay()' to control how
fast the main loop runs. Activity 9 set STEP_DELAY to 100ms;
Activity 10 set it to 20ms, making that loop run approximately
50 times per second.

This activity sets LOOP_DELAY to 1ms - the loop runs approximately
1000 times per second. Why does this activity need a much faster
loop rate than previous activities?

More fundamentally: in Activity 10, the fade rate was coupled
to STEP_DELAY. Look at this activity's loop. If you added a sensor
read that takes 50ms to execute, would the blink rates be affected?
Why? What would need to change to make the blink rates truly
independent of all other code in the loop?

--------------------------------------------------------------------------------
GE 2 - Unsigned arithmetic and counter rollover
--------------------------------------------------------------------------------

The timing pattern used throughout this program follows the
same structure every time:

Example code:

unsigned long current_time = millis();
if ((current_time - last_event_time) >= INTERVAL)
{
    last_event_time = current_time;
    // take action
}

'millis()' returns the number of milliseconds since the
program started as an 'unsigned long' - a 32-bit unsigned
integer. After approximately 49 days of continuous running,
this counter rolls over from its maximum value back to zero.

Arduino's unsigned arithmetic handles this rollover
calculation correctly, but doing the same calculation with
signed numbers would cause an error. To understand why,
consider what happens when 'current_time' has just rolled
over to a small value (say 10) and 'last_event_time' is still
a large value (say 4294967290):

Example code:

10 - 4294967290

In signed arithmetic this gives a large negative number.
In unsigned long arithmetic, the result wraps around to 16,
which correctly represents that 16ms has elapsed since the
last event. This is why all timing variables in this program
are declared 'unsigned long' rather than 'int' or 'long'.

Notice the cast '(unsigned long)HOLD_TIME' in the comparison.
'HOLD_TIME' is declared as 'int'. What would happen if the
comparison were written without the cast:
'(current_time - button_down_time) >= HOLD_TIME'?

Try removing the cast and observe whether the behaviour
changes. When would the missing cast cause a problem?

--------------------------------------------------------------------------------
GE 3 - Tracing the button hold state machine
--------------------------------------------------------------------------------

The button hold detection uses three variables: 'button_is_down',
'button_down_time', and 'hold_fired'. Trace through the program
carefully for each of these three scenarios and record the state
of all three variables at each step:

Scenario A - Quick tap (button held less than HOLD_TIME):
- Button goes down
- Button released after 200ms

Scenario B - Hold (button held longer than HOLD_TIME):
- Button goes down
- 500ms elapses
- Button released after 800ms total

Scenario C - Long hold (button held much longer than HOLD_TIME):
- Button goes down
- 500ms elapses (hold fires)
- 1000ms elapses
- Button released after 1500ms total

Why are both 'button_is_down' and 'button_down_time' needed
as separate variables? 'button_is_down' tells the program
whether the button is currently held. 'button_down_time'
records when it went down so the hold duration can be
measured. Each variable has one clear responsibility.

Why is 'hold_fired' necessary? What would happen in Scenario C
if 'hold_fired' were not used and the hold action had no
guard condition?

Notice that in a tap, LED2 changes on button release rather
than on button press. This is essential for tap-vs-hold
detection - why? Could you detect a tap on button press
instead, and what information would you need that is not
available at that moment?

--------------------------------------------------------------------------------
GE 4 - Multi-rate blinking and toggle vs. blink rate
--------------------------------------------------------------------------------

Part 2 blinks LED4 and LED5 at different rates simultaneously.
Both LEDs share the same main loop, but each has its own
timestamp and interval constant.

LED4 toggles every BLINK4_INTERVAL milliseconds (200ms). A
full blink cycle - on, then off again - takes two toggles,
so 200ms per toggle means 400ms per full cycle: a blink rate
of 2.5 Hz, not 5 Hz. LED5 toggles every BLINK5_INTERVAL
milliseconds (350ms), for a blink rate of approximately
1.4 Hz. Since these rates are not simple multiples of each
other, the LEDs drift in and out of phase, sometimes toggling
close together, sometimes far apart.

Calculate when LED4 and LED5 will next toggle at the same
time (within one loop iteration), starting from the moment
both are initialised. This is the least common multiple of
their intervals. After this time, does the pattern repeat?

The program uses '>=' rather than '==' to compare elapsed
time against the interval. Explain why '==' would fail
almost every time, even with a 1ms loop delay. What does
this mean for the actual accuracy of the blink interval -
if BLINK4_INTERVAL is 200ms and the loop runs every 1ms,
what is the worst-case timing error for each toggle?

--------------------------------------------------------------------------------
GE 5 - Repeating interval vs. one-shot elapsed time
--------------------------------------------------------------------------------

Look at the two timing patterns side by side:

Button hold detection:
'button_down_time' is set once when the button goes down, and
the elapsed time is checked every iteration while the button
remains held. The important value is the elapsed time from
the start to the end of the button press - a one-shot event.

LED blinking:
'last_blink4_time' is updated each time the LED toggles, and
the elapsed time is checked every iteration unconditionally.
The time is reset every event, and used to set the interval
until the next blink - a periodic, repeating event.

This distinction - a one-shot elapsed time versus a repeating
interval - covers the majority of non-blocking timing needs
in embedded programs. In Activity 12 you will see how these
patterns combine with program state to produce more complex
timed behaviours.

Identify which pattern (repeating or one-shot) would be most
appropriate for each of these timing needs:
a) A status LED that blinks once per second indefinitely
b) A timeout that triggers if no button is pressed for 30s
c) A motor that runs for exactly 2 seconds when SW3 is pressed
d) A sensor read every 500ms regardless of other activity


================================================================================
Extension Activities
================================================================================

The following activities extend the program you have already
been working with. Add each feature directly to this sketch
rather than opening a new one, building on the timing patterns
already in place. EA5 is the exception - it opens a separate
skeleton sketch that reimplements Activity 10's analog output
using the techniques from this activity.

--------------------------------------------------------------------------------
EA 1 - Debouncing SW3 with timing
--------------------------------------------------------------------------------

Mechanical buttons produce multiple rapid transitions (bounces)
when pressed, which can register as multiple presses. This
exercise first lets you see bounce directly, then fixes it.

Part 1 - See the bounce:

Declare an int 'raw_count' starting at 0, and a bool 'sw3_last'
to track the previous reading. In loop(), detect a new press
using simple edge detection (no debounce yet) and increment
raw_count:

Example code:

bool sw3_current = (digitalRead(SW3) == LOW);
if (sw3_current && !sw3_last)
{
    raw_count++;
    Serial.print("Raw count: ");
    Serial.println(raw_count);
}
sw3_last = sw3_current;

Press SW3 once, firmly but normally. Does raw_count increase by
exactly 1? Try several presses. Try pressing the button more
gently and forcefully. Some presses may register as 2 or more,
depending on your specific switch - this is mechanical bounce
being detected as separate presses.

Part 2 - Add debouncing:

A software debounce ignores transitions that occur within
DEBOUNCE_MS of the previous transition. Declare a
'last_sw3_change' unsigned long, an int 'sw3_state' to track the
last stable state, and an int 'debounced_count':

Example code:

int current_sw3 = digitalRead(SW3);
if (current_sw3 != sw3_state &&
    (current_time - last_sw3_change) >= DEBOUNCE_MS)
{
    sw3_state = current_sw3;
    last_sw3_change = current_time;
    if (sw3_state == LOW)
    {
        debounced_count++;
        Serial.print("Raw: "); Serial.print(raw_count);
        Serial.print("  Debounced: "); Serial.println(debounced_count);
    }
}

Keep both counters running side by side and press SW3 several
times. Does debounced_count now match the number of times you
actually pressed the button, even when raw_count shows extra
bounces?

Try DEBOUNCE_MS values of 10, 20, 50, and 100ms and observe the
difference in responsiveness and reliability. What is the minimum
debounce time that eliminates false triggers on your hardware?

--------------------------------------------------------------------------------
EA 2 - Inactivity timeout
--------------------------------------------------------------------------------

Implement an inactivity timeout that turns LED2 and LED3 off after
a time-out delay, and turns them back on when a button is pressed.

Declare a 'last_activity_time' unsigned long that resets to
'current_time' whenever any button is pressed. Set TIMEOUT_MS with
an appropriate time-out value (say 10s, but in milliseconds). If
TIMEOUT_MS elapses with no button activity, enter an idle state:
turn off LED2 and LED3, print a timeout message, and blink the
status LED slowly (say once per second) instead of leaving it
solidly on using the same multi-rate technique from Part 2, just
applied to a new LED at a slower interval. The next button press
should turn the status LED solidly back on, restore normal
LED2/LED3 operation, and reset the timeout.

You will need a 'timed_out' bool, a 'last_heartbeat_time'
unsigned long, and a HEARTBEAT_INTERVAL constant. Only run the
heartbeat logic while 'timed_out' is true:

Example code:

if (timed_out)
{
    if ((current_time - last_heartbeat_time) >= (unsigned long)HEARTBEAT_INTERVAL)
    {
        digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
        last_heartbeat_time = current_time;
    }
}

Notice that LED4 and LED5 keep blinking at their own rates
throughout, completely unaffected by the timeout - a direct
demonstration that independent timers really are independent,
even when a new one (the heartbeat) is added alongside them.

What TIMEOUT_MS value feels natural for a bench instrument that
should indicate it is idle? How does this pattern relate to the
screen-off timers used in battery-powered devices? Why does a
slow blink communicate "idle" more clearly than turning the LED
off completely?

As a further challenge: reconfigure the status LED as a PWM
output (Activity 10) and slowly breathe its brightness up and
down during timeout, rather than blinking it on and off. This
combines this activity's independent timers with Activity 10's
PWM output - a preview of how non-blocking timing can drive
smoothly varying effects, not just on/off toggling.

--------------------------------------------------------------------------------
EA 3 - One-shot timed signal
--------------------------------------------------------------------------------

Implement a one-shot timed signal. When SW4 is pressed, LED2
lights for exactly SIGNAL_MS milliseconds then turns off
automatically, without using 'delay()'. If SW4 is pressed
again while the signal is active, restart the timer from the
new press time.

You will need a 'signal_active' boolean and a
'signal_start_time' unsigned long. Each loop iteration checks
whether the signal is active and whether SIGNAL_MS has elapsed:

Example code:

if (signal_active &&
    (current_time - signal_start_time) >= (unsigned long)SIGNAL_MS)
{
    signal_active = false;
    digitalWrite(LED2, LOW);
}

Try SIGNAL_MS values of 100, 500, and 2000ms. Notice that at
2000ms the main loop continues running normally during the
signal - SW2 tap-and-hold still works, and LED4 and LED5
continue blinking. This would be impossible with 'delay(2000)'.

--------------------------------------------------------------------------------
EA 4 - Independent timing for a slow sensor read
--------------------------------------------------------------------------------

Add independent timing for a slow sensor read alongside the
fast timing already in the loop. Declare a 'last_temp_time'
unsigned long and a TEMP_INTERVAL constant of 2000ms. Each
time TEMP_INTERVAL elapses, call 'temp_level()' and print
the result.

The button and blink timing should be completely unaffected
by the sensor read. Verify this by observing the blink rates
and hold detection while the temperature prints every 2
seconds.

Now temporarily add 'delay(50)' inside the sensor read block
and observe what happens to the blink rates and hold
sensitivity. This demonstrates concretely why blocking calls
anywhere in the loop affect all timing in the loop.

--------------------------------------------------------------------------------
EA 5 - LED Controller Project
--------------------------------------------------------------------------------

Re-implement Activity 10's analog output controls using
independent non-blocking timers.
Open: B11_LED_Controller_Project

This skeleton applies the timing patterns from this activity
to the PWM brightness controls from Activity 10. Each control
gets its own update rate, independent of the others - the
dim rate for LED2, the fade step rate for LED3, and the
pot-polling rate for LED4/LED5 can all be set separately.

*/
