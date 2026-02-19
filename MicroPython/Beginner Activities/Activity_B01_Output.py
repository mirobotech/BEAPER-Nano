"""
================================================================================
Beginner Activity 1: Digital Output [Activity_B01_Output.py]
January 30, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPER_Nano.py board module file.
================================================================================
"""
# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32
import BEAPER_Nano as beaper

# Turn on one LED
beaper.LED2.value(1)

# Main loop
while True:
  # Nothing here for now
  pass


"""
Program Analysis Activities

1.  The BEAPER_Nano.py board module file is 'imported' at the top of
    this program to help you start programming more quickly. It does
    this by defining each BEAPER Nano I/O device, and the pin of the
    Arduino Nano ESP32 microcontroller that it connects to.
    
    For example, the program statement:
    
    beaper.LED2.value(1)
    
    changes the value of the 'LED2' pin defined by the 'beaper' module
    to make that pin either 1 (on, or 3.3V), or 0 (off, or 0V). All of
    the other BEAPER Nano LEDs (LED3 - LED5) can be controlled in
    exactly the same way. Let's try it!

    Add a second LED output statement to light LED3 into your program
    below the existing statement that lights LED2. Run the updated
    program to verify that it works as expected.

2.  MicroPython runs all programs by reading, interpreting, and
    executing each program statement, from the top to the bottom of
    the program code.
    
    While the statement that turns LED2 on in this program only runs
    once, most microcontroller programs typically run a group of
    statements over and over again in a program loop. In MicroPython
    programs, a 'while True:' structure is used to create a program
    loop, and any statements that are indented below it will repeat
    forever.
        
    Indentation is very important in MicroPython, so let the program
    editor help you indent your program code consistently. (If program
    lines are meant to be parts of the same structure but use different
    indent characters or different numbers of spaces to indent the
    code, the MicroPython interpreter will generate an error. You'll
    often run into this problem when copying and pasting code from
    different examples or sources.)
    
    Would it make sense to put the 'beaper.LED2.value(1)' statement
    inside the loop? Why or why not? What would the program be doing
    if the statement used to turn LED2 on was moved into the loop?

3.  The 'pass' statement in the main 'while True:' loop prevents
    MicroPython from generating an error due to the otherwise empty
    loop. Comment-out the pass statement by placing a pound sign in
    front of pass, like this:
    
    # pass
    
    The MicroPython interpreter will ignore the rest of any line
    after a pound sign, so this pass statement will now be ignored.
    Try to run the program and describe what happens. Why do you think
    this is? What does pass do? How might pass be helpful to us later?

4.  Let's try to blink LED3 on and off. Replace the contents of the
    main 'while True:' loop with one statement to turn the LED on,
    followed by a second to turn the LED off, so that it looks like
    this:

while True:
  beaper.LED3.value(1)  # LED3 on
  beaper.LED3.value(0)  # LED3 off

    Since these two statements are now inside the main loop, 'pass' is
    no longer needed. The loop will run each statement once, first
    turning LED3 on, and then turning LED3 off. After that, the loop
    will repeat from the top, turning LED3 on and off again... forever.
    
    Run the program and observe LED3. Is LED3 on, off, or flashing?
    What should be happening? How could you test if it actually is?


Programming Activities

1.  The statement to turn LED2 on runs before the loop. What do you
    think will happen if this statement is immediately followed by
    a second statement to turn LED2 off?

    Try it! Do you see LED2 turning on and then off? Explain what is
    happening and why you think this happens.
    
2.  Predict what will happen if the order of the two LED2 statements
    in activity 1, above, is reversed so that LED2 is turned off first,
    and then turned on.
    
    Try it! Does the state of LED2 match your prediction?
    
3.  Create a program that lights a pattern using at least two of the
    on-board LEDs. Run your program to verify that it works as
    expected.

4.  The BEAPER_Nano.py board module file includes functions to control
    the Arduino Nano ESP32 module's on-board LED (as well as many
    other pin definitions and pre-made functions for the BEAPER Nano
    circuit - feel free to open the file and explore all of the code
    that it contains!).
    
    Its nano_led_on() function can be used to turn the Arduino Nano
    ESP32's circuit module LED on, like this:
    
    beaper.nano_led_on()

    Add this function at the very beginning of your program so that
    the Arduino Nano ESP32's LED acts as a status indicator to show
    you that your program is running. Run the program to verify that
    it works.

"""