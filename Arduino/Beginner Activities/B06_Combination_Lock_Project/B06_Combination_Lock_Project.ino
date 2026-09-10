/* ================================================================================
Beginner Activity 6 Project: Combination Lock [B06_Combination_Lock_Project]
Version: 1.2
Updated: September 10, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPERNano.h header file
=================================================================================*/
// IMPORTANT: Make sure that BEAPERNano.h is accessible as a tab in this project.
#include "BEAPERNano.h"   // Define BEAPER Nano I/O devices

/* ================================================================================
Combination Lock
================================================================================

Real combination locks require a specific sequence of inputs before
they open. This project asks you to build one, using a step counter
and conditional loops from this activity's examples.

Your combination lock should:

 - Use a sequence of at least four button presses as the combination
   (buttons can repeat - for example SW2, SW3, SW2, SW5 is a valid
   four-step combination).
 - Track progress through the sequence using a step counter variable.
 - Give confirmation feedback for a correct press, and a clearly
   different error signal for a wrong press, resetting the step
   counter back to 0 so the whole sequence must be re-entered from
   the start.
 - Celebrate somehow when the full sequence is entered correctly, and
   stop accepting input until the program is reset (or restarted).

The exact combination, the confirmation and error signals, and the
celebratory correct code signal are up to you - there's no single
correct design. Use Serial.print() while developing your program to
check that your step counter is behaving as you expect it to, and
then remove or comment out the calls when you're satisfied that the
program is working properly.

Stretch goals:

 - Add a lockout: after a number of incorrect attempts, ignore all
   input for several seconds before allowing the user to try again.
 - Add a timed entry window: each step must be pressed within a few
   seconds of the last one, or the sequence resets automatically.
 - Track and display the longest correct partial sequence entered so
   far, even on attempts that were never completed.
*/

// ---- Program Constants ----------------
// TODO: Set the code length.

// ---- Program Variables ----------------
// TODO: Define a step counter variable, starting at 0.

// TODO: Define a variable to track whether the most recent button
// press matched the expected button for the current step - you'll
// update this on every press, not just once at the end.

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

    Serial.begin(9600);                 // Initialize serial output for debugging
    delay(2000);                        // Give the Serial Monitor time to connect
}

void loop()
{
    // TODO: Wrap everything below in a counted while loop that runs
    // while the step counter is less than your code length. This
    // forms the digit-entry loop, and it exits once the full sequence
    // has been entered correctly. Note that loop() itself already
    // runs forever, the same way Python's outer 'while True:' does -
    // you don't need an extra loop around this one.

    // TODO: Read all four pushbuttons.

    // TODO: If any button is pressed:
    //   - Compare it against the button expected for the current
    //     step using an if/else if chain keyed on the step counter's
    //     value (see Activity 5's GE 5 for a similar pattern,
    //     comparing a variable against several possibilities in
    //     turn).
    //   - If it matches: advance the step counter, and give
    //     confirmation feedback.
    //   - If it doesn't match: give error feedback, and reset the
    //     step counter back to 0.
    //   - Wait in a second, indefinite while loop until the button is
    //     released, before continuing - this prevents a single press
    //     from being counted more than once.

    // TODO: The digit-entry loop exits on its own once the full
    // combination has been entered correctly. Celebrate, and stop
    // responding to further button presses until reset - as long as
    // the step counter isn't reset back to 0, the while loop's
    // condition above will stay false on every future call to
    // loop(), which keeps the program from responding to any more
    // presses on its own.

    delay(20);  // Short delay for button debouncing
}
