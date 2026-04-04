/* ================================================================================
Beginner Activity 1: Output [BEAPERNano-Activity-B01-Output]
March 30, 2026

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

1.  Most computer programs contain both text comments (which help
    anyone reading the program code to understand it) and the actual
    program statements that the computer will compile and run.

    Single line comments in Arduino C follow double slashes '//'.
    The compiler ignores everything that follows double slashes in
    a single line of text.

    Multi-line comments ignore all of the text between an opening
    slash-star marker and a closing star-slash marker.

    Look at the program, above. How does the Arduino IDE treat the
    comments differently from the actual program code?

2.  The first real statement in this program includes a 'header file'
    for your BEAPER Nano circuit:

#include "BEAPERNano.h"

    The 'BEAPERNano.h' header file must be accessible as a tab in the
    same Arduino project as this program before this program compiles.
    The header file contains ordinary Arduino C code that defines and
    configures BEAPER Nano's I/O devices and microcontroller pins for
    you, helping you to start writing programs for it more quickly.
    (You can click the BEAPERNano.h tab in the IDE to see the code it
    contains!)

    This include statement makes the contents of BEAPERNano.h available
    to this program, which enables the next statements to use device
    LED2 (since LED2 is defined inside the header file):

    pinMode(LED2, OUTPUT);
    digitalWrite(LED2, HIGH);

    Let's break these statements down: 'LED2' is one of the pin
    constants defined in BEAPERNano.h. The pinMode() statement
    configures the LED2 pin as an OUTPUT, and the digitalWrite()
    statement sets its output voltage to either HIGH (3.3V) or LOW
    (0V). Setting it HIGH turns LED2 on!

    All of BEAPER Nano's other LEDs (LED3 - LED5) can be controlled
    in exactly the same way. Let's try it!

    Add statements to configure LED3 as an output and then turn it on.
    Run the updated program to verify that it works as expected.

3.  Arduino runs every program by reading and executing each program
    statement, in order, from the top of the program code to the
    bottom.

    So, after adding a statement to light LED3 below the existing
    statement that lights LED2 in the previous GE2 activity, LED2
    would turn on first, followed by LED3. Though this happens
    sequentially, it happens so fast that, to us at least, it looks
    like both LEDs turn on simultaneously!

4.  If all that we wanted the program to do was to turn two LEDs on,
    it could end after these two statements have run. In reality,
    microcontroller programs usually don't end. Instead, they continue
    running the task they were designed to do over and over again in
    what is called a main program loop.

    In Arduino C, program statements inside the setup() function run
    once at power-up, while program statements inside the loop()
    function are repeated forever. All program statements must be
    enclosed within the curly braces '{ }' of either setup() or loop().

    Would it make sense to move the digitalWrite() statement that turns
    LED2 on into loop()? Why or why not? What would the program be doing
    if the statement used to turn LED2 on was moved into loop()?

5.  Since loop() contains no program code, you might think it would
    be possible to simply get rid of it. Instead of deleting it,
    let's comment it out using double slashes, like this:

// void loop()
// {
    // Nothing here for now
// }

    The compiler ignores anything following double slashes, so this
    code will be commented-out and ignored. Try to compile the program
    and describe the result. Why do you think this is? What role does
    the empty loop() serve? How might it be useful to us later?

6.  Let's try to blink LED3 on and off. Replace the contents of the
    loop() function with two statements, one to turn the LED on
    followed by a second one to turn the LED off:

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
    in EA1, above, is reversed so that LED2 is turned off first, and
    then turned on.

    Try it! Does the state of LED2 match your prediction?

3.  Create a program that lights a pattern using at least two of the
    on-board LEDs. Run your program to verify that it works as
    expected.

4.  The BEAPERNano.h header file refers to the pin definitions for the
    Arduino Nano ESP32 module's on-board LEDs (it doesn't need to
    define them since the Arduino IDE already knows that they are part
    of the Arduino Nano ESP32 module).

    One of the Arduino Nano ESP32's on-board LEDs is called
    LED_BUILTIN. To use it, first configure it as an output, then
    turn it on using digitalWrite(), exactly as with BEAPER Nano's
    other LEDs:

    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, HIGH);

    Add these statements to your program so that the Arduino Nano
    ESP32's LED acts as a status indicator to show you that your
    program is running. Run the program to verify that it works.

    Which other LEDs does the Arduino Nano ESP32 module contain?
    Can you turn them on too?

*/
