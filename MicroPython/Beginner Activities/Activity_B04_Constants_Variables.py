"""
================================================================================
Beginner Activity 4: Constants and Variables [Activity_B04_Constants_Variables.py]
February 9, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPER_Nano.py board module file.
================================================================================
"""
# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32
import BEAPER_Nano as beaper

import time

import time

# --- Program Constants ----------------
BLINK_DELAY = const(200)

# --- Program Variables ----------------
SW2_pressed = False
display_pattern = False

beaper.nano_led_on()

while True:
  SW2_pressed = (beaper.SW2.value() == 0)
  
  # Start pattern with SW2 press
  if SW2_pressed:
    display_pattern = True
        
  # Show pattern on LEDs
  if display_pattern:
    beaper.LED2.value(1)
    time.sleep_ms(BLINK_DELAY)
    beaper.LED3.value(1)
    time.sleep_ms(BLINK_DELAY)
    beaper.LED4.value(1)
    time.sleep_ms(BLINK_DELAY)
    beaper.LED5.value(1)
    time.sleep_ms(BLINK_DELAY)
    beaper.LED2.value(0)
    time.sleep_ms(BLINK_DELAY)
    beaper.LED3.value(0)
    time.sleep_ms(BLINK_DELAY)
    beaper.LED4.value(0)
    time.sleep_ms(BLINK_DELAY)
    beaper.LED5.value(0)
    time.sleep_ms(BLINK_DELAY)
    display_pattern = False

    
"""
Program Analysis Activities

1.  There are a lot of new and important concepts to cover in this
    program, so let's start at the top with the simplest one: program
    constants:

# --- Program Constants ----------------
BLINK_DELAY = const(200)

    A program constant is simply an un-changing, named value used in
    a program. In this program, the named constant 'BLINK_DELAY' is
    defined as 200 – and it won't change while the program runs.
    (Constants are often written in ALL_CAPS to distinguish them
    from variables, which we'll find out about below.)

    It might seem like extra work to write BLINK_DELAY instead of
    200, but using a name instead of a number provides two important
    benefits. First, the name 'BLINK_DELAY' is more descriptive
    than '200', and provides instrinsic meaning for anyone reading the
    program. Second, using the BLINK_DELAY constant in all instances
    of the delay functions allows all of the delay values to be
    changed simultaneously using just one, single edit at the top of
    the program.

    Run the program. Then, change the BLINK_DELAY constant to 100 and
    run it again. Then, change it to 50, or another number. Imagine
    how much longer it would have taken to make the changes in every
    single delay statement instead!

2.  The next important concept introduced in this program is the use
    of true or false logic, also known as Boolean logic, in variable
    expressions:

# --- Program Variables ----------------
SW2_pressed = False
display_pattern = False

    Both of these variables have been set to be 'False' but, unlike
    constants, they don't have to remain that way. Variables can
    change their value while the program executes.

    Let's look at how the 'display_pattern' variable changes as this
    program runs. Pressing SW2 sets display_pattern to 'True'. Later,
    it's set back to 'False' at the end of the 'if display_pattern'
    condition. 

    What's special about using Boolean variables is that they enable
    if conditions to take a short-cut. Instead of being written as a
    typical conditional expression, like this:

  if display_pattern == True:

    ... it can simply be written as:
    
  if display_pattern:

    In the first example the MicroPython interpreter needs to evaluate
    the 'display_pattern == True' expression to produce either a true
    or false result. If the result of the expression is true, the
    contents of the if structure will be executed.

    Since the expression 'display_pattern == True' can only be true
    when the display_pattern variable itself is True, the second
    example simply uses the variable to determine the if structure's
    outcome.

    Every cycle of the main loop, the SW2 button is checked and 
    will set the display_pattern variable to True if pressed. Unlike
    the if-else structure used in the previous activity, there is
    no program code tied to SW2 to make display_pattern False. Explain
    why the LED animation stops after SW2 is released.

3.  The third important concept in this program blends the features
    and benefits of the previous two. Near the top of the program,
    'SW2_pressed' is defined as a Boolean variable by setting it to
    be False:

SW2_pressed = False

    Then, the first statement in the main while loop reads the value
    of the SW2 button pin, and compares it with 0 (because SW2 is an
    active-low pushbutton, wired to the microcontroller as a resistor
    pull-up input circuit):
    
  SW2_pressed = (beaper.SW2.value() == 0)
  
    If SW2's value is 0, the expression being evaluated will be True,
    making the 'SW2_pressed' variable 'True'. The 'SW2_pressed' 
    variable can now be used in a condition structure without another
    expression evaluation, exactly as with display_pattern, above.

    And, just like the name BLINK_DELAY, the variable name SW2_pressed
    also carries meaning. SW2_pressed will only be True only when SW2
    is actually pressed.

    How could a program check for a pushbuton being released? Create
    both an appropriate variable name and an expression that could be
    used to detect if the SW2 pushbutton is in an un-pressed state.
    
4.  The last new concept introduced in this program is that of ensuring
    input state remains consistent for the duration of each main loop
    cycle in the program.

    This is not a critical feature for this program since it's just a
    simple example, but imagine a complex program that needs to read
    SW2 multiple times during a long, complicated main program loop.
    If the state of SW2 is re-read every time with a typical input
    expression, like this one:
    
    if beaper.SW2.value() == 0:

    ... there is no guarantee that the value of SW2 would be the same
    for every read during a main loop cycle. Instead of re-reading SW2,
    this program saves SW2's state in the 'SW2_pressed' variable after
    reading it just once during every main loop cycle:
    
    SW2_pressed = (beaper.SW2.value() == 0)
    
    Every subsequent use of SW2 in the main code can now simply refer
    to the SW2_pressed variable instead of reading the SW2 pin again,
    ensuring that its state remains consistent for the duration of
    each main loop cycle. On top of that, this method of saving the
    button state also makes button conditions read nicely:

    if SW2_pressed:

    This conditional espression is simple, short, and unambiguous. In
    addition, a programmer adding code to the program later doesn't
    have to remeber if SW2 is active-high or active-low, making it
    quicker and easier for them to modify the program or add additional
    functionality. It's so clear and useful that this method of storing
    input state using a variable will be used in all future learning
    activities.
    
5.  Let's make some big changes to the program, with the main focus
    being to replace the BLINK_DELAY constant with a blink_delay_ms
    variable. Doing this will allow the program itself to change the
    speed of the LED pattern without requiring the program to be
    stopped to edit the value of the constant.

    Replace all of the existing program code with the code below,
    starting from the 'Program Constants' comment to the end of the
    program:

# --- Program Constants ----------------
SLOW_DELAY = const(200)
MEDIUM_DELAY = const(100)
FAST_DELAY = const(50)
LUDICROUS_DELAY = const(25)

# --- Program Variables ----------------
SW2_pressed = False
display_pattern = False
blink_delay_ms = 200

beaper.nano_led_on()

while True:
  # Check pushbuttons
  slow_button = (beaper.SW2.value() == 0)
  medium_button = (beaper.SW3.value() == 0)
  fast_button = (beaper.SW4.value() == 0)
  ludicrous_button = (beaper.SW5.value() == 0)
  
  if slow_button:
    blink_delay_ms = SLOW_DELAY
    display_pattern = True

  if medium_button:
    blink_delay_ms = MEDIUM_DELAY
    display_pattern = True
    
  if fast_button:
    blink_delay_ms = FAST_DELAY
    display_pattern = True

  if ludicrous_button:
    blink_delay_ms = LUDICROUS_DELAY
    display_pattern = True

  # Show the pattern
  if display_pattern:
    beaper.LED2.value(1)
    time.sleep_ms(blink_delay_ms)
    beaper.LED3.value(1)
    time.sleep_ms(blink_delay_ms)
    beaper.LED4.value(1)
    time.sleep_ms(blink_delay_ms)
    beaper.LED5.value(1)
    time.sleep_ms(blink_delay_ms)
    beaper.LED2.value(0)
    time.sleep_ms(blink_delay_ms)
    beaper.LED3.value(0)
    time.sleep_ms(blink_delay_ms)
    beaper.LED4.value(0)
    time.sleep_ms(blink_delay_ms)
    beaper.LED5.value(0)
    time.sleep_ms(blink_delay_ms)
    display_pattern = False

    Can you predict how the program will work and what the program
    will do? Which characteristics of the new program code helped you
    to make your prediction? Describe how each helped.

7.  Predict what will happen in the above program if two buttons are
    pressed at the same time. Try it! Was your prediction correct?
    Explain why you think this happens.
    

Programming Activities

1.  Create a program that simulates the separate 'Start' and 'Stop'
    buttons that would be found on large, industrial machines. The
    machine (simulated by an LED) should turn on when the 'Start'
    button is pressed, and remain on until the 'Stop' button is
    pressed. Use variables to store both the button state and machine
    state, and ensure that the machine cannot be turned on while the
    Stop button is being pressed.

2.  Create the code for a 'toggle' button, a type of switch behaviour
    that uses a single button to alternately turn a device or feature
    on and off. In order to do this, the previous state of the button
    must be compared with its current state, and the output should
    only change when the button state changes from not being pressed
    to being pressed. Each new press of the toggle button should
    alternately turn a single LED on or off. Ensure that the LED state
    doesn't change if the toggle button is held for any length of time.

3.  Extend the toggle button program you created, above, so that each
    pushbutton on your circuit toggles a corresponding LED, allowing
    a user to simply set any light pattern on the circuit.
    
"""