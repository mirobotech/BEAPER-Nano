"""
================================================================================
Beginner Activity 1: Digital Output
Jan 26, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requirements: BEAPER_Nano.py board module file. Copy the BEAPER_Nano.py
file into the memory of the Arduino Nano ESP32 microconroller.
================================================================================
"""
# BEAPER Nano board set-up
import BEAPER_Nano as beaper

# Turn on one LED
beaper.LED2.value(1)

# Main loop
while True:
  # Nothing here for now
  pass


"""
Program Analysis Activities

1.  The BEAPER_Nano board module helps you get started more quickly by
    pre-defining and setting up BEAPER Nano's I/O pins. The statement:
    
    beaper.LED2.value(1)
    
    uses the 'beaper' module to let you change the 'LED2' pin's output
    value (1 = on, or 3.3V, and 0 = off, or 0V). Each of the other BEAPER
    Nano LEDs (LED3 - LED5) can be controlled in exactly the same way!

    Add a second LED output statement to light LED3 below the statement
    that lights LED2. Run the program and describe what happens.

2.  MicroPython runs this program by reading and intepreting each program
    statement, from top to bottom in the program code. Each statement,
    such as the statement that turns LED2 on, runs only once.
    
    Most microcontroller programs need to run their main code over and
    over again instead of just once. In MicroPython, program statements
    can be repeated by arranging them into a loop. In this program, the
    'while True:' structure creates a program loop that will repeat any
    statements that are indented below it. Indentation is very important
    in MicroPython, so let the IDE help you indent your program code
    consistently. If program lines that are meant to be part of the same
    structure are indented in different ways from each other, the
    MicroPython intepreter will generate an error.
    
    In this program, would it make sense to turn LED2 on in the loop? Why
    or why not? What would the program be trying to do if we did that?

3.  The 'pass' statement in the main 'while True:' loop prevents MicroPython
    from generating an error due to the otherwise empty loop. Comment-out
    the pass statement by placing a pound sign in front of pass, like this:
    
    # pass
    
    The MicroPython interpreter will ignore the rest of the line following
    the pound sign, so this pass statement will now be ignored. Try to run
    the program and describe what happens. Why do you think this is? What
    does pass do? How might this be helpful for us later?

4.  Let's try to blink LED3 on and off. Replace the contents of the main
    'while True:' loop with two LED satements, so that it looks like this:

while True:
  beaper.LED3.value(1)  # LED3 on
  beaper.LED3.value(0)  # LED3 off

    Since these statements are now part of the main loop, 'pass' is no
    longer needed. The loop will run each statement once, from top to
    bottom, and then return to the top to re-run the statements. In this
    case LED3 should repeatedly turn on, then off, then on again, then
    off again... forever. Run the program and observe LED3. Is LED3 on,
    off, or flashing? What do you think is happening?


Programming Activities

1.  The original program included a statement to turn LED2 on. What do
    you think will happen if this statement is immediately followed by
    a second statement to turn LED2 off?

    Try it! Do you see LED2 turning on and then off? Explain what is
    happening and why you think this happens.
    
2.  Predict what will happen if the order of the two LED2 statements,
    above, is reversed so that LED2 is turned off first, and then on.
    
    Try it! Does the state of LED2 match your prediction?
    
3.  Make a pattern using the LEDs. Create a program that lights two or
    more of the BEAPER Nano LEDs in a unique pattern. Run your program
    to verify that it works as expected.

4.  The BEAPER_Nano board module file includes functions to control the
    Arduino Nano ESP32 module's on-board LED (as well as many other pin
    definitions and pre-made functions for the BEAPER Nano circuit – feel
    free to open the file and explore all the code that it contains!).
    
    The nano_led_on() function can be used to turn the Nano's LED on like
    this:
    
    beaper.nano_led_on()

    Add this function at the very beginning of your program so that the Nano
    LED acts as a status indicator to show you that your program is running.
    Run the program to verify that it works.
    
"""
