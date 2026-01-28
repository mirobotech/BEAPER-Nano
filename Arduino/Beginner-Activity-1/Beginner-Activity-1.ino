/* ================================================================================
Beginner Activity 1: Digital Output
Jan 28, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requirements: BEAPERNano.h header file. Make sure that BEAPERNano.h is available
as a tab in this Arduino project.
=================================================================================*/

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

1.  The included BEAPERNano.h header file helps you get started more
    quickly by pre-defining the I/O pins connected to BEAPER Nano's 
    devices, such as its LEDs. The statement:
    
    pinMode(LED2, OUTPUT);
    
    defines LED2 as an OUTPUT device, and the statement:
    
    digitalWrite(LED2, HIGH);
    
    sets the LED2 pin's output voltage to either HIGH (5V) or LOW (0V).
    Each of the other BEAPER Nano LEDs (LED3 - LED5) can be controlled
    in exactly the same way. Let's try it!

    Add a second LED output statement to light LED3 below the statement
    that lights LED2. Run the program and describe what happens.

2.  Each line of the program code is read in sequence from the top to
    the bottom of the program, and each statment is run only once.
    
    Most microcontroller programs need to run their main code over and
    over again instead of just once. In Arduino C code, program statements
    inside the setup() function run once, while program statements in the
    loop() function are repeated. In Arduino programs, it's important that
    all program statments are part of a function, and this can be ensured
    by placing them inside a function's curly braces '{ }'.
    
    In this program, would it make sense to turn LED2 on in the loop? Why
    or why not? What would the program be trying to do if we did that?

3.  Since the loop() function contains no program code, you might think
    it would be possible to simply get rid of it. Instead of deleting it
    (you can, we'll add a new loop() in next step), let's just comment
    out the code inside the loop using double slashes, like this:

void loop()
// {
  // Nothing here for now
// }

    The double slashes cause the rest of the line that follows them to 
    be ignored, or 'commented-out'. Try to compile the program and
    describe the result.

4.  Let's try to blink LED3 on and off. Replace the contents of the main
    loop() function with two LED statements, so that it looks like this:

void loop()
{
  digitalWrite(LED3, HIGH);
  digitalWrite(LED3, LOW);
}

    The loop will run each statement once, from top to bottom, and then
    return to the top to re-run the statements. In this case, LED3 should
    turn on, then off, then on again, then off again... forever.
    
    Run the program and observe LED3. Is LED3 on, off, or flashing? What
    do you think is happening? How could you know?


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
    
3.  Make a pattern using the LEDs. Create a program that lights two or
    more of the BEAPER Pico LEDs in a unique pattern. Run your program
    to verify that it works as expected.

*/