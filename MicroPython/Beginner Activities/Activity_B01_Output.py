"""
================================================================================
Beginner Activity 1: Digital Output [Activity_B01_Output.py]
February 25, 2026

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
Guided Exploration

Guided exploration questions and activities help learners further
investigate and expand on the key concepts introduced in the activity.

1.  Most computer programs contain text comments to help anyone
    reading the program code to understand it, as well as the actual
    program statements that the computer will 'run' or execute.

    Single line comments in MicroPython follow a pound sign '#'.
    MicroPython will ignore everything in a single line that follows
    a pound sign.

    Multi-line comments ignore all text between matching sets of 
    three single-quote (') or double-quote (") marks.

    Look at the program, above. It's mostly comments! How does the
    MicroPython editor you're using treat the comments differently
    from the actual program code?

2.  The first real statement in this program imports a file known
    as a 'board module':

import BEAPER_Nano as beaper

    The 'BEAPER_Nano.py' board module file has to be copied into the
    filesystem of the microcontroller so this program can find it.
    This file contains ordinary MicroPython program code that defines
    and configures BEAPER Nano's I/O devices for you, helping you to
    start programming more quickly. (You can easily open this file in
    the code editor to look at what it contains!)

    The import statement includes the contents of the BEAPER_Nano.py
    file into this program, enabling the next statement to use LED2
    (which is defined in the board module):

beaper.LED2.value(1)
    
    Let's break this statement down: the BEAPER_Nano board module has
    been given the shorter name 'beaper' in the import statement,
    'LED2' is one of the objects defined in the beaper file, and the
    MicroPython 'value' method is used to read or set pin values. So,
    this program statement sets the value of LED2 to 1, which sets it
    to output 3.3V, and turns LED2 on!

    All of BEAPER Nano's LEDs (LED2 - LED5) can be controlled in
    exactly the same way. Let's try it!

    Add a second LED output statement to light LED3 into your program
    below the existing statement that lights LED2. Run the updated
    program to verify that it works as expected.

3.  MicroPython runs every program by reading, interpreting, and
    executing each program statement, in order, from the top of the
    program code, to the bottom of the program.

    So, if you added the statement 'beaper.LED3.value(1)' below the
    existing 'beaper.LED2.value(1)' statement in the previous GE2
    activity, LED2 would turn on first, followed by LED3. Though this
    happens sequentially, it happens so fast it looks like both LEDs
    turn on simultaneously to us.

    If all that we needed this program to do was turn two LEDs on, it
    could end after both of these statements have run. In reality,
    microcontroller programs don't end, but continue doing the thing
    they were designed to do over and over again in a program loop.

    In MicroPython programs, the 'while True:' structure is the most
    common method used to create a program loop. Any statements
    indented below the 'while True:' line will be repeated forever.

    Indentation is very important in MicroPython, and the program
    editor will try to help you to indent your program code in a
    consistent way - let it! If two or more program statements are
    meant to be in the same structure but use different numbers of
    spaces to indent the code, the MicroPython interpreter will
    generate an error. You'll often run into this problem when
    copying and pasting code from different examples or sources.
    
    Would it make sense to put the 'beaper.LED2.value(1)' statement
    inside the 'while True:' loop? Why or why not? What would the
    program be doing if the statement to turn LED2 on was moved into
    the loop?

4.  The 'pass' statement in the main 'while True:' loop prevents
    MicroPython from generating an error due to the otherwise empty
    loop. Comment-out the pass statement by placing a pound sign in
    front of pass, like this:
    
    # pass
    
    Since the MicroPython interpreter will ignore the rest of the line
    following the pound sign, the pass statement will now be ignored.
    Try to run the program and describe what happens. Why do you think
    this is? What does pass do? How might pass be helpful to us later?

5.  Let's try to blink LED3 on and off. Replace the contents of the
    main 'while True:' loop with one statement to turn the LED on,
    followed by a second one to turn the LED off:

while True:
  beaper.LED3.value(1)  # LED3 on
  beaper.LED3.value(0)  # LED3 off

    Since these two statements are now inside the main loop, 'pass' is
    no longer needed. The loop will run each statement once, first
    turning LED3 on, and then turning LED3 off. After that, the loop
    will repeat from the top, turning LED3 on and off again... forever.
    
    Run the program and observe LED3. Is LED3 on, off, or flashing?
    What should be happening? How could you test your prediction?


Extension Activities

Extension activities let you apply your skills and extend the learning
of the concepts introduced in the activity.

1.  The statement to turn LED2 on runs before the loop. What do you
    think will happen if this statement is immediately followed by
    a second statement to turn LED2 off?

    Try it! Do you see LED2 turning on and then off? Explain what is
    happening and why you think this happens.
    
2.  Predict what will happen if the order of the two LED2 statements
    in EA1, above, is reversed so that LED2 is turned off first,
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
    ESP32's on-board LED on, like this:
    
    beaper.nano_led_on()

    Add this function call at the very beginning of your program so
    that the Arduino Nano ESP32's LED acts as a status indicator to
    show you that your program is running. Run the program to verify
    that it works.

"""