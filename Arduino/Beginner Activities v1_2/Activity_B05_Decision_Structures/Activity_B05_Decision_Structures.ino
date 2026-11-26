/* ================================================================================
Beginner Activity 5: Decision Structures [Activity_B05_Decision_Structures.ino]
Version: 1.2
Updated: November 24, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPERNano_v1_2.h header file
=================================================================================*/
// IMPORTANT: Make sure that BEAPERNano_v1_2.h is added as a tab in this project.
#include "BEAPERNano_v1_2.h"   // Define BEAPER Nano I/O devices

// ---- Program Constants ----------------
const int MAX_COUNT = 50;

// ---- Program Variables ----------------
bool SW2_pressed;
bool SW3_pressed;
bool SW4_pressed;
int SW2_presses = 0;
int SW3_presses = 0;
bool SW2_last = false;
bool SW3_last = false;

void setup()
{
    // Configure Arduino Nano ESP32 status LED as output
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, HIGH);    // Status LED on

    // Configure BEAPER Nano LEDs as outputs
    pinMode(LED1, OUTPUT);
    pinMode(LED2, OUTPUT);
    pinMode(LED3, OUTPUT);
    pinMode(LED4, OUTPUT);

    // Configure BEAPER Nano pushbuttons as inputs
    pinMode(SW1, INPUT_PULLUP);
    pinMode(SW2, INPUT_PULLUP);
    pinMode(SW3, INPUT_PULLUP);
    pinMode(SW4, INPUT_PULLUP);

    Serial.begin(9600);                 // Initialize serial output for debugging
    delay(2000);                         // Give the Serial Monitor time to connect
}

void loop()
{
    // Read pushbuttons
    SW2_pressed = (digitalRead(SW2) == LOW);
    SW3_pressed = (digitalRead(SW3) == LOW);
    SW4_pressed = (digitalRead(SW4) == LOW);

    if (SW2_pressed)
    {
        digitalWrite(LED1, HIGH);
    }
    else
    {
        digitalWrite(LED1, LOW);
    }

    delay(20);  // Short delay for button debouncing
}


/* =============================================================================
Guided Exploration
================================================================================

Real programs rarely make simple yes/no decisions. Most interesting
behaviour comes from choosing between multiple possibilities based
on changing input conditions or values, and from comparing them with
what has happened before.

This activity introduces the if/else if chain - a way of expressing
multi-way decisions - along with comparison operators, counting
variables, and edge detection. Combined with the named variables and
Boolean logic from Activity 4, these features make it possible to
create programs with memory and multi-way judgment.

--------------------------------------------------------------------------------
GE 1 - Combining conditions with '&&'
--------------------------------------------------------------------------------

This program's button variables (SW2_pressed, SW3_pressed, etc.) hold
true or false Boolean values, which means they can easily be combined
using the Boolean logical operators '&&' (AND), '||' (OR), and '!' (NOT).
For example, changing the if condition in the program to:

Example code:

if (SW2_pressed && SW3_pressed)

...will light LED1 only when both SW2 and SW3 are pressed at the same
time. Modify the if condition in your program to match this example
and verify that it works as expected.

--------------------------------------------------------------------------------
GE 2 - The '||' operator
--------------------------------------------------------------------------------

Replace the '&&' operator in the if condition with '||' and run the
program again. Does it work the way you would expect it to?

--------------------------------------------------------------------------------
GE 3 - The '!' operator
--------------------------------------------------------------------------------

It's just as easy to invert an input to its opposite state using the
'!' (NOT) logical operator. Predict how you think this conditional
expression will behave:

Example code:

if (SW2_pressed && !SW3_pressed)

Try the condition in your program to verify your prediction.

--------------------------------------------------------------------------------
GE 4 - Counting button presses
--------------------------------------------------------------------------------

Let's make this program count the number of times SW2 is pressed.
Start by reverting the if condition back to reading only the state of
SW2.

Next, add the 'SW2_presses++' increment operation inside the if
block to accumulate SW2 presses. This is shorthand for
'SW2_presses = SW2_presses + 1' - it adds 1 to the current value and
stores the result back into the same variable:

Example code:

if (SW2_pressed)
{
    digitalWrite(LED1, HIGH);
    SW2_presses++;
}
else
{
    digitalWrite(LED1, LOW);
}

Add Serial.print() calls inside the if block to display the count in
the Serial Monitor each time SW2 is pressed:

Example code:

if (SW2_pressed)
{
    digitalWrite(LED1, HIGH);
    SW2_presses++;
    Serial.print("SW2_presses: ");
    Serial.println(SW2_presses);
}

Run the program, open the Serial Monitor, and press SW2 a few times.
How quickly does the count increase? Does the count go up once per
press, or faster? What do you think is happening?

--------------------------------------------------------------------------------
GE 5 - Comparison operators and if/else if chains
--------------------------------------------------------------------------------

Previous programs have used the '==' (equal to) conditional operator
to check if two values are the same. Arduino C supports six
comparison operators that can be used in if conditions:

==  equal to
!=  not equal to
<   less than
>   greater than
<=  less than or equal to
>=  greater than or equal to

Now add this set of if/else if conditions below the SW2 if block to
display the count using the LEDs:

Example code:

// Light LEDs for different numbers of presses
if (SW2_presses >= 1)
{
    digitalWrite(LED2, HIGH);
}
else if (SW2_presses >= 10)
{
    digitalWrite(LED3, HIGH);
}
else if (SW2_presses >= MAX_COUNT)
{
    digitalWrite(LED4, HIGH);
}

The if/else if structure is a chain of conditional decisions.
Starting with the first if, each condition is evaluated in turn until
the first true condition is found. Once a true condition is found,
its code runs and the rest of the chain is skipped entirely.

Run the program and press SW2. LED2 should light after the first
press - does it? Does LED3 light after ten presses? Using what you
now know about how the chain works, can you explain why?

Re-arrange the conditions so that the chain evaluates from the
largest value down to the smallest, and add a reset block for SW4:

Example code:

// Light LEDs for different numbers of presses
if (SW2_presses >= MAX_COUNT)
{
    digitalWrite(LED4, HIGH);
}
else if (SW2_presses >= 10)
{
    digitalWrite(LED3, HIGH);
}
else if (SW2_presses >= 1)
{
    digitalWrite(LED2, HIGH);
}

// Reset the count
if (SW4_pressed)
{
    SW2_presses = 0;
    digitalWrite(LED2, LOW);
    digitalWrite(LED3, LOW);
    digitalWrite(LED4, LOW);
}

Test the updated program. Does the LED behaviour now match what you
would expect? Press SW4 to reset the count and confirm that all three
LEDs turn off.

Watch closely as the count climbs past 1 and past 10 - does the LED
from an earlier range ever turn back off once a later range lights
up, or do you end up with more than one LED lit at a time? If you
wanted only the current range's LED to be lit at any moment, what
would an else if branch need to do about the other LEDs, and how
might an else at the end of the chain help?

--------------------------------------------------------------------------------
GE 6 - Edge detection
--------------------------------------------------------------------------------

You may have noticed that the counter increases very quickly - much
faster than you are actually pressing the button. This is because the
button state is read every loop cycle, so holding SW2 for even a
fraction of a second registers dozens of counts.

The solution is edge detection - counting a press only when the
button transitions from not pressed to pressed. The program already
declares SW2_last for exactly this purpose:

Example code:

// Detect a new SW2 press (not pressed to pressed transition)
if (SW2_pressed && !SW2_last)
{
    SW2_presses++;
    digitalWrite(LED1, HIGH);
}
else
{
    digitalWrite(LED1, LOW);
}

SW2_last must be updated at the end of each loop cycle, after all the
button logic has run, so it correctly holds the previous loop's
button state:

Example code:

// Save button states for next loop
SW2_last = SW2_pressed;

Add both of these changes to your program. The Serial.print() calls
from GE 4 will now show exactly one count per press in the Serial
Monitor, regardless of how long the button is held. This is a good
example of using serial output to verify that a fix is working
correctly - once you are satisfied, the Serial.print() calls can be
removed or commented out.

The SW3_last variable is also already declared for the same purpose.
Can you add edge detection for SW3 as well?

--------------------------------------------------------------------------------
GE 7 - Comparing to Activity 4
--------------------------------------------------------------------------------

Remove the Serial.print() calls from your program and run it to
confirm everything still works correctly. Now think back to
Activity 4, where pressing SW1 during the light pattern had no effect
until the pattern finished. How is the approach in this activity
different, and what makes edge detection better suited to counting
presses accurately?


================================================================================
Extension Activities
================================================================================

The activities below build directly on the counting and edge
detection techniques from the Guided Exploration. Use named variables
and constants throughout, and use Serial.print() to help develop and
debug your programs - removing or commenting out debugging output
once you are satisfied that everything works correctly.

--------------------------------------------------------------------------------
EA 1 - Up/down counter with clamping
--------------------------------------------------------------------------------

Modify the press-counting program from the Guided Exploration so that
pressing SW3 increases the count and pressing SW2 decreases it. Clamp
the count so that it can never go below zero or above MAX_COUNT. Use
the LEDs to display four ranges of the count value (off, low, medium,
and high).

--------------------------------------------------------------------------------
EA 2 - Scrolling patterns
--------------------------------------------------------------------------------

Create a program that uses SW2 and SW3 as 'back' and 'forward'
buttons to scroll through four different LED patterns, one per button
press. Pressing SW3 should advance to the next pattern, and pressing
SW2 should go back to the previous one. The sequence should wrap
around - going past the last pattern returns to the first, and going
before the first returns to the last.

--------------------------------------------------------------------------------
Project: Rapid-Clicker Game
--------------------------------------------------------------------------------

Looking for a bigger challenge that pulls these ideas together?
B05_Rapid_Clicker_Project is a separate, open-ended
project file that asks you to build a two-player clicking race, using
edge-detected counters, an if/else if chain, and a Boolean game-state
variable from this activity's own toolkit. It's provided as a
skeleton with TODOs rather than a finished program - a good next step
if you'd like to develop your skills more independently.

*/