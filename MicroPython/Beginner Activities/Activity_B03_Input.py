"""
================================================================================
Beginner Activity 3:  Digital Input [Activity_B03_Input.py]
February 5, 2026

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
  if beaper.SW2.value() == 0:
    beaper.LED2.value(1)
  else:
    beaper.LED2.value(0)

  # Start a pattern
  if beaper.SW5.value() == 0:
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

    
"""
Program Analysis Activities

1.  The pushbuttons in the BEAPER Nano circuit are connected in what
    is known as a pull-up configuration, meaning one side of each
    pushbutton switch is wired in series with a resistor that is
    connected, or 'pulled-up', to the power supply potential. The
    other terminal of the pushbutton switch is connected to ground,
    and the microcontroller input pin is connected in-between the
    pull-up resistor and the switch, so that it reads the potential
    across the switch.
    
    The inactive potential (when the pushbutton is not pressed) of a
    pull-up circuit will be a high voltage due to the resistor's power
    supply connection, and the active potential (when the pushbutton is
    pressed) will be 0V. This pull-up circuit arrangment creates what
    is commonly referred to as an 'active-low' pushbutton switch.
    
    MicroPython's value() method can be used without an argument
    (the 0, or 1, used to make the pin output low, or high) to read
    the value of an I/O pin, like this:

  if beaper.SW2.value() == 0:

    The 'if' statement, known as an 'if condition', employs a similar
    structure to that used by the 'while' loop. That is, the program
    statements indented below the if statement will execute whenever
    the condition is true (or, 'True' in the case of MicroPython,
    since capitalization matters). And, in this case the condition
    will be true when the value of the SW2 pin is equal to zero (two
    equals signs are used to check and compare values, as oppposed to
    one equals sign being used to set a value).

    This if condition also includes a complementary 'else:' statement,
    whcih will logically be the opposite of if. When if is true, else
    will be false, and when if is false, else will become true.

    Looking at SW2's if-else condition, explain the program flow when
    SW2 is not pressed, and when SW2 is pressed. Which LED2 value()
    function executes in each case?

2.  Press SW5 to start a light pattern. While the light pattern is
    running, does pressing and holding SW2 turn LED2 on? Explain why
    or why not, and what you think is happening in the program. Can
    you think of a way to test and verify your assumption?

3.  The previous programming activity demonstrated how to use the
    tone() function to play a tone for a specific amount of time by
    passing it both frequency and duration arguments. Passing the
    tone() function only a frequency argument will cause it to start
    playing the tone until either: another call to tone() changes the
    frequency, or the noTone() function is called to stop the tone.

    An if-else condition is an ideal way to play the tone while a
    button is being pressed, and stop it when the button is released.
    Add this code to your program to try it out:

  if beaper.SW3.value() == 0:
    beaper.tone(440)
  else:
    beaper.noTone()

    What is the advantage of using an 'if-else' structure instead of
    using two separate if conditions – one to start the tone, and a
    second to stop the tone – to do the same thing?


Programming Activities

1.  Create a program that simulates the separate 'Start' and 'Stop'
    buttons that would be found on large, industrial machines. The
    machine (simulated by an LED) should turn on when the 'Start'
    button is pressed, and remain on until the 'Stop' button is
    pressed.

2.  Describe what happens in the Start/Stop program, above, if both
    pushbuttons are held? Is the machine (LED) on, or off? Describe
    what the program is doing.

3.  Modify the program in activity 1, to only turn the LED on if
    the 'Start' button is pressed while the 'Stop' button is released.
    
4.  Modify the program in activity 1, above, to light the LED only
    after the 'Start' button is held for longer than one second.

5.  Create a program that uses each pushbutton to either display its
    own, unique lighting pattern using any combination of LEDs, or to
    play different tones (or even short tunes) when each button is
    pressed.
    
"""