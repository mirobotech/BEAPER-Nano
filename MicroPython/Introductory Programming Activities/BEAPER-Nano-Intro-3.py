"""
Project:  Introductory Programming Activity 3 - Loops
Activity: mirobo.tech/micropython/intro-3-loops
Updated:  May 22, 2025

This introductory programming activity for the mirobo.tech BEAPER Nano
circuit demonstrates the use of both while-loop and for-loop structures
to change the brightness of an LED using PWM (Pulse-Width Modulation).

Additional program analysis and programming activities introduce the
concepts of local and global variables and demonstrate the use of the
PWM pin function to create PWM output.

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

# Define program variables
LED2_level = 127

while(True):
  # Decrease brightness?
  if SW3.value() == 0 and LED2_level > 0:
    LED2_level -= 1
  
  # Increase brightness?
  if SW4.value() == 0 and LED2_level < 255:
    LED2_level += 1

  # PWM LED2
  pwm_counter = 255
  while pwm_counter > 0:
    if LED2_level == pwm_counter:
      LED2.value(1)
    pwm_counter -= 1
    time.sleep_us(10)
  
  LED2.value(0)

"""
Learn More -- Program Analysis Activities
   
1.  The LED2_level variable is defined before start of the main
    'while' loop in this program. Inside the main while loop, the
    value of LED2_level is allowed to be changed if one of two
    pushbuttons is pressed, and if LED2_level is within a specified
    range of values. What actual range of values is the LED2_level
    variable allowed to be?
    
2.  The main while loop of this program is an infinite, condition-
    less loop, and inside this main loop is a second, conditional
    while loop. The addition of the conditional operator allows the
    loop to repeat only while its condition is true.

    What condition is being evaluated by the inner while loop
    statement? How many times will this inner loop will run?

3.  An 'if' condition inside the inner while loop compares the
    pwm_counter variable (used as a loop counter) with the value of
    the LED2_level variable. With a starting LED2_level value of 127,
    approximately how much time will pass before the 'if' condition
    becomes true and LED D2 turns on? For approximately how much
    time will LED D2 then remain on before it is turned off again?
   
4.  As the value of the LED2_level variable is changed, LED D2's
    on-time will change relative to its off-time, while leaving the
    overall loop time relatively constant. This process of repeatedly
    generating pulses whose on-time are varying portions of a fixed
    time period is referred to as PWM, or Pulse-width Modulation. If
    the PWM pulse frequency is fast enough, LED D2 will appear to
    change brightness instead of visibly flashing on and off.
    
    Knowing the number of loop cycles, and the time taken to create
    each on-off pulse, calculate the approximate PWM frequency, or
    how many on-off pulses you would expect this program to create
    per second. (If you have access to an oscilloscope or frequency
    counter, you can view the wave and try to measure the actual
    PWM output frequency.)
    
5.  How many different levels of brightness can LED D2 have in this
    program? Calculate the percentage brightness change corresponding
    to a single digit change in the value of the LED2_level variable.
   
6.  This finite 'while' loop consists of three parts:

    1) An assignment statement to pre-assign a value to the loop's
    conditional variable (which in this case is used as a loop
    counter). In this program, the assignment statement is the
    'pwm_counter = 255' statement just above the while condition.
    
    2) A conditional expression that determines whether or not the
    loop will repeat. The 'while pwm_counter != 0:' structure will
    keep repeating the loop until pwm_counter is equal to 0. (Unlike
    'if' statements, which run the code indented below them only
    only once *if* a condition is true, while statements keep
    repeating their indented code *while* the condition is true.)

    3) An expression that updates or modifies the conditional
    variable inside the while loop. In this program, the expression
    'pwm_counter -= 1;' uses a decrement by one operator to decrease
    the value of the loop variable every cycle through the loop.
    (If a loop variable is never modified inside the loop, the program
    will appear to be stuck in the loop, making it into an infinite
    loop!)

    A 'for' loop is an alternative to a while loop and incorporates
    the same three parts of a while structure into a single program
    statement. Compare the structure of the while loop in the
    program above with the for loop structure, below:

  for pwm_counter in range(255, 0, -1):
    if LED2_level == pwm_counter:
      LED2.value(1)
    time.sleep_us(10)

    The numbers inside the for statement's range brackets represent:
    the starting value, the ending value, and the size of the step
    between successive values of the pwm_counter variable.
    
    Can you identify at least two advantages of using a for loop
    structure instead of using a while loop structure?

7.  There is one potentially important disadvantage of a for loop
    compared with a while loop, though it doesn't affect the loop
    used here. Can you think of an advantage of a while loop that
    might involve a different type of condition than the one used
    here?
 
8.  Replace the entire while loop structure in the original program
    with the for loop structure, above.

    Upload the revised program into your circuit and run it. Does it
    work the same way as the program did with the while loop?

9.  One aspect of 'for' loop operation that is very important to
    understand is that the loop variable always includes the starting
    value of the range, but excludes the ending value of the range.
    
    Let's test this. Remember that this 'for' loop's range specifier
    is written as 'range(255, 0, -1)', so it would be reasonable to
    expect the pwm_counter varaible to count down from 255 to 0. Add
    the following conditional block right below the for loop. It will
    light LED D5 if the loop finishes with the value of zero in the
    pwm_counter variable:

  if pwm_counter == 0:
    LED5.value(1)
  else:
    LED5.value(0)

    Run the program and watch what happens. Is LED D5 lit?

    In reality, the loop will end one count before the ending value
    of its range, or at a value of one instead of zero. Let's verify
    this. Change the conditional block to light LED D5 if pwm_counter
    equals one and re-run the program. Is LED D5 lit now?

10. Did the 'for' loop happen to stop before reaching the end of its
    range only because the loop was counting down, or would a loop
    that counts up behave the same way? Let's test it using another
    loop range that will result in the loop variable being counted
    up. Change the loop initialization statement to match this one:

  for pwm_counter in range(255):

    Notice that this range specifier contains only a single number
    instead of a separate starting value, ending value, and interval.
    This compact form is equivalent to specifying 'range(0, 255, 1)'.
    In both cases, pwm_counter starts at zero and will complete 255
    counts, incrementing by one from loop to loop. What do you think
    the ending value of pwm_counter will be? Modify the previously
    created conditional code block to verify your guess.

11. MicroPython includes a PWM function that can be used to easily
    generate PWM waves on digital output pins. Using this function
    allows all of the previous PWM loop code in this program to be
    replaced by a single PWM statement (along with a few other small
    changes). Let's try it!
    
    First, comment-out the existing LED2 pin constructor statement
    in the program, and replace it with this new one that initializes
    LED2 as a PWM outout instead:

LED2 = PWM(Pin(7), freq=1000, duty_u16=0)

    This pin constructor sets pin 7 as a PWM output, assigns it a PWM
    frequency of 1000 Hz, and sets a 16-bit duty cycle value (the
    on-time of the output pulse) of 0 out of 65535 -- which keeps the
    PWM output off.
    
    Next, remove or comment out the for loop and add these two new
    lines to the program:

  LED2.duty_u16(LED2_level * 256)
  time.sleep_ms(5)
    
    The first line updates the PWM duty cycle from the the value of
    the LED2_level variable. Since LED2_level variable has only 256
    states (0-255), it must be multiplied by 256 to match the range
    of the 16-bit (0-65535) value used by the .duty_u16() duty cycle
    specifier in MicroPython's PWM function.
    
    Upload the program and verify that SW3 and SW4 change LED D2's
    brightness similar to the way the program worked previously.
    
    Why do you think the 'time.sleep_ms(5)' delay has been added to
    the program code? What do you think would happen if it was
    removed or commented-out? Try it and see if you're right!

12. All of the work that went into generating and testing a PWM
    algorithm might seem like wasted effort after realizing that a
    single instruction can replace all of our code, but this isn't
    necessarily the case. Developing and testing an algorithm to 
    accomplish a specific task is an important skill, and this
    exercise hopefully helped you to develop a better understanding
    of how both loops and PWM work!

    Other than using less program code to create a PWM output, what
    other advantages does using the PWM pin output provide?

    Can you think of any disadvantages or limitations of using PWM
    output? Look up the PWM class in the MicroPython documentation
    (https://docs.micropython.org/en/latest/index.html), as well as
    information on PWM in the quick reference sections for specific 
    MicroPython ports (eg. ESP32, or RP2).


Programming Activities

1.  Modify this program to control the brightness of two LEDs
    independently. The existing program uses pushbuttons SW3 and SW4
    to control the brightness of LED D2. Add the capability to use
    pushbuttons SW2 and SW5 to control the brighness of another LED.
  
2.  Let's combine loops with PWM. Comment-out your previous PWM code
    and replace it with these two loops that successively brighten
    and dim LED2:

  for brightness in range(0, 65535, 1):
    LED2.duty_u16(brightness)
  for brightness in range(65535, 0, -1):
    LED2.duty_u16(brightness)
   
3.  Create a program that uses SW2 and PWM to fade-up an LED from off
    to full brightness, and SW5 to fade-down the same LED and turn it
    off. (A protram like this could be used to implement a soft-start
    for an elecric motor to limit the mecahnical stress caused by a
    full power start.)

4.  Modify your program above to make it into a programmable light
    dimmer. After SW2 is pressed and the LED finishes its fade-up,
    allow the user to fine-tune the brightness of the LED using SW3
    and SW4. Pressing pushbutton SW5 should cause the LED to fade to
    off from the current level, and pressing SW2 to turn the LED
    on again should brighten it only to the previously set level
    instead of to full brightness.

5.  The PWM function can be used with the piezo speaker to make
    sounds! Create a program that uses PWM outout make a 440Hz tone
    for a duration of 1s in response to a button press.

6.  Try making a 'chirp' or 'pew-pew' sound effect by using a for
    loop to sweep through a range of frequencies from low to high,
    or from high to low, when a button is pressed.

7.  Arduino Nano ESP32 has a built-in RGB LED. Create a program to
    cycle between a range of colour combinations using PWM to control
    the brightness of each R (red), G (green), and B (blue) LED
    element. To display all of the colours in rainbow colour order,
    for example, start with the red LED at maximum brighness, and the
    green and blue LEDs at minimum brightness. Then, decrease the red
    LED's brightness while increasing green LED's brightness, leaving
    the blue LED off. Next, decrease the green brightness value while
    increasing blue (and leaving the red LED off). Finally, increase
    the red brightness while decreasing blue (and leaving green off).
    The cycle is now back to its starting point and ready to be
    repeated.

"""