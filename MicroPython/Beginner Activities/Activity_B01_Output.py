"""
================================================================================
Beginner Activity 1: Digital Output [Activity_B01_Output.py]
March 30, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPER_Nano.py board module file.
================================================================================
"""
# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32
import BEAPER_Nano as beaper

# Turn on one LED
beaper.LED2.value(1)

# Main loop - code indented below while True: repeats forever
while True:
  # Nothing here for now
  pass


"""
Guided Exploration

Guided exploration questions and activities help learners further
investigate and expand on the key concepts introduced in the activity.

1.  Most computer programs contain both text comments (which help
    anyone reading the program code to understand it) and the actual
    program statements that the computer will 'run' or execute.

    Single line comments in MicroPython follow a pound sign '#'.
    MicroPython ignores everything that follows a pound sign in a
    single line of text.

    Multi-line comments ignore all of the lines of text between
    matching sets of three single-quote (') or double-quote (") marks.

    Look at the program, above. It's mostly comments! How does the
    MicroPython editor you're using treat the comments differently
    from the actual program code?

2.  The first real program statement encounterd in this program
    imports a 'board module' file for your BEAPER Nano circuit:

import BEAPER_Nano as beaper

    The 'BEAPER_Nano.py' board module file must be copied into the
    filesystem memory of the microcontroller before this program runs.
    Otherwise, when this program starts to run, the import statement
    won't be able to find it. The board module contains ordinary
    MicroPython program code that defines and configures BEAPER Nano's
    I/O devices and microcontroller pins for you, helping you to start
    writing programs for it more quickly. (You can easily open the
    board module file in the code editor to see the code it contains!)

    This import statement includes the contents of the BEAPER_Nano.py
    file into this program, which enables the next statement to use
    device LED2 (since LED2 is defined inside the board module):

beaper.LED2.value(1)
    
    Let's break this statement down: the BEAPER_Nano board module has
    been given the shorter name 'beaper' by the import statement, and
    'LED2' is one of the objects defined in the BEAPER_Nano board 
    module file. MicroPython's 'value' method is used to read or set
    pin values, so the end result of the microcontroller running this
    statement is that the value of the LED2 pin gets set to 1, meaning
    the output voltage of the pin connected to LED2 is set to 3.3V,
    which turns LED2 on!

    All of BEAPER Nano's other LEDs (LED2 - LED5) can be controlled
    in exactly the same way. Let's try it!

    Add a second LED output statement to light LED3 into your program
    below the existing statement that lights LED2. Run the updated
    program to verify that it works as expected.

3.  MicroPython runs every program by reading, interpreting, and
    executing each program statement, in order, from the top of the
    program code, to the bottom.

    So, after adding the statement 'beaper.LED3.value(1)' below the
    existing 'beaper.LED2.value(1)' statement in the previous GE2
    activity, the microcontroller will turn LED2 on first, followed
    by LED3. Though these two actions take place sequentially, they
    happens so fast that, to us at least, it looks like both LEDs
    turn on simultaneously!

4.  If all that we wanted the program to do was to turn two LEDs on,
    it could end after these two statments have run. In reality,
    microcontroller programs usually don't end. Instead, they continue
    running the task they were designed to do over and over again in
    what is called a main program loop.

    In MicroPython programs, the 'while True:' structure is the most
    common method used to create a main program loop. Any statements
    indented below the 'while True:' line will be repeated forever.

    Indentation is very important in MicroPython, and the program
    editor will try to help you to indent your program code in a
    consistent way - let it! If two or more program statements are
    meant to be in the same code structure but use different amounts
    of spaces to indent their code, the MicroPython interpreter will
    generate an error. You'll often run into this problem when
    copying and pasting code from different examples or sources.
    
    Would it make sense to put the 'beaper.LED2.value(1)' statement
    inside the 'while True:' loop? Why or why not? What would the
    program be doing if the statement used to turn LED2 on was moved
    into the 'while True:'' loop?

5.  The 'pass' statement in the main 'while True:' loop prevents
    MicroPython from generating an error due to the otherwise empty
    loop. Comment-out the pass statement by placing a pound sign in
    front of pass, like this:
    
    # pass
    
    Since the MicroPython interpreter will ignore the rest of the line
    following the pound sign, the pass statement will now be ignored.
    Try to run the program and describe what happens. Why do you think
    this is? What does pass do? How might pass be helpful to us later?

6.  Let's try to blink LED3 on and off. Replace the contents of the
    main 'while True:' loop with two statements: one to turn the LED
    on, followed by a second one to turn the LED off:

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
    in EA1, above, is reversed so that LED2 is turned off first, and
    then turned on.
    
    Try it! Does the state of LED2 match your prediction?
    
3.  Create a program that lights a pattern using at least two of
    the on-board LEDs. Run your program to verify that it works as 
    expected.

4.  The BEAPER_Nano.py board module file includes functions to control
    the Arduino Nano ESP32 module's on-board LED (as well as many
    other pin definitions and pre-made functions for the BEAPER Nano
    circuit - feel free to open the file to explore all of the code
    that it contains!).
    
    One of the functions in the BEAPER Nano board module is used to
    turn the Arduino Nano ESP32 microcontroller's on-board LED on,
    like this:
    
    beaper.nano_led_on()

    Add this function call at the very beginning of your program so
    that the Arduino Nano ESP32's LED can act as a status indicator to
    show that your program is running even if none of BEAPER Nano's
    on-board LEDs are lit. Run the program to verify that it works.

"""