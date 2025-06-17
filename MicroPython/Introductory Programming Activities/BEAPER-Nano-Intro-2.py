"""
Project:  Introductory Programming Activity 2 - Variables
Activity: mirobo.tech/micropython/intro-2-variables
Updated:  June 16, 2025

This introductory programming activity for the mirobo.tech BEAPER Nano
demonstrates the use of variables to count button presses and compares
the use of constant and varaible conditional checks used to trigger an
action when a limit is reached.
 
Additional program analysis and programming activities demonstrate the
use of Boolean (True/False) variables to store state during successive
program loops, the creation of a two-player rapid-clicker game, the
simulation of real-world toggle and multi-function buttons, as well as
investigating and mitigating the effects of switch contact bounce.

See the https://mirobo.tech/beaper webpage for additional BEAPER Nano
programming activities and starter progams.
"""

# Import Pin and time functions
from machine import Pin
import time

# Configure Arduino Nano ESP32 built-in LEDs
LED_BUILTIN = Pin(48, Pin.OUT, value=0)   # Active high
LED_BLUE = Pin(45, Pin.OUT, value=1)      # Active low
LED_GREEN = Pin(0, Pin.OUT, value=1)      # Active low
LED_RED = Pin(46, Pin.OUT, value=0)       # Active low

# Configure BEAPER Nano Educational Starter I/O devices
SW2 = Pin(44, Pin.IN, Pin.PULL_UP)
SW3 = Pin(43, Pin.IN, Pin.PULL_UP)
SW4 = Pin(5, Pin.IN, Pin.PULL_UP)
SW5 = Pin(6, Pin.IN, Pin.PULL_UP)
LED2 = Pin(7, Pin.OUT)
LED3 = Pin(8, Pin.OUT)
LED4 = Pin(9, Pin.OUT)
LED5 = Pin(10, Pin.OUT)
BEEPER = Pin(17, Pin.OUT)

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
  
  # Press SW5 to reset the count and turn off LED D3
  if SW5.value() == 0:
    SW3_count = 0
    LED3.value(0)
  
  # Limit the main loop cycle rate
  time.sleep_ms(10)

"""
Learn More -- Program Analysis Activities

1.  The 'SW3_count' variable gets defined as an integer (int)
    value by the program statement:
    
    SW3_count = 0
   
    What range of numbers can a Python integer store? What will
    happen if you try to store a number larger than the upper limit
    of an int integer in the SW3_count variable? What type of
    variables would need to be used to store numbers larger (or
    smaller) than would fit into an integer variable?
   
2.  The 'max_count' constant definition looks similar to a variable
    definition, with the difference being the addition of a const()
    delclaration:
    
    max_count = const(50)
    
    Defining max_count as a constant means that, unlike a variable,
    the value of max_count cannot be changed by the program while
    the program runs. Use the MicroPython documentation to find at
    least one advantage of defining constants using the const()
    declaration. (MicroPython's documentation can be found here:
    https://docs.micropython.org/en/latest/index.html)
    
3.  The if condition:

    if SW3_count >= max_count:

    simply compares the value of the SW3_count variable with the
    max_count constant, and could have instead been written as:
    
    if SW3_count >= 50:
  
    Can you think of other potential advantages of defining and
    using constants in programs (in general) other than the
    specific example identifier for MicroPython programs, above?
   
4.  At first glance, it seems that this program should light LED
    D2 and increment the SW3_count variable every time SW3 is
    pressed, but you'll soon realize this is not the case. 

    Connect your circuit and run the program while mentally
    counting how many times SW3 has to be pressed before LED D3
    turned on. SW5 resets the count and turns of LED D3 so you
    can easily repeat the test.

    Does your count reach 50 before LED D3 turns on? If not, can
    you describe why the program may over-counting button presses?
    
    (Hint: You might be able to gain some insight into what the
    program is actually doing by pressing and *quickly* releasing
    SW3 during one test, and repeating the test (after resettign
    the count) the next time pressing and *slowly* releading SW3.)
   
5.  It's okay if you haven't identified any obvious problem(s)
    with the program, yet. One technique used by programmers to
    help solve why a program seems to be misbehaving is to add
    some extra debugging code to the program.
    
    In this case, it seems like the program is counting too fast,
    or over-counting each button press. To test this theory, let's
    add a second SW3_count condition block to the program that will
    turn off LED D3 if the count value becomes very large -- say
    ten times larger than expected. Add this block to the program
    immediatly following the existing condition, like this:
    
  # Light LED D3 when the maximum count is reached
  if SW3_count >= max_count:
    LED3.value(1)
  # Turn off LED D3 if the count becomes very large
  if SW3_count >= 10 * max_count:
    LED3.value(0)

    Now, press and hold pushbutton SW3 for at least 10 seconds
    while watching LED D3. Based on our initial interpretation of
    the program, LED D3 should not turn on at all while only being
    pressed once. Does LED D3 turn on? Does it turn also turn off?
        
    If LED D3 turned on, or turned on and off while being held,
    what can you infer about the value of the SW3_count variable?
   
6.  One big challenge for new programmers is learning to understand
    program flow, especially in relation to how relatively slow
    human initiated events are processed by comparatively fast
    microcontrollers.
    
    Recall from the previous programming activity that all typical
    microcontroller programs include a repeating main program loop.
    Each time this program's loop runs, the first thing it does is
    to read the state of the SW3 pushbutton. If SW3 is pressed,
    another count is added to the SW3_count variable. Since
    microcontrollers are so fast, the program can run through its
    main loop many times during a single button press. This should
    explain why SW3_count quickly exceeds max_count.
    
    To solve this problem, the program must only count new pushbutton
    presses, and somehow be made to ignore a previously button press.
    New button presses consist of a change of state, with the button
    input value chagning from a 1 to a 0. In order for our program
    to identify a change of state, it must have a way to remember
    the previous state, and this can be compared with the button's
    current state.
    
    Remembering the button's state can be done using a variable, and
    the simplest type of varaible that happens to be ideally suited
    for this type of application is a Boolean (sometimes called bool)
    variable. Boolean variables store one of two binary values, but
    instead of 0 and 1 in MicroPython these values are represented
    by the words 'False' and 'True'.
    
    Below is a re-written input function incorporating SW3_pressed
    as a Boolean variable -- SW3_pressed has been pre-defined with
    the other variables in the header section at the top of the
    program. Replace the first SW3 'if-else' conditional structure
    in your program with these two new 'if' condition structures:

  if SW3.value() == 0 and SW3_pressed == False:
    LED2.value(1)
    SW3_pressed = True
    SW3_count += 1

  if SW3.value() == 1:
    LED2.value(0)
    SW3_pressed = False
        
    The first 'if' condition will now logically AND the current
    button state and the SW3_pressed Boolean variable representing
    the button's previous state. Using this logic, the button must
    both be pressed and the state of SW3_pressed must be false
    (which it was initialzed as) in order to count as a new button
    press. If both conditions are met, LED D2 will light as it did
    before, the SW3_pressed Boolean variable will be set to 'True'
    to store the new state of the pushbutton, and the SW3_count
    variable will be incremented by 1 using the compound operator
    in the statement 'SW3_count += 1' (this produces the same
    result as the original 'SW3_count = SW3_count + 1' statement,
    but with less typing). Since the SW3_pressed variable is now
    True, this block of code will not be able to run again, no
    matter what the state of the SW3 button is.
    
    The second if condition is necessary to reset the SW3_pressed
    Boolean variable to 'False' once the switch has been released. 

    Try these new code blocks in your program and verify that the
    program now properly counts each individual button press.
      
7.  The new conditional statement added in the previous step can
    also be written as:

    if SW3.value() == 0 and not SW3_pressed:

    The expression 'not SW3_pressed' is equivalent to the Boolean
    variable SW3_pressed being False (or *not* True). Similarly,
    if the SW3_pressed Boolean variable's name is used by itself
    in a program, it is equivalent to it being True. Try replacing
    the first if conditional statement in your program with this
    new conditional expression and verify that it works as expected.
   
Programming Activities
   
1.  Create a two-player, rapid-clicker style game using this program
    as a starting point. The only purpose of the game will be to see
    which player can press a button the fastest and become the first
    player to reach the maximum count and win the game!

    Use SW4 for the second player, and have your program light LED
    D5 when button SW4 is pressed. Light LED D4 to show when the
    second player's count reaches the max_count.
    
    Start by duplicating the existing program variables to create a
    similar set of variables for the second player. Next, create
    copies of the if condition structures for the second player and
    modify them to use the variables created for the second player.
    Finally, modify the program code so that SW5 reset the counts
    and turns off the LEDs for both players.

2.  When two closely-matched players are playing the rapid-clicker
    game, it might be hard to tell which player hit the max_count 
    value first. Use your knowledge of Boolean variables to prevent
    any more presses from increasing the individual player counts
    once one player has achieved the maximum count.

3.  Use a Boolean variable to create a program that simulates the
    operation of a toggle button. Toggle buttons are commonly used
    as push-on, push-off power buttons in digital devices, such as
    the power button that turns a computer monitor on and off.
    
    For your program, each new press of the toggle button must
    'toggle' an LED to its opposite state. Pressing and holding
    the toggle button should only cause the LED to switch states,
    or toggle, once and not rapidly cycle on and off. Test your
    toggle button's action for reliability.
   
4.  A multifunction button can be used to initiate one action when
    pressed, and a second or alternate action when it is held for
    a specific length of time. One simple way to implement a multi-
    function button is by using a variable to count timed program
    loops -- exactly as this program initially did (though
    unitentionally!).
    
    Create a program that implements a multifunction button to light
    one LED as soon as a button is pressed, and light a second LED
    if the button is held for more that one second. Have the program
    turn both LEDs off when the button is released.
   
5.  Do your pushbuttons bounce? Switch bounce is the term used to
    describe switch contacts repeatedly closing and opening before
    settling in their final (closed) state. Switch bounce in a room's
    light switch might not be a big concern because it happens so
    quickly that we wouldn't notice the light flickering briefly
    before staying on. But, switch bounce can be an issue in a
    program because the fast operating speed of a microcontroller
    lets it see each contact closure as a new, separate event.
    Imagine if a power button set up as a toggle button bounced and
    each press randomly triggered between 1 and 4 contact closures.
    Any device controlled by this switch would not be able to turn
    on or off reliably.
   
    To determine if your circuit's pushbuttons exhibit switch bounce,
    create a program that counts the number of times a pushbutton's
    contacts close, and then display the count on the LEDs. Comment-
    out the delay(10); statement in the main loop to ensure that
    short bounce events won't be missed. Use a second pushbutton to
    both reset the count, and to turn off the LEDs, so that the test
    can be repeated.
   
6.  Did any of your pushbuttons bounce? Typical switch bounces appear
    as multiple contact closures within 20-30ms after the initial 
    switch activation. Can you think of a simple software technique
    that could easily be implemented to ignore multiple switch
    activations within a 20ms span?

    External switches can be connected to your circuit's I/O header
    pins to check them for bounce instead. Try to find a switch that
    exhibits switch bounce and then add your de-bouncing code to the
    bounce counting program you created in the previous step to
    verify its effectiveness.
    
"""
