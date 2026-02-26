/* ================================================================================
Beginner Activity 1: Output [Activity-B01-Output]
February 25, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPERNano.h header file
=================================================================================*/
// IMPORTANT: Make sure that BEAPERNano.h is accessible as a tab in this project.
#include "BEAPERNano.h"   // Define BEAPER Nano I/O devices

// ---------------------------------------------------------------
// Setup runs once at power-up
// ---------------------------------------------------------------
void setup()
{
    // Configure BEAPER Nano LEDs as outputs
    pinMode(LED2, OUTPUT);
    pinMode(LED3, OUTPUT);
    pinMode(LED4, OUTPUT);
    pinMode(LED5, OUTPUT);

    // Turn on one LED
    digitalWrite(LED2, HIGH);
}

// ---------------------------------------------------------------
// Loop runs forever
// ---------------------------------------------------------------
void loop()
{
    // Nothing here for now
}

/*
Guided Exploration

Guided exploration questions and activities help learners further
investigate and expand on the key concepts introduced in the activity.

1.  Most computer programs contain text comments to help anyone
    reading the program code to understand it, as well as the actual
    program statements that the computer will compile and run.

    Single line comments in Arduino C follow double slashes '//'.
    The compiler ignores everything in a single line that follows
    double slashes.

    Multi-line comments ignore all text between an opening slash-star
    marker and a closing star-slash marker.

    Look at the program, above. How does the Arduino IDE treat the
    comments differently from the actual program code?

2.  The 'included' BEAPERNano.h header file helps you start
    programming more quickly. It does this by defining each BEAPER
    Nano I/O device, and the pin of the Arduino Nano ESP32
    microcontroller that it connects to.

    For example, the program statement:

    pinMode(LED2, OUTPUT);

    first configures LED2 as an OUTPUT. Then, the statement:

    digitalWrite(LED2, HIGH);

    sets the output voltage of the LED2 pin to either HIGH (3.3V)
    or LOW (0V), turning the LED on or off. All of the other BEAPER
    Nano LEDs (LED3 - LED5) can be controlled in exactly the same
    way. Let's try it!

    Add a second LED output statement to light LED3 into your program
    below the existing statement that lights LED2. Run the updated
    program to verify that it works as expected.

3.  Arduino runs every program by reading and executing each program
    statement, in order, from the top of the program code to the
    bottom.

    So, if you added a statement to light LED3 below the existing
    statement that lights LED2 in the previous GE2 activity, LED2
    would turn on first, followed by LED3. Though this happens
    sequentially, it happens so fast it looks like both LEDs turn
    on simultaneously to us.

    Most microcontroller programs don't end, but continue doing the
    thing they were designed to do over and over again in a program
    loop. In Arduino C, program statements inside the setup() function
    run once at power-up, while program statements inside the loop()
    function are repeated forever.

    All program statements must be enclosed within the curly braces
    '{ }' of a function. Would it make sense to move the digitalWrite
    statement that turns LED2 on into the loop()? Why or why not?
    What would the program be doing if it was moved there?

4.  Since the loop() function contains no program code, you might
    think it would be possible to simply get rid of it. Instead of
    deleting it (you can try!), let's comment it out using double
    slashes, like this:

// void loop()
// {
    // Nothing here for now
// }

    The compiler ignores anything following double slashes, so this
    code will be commented-out and ignored. Try to compile the program
    and describe the result. Why do you think this is?

5.  Let's try to blink LED3 on and off. Replace the contents of the
    main loop() function with two LED statements, one to turn the LED
    on followed by a second one to turn the LED off:

void loop()
{
    digitalWrite(LED3, HIGH);   // LED3 on
    digitalWrite(LED3, LOW);    // LED3 off
}

    The loop will run each statement once, first turning LED3 on,
    and then turning LED3 off. After that, the loop will repeat
    from the top, turning LED3 on and off again... forever.

    Run the program and observe LED3. Is LED3 on, off, or flashing?
    What should be happening? How could you test your prediction?


Extension Activities

Extension activities let you apply your skills and extend the learning
of the concepts introduced in the activity.

1.  The setup() function includes a statement to turn LED2 on. What
    do you think will happen if this statement is immediately followed
    by a second statement to turn LED2 off?

    Try it! Do you see LED2 turning on and then off? Explain what is
    happening and why you think this happens.

2.  Predict what will happen if the order of the two LED2 statements
    in EA1, above, is reversed so that LED2 is turned off first,
    and then turned on.

    Try it! Does the state of LED2 match your prediction?

3.  Create a program that lights a pattern using at least two of the
    on-board LEDs. Run your program to verify that it works as
    expected.

4.  The BEAPERNano.h header file refers to the pin definitions for the
    Arduino Nano ESP32 module's on-board LEDs (it doesn't need to
    define them since the Arduino IDE already knows that they are part
    of the Arduino Nano ESP32 module).

    To use the Arduino Nano ESP32's primary LED, it must first be
    configured as an output using the pinMode() function:

    pinMode(LED_BUILTIN, OUTPUT);

    Then, it can be turned on using the digitalWrite() function,
    exactly as with the BEAPER Nano LEDs:

    digitalWrite(LED_BUILTIN, HIGH);

    Add these statements to your program so that the Arduino Nano
    ESP32's LED acts as a status indicator to show you that your
    program is running. Run the program to verify that it works.

    Which other LEDs does the Arduino Nano ESP32 module contain?
    Can you turn them on too?

*/
