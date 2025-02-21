"""
Project:  Introductory Programming Activity 1 - Input and Output
Activity: mirobo.tech/micropython/intro-1-input-output
Updated:  February 20, 2025

This introductory programming activity for the mirobo.tech BEAPER Nano
demonstrates pushbutton input, LED outut, the use of time delay
functions, and simple 'if ' condition structures.

Additional programming analysis activities explore I/O pin behaviour,
compare the operation of 'if' and 'while' structures, and demonstrate 
logical conditional operators. Programming activities introduce the
making sounds, and encourage learners to create software-based simulated
start-stop buttons and a turn signal program.

See the https://mirobo.tech/beaper webpage for additional BEAPER Nano
resources, programming activities, and starter programs.
"""

# Import Pin and time functions
from machine import Pin
import time

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

# Configure Arduino Nano ESP32's built-in LEDs
LED_BUILTIN = Pin(48, Pin.OUT, value = 0)   # Active High
LED_BLUE = Pin(45, Pin.OUT, value = 1)      # Active Low
LED_GREEN = Pin(0, Pin.OUT, value = 1)      # Active Low
LED_RED = Pin(46, Pin.OUT, value = 0)       # Active Low

while True:
    if SW2.value() == 0:
        LED2.value(1)
        time.sleep(0.1)
        LED3.value(1)
        time.sleep(0.1)
        LED4.value(1)
        time.sleep(0.1)
        LED5.value(1)
        time.sleep(0.1)
        
        LED2.value(0)
        time.sleep(0.1)
        LED3.value(0)
        time.sleep(0.1)
        LED4.value(0)
        time.sleep(0.1)
        LED5.value(0)
        time.sleep(0.1)

    # Add code from the Program Analysis Activities and Programming Activities here

    time.sleep_ms(10)


"""
Learn More -- Program Analysis Activities

1.  Let's analyze this program! Program analysis is an important skill to
    develop since it helps you to understand a program's operation. Open
    this program in the Arduino Lab for MicroPython IDE (or another similar
    MicroPython IDE) and connect your BEAPER Nano to your computer. Use the
    Connect button to connect the Arduino Nano ESP32 to the IDE, and then
    press the Run button in the IDE to start running the program. With the
    program running, press and release pushbutton SW2 on your BEAPER Nano
    circuit while observing its LEDs.
   
    What happens? How many LEDs flash? How many times does each LED flash? Do
    the LEDs flash again if SW2 is pressed and released a second time? What
    happens if SW2 is held? Does the flashing pattern immediately stop when
    SW2 is released?
   
    Examine the program and try to match your observations with the program's
    instructions. Explain why all of the LEDs flash on and then off after
    SW2 is pressed, and why you think the flashing pattern continues -- 
    instead of stopping immediately -- after pushbutton SW2 is released.
    
2.  The first line of code in 'while True:' program structure is:

    if SW2.value() == 0:

    The empty brackets used in the 'SW2.value()' function make it act as an
    input statement, which is this case is used to read the external voltage
    applied to pin SW2. If the voltage on the pin is high, SW2's value will 
    become 1, and if the voltage is low, its value will be 0.
    
    The entire 'if SW2.value() == 0:' conditional statement compares the
    value of SW2 with 0. In MicroPython (and many other programming languages)
    two equal signs '==' are the conditional check for equality, while a
    single equal sign assigns a value. If SW2's value is 0, the condition is
    true, and  all of the program statements below and indented to the right
    of the conditional if statement will run. If SW2's value is 1, the condition
    is false, and all of the indented program code below the if statement will
    be skipped.
    
    The next statment:
    
        LED2.value(1)

    uses the same .value() method as the input statement, but putting a number
    into its brackets makes it into an output statement. Setting LED2's value
    to 1 in this output statement sets LED2's pin voltage high, enabling current
    to flow through its connected LED, and lighting LED2.

    A few lines further down in the program, a similar output statement
    is used to set the LED2 pin value to zero, making its output voltage low,
    and turning off the LED:
    
        LED2.value(0)

    Both the digital input and output statements use the same '.value()' method
    to either read from or write to the pins defined as SW2 and LED2, respectively.
    Both input and output statements also use the same values (0 or 1) to represent
    input and output voltages. What real-world voltages do you think the values 0
    and 1 correspond to in the Arduino Nano ESP32 microcontrolelr used in your
    BEAPER Nano?
    
3.  A time delay statement follows each LED output statement in the program:

        time.sleep(0.1)

    The '.sleep' method causes the microcontroller to pause for the specified
    amount of time -- 0.1 seconds in this case. Try changing the time value
    to 1 second and run the program again. Press SW2 while observing the
    LEDs. Did you notice the change?
    
    The time module has two other sleep methods that make it easier to use
    shorter time delays:
    
        time.sleep_ms()  - pauses for the specified number of milliseconds
        time.sleep_us()  - pauses for the specified number of microseconds
    
    What delay value would have to be used with time.sleep_ms() to provide
    the same delay as the original time.sleep(0.1)? Replace one or more of
    the time.sleep() functions in your program with time.sleep_ms() and run
    it using the value you chose to verify that the light pattern looks the
    same as it did with time.sleep(0.1).

4.  Understanding circuit operation is just as important as understanding
    program operation when analyzing and debugging interfacing circuits
    (hardware components controlledy by or interacting with software). If
    you have access to a voltmeter, you can use it to confirm the voltage
    measurements at different points in your circuit, and specifically to
    verify the '0' or '1' values you predicted above. To be able to read
    the LED voltages, you may need to lengthen the time delay after the
    output statement(s) for the LED being measured.

    First, try measuring the potential across one of the LEDs. Press SW2
    and note how the voltage changes. Is the voltage the level you expected
    it to be? If not, use the schematic to look up which resistor is connected
    to the LED you were measuring, and measure the potential across both the
    LED and its series resistor. Is this the closer to the voltage value
    you expected?
  
    Next, measure the potential across both leads of one of the pushbuttons
    while it is not being pressed. The microcontroller's pushbutton input
    pins have been configured with internal pull-up resistors enabled, so a
    voltage should be present across every pushbutton as soon as the program
    starts running. Press and hold the pushbutton and you should observe
    a change in the voltage across the pushbutton. Do thess values match
    your predictions? How does the voltage across a pressed pushbutton relate
    to the value used by the SW2 input statement?
    
5.  Let's compare the operation of 'if' and 'while' structures by making two
    new program blocks that will simulate the operation of real-world momentary
    buttons. Copy and paste the program code, listed below, into your program
    between the existing SW2 'if' block and the 10ms sleep delay (shown with a
    comment in the program code).

    # Momentary button using an if structure
    if SW3.value() == 0:
        LED3.value(1)
    else:
        LED3.value(0)
    
    # Momentary button using a while structure
    while SW4.value() == 0:
        LED4.value(1)
    LED4.value(0)
    
    First, press and release pushbutton SW3. LED D3 should only light
    while SW3 is being pressed.
    
    Next, press and release pushbutton SW4. LED D4 should operate exactly
    the same way as LED D3, staying lit only while SW4 is being pressed.
    
    While both program switch blocks are designed to effectively mimic the
    operation of real-world momentary pushbuttons, implementing them using
    a sequence of software steps makes them behave differently than physical
    physical buttons would. To see the difference press and hold SW3, and
    while holding SW3 press and release SW4. Do both switches still operate
    as expected?
    
    Next, try it in the opposite order. Press and hold SW4, and then press
    and release SW3. Do both switches still operate as expected?
    
    Explain the differences in the operation of the 'if' and 'while' blocks
    used to make the momentary button functions. How does each affect the
    program flow -- the steps taken by the microcontroller through the 
    main program loop. Which block should be used when creating a program
    that needs to sense both switches simultaneously, as if they were intended
    to replace wired parallel switch circuits?

6.  Next, let's try nesting if conditions to mimic an operator safety circuit
    for an industrial machine. To prevent operator injury, some machines have
    two, widely-spaced start buttons that a machine operator is required to
    press at the same time in order to activate it. The machine will only
    start if one button *and* the other button are pressed simultaneously.
    Spacing the buttons far enough apart requires the machine operator to 
    press one button with each hand, ensuring that both hands are safely away
    from the dangerous parts of the machine when it starts.
    
    Replace the momentary button program blocks added above with the new
    program block, below. This program combines two if conditions to light
    LED3 (representing our machine) when both SW3 and SW4 are pressed.
    
    # Nested if conditions
    if SW3.value() == 0:
        if SW4.value() == 0:
            LED3.value(1)
        else:
            LED3.value(0)
    else:
        LED3.value(0)

    Test the code to ensure it works as expected. Does the order of button
    presses matter? Do you think the order of the conditional checks in the
    program matters? Try swapping the conditional input checks for SW3 and
    SW3 and test it again if you are unsure.
    
7.  As shown in the example above, nesting conditional statements does work
    to ensure the light turns on when both switches are pressed. There is an
    easier and shorter way to accomplish the same task by implementing the
    logical AND conditional operator represented by the word 'and' in
    MicroPython. This software conditional operation is the programming
    equivalent of an AND gate logic circuit. Replace the code added in the
    previous step with this new code block using the logical AND operator:
    
    # Logical if condition
    if SW3.value() == 0 and SW4.value() == 0:
        LED3.value(1)
    else:
        LED3.value(0)
    
    Run the code and test it to ensure it works as expected. Can you think of
    at least two advantages of using a logical AND condition instead of nested
    if structures as was done in the previous example?
    
8.  If a logical AND operator can implemented in a conditional statement,
    it seems reasonable to expect that a logical OR operator must also exist.
    Similar to AND, an OR operation in MicroPython is represented by the 'or'
    operator. Replace 'and' with 'or' in your program to implement a logical
    OR condition. Your code block should now look like this:
    
    # Logical if condition
    if SW3.value() == 0 or SW4.value() == 0:
        LED3.value(1)
    else:
        LED3.value(0)
    
    Run the code and test it. List the conditions under which LED D3 turns on.
    Do these conditions match the truth table of a logical OR gate?
    
9.  The equivalent of the XOR logical operation is inequality -- the output
    will be true only when one input is different, or not equal, to the other.
    Inequality in MicroPython is represented by the '!=' (read as 'not equal to')
    conditional operator. Try this:
 
    if SW3.value() != SW4.value():
        LED3.value(1)
    else:
        LED3.value(0)
   
    Does it correctly mimic the output of an XOR gate? Can you re-create the
    XOR operation using the quality '==' operator instead of using the 
    inequality '!=' operator, and still produce the same output? Try it!
    
Programming Activities

1.  The 'time.sleep(0.1)' function pauses the microcontroller for 0.1 second,
    and the delay value inside its brackets can be replaced by larger or smaller
    numbers to create different lengths of delays. Very short delays can be
    represented more easily in milliseconds or microseconds instead of seconds
    using one of these two related sleep methods available in the time module:

        time.sleep_ms()  - delays for the specified number of milliseconds
        time.sleep_us()  - delays for the specified number of microseconds
    
    Create a program using the 'time.sleep_ms() method that rapidly flashes
    LED D5 on and off while pushbutton SW5 is pressed. Start with a value of
    100ms (equivalent to 0.1s), to make it visually similar to the LED delays
    used in the SW2 if condition, and then decrease the time delay value to
    experiment with shorter LED flashes.
    
    As the delay gets smaller, your eyes will have a harder time distinguishing
    each flash. What is the shortest time delay that allows you to percieve the
    LED as flashing as opposed to it just appearing to be continuously lit?
    
2.  Microsecond-length time pulses are too short to be seen with our eyes but
    can be measured using an oscilloscope, or heard as an audio tone if they
    are used to turn the piezo speaker on and off.

    Add the following block of code to your program. The delay between each
    change in the BEEPER pin's output voltage is half of the time period of
    one wave of music note A5, so when SW5 is pressed your circuit should
    play a tone at a frequency of approximately 880 Hz.
    
    if SW5.value() == 0:
        BEEPER.value(1)
        time.sleep_us(568)
        BEEPER.value(0)
        time.sleep_us(568)
    
    If you try to run the program after adding this section, you'll find that
    pressing and holding SW5 will make a buzzing noise instead of a musical
    sounding tone. Can you figure out why?
    
    Did you figure it out? After the second 568us delay, the 'time.sleep_ms(10)'
    statement adds an additional 10ms of delay at the end of the program's main
    while loop function before the BEEPER pin can change back to 1 again. This
    creates an extra-long zero output of 10568us instead of the 568us low time
    the program intended! The simplest way to fix the program without deleting
    the line is to comment-out the 10ms delay using a pound sign, making it into
    a single-line comment, as shown below:
    
    # time.sleep_ms(10)

    Run the program again and press SW5. Does it sound more like a tone now?
    Try altering both of the delay values, always keeping them the same as you
    increase or decrease the delay. Does the pitch of the tone increase or
    decrease when the delay values are made smaller? Does the opposite happen
    if the delay values are made larger?
     
3.  BEAPER Nano's LED circuits use 'active-high' logic, meaning that each LED
    turns on when its output pin is set to 1, or is connected to the power 
    supply potential by each pin's output transistor. In contrast, the individual
    elements of the RGB (red, green, blue) LED built into the Arduino Nano ESP32
    microcontroller are controlled using 'active-low' logic. This means that
    current flows through the LED element when its associated output is made 0, 
    or connected to ground.

    The configuration statements near the top of the program both define and
    initialize the Arduino Nano ESP32's built-in RGB LED. The Pin constructors'
    initialization values can be modified to display a different colour on
    startup, or to keep the LED off, by changing their values. Let's do an
    experiment to determine all of the possible colours the RGB LED can create.
    To help you figure it out, create a chart that lists every colour along with
    the values of the red, green, and blue LED elements to make that colour.

    What values correspond to the RGB LED being off? How many colours can the
    RGB LED produce using only simple 0 and 1 output values for control? (We'll
    explore how to display far more colours than this in a later activity!)
    
4.  Create a program so that each button on BEAPER Nano will generate either
    a unique flashing pattern using any of the LEDs on BEAPER Nano or the LED
    built into the Arduino Nano ESP32 (or both), or that will play a series of
    tones from the piezo speaker.
    
    Test each of your flashing or sound patterns to verify that it works as
    expected. Describe what happens when multiple buttons are held. Do all of
    the patterns flash the LEDs, or play the tones, at the same time, or does
    each pattern play in sequence? Explain why this is the case.
    
5.  Create a new program that uses individual if structures to simulate the
    operation of 'Start' and 'Stop' buttons for an industrial machine. Use SW2
    as the Start button to turn LED D2 (representing the machine) on when it
    is pressed, and ensure that LED D2 stays on even after SW2 has been released.
    Use SW5 as the Stop button to turn LED D2 off when it is pressed. Test your
    program to ensure that your simulated machine turns on and off as expected.
    
6.  Run the Start-Stop program created in the previous step again, and
    describe the result when both 'Start' and 'Stop' pushbuttons, SW2 and SW5,
    are held. Does LED D2 turn on at all when both buttons are pressed? Would
    this be considered safe behaviour for a machine?
    
    Let's do some additional program analysis to try to determine what is
    actually happening. Watch the brightness of LED D5 when both buttons are
    pressed, and compare its brightness to when only the start button is
    pressed. If the brightness is different, there must be some part of the
    program's operation responsible for the difference. Can you explain what
    the program does differently when the stop button is pressed in addition
    to the start button that might causing the difference in brightness?
    (Hint: pretend to be the computer and simulate each step of the program.)
    
7.  As you can imagine, an industrial machine that is able to turn on even while
    its Stop button is being pressed represents a significant safety hazard to
    its operators! Use one or more of the logical conditional operators introduced
    in the program analysis activities, above, to make the start-stop program
    operate safely. The machine should not be able to turn on at all while the
    Stop button is being pressed. Test your program to ensure LED D5 stays off
    while SW5 is being pressed.

8.  Let's say that you're ready to apply your newly-acquired microcontroller
    hardware and programming experience to create a turn signal circuit for your
    bicycle. Assume that you have designed a 3D-printed holder that holds an
    Arduino Nano ESP32, a battery pack, and up to four LEDs, and that this
    holder is designed to be mounted on the bicycle's seat post. The LEDs will
    be controlled by two momentary pushbuttons mounted on the bicycle's
    handlebars. Plan the best way to implement a turn signal system that is
    both easy to use, and makdes and easily visible turn signals. Then, write
    a program that uses the LEDs and pushbuttons on your circuit board to
    simulate its operation.
    
9.  Modify the bicycle turn signal program, above, to add one or more extra
    features such as a brake signal, a horn or bell function using an unused
    pushbutton, or add a rapidly flashing visibility light that blinks constantly
    until one of the turn signals is activated. Test your program to ensure that
    each of its functions works as expected under all operating conditions (e.g.
    signalling and applying the brakes, or using signalling while using the horn).
    
"""