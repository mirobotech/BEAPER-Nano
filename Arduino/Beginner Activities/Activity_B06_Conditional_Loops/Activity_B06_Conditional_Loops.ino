/* ================================================================================
Beginner Activity 6: Conditional Loops [Activity_B06_Conditional_Loops]
Version: 1.2
Updated: September 9, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPERNano.h header file
=================================================================================*/
// IMPORTANT: Make sure that BEAPERNano.h is accessible as a tab in this project.
#include "BEAPERNano.h"   // Define BEAPER Nano I/O devices

// ---- Program Constants ----------------
const int FLASH_DELAY = 100;
const int COUNT_DELAY = 500;

// ---- Program Variables ----------------
bool SW5_pressed = false;
int count = 0;

void setup()
{
    // Configure Arduino Nano ESP32 status LED as output
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, HIGH);    // Status LED on

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

    digitalWrite(LED2, HIGH);
    digitalWrite(LED3, HIGH);
    digitalWrite(LED4, HIGH);
    digitalWrite(LED5, HIGH);

    Serial.begin(9600);                 // Initialize serial output for debugging
    delay(2000);                        // Give the Serial Monitor time to connect

    // Wait for SW5 to start the countdown
    Serial.println("Press SW5 to start the countdown...");
    while (!SW5_pressed)
    {
        digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));   // Toggle status LED
        delay(FLASH_DELAY);
        SW5_pressed = (digitalRead(SW5) == LOW);
    }

    // Set status LED and starting count
    digitalWrite(LED_BUILTIN, HIGH);
    count = 4;

    // Count down using LEDs
    while (count > 0)
    {
        if (count >= 4)
            digitalWrite(LED5, HIGH);
        else
            digitalWrite(LED5, LOW);
        if (count >= 3)
            digitalWrite(LED4, HIGH);
        else
            digitalWrite(LED4, LOW);
        if (count >= 2)
            digitalWrite(LED3, HIGH);
        else
            digitalWrite(LED3, LOW);
        if (count >= 1)
            digitalWrite(LED2, HIGH);
        else
            digitalWrite(LED2, LOW);
        Serial.print("count: ");
        Serial.println(count);
        delay(COUNT_DELAY);
        count--;
    }

    // Countdown finished
    Serial.println("Countdown complete!");
    digitalWrite(LED2, LOW);
    delay(COUNT_DELAY);

    // Beep and blink LED three times
    digitalWrite(LED2, HIGH);
    tone(LS1, 4000, FLASH_DELAY);
    delay(FLASH_DELAY);
    digitalWrite(LED2, LOW);
    delay(FLASH_DELAY);
    digitalWrite(LED2, HIGH);
    tone(LS1, 4000, FLASH_DELAY);
    delay(FLASH_DELAY);
    digitalWrite(LED2, LOW);
    delay(FLASH_DELAY);
    digitalWrite(LED2, HIGH);
    tone(LS1, 4000, FLASH_DELAY);
    delay(FLASH_DELAY);
    digitalWrite(LED2, LOW);
    delay(FLASH_DELAY);
}

void loop()
{
    // Program completes in setup() for this activity.
    // See GE 4 to learn how to restructure this using loop().
}


/* ================================================================================
Guided Exploration
================================================================================

Every program written so far has relied on the loop() function running
forever.

A while loop is another kind of loop. Its condition can be any expression
that evaluates to true or false, and the loop will keep running only as long
as that expression remains true. This means a loop can exit when something
happens, or when a value reaches a target. Choosing the right loop condition
is an important part of program design, and this activity explores different
options and when each one is most useful.

--------------------------------------------------------------------------------
GE 1 - Two while loop conditions
--------------------------------------------------------------------------------

This program uses two while loops, each with a different condition.
The first one:

Example code:

while (!SW5_pressed)

...keeps running as long as SW5 is NOT pressed. The loop body toggles
the status LED to let the user know the program is waiting. As soon as
SW5 is pressed, SW5_pressed becomes true, !SW5_pressed becomes false,
and the loop exits.

The second loop:

Example code:

while (count > 0)

...keeps running as long as 'count' is greater than zero. Each
iteration of the loop decreases 'count' by 1, so the loop will exit
after exactly four iterations.

There is an important difference between these two loops. Can you
describe what that difference is? Which one could you predict the
exact number of iterations for before the program runs, and which one
couldn't you? What does this tell you about when each type of
condition is most useful?

--------------------------------------------------------------------------------
GE 2 - Initialize, check, update
--------------------------------------------------------------------------------

The variable 'count' plays three roles in the countdown loop: it is
set to a starting value before the loop begins, it is checked in the
loop's condition on every iteration, and it is changed inside the
loop body. This combination - initialize, check, update - is the
standard pattern for a loop control variable.

Look at the countdown loop and identify where each of these three
things happens:

Example code:

count = 4;              // Initialize
while (count > 0)       // Check
{
    ...
    count--;            // Update
}

What would happen if the 'count--;' line were missing? Try removing
it from your program and running it. What do you observe? Why does
this happen? Open the Serial Monitor to observe the output, then
press the reset button to stop the program and restore the line
before continuing.

--------------------------------------------------------------------------------
GE 3 - The SW5 wait loop's control variable
--------------------------------------------------------------------------------

The SW5 wait loop doesn't count, but still needs to initialize,
check, and update a variable to either continue looping or exit. Look
at the loop and identify what variable it uses, where it gets
initialized, where it is checked, and where it is updated as the loop
runs.

--------------------------------------------------------------------------------
GE 4 - Code after a loop
--------------------------------------------------------------------------------

Notice that the program has code between and after the two main while
loops. The 'digitalWrite(LED_BUILTIN, HIGH)' line runs after the SW5
wait loop exits but before the countdown loop begins, and the
countdown-complete signal runs only after both loops have finished.

You may have noticed that this program places all its code in setup()
rather than loop(), with a comment in loop() explaining why. This
works for a program that runs once and stops, but most microcontroller
programs need to keep running forever.

Modify the program to move all the code from setup() into loop(), so
that after the countdown finishes and the done signal plays, the
program resets and waits for SW5 to be pressed again. What variable
needs to be reset at the start of each loop() cycle, and why?

--------------------------------------------------------------------------------
GE 5 - Three ways to write a wait condition
--------------------------------------------------------------------------------

The 'while (!SW5_pressed)' loop in this program is a common and
useful pattern - a loop that simply waits until something happens
before allowing the program to continue. It can be used any time a
program needs to pause at a specific point until a condition is met.

You have also seen '!' used in if conditions in Activity 5. In both
cases, '!' inverts the truth value of whatever follows it.

Here are three equivalent ways to write the same wait loop:

Example code:

while (!SW5_pressed)                // While SW5 is NOT pressed
while (SW5_pressed == false)        // Same thing, more verbose
while (digitalRead(SW5) != LOW)     // Reading the pin directly

All three do the same thing. The third option reads the hardware pin
directly rather than using a named variable - notice that it requires
you to know whether the switch is active-low or active-high, while
the first two options hide that detail behind a meaningful name.
Which do you find most readable, and why? What does your answer tell
you about the value of meaningful variable names?

--------------------------------------------------------------------------------
GE 6 - Debug output speed
--------------------------------------------------------------------------------

The Serial.print() statements in this program reveal what is
happening inside the loops in the Serial Monitor. Run the program and
observe the output as the countdown progresses.

Add a Serial.println() statement inside the 'while (!SW5_pressed)'
loop to show that the waiting loop is running. What do you observe
about how quickly the messages appear compared to the countdown
loop's messages? What accounts for the difference in speed?

--------------------------------------------------------------------------------
GE 7 - Infinite loops
--------------------------------------------------------------------------------

A conditional loop whose condition never becomes false will run
forever. This is sometimes called an infinite loop, and is usually
the result of a bug rather than intentional design.

The countdown loop exits because 'count--' eventually makes 'count'
reach zero. But what if the condition were 'while (count != 0)' and
count started at an odd number and decreased by 2 each iteration?
Would the loop ever exit? Try it:

Example code:

count = 5;
while (count != 0)
{
    Serial.print("count: ");
    Serial.println(count);
    delay(COUNT_DELAY);
    count -= 2;
}

What happens? Why? What would be a safer condition to use here? Open
the Serial Monitor to observe the output, press the reset button to
stop the program, then change the condition to 'while (count > 0)'
and verify that it now exits correctly.

Arduino C also has a 'do-while' loop variant that guarantees the loop
body runs at least once before the condition is checked - unlike a
regular while loop, which may never execute at all if the condition
starts out false. It looks like this:

Example code:

do
{
    // This always runs at least once
} while (condition);

A do-while is useful when you need to perform an action before you
can evaluate whether to continue - for example, reading a sensor once
before deciding whether to keep reading.


================================================================================
Extension Activities
================================================================================

These activities use conditional loops as a core structural tool. As
you write each program, think carefully about what the loop's exit
condition should be before you start coding - the condition is a
design decision that determines when the program moves on, and
getting it right is just as important as getting the code inside the
loop right.

--------------------------------------------------------------------------------
EA 1 - Refactor the beep-blink pattern
--------------------------------------------------------------------------------

Look at the 'Beep and blink LED three times' section at the end of
the program. It works, but the three repetitions have been written
out manually, which is not ideal and would become impractical if you
wanted five or ten repetitions instead of three.

Replace the three manual repetitions with a single while loop that
produces the same beep-and-blink pattern exactly three times. You
will need a loop control variable to count the repetitions and an
exit condition that stops the loop after the third one.

What is the minimum number of lines your while loop solution
requires? How does it compare in length to the manual version?

--------------------------------------------------------------------------------
EA 2 - Press-and-release detection
--------------------------------------------------------------------------------

Write a program that waits in a loop for SW2 to be pressed, then
waits in a second loop for SW2 to be released, then lights LED2 to
indicate the button was pressed and released. Use Serial.println() to
show each phase - waiting for a press, waiting for release, and done.

Edge detection from Activity 5 catches the moment a button transitions
from not pressed to pressed, but it does so by comparing the current
and previous loop states on every cycle. This press-and-release
approach is different - it explicitly waits in a dedicated loop for
each transition to complete before moving on. When might one approach
be preferred over the other?

--------------------------------------------------------------------------------
EA 3 - Input then output
--------------------------------------------------------------------------------

Write a program that uses a conditional loop to flash LED2 a number
of times equal to the number of times SW3 was pressed before SW5 was
pressed. The program should:

 - Wait in a loop for button presses, counting SW3 presses using edge
   detection and flashing LED2 momentarily on each press
 - Exit the waiting loop when SW5 is pressed
 - Flash LED3 once for each press that was counted, with a short
   pause between each flash

This structure - an input phase that collects data in one loop,
followed by an output phase that acts on that data in a second loop -
is a useful pattern in many programs.

--------------------------------------------------------------------------------
EA 4 - Reaction timer
--------------------------------------------------------------------------------

Create a reaction timer program. The program should:

 - Display a brief 'get ready' signal by lighting LED2
 - Wait for a random delay between 2 and 5 seconds before lighting
   LED3 as the 'go' signal (use the hint below)
 - Wait in a loop for SW3 to be pressed, using a fixed delay(10)
   inside the loop so each iteration takes a known 10ms - this makes
   the iteration count a reliable measure of elapsed time
 - Display the result by lighting a different combination of LEDs
   depending on whether the count was low (fast), medium, or high
 - Use Serial.print() to show the exact iteration count in the Serial
   Monitor

Hint: Arduino's random number generator can produce a random integer
in a range like this:

Example code:

randomSeed(millis());               // Seed using elapsed time since boot
long delay_ms = random(2000, 5001); // Random value between 2000-5000
delay(delay_ms);

--------------------------------------------------------------------------------
EA 5 - Rapid-clicker with a while loop
--------------------------------------------------------------------------------

Re-create the two-player rapid-clicker game from Activity 5's
Rapid-Clicker Project, but replace the 'if (game_active)' block with
a conditional while loop. The game loop should keep running while
neither player has reached MAX_COUNT. When the loop exits, determine
the winner and light the appropriate LED.

How does restructuring the game around a while loop change the
program compared to the Activity 5 version? Is the logic clearer or
less clear? What are the trade-offs?

--------------------------------------------------------------------------------
Project: Combination Lock
--------------------------------------------------------------------------------

Looking for a bigger challenge that pulls these ideas together?
B06_Combination_Lock_Project is a separate, open-ended project file
that asks you to build a button-sequence lock, using a step counter
and conditional loops from this activity's examples. The project is
provided as a skeleton with TODOs, making it a good next step to
build confidence and design projects yourself.

*/
