/* ================================================================================
Beginner Activity 1: Digital Output [Activity-B01-Output]
February 2, 2026

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
  // Configure ARPS2 LEDs as outputs
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
Program Analysis Activities

1.  The 'included' BEAPERNano.h header file helps you start programming
    more quickly. It does this by defining each BEAPER Nano I/O device,
    and the pin of the Arduino Nano ESP32 microcontroller that it
    connects to. 
    
    For example, the program statement:
   
    pinMode(LED2, OUTPUT);
    
    first defines LED2 as an OUTPUT device. Then, the statement:
    
    digitalWrite(LED2, HIGH);
    
    mmakes the output voltage of the LED2 pin either HIGH (5V), or
    LOW (0V). All of the other ARPS2 LEDs (LED3 - LED5) can be
    controlled in exactly the same way. Let's try it!

    Add a second LED output statement to light LED3 into your
    program below the existing statement that lights LED2. Run
    the program to verify that it works as expected.

2.  Arduino microcontrollers run every program by reading and
    executing each program statement, from the top to the bottom
    of the program code. 
    
    While the statement that turns LED2 on in this program only runs
    once, most microcontroller programs typically run a group of
    statements over and over again in a program loop. In Arduino C
    code, program statements inside the setup() function run once,
    while program statements in the loop() function are repeated.
    
    In Arduino programs, all program statements must be part of a
    function, and this can be ensured by placing them inside a the
    curly braces '{ }' that enclose the function.
    
    In this program, would it make sense to put the digitalWrite
    statement that turns LED2 on inside the loop? Why or why not?
    What would the program be doing if the statement used to turn
    LED2 on was moved into the loop?

3.  Since the loop() function contains no program code, you might
    think it would be possible to simply get rid of it. Instead of
    deleting it (you can, we'll add a new loop() in next step),
    let's just comment-out the looop code using double slashes,
    like this:

// void loop()
// {
  // Nothing here for now
// }

    Doubld slashes signify the start of a code comment, used by
    programmers to explain the meaning or actions of complex code.
    The C compiler ignores anything in the same line following the
    double slashes, so this code will be 'commented-out', or 
    ignored. Try to compile the program and describe the result.

4.  Let's try to blink LED3 on and off. Replace the contents of the
    main loop() function with two LED statements, one to turn the 
    LED on followed by a second one to turn the LED off, so that it
    looks like this:

void loop()
{
  digitalWrite(LED3, HIGH);
  digitalWrite(LED3, LOW);
}

    The loop will run each statement once, first turning LED3 on,
    and then turning LED3 off. After that, the loop will repeat
    from the top, turning LED3 on and off again... forever.
   
    Run the program and observe LED3. Is LED3 on, off, or flashing?
    What should be happening? How could you test if it actually is?


Programming Activities

1.  The setup() function includes a statement to turn LED2 on. What do
    you think will happen if this statement is immediately followed by
    a second statement to turn LED2 off?

    Try it! Do you see LED2 turning on and then off? Explain what is
    happening and why you think this happens.
    
2.  Predict what will happen if the order of the two LED2 statements
    in activity 1, above, is reversed so that LED2 is turned off first,
    and then turned on.
    
    Try it! Does the state of LED2 match your prediction?
    
3.  Create a program that lights a pattern using at least two of the
    on-board LEDs. Run your program to verify that it works as expected.

4.  The BEAPERNano.h header file refers to the pin definitions for 
    Arduino Nano's on-board LEDs (it doesn't need to define them
    since the Arduino IDE already knows that they are part ot the
    Arduino Nano ESP32 module).
    
    To use the Arduino Nano ESP32's primary LED, it must first be
    configured as an output using the pinMode() function:

    pinMode(LED_BUILTIN, OUTPUT);

    Then, it can be turned on using the digitalWrite() function,
    exacltly as with BEAPER Nano's LEDs:
    
    digitalWrite(LED_BUILTIN, HIGH);

    Add these statements to your program so that the Arduino Nano ESP32's
    LED acts as a status indicator to show you that your program is
    running. Run the program to verify that it works.

    Which other LEDs does the Arduino Nano ESP32 contain? Can you turn
    them on too?

*/