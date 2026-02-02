"""
================================================================================
Beginner Activity 3:  Digital Input [Activity_B03_Input.py]
February 2, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPER_Nano.py board module file.
================================================================================
"""
# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32
import BEAPER_Nano as beaper

import time

beaper.nano_led_on()

while True:
  # Momentary button SW2
  if beaper.SW2_pressed():
    beaper.LED2.value(1)
  else:
    beaper.LED2.value(0)
    
  # Start a pattern
  if beaper.SW5_pressed():
    beaper.LED2.value(1)
    time.sleep(0.2)
    beaper.LED3.value(1)
    time.sleep(0.2)
    beaper.LED4.value(1)
    time.sleep(0.2)
    beaper.LED5.value(1)
    time.sleep(0.2)
    beaper.LED2.value(0)
    time.sleep(0.2)
    beaper.LED3.value(0)
    time.sleep(0.2)
    beaper.LED4.value(0)
    time.sleep(0.2)
    beaper.LED5.value(0)
    time.sleep(0.2)

  if beaper.SW3_pressed():
    beaper.tone(440)
  else:
    beaper.noTone()

    
"""
Program Analysis Activities

1.  The previous two activities helped you develop an understanding of
    program operation (as well as output, and timing, of course),
    including an understanding of the program structure that results
    in the contents of the main 'while True:' loop being repeated.
    
    The 'if' statement in this program, known as an 'if condition',
    employs a similar structure to 'while'. That is, the program
    statements that are indented below the if statement will be
    executed whenever the condition is true (or, 'True' in the case
    of MicroPython -- capitalization is important!).
    
    In this part of the program, the if condition checks if SW2 is
    pressed using the SW2_pressed() function in the beaper module:

  # Momentary button SW2
  if beaper.SW2_pressed():
    beaper.LED2.value(1)
  else:
    beaper.LED2.value(0)
    
    If SW2 is pressed, then the if condition is considered to be true
    and LED2 will turn on. It also means that the if statement's
    corresponding 'else:' statement will be false, so the LED2.value(0)
    statement that follows it will not run, and preventing it from
    turning LED2 off.

    On the other hand, if SW2 is not pressed, then the if condition is
    false, preventing LED2 from being turned on. But, in this case,
    the else condition will be true, and LED2 will be turned off.

    Give it a try! Verify that SW2 acts as a momentary button, and
    that LED2 on only turns on while SW2 is pressed.

2.  Press SW5 to start its light pattern. While the light pattern is
    running, does pressing SW2 turn LED2 on at all? Explain why or
    why not, or what you think is happening. Can you think of a way
    to test and verify your assumption?

3.  The pushbuttons in the BEAPER Nano circuit are connected in what
    is known as a pull-up configuration, meaning that one side of each
    switch is wired in series with a resistor that 'pulls' it up to
    the power supply potential, while the opposite side of the switch
    connects to ground. A microcontroller reading the potential between
    the switch and the resistor will see the inactive potential (when
    the switch is not pressed) as a high voltage, and the active
    potential (when the switch is pressed) as a low voltage. This
    arrangment makes what is commonly known as an 'active-low' switch.
    
    A common way to read an input pin's potential in MicroPython is
    by using a parameter-less 'value()' method, like this:

  # Momentary button SW3
  if beaper.SW3.value() == 0:
    beaper.LED3.value(1)
  else:
    beaper.LED3.value(0)

    The empty brackets in 'beaper.SW3.value()' signify that a value
    must be measured (as an input) instead of being provided by the
    program (as an output). The double equals expression '== 0' checks
    if the input value is equal to 0, or low (which it would be if SW3
    is pressed), making the condition true. And, by now, you likely
    know how the rest of this code works. If the condition is true,
    then the statement(s) indented below it execute. If the condition
    is false, the statement(s) below 'else:' execute instead.

    Try copying the momentary SW3 program code, above, into your
    program. It should work exactly the same way as the momentary SW2
    code already in the program. Confirm that the two momentary
    buttons act the same way.

4.  The BEAPER_Nano.py board module contains a 'SW2_pressed()' helper
    function (as well as equivalent helper functions for the other
    switches). Let's compare the two switch input conditions, one
    using the helper function, and the other using the value() method:

    if beaper.SW2_pressed():    vs.    if beaper.SW3.value() == 0:

    While both perform the same conditional operation, SW2_pressed()
    provides semantic meaning (an understanding that the switch is
    being pressed), while SW3.value provides more technical accuracy
    (a pressed switch creates a low voltage) – but requires programmers
    to understand that the switches are active-low. The value() method
    is commonly found in most online MicroPython examples, but you
    might find that using the SW2_pressed() function makes the code
    easier to read and use. Feel free to use whichever input method
    makes the most sense to you.


Programming Activities

1.  Create a program that simulates the separate 'Start' and 'Stop'
    buttons that would be found on large, industrial machines. Pressing
    the 'Start' button should turn on an LED (simulating the machine).
    The LED should remain on even after the 'Start' button is released,
    and turn of only when the 'Stop' button is pressed.

2.  Modify the program in activity 1, above, to light the LED only
    after the 'Start' button is held for longer than one second.

3.  Create a program that uses each pushbutton to display its own,
    unique lighting pattern using any of the LEDs on BEAPER Nano or
    the Arduino Nano ESP32 module.

4.  The previous activity showed how to use the tone() function to
    play a tone for a specific amount of time. Passing only the audio
    frequency to the tone causes it to continue playing the tone until
    it is stopped using the noTone() function. Create a program that
    plays a different tone while each button is being pressed.
    
"""