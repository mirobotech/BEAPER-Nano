"""
Project:  Introductory Programming Activity 2 - Variables
Activity: mirobo.tech/micropython/intro-2-variables
Updated:  February 22, 2025

This introductory programming activity for the mirobo.tech BEAPER Nano
circuit demonstrates the use of a variable to count button presses and
comparisons between constants and varaibles to trigger an action when
a limit is reached.
 
Additional program analysis and programming activities demonstrate the
use of Boolean (or bool) variables to store state during successive
program loops, the creation of a two-player rapid-clicker game,
simulation of real-world toggle and multi-function buttons, and
the investigation and mitigation of switch contact bounce.

See the https://mirobo.tech/beaper webpage for additional BEAPER Nano
programming activities and starter progams.
"""

# Import Pin and time functions
from machine import Pin
import time

# Configure BEAPER Nano user I/O devices
SW2 = Pin(44, Pin.IN, Pin.PULL_UP)
SW3 = Pin(43, Pin.IN, Pin.PULL_UP)
SW4 = Pin(5, Pin.IN, Pin.PULL_UP)
SW5 = Pin(6, Pin.IN, Pin.PULL_UP)
LED2 = Pin(7, Pin.OUT)
LED3 = Pin(8, Pin.OUT)
LED4 = Pin(9, Pin.OUT)
LED5 = Pin(10, Pin.OUT)
BEEPER = Pin(17, Pin.OUT)

# Configure Arduino Nano ESP32's built-in LEDs
LED_BUILTIN = Pin(48, Pin.OUT, value = 0)   # Active High
LED_BLUE = Pin(45, Pin.OUT, value = 1)      # Active Low
LED_GREEN = Pin(0, Pin.OUT, value = 1)      # Active Low
LED_RED = Pin(46, Pin.OUT, value = 0)       # Active Low

# Define program constants and variables
max_count = const(50)
SW3_count = 0
SW3_pressed = False
LED3.value(0)       # Ensure LED D3 is off when the program re-starts

while True:
    # Count SW3 button presses
    if SW3.value() == 0:
        LED2.value(1)
        SW3_count = SW3_count + 1
    else:
        LED2.value(0)
    
    # Light LED D3 when the maximum count is reached
    if SW3_count >= max_count:
        LED3.value(1)
    # Turn off LED D3 if the real count is very large
    if SW3_count >= 10 * max_count:
        LED3.value(0)
    
    # Turn off LED D3 and reset the count if SW5 is pressed
    if SW5.value() == 0:
        SW3_count = 0
        LED3.value(0)
    
    time.sleep_ms(10)   # Limit main loop cycle rate

"""
Learn More -- Program Analysis Activities

1.  The 'SW3_count' variable gets defined as an integer (int)
    variable by the program declaration:
    
    SW3_count = 0
   
    What range of numbers can a Python integer store? What will
    happen if you try to store a number larger than the upper limit
    of an int integer in the SW3_count variable? What type of
    variable can be used to hold numbers larger or smaller than
    an integer can hold?
   
2.  The 'max_count' constant is defined similarly to a variable,
    but has been made into a constant by defining its value using
    the const() declaration in the program:
    
    max_count = const(50)
    
    Doing this means that, unlike a variable, the value of max_count
    can not be changed as the program runs. The reason for creating
    a constant instead of a variable is to help MicroPython run 
    the program faster.

3.  The max_count constant is used at the start of an if condition:

    if SW3_count >= max_count:

    The condition compares the value of the SW3_count variable with
    the max_count constant to check if a limit has been reached.
    
    Defining a constant for this seems like extra work when the
    conditional statement could simply have been written as:

    if SW3_count >= 50:
  
    Can you think of any advantages of defining and using the
    max_count constant instead of simply embedding the number 50
    into the condition (other than program speed)? List at least
    two advantages.
   
4.  At first glance, it seems that this program should light LED D2
    and increment the SW3_count variable every time that SW3 is
    pressed, but that's not the case. 

    Upload the program and run it, mentally counting how many times
    you pressed SW3 until LED D3 turns on. The count, and LED D3, can
    be reset by pressing SW5 so you can try it multiple times.

    Did the count reach 50? If not, can you describe why, or what
    might be happening in the program to make it mis-count? You may
    be able to gain some insight into what might be happening by
    pressing and quickly releasing SW3 during one attempt to reach
    50, clearing the count using SW5, and then repeating the attempt
    by pressing and slowly releasing SW3.
   
5.  It's okay if you haven't identified any obvious problems with the
    program yet. We can add some debugging code that might help in
    discovering the nature of the problem. It seems like the program
    is counting too quickly. To check, let's add another condition to
    turn LED D3 off if the count gets very large, say ten times bigger
    than expected. We'll add this new condition right after the 
    existing condition that turns LED D3 on, like this:

    # Light LED D3 when the maximum count is reached
    if SW3_count >= max_count:
        LED3.value(1)
    # Turn off LED D3 if the real count is very large
    if SW3_count >= 10 * max_count:
        LED3.value(0)

    Now, press and hold pushbutton SW3 for at least 10 seconds while
    watching LED D3. LED D3 should stay off until the value of the
    SW3_count variable becomes higher than max_count. If LED D3 turns
    on, it should stay on until the value of SW3_count becomes ten
    times higher than max_count. If LED D3 goes off while still holding
    SW3, the SW3_count must be at least ten times the max_count value. 
    
    If LED D3 does that, can you explain how the count could go that
    high while SW3 was only pressed once?
   
6.  One of the fundamental challenges when creating programs that run
    inside a main program loop is separating input events from input
    state. Since the state of SW3 is sensed every cycle through the
    main loop() function, reading its state as 0 simply means that
    the button happened to be pressed during the current loop cycle.
    Since humans are slow, and microcontrollers can run through a
    simple loop like this very fast, the button will likely be read
    as pressed for many cycles through the loop. This explains why
    the SW3_count quickly exceeds max_count.

    To solve this problem, the program cannot simply read the state
    of the switch and assume that a 0 input is a new button press.
    Instead, the program has to identify the change from a 1 to a 0
    input during sucessive loops, as it's this *change* in state
    that is the only reliable indicator of a new button press having
    occurred.

    To do this, a new variable is required to store the state of the
    button from the previous cycle through the loop. The simplest type
    of variable, and one that is ideally suited for this, is a Boolean
    (or, bool) variable. Boolean variables store one of two binary 
    alues -- in MicroPython, the values are represented by the words
    'False' and 'True'.
    
    Below is a re-written input function incorporating the SW3_pressed
    Boolean variable that has been pre-defined in the header section
    of the program. Replace the first SW3 'if-else' conditional
    structure with the following two new 'if' condition structures:

    if SW3.value() == 0 and SW3_pressed == False:
        LED2.value(1)
        SW3_pressed = True
        SW3_count += 1

    if SW3.value() == 1:
        LED2.value(0)
        SW3_pressed = False
        
    The first 'if' condition now logically ANDs both the current
    button state and the SW3_pressed Boolean variable representing
    the button's previous state. Using this logic, the button must
    currently be pressed and it's previous state must be False in
    order to count as a new button press. When both conditions are 
    met, LED D2 will light, the SW3_pressed Boolean variable will be
    set to 'True', and the SW3_count variable will be incremented
    by 1 using the compound operator in the statement 'SW3_count += 1'
    (this produces the same result using less code than the original 
    'SW3_count = SW3_count + 1' statement).

    Notice that even if SW3State is still 0 the next time through
    the main loop, the SW3_pressed variable being 'True' will prevent
    the same button press from being counted more than once. A second
    if condition is used to reset the SW3_pressed Boolean variable to
    'False' when the switch has been released. 

    Try these new code blocks in your program and verify that each
    individual button press is now properly counted.
      
7.  The conditional statement in the first if condition can also be
    written:

    if SW3.value() == 0 and not SW3_pressed:

    The expression 'not SW3_pressed' is equivalent to the Boolean
    variable SW3_pressed being False (or *not* True). Similarly,
    using the SW3_pressed Boolean variable's name by itself is
    equivalent to it being true. Try replacing the first if condition
    in your program with this expression and verify that it works as
    expected.
   
Programming Activities
   
1.  Create a two-player rapid-clicker style game using this program
    as a starting point. The only purpose of the game will be to see
    which player can press a button the fastest and become the first
    player to reach the maximum count and win the game!

    Use SW4 for the second player, and light LED D5 when button SW4
    is pressed. Light LED D4 to show when the second player's count
    equals the max_count.
    
    Start by duplicating the existing program variables to create a
    similar set of variables for the second player. Next, create
    copies of the if condition structures for the second player and
    modify them to use the newly-created second player variables.
    Finally, modify SW5 to reset the counts and LEDs for both players.

2.  When two closely-matched players are playing the rapid-clicker
    game it might be hard to tell which player hit the max_count 
    value first. Use your knowledge of Boolean variables to prevent
    any more presses from increasing the individual player counts
    once one player has achieved the maximum count.

3.  Use a Boolean variable to create a program that simulates the
    operation of a toggle button. Each new press of the toggle button
    must 'toggle' an LED to its opposite state. (Toggle buttons are
    commonly used as push-on, push-off power buttons in digital
    devices, like the power button that turns a computer monitor on
    and off.)
    
    Pressing and holding the toggle button should only cause the LED
    to switch states, or toggle, once -- and not rapidly cycle on and
    off continuously. Test your button's action for reliability.
   
4.  A multifunction button can be used to initiate one action when
    pressed, and a second or alternate action when it is held for
    a certain length of time. One way to implement a multi-function
    button is by using a variable that counts timed program loops --
    exactly as this program did initially (and unitentionally)!
    
    Create a program that implements a multifunction button to light
    one LED as soon as a button is pressed, and light a second LED
    if the button is held for more that one second. Have both LEDs
    turn off when the button is released.
   
5.  Do your pushbuttons bounce? Switch bounce is the term used to
    describe switch contacts repeatedly closing and opening before
    settling in their final (closed) state. Switch bounce in a room's
    light switch might not be a big concern because it happens so
    fast that we would not notice the lights briefly flickering
    before staying on. But, switch bounce could be an issue in a
    software button program because a microcontroller's fast operating
    speed lets it see each contact closure as a new, separate event.
    Imagine if a power button set up as a toggle button bounced and
    each press had between 1 and 4 contact closures. The device would
    not be able to turn on or off reliably.
   
    To determine if your circuit's pushbuttons exhibit switch bounce,
    create a program that counts the number of times a pushbutton's
    contacts close, and then displays the count on the LEDs. Comment-
    out the delay(10); statement in the main loop to ensure that
    short bounce events won't be missed. Use a second pushbutton to
    both reset the count, and to turn off the LEDs, so that the test
    can be repeated.
   
6.  Did any of your pushbuttons bounce? Typical switch bounces appear
    as multiple contact closures within 20-30ms after the initial 
    switch activation. Can you think of a simple software technique
    that could easily be implemented to ignore multiple switch
    activations within a 20ms span?

    External switches can be connected to the expansion header pins
    to check them for bounce as well. Try to find a switch that
    exhibits switch bounce and then add your de-bouncing code to the
    bounce counting program you created in the previous step to
    verify its effectiveness.
"""
