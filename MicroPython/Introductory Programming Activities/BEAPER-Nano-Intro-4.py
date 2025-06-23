"""
Project:  Introductory Programming Activity 4 - Functions
Activity: mirobo.tech/micropython/intro-4-functions
Updated:  June 23, 2025

This introductory programming activity for the mirobo.tech BEAPER Nano
circuit demonstrates the operation and use of functions including
passing parameters and returning values to make sounds using PWM.

Additional program analysis and programming activities introduce
Arduino-like tone() and noTone() functions, and challenge learners
to produce a variety of functions.

See the https://mirobo.tech/beaper webpage for additional BEAPER Nano
programming activities and starter progams.
"""

# Import Pin and time functions
from machine import Pin, PWM
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
BEEPER = PWM(Pin(17), freq=1000, duty_u16=0)

# Makes a short beep
def beep():
  BEEPER.freq(4000)
  BEEPER.duty_u16(32768)
  time.sleep(0.5)
  BEEPER.duty_u16(0)
  
while True:
  # Beep!
  if SW2.value() == 0:
    beep()

  # Beep, beep!
  if SW3.value() == 0:
    beep()
    time.sleep(0.25)
    beep()
    time.sleep(0.25)
    
  time.sleep_ms(20)

# Try moving the beep() function to here:

  
"""
1.  Let's learn how functions are used in a program. Functions are
    blocks of code created to perform one or more specific tasks, and 
    are often used for parts of programs that repeat, such as reading
    inputs, processing data, or producing specific outputs. All of
    the previous introductory programming activities have used a
    few different functions.
    
    Let's take a look at one very useful microcontroller function 
    that has been an integral part of every previous introductory
    program: the value() function. The value() function can be used
    as an output function and sets the voltage of an I/O pin. In this
    case, the output voltage is set by providing the value() function
    with a numeric value (called an argument) supplied inside its
    brackets, like this:
    
    LED2.value(1)
    
    The argument '1' inside the value() function's brackets sets the
    LED2 output pin to produce a high voltage. The same value()
    function can also be used as an input function to read the state
    of an I/O pin when it is called with empty brackets, like this:
    
    SW2_state = SW2.value()
    
    In this case, the SW2 pin voltage will be returned as either '0'
    or '1' by the function, and this value will be stored in the
    program's 'SW2_state' variable.
    
    Whenever brackets are found in a Python program statement, no
    matter if those brackets are empty or they contain optional
    parameters, the presence of the brackets is a good indicator that
    the statement they are part of includes a function.
    
    In addition to value(), what other MicroPython functions are used
    by this program?

2.  MicroPython allows programmers to define new functions which
    typially take the following form:
    
    def function_name(optional parameters):
      one or more program expressions
      (return (optional value))
    
    The function definition begins with a header statement that
    includes the keyword 'def' followed by the name of the defined
    function. It's a good idea to give functions a name that describes
    their primary purpose or action. Functions can also be provided
    with one or more optional parameters (if required), and these
    take the form of variable declarations listed inside the brackets
    following the function's name. The function header is terminated
    with a colon and, exactly like conditional and loop structures,
    and the body of the function is indented below the header.
    
    The function body can include any typical MicroPython programming
    expressions, and after these statements run, the function
    terminates and the program resumes operation from the function
    call statement. Optional 'return' statements within the function
    body allow it to return to the calling code from any point in
    the function, meaning the function can quit without having all
    of the program code within the function's body run. Return
    statements can also include an optional value that will be passed
    to the code that originally called the function.

    This program defines a beep() function. Does the beep() function
    use any parameters that require data from the calling code? Does
    the beep() function return any data to the calling code?
    
3.  Run the example program in your BEAPER circuit. You may have
    noticed that although the beep() function is located above the
    main 'while True:' loop in the program, the code inside the
    function itself didn't run until it was called by the beep()
    statements in the 'if' condition statements within the program's
    main while loop.
    
    How do we know that the beep() function code doesn't actually
    run until it is called? What would we expect to happen if it did
    run as part of the program's start-up processing, before the
    program entered the main 'while True:' program loop?
    
4.  Added function code, like the beep() function, is not part of the
    main program flow despite being part of the program. Since the
    program statements execute from the top down, and the beep() 
    function is not used until later, wouldn't it make more sense to
    place the beep() function itself below the code in the main while
    loop, in the location shown by the code comment? Try it to see
    what happens.
    
    Run the program and press one of the pushbuttons after you have
    moved the beep() function below the main while loop in the code.
    Explain what happens and why you think this happens.
    
5.  As you can see in this program, the ability to call the beep()
    function multiple times, and from different locations, makes the
    overall program smaller than if all of the code inside the beep()
    function had to be repeated in each of the areas of the program 
    in which it's used.
    
    Other than reducing the overall size of a program, can you think
    of other potential advantages of creating and using functions in
    your programs? List at least two.
    
6.  The existing beep() function creates a tone of a single frequency
    and stops the tone after a pre-determined amount of time. Let's
    modify the beep function to use a parameter variable so that
    users can specify the desired frequency every time it's called.
    Replace the beep() function in your program with this one:
    
# Creates a 0.5 second beep of the specified frequency 
def beep(frequency):
  if frequency > 0:
    BEEPER.freq(frequency)
    BEEPER.duty_u16(32768)
    time.sleep(0.5)
    BEEPER.duty_u16(0)

    Next, modify the conditional expressions in the main loop to
    supply frequency arguments for the parameter used by the updated
    beep() function, like this:

while True:
  # Beep!
  if SW2.value() == 0:
    beep(4000)

  # Beep, boop!
  if SW3.value() == 0:
    beep(4000)
    time.sleep(0.25)
    beep(1000)
    time.sleep(0.25)
    
  time.sleep_ms(20)

    Try the new program after making the changes. The frequency 
    variable in the beep() function now accepts an argument supplied
    by the call to the function. For exmample, beep(4000) produces
    a tone at a 4000Hz frequency. The piezo speaker on BEAPER Nano
    doesn't reproduce all frequencies equally well. Experiment with
    different frequencies and list the range of frequencies you 
    might consider using in your programs.

7.  Functions can also be written to return arguments to their
    calling statements. Let's add a function to read the pushbuttons
    and return frequency values that can then be used by the beep()
    function to make sounds. Add this new function above the main
    while loop in your program:

# Reads buttons and returns frequency values, or 0 if no buttons are pressed.
def read_buttons():
  if SW2.value() == 0:
    return (523) # note C5
  elif SW3.value() == 0:
    return(659) # note E5
  elif SW4.value() == 0:
    return(784) # note G5
  elif SW5.value() == 0:
    return(1047) # note C6
  else:
    return(0)

    Next, replace the main while loop code with this new code:

while True:
  freq = read_buttons()
  beep(freq)
  
  time.sleep_ms(20)

    Notice how simple the main while loop code appears to be now! The
    complexity, of course, has just been moved into the two functions
    that are now a part of the program.

    Describe the way in which a button press becomes a tone, and
    specifically how the frequency value is passed to the beep()
    function.

8.  There is an even more streamlined way to pass a value returned
    from one function as an argument to another function, without
    explicity declaring a variable (like the freq variable, above).
    Replace the main while loop code with this version, and verify
    that the program works the same way it did before:

while True:
  beep(read_buttons())
  
  time.sleep_ms(20)

    How is the frequency value passed between the read_buttons()
    function and the beep() function now? List an advantage and
    a disadvantage of combining functions in this way.

9.  Let's replace the beep() function with two new functions modelled
    after Arduino's tone() and noTone() functions. Add these functions
    above the main while loop in the program:
    
# Plays a tone of the specified frequency (in Hz) at a regular volume
# (50% duty cycle unless an alternate duty cycle value (0-65535) is
# supplied) until either 1) the frequency is changed with a successive
# tone statement, or 2) an optional duration (in seconds) has elapsed,
# or 3) until the tone is stopped using the noTone() function.
def tone(frequency, duration=None, volume=32768):
  BEEPER.freq(frequency)
  BEEPER.duty_u16(volume)
  if duration is not None:
    time.sleep(duration)
    noTone()

# Stops the playing tone and pauses for an optional duration in seconds.
def noTone(duration=None):
  BEEPER.duty_u16(0)
  if duration is not None:
    time.sleep(duration)

    Next, replace the main while function with this one:

while True:
  freq = read_buttons()
  if freq == 0:
    noTone()
  else:
    tone(freq)

  time.sleep_ms(20)

    The new tone() function allows a frequency to be supplied, exaclty
    like the previous beep() function did, but also enables extra,
    optional parameters to be supplied. Let's take a closer look at
    the tone() function's definition header statement to see how
    this works in practice:

def tone(frequency, duration=None, volume=32768):

    The 'frequency' parameter is required, while the 'duration' and
    'volume' parameters are both optional and have had their values
    pre-defined. The duration value of 'None' is logically more
    elegant than using a number such as 0 to indicate a continuously
    sounding tone, and the volume variable is set to create a 50%
    duty cycle tone (using lower duty cycles can lower the volume).

    So, the tone() fucntion can be used in multiple, flexible ways:

    tone(1000) produces a 1000Hz tone until the tone is stopped

    tone(1000, 1) produces a 1000Hz tone for 1 second

    tone(1000, 1, 100) produces a quieter 1000Hz tone for 1 second

    Examine the noTone() function's definition and explain how
    it can be used. What purpose would its duration be useful for?
    
10. Let's try something fun by combining for loops from the previous
    activity with the tone() function introduced in this program. Add
    the following code to your program:

# Define note frequencies
notes = [523, 523, 784, 784, 880, 880, 784]
note_duration = 0.4

    Next, replace the main while loop with this one:

while True:
  if SW2.value() == 0:
    for note in notes:
      tone(note, note_duration)
      noTone(0.1)
    time.sleep(1)

  time.sleep_ms(20)

    Run the program and press SW2. How does it make a tune using 
    different notes? A powerful MicroPython feature allows the
    'notes' variable to be created as a list which contains the
    frequency of each note in the tune. A MicroPython 'for' loop
    is able to iterate through each successive variable in the list.

    Explain how the program works and what MicroPython must know
    about the 'notes' list.

 
Programming Activities
 
1.  Create a function that uses your circuit board's LEDs as a simple
    level gauge to display the value of a variable. Think about the
    range of values you would want to display, perhaps 0-100, 0-255,
    or even 0-65535. Next, think about how the data will be displayed
    and reresented on the four LEDs. For example, when displaying
    data from 0-100, each LED could represent a value of 25, so that
    when all four LEDs are lit, the value could be inferred as being
    close to 100.

    When creating your funciton, you'll have to determine if the LED
    representing the highest level will be lit only at that value, or
    at a value close to the highest level.

2.  Create a function to display the binary numbers from 0-15 using
    the four LEDs on your circuit. Then, create a function to test
    your display function that reads the pushbuttons and returns
    binary equivalents (e.g. 1, 2, 4, 8).

3.  A function that converts an 8-bit value (0-255) into its three,
    constituent digits might be useful to output numeric data to a
    seven-segment LED, or an LCD display. Create a function that
    will convert a number passed to it into three separate variables
    represending the hundreds, tens, and ones digits of the number.
    For example, passing the function the value of 142 will result in
    the hundreds digit variable containing the value 1, the tens digit
    variable containing the value 4, and the ones digit contining 2.
    Test this function using the binary output display function that
    you created in step 2, above.

4.  Create a siren function that calls the tone() function to produce
    its sounds. Allow the user to set low and high frequency limits,
    as well as individual rates for alternately raising and lowering
    the tone frequency.
"""
