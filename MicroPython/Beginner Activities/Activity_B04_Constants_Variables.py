"""
================================================================================
Beginner Activity 4: Constants and Variables [Activity_B04_Constants_Variables.py]
February 17, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPER_Nano.py board module file.
================================================================================
"""
# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32
import BEAPER_Nano as beaper

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

    A program constant is simply an un-changing, named value used
    instead of a number in a program. In this program, 'BLINK_DELAY'
    is defined as a constant ('const') with a value of 200. This
    value won't change while the program runs. (The names of
    constants are often written in ALL_CAPS to distinguish them
    from variables -- which we'll learn about, below.)

    The extra work of writing BLINK_DELAY instead of 200 provides
    two important benefits. First, the name 'BLINK_DELAY' is
    descriptive, and provides more meaning to anyone reading the
    program than the number 200 would.

    Second, all of the parts of the program that make use of the
    BLINK_DELAY constant can now be changed simply by editing one
    line at the top of the program. 

    Run the program and watch its blink rate. Then, change the
    value of the BLINK_DELAY constant to 100 and run the program
    again. Then, change it to 50 and run it again. Imagine how much
    longer it would have taken change every single sleep statement
    instead of just changing the constant.

2.  The second important concept introduced in this program is the
    use of variables to store simple true/false values. Variables
    are named, just like constants, but their values are expected to
    change as the program runs. This program defines two variables:

# --- Program Variables ----------------
SW2_pressed = False
display_pattern = False

    Both of these variables have been set to be 'False' but, unlike
    constants, they won't remain that way. Both of these variables
    will switch between being True and False while the program runs.
    Variables that use the 'True' and 'False' states are known as
    Boolean variables, referring to their use in Boolean logic.
    
    What's special about Boolean variables is not just that they
    can change state between True and False, but that that they
    also enable if conditions to use a clever short-cut. Instead
    of checking the value of the display_pattern variable with
    this typical if expression:

    if display_pattern == True:

    The program instead uses this shorter if condition:
    
    if display_pattern:

    In the first case the MicroPython interpreter needs to evaluate
    the 'display_pattern == True' expression to produce either a true
    or false result that will determine the program flow either into
    or around the code inside the if structure.

    Since the expression 'display_pattern == True' can only be true
    if the display_pattern variable itself is True, the second case
    simply uses the state of the display_pattern variable istelf
    (True/False) to determine the path of program execution.

    Explain which part of the program sets the display_pattern
    variable to true, and which part resets it to false.

3.  The third important concept introduced in this program blends
    the features and benefits of the previous two. The SW2_pressed 
    variable is a Boolean variable, just like display_pattern. It
    is assigned a value using this statement:
    
    SW2_pressed = (beaper.SW2.value() == 0)
  
    The SW2 pin is read and compared with 0 because SW2 is connected
    in an active-low resistor pull-up circuit. If the SW2 pin is 0,
    the SW2_pressed variable will be True, enabling it to determine
    the path of any if condition it's used in.

    And, just like the name BLINK_DELAY, the variable name SW2_pressed
    also carries meaning. The variable SW2_pressed will be true only
    when SW2 is actually pressed.

    Could the program use a similar statement to check for a pushbutton
    being released? Create both an appropriate variable name and an
    expression that could be used to detect if the SW2 pushbutton is
    in an un-pressed state.
    
4.  The last new concept introduced in this program demonstrates a
    method of ensuring that input state remains consistent for the
    duration of each main loop cycle in the program.

    Doing this is not a critical requirement for this program, but it
    does become important in a large, complex program loop. Imagine if
    the state of SW2 needs to be evaluated multiple times, and each
    time SW2 is read using a typical input expression: 
    
    if beaper.SW2.value() == 0:

    There is no guarantee that every read of SW2 during the same
    program loop will produce the same, consistent value. A solution
    to this problem is to store SW2's state in a variable just once
    during each program cycle, and then to have any other parts of
    the program that need to use SW2's state read the value of the
    variable instead of the switch itself:
    
    SW2_pressed = (beaper.SW2.value() == 0)
    
    The SW2 state now remains consistent for the duration of each main
    loop cycle and, as a bonus, conditional expressions reading the 
    variable now read logically and can be more helpful to anyone
    trying to understand the code:

    if SW2_pressed:

    This conditional espression is simple, short, meaningful, and
    unambiguous. A programmer trying to understand or add features
    to the code won't have to think about whether the switch is
    active-high or active-low (although somebody had to, earlier),
    making code maintenace easier. Because this method is so clear
    and useful, you'll see it used more in future learning activites.
    
5.  Let's make some extensive changes to the program, with the goal
    of replacing the BLINK_DELAY constant with a blink_delay_ms
    variable, defined in the new program as shown:

blink_delay_ms = 200

    The blink_delay_ms variable is defined as having a value of 200,
    but the lack of a 'const' qualifier means that it will be able
    to change as the program runs.

    Replace all of the existing program code with the new program
    code below, starting from the 'Program Constants' comment down 
    to the end of the program:

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

    Can you predict what the program will do and how it works? 
    Which characteristics of the new program code helped you to
    make your prediction or helped you to understand the code?

7.  How does the compiler know that BLINK_DELAY is a constant,
    and that blink_delay_ms is a variable?

8.  Predict what will happen in the above program if two buttons are
    pressed at the same time. Try it! Was your prediction correct?
    Explain why you think this happens.
    

Programming Activities

1.  Re-create the Start-Stop pushbutton program from Activity B03
    using named buttons and logical variables. (The details are
    repeated below.)

    Create a program that simulates the separate 'Start' and 'Stop'
    buttons that would be found on large, industrial machines. The
    machine (simulated by an LED) should turn on when the 'Start'
    button is pressed, and remain on until the 'Stop' button is
    pressed. Ensure that the machine cannot be turned on while the
    Stop button is being pressed.

2.  Create the code for a 'toggle' button, a type of switch behaviour
    that uses a single button to alternately turn a device or feature
    on and off. Toggle buttons are commonly used as power buttons in
    electronics devices.
    
    In order to use a momentary button to turn a device on or off, the
    program needs to remember the current power state. And, in order
    for the program to only change states when there a new button press
    occurs, the program must also remember the last button state. This
    allows the current button state to be compared with the previous
    button state so that only a change from not-pressed to pressed
    will enable the toggle button to perform its intended action. For
    this program each press of the toglle button should alternately
    turn a single LED on or off. Ensure that the LED state doesn't
    change if the toggle button is held for any length of time.

3.  Extend the toggle button program you created, above, so that each
    pushbutton on your circuit toggles a corresponding LED, allowing
    a user to set any light pattern on the circuit simply by repeatedly
    pressing the individual buttons.

4.  Re-create the bicycle turn signal circuit from Activity B03 using
    named buttons and logical variables. (The details are repeated
    below.)

    Imagine that you're creating a turn signal circuit for a bicycle.
    The circuit design uses four LEDs mounted in a horizontal row
    under the rider's seat, and these will be controlled by two
    pushbuttons mounted on the bicycle's handlebars. Write a program
    to simulate the operation of the turn signal circuit using one
    or more of the LEDs to indicate a turn while its corresponding
    direction button is being held.

    For an extra challenge, add brake functionality or a bell/horn
    feature. Can you make the brake or horn operate while the turn
    signal is in operation? 
    
"""