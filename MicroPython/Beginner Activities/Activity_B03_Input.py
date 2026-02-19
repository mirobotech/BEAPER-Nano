"""
================================================================================
Beginner Activity 3:  Digital Input [Activity_B03_Input.py]
February 9, 2026

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

  time.sleep_ms(20)  # Short delay for button debouncing


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
    pressed) will be 0V. This pull-up circuit arrangement creates what
    is commonly referred to as an 'active-low' pushbutton switch.

    What value do you expect beaper.SW2.value() to return when SW2 is
    not pressed? What about when SW2 is pressed?

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
    equals signs are used to check and compare values, as opposed to
    one equals sign being used to set a value).

    This if condition also includes a complementary 'else:' statement,
    which will logically be the opposite of if. When if is true, else
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

    An if-else condition is an ideal way to play a tone while a
    button is being pressed, and stop it when the button is released.
    Add this code to your program to try it out:

  if beaper.SW3.value() == 0:
    beaper.tone(440)
  else:
    beaper.noTone()

    What is the advantage of using an 'if-else' structure instead of
    using two separate if conditions - one to start the tone, and a
    second to stop the tone - to do the same thing?

4.  Let's try using a combination of two pushbuttons to turn on one
    LED. One way to accomplish this is by nesting one if-else
    condition inside another, like this:

  if beaper.SW3.value() == 0:
    if beaper.SW4.value() == 0:
      beaper.LED3.value(1)
    else:
      beaper.LED3.value(0)
  else:
    beaper.LED3.value(0)
    
    The nested if-else logic enables SW4 to turn the LED only if both
    it and SW3 are pressed. Try the code in your program to verify
    that it works as expected.

5.  A better way to use two buttons to turn on one LED is by using
    an 'and' logical operator in the if condition, like this:

  if beaper.SW3.value() == 0 and beaper.SW4.value() == 0:
    beaper.LED3.value(1)
  else:
    beaper.LED3.value(0)

    Try this code in your program to verify that it works. In what
    ways is this solution better than using nested if-else conditions?

6.  The logical 'or' operator can also be used in conditional
    expressions. Describe when the LED would be lit if the SW3
    and SW4 pushbutton inputs in the activity were combined using a
    logical or operator instead of the and operator in the condition.
    

Programming Activities

1.  Create a program that simulates the separate 'Start' and 'Stop'
    buttons that would be found on large, industrial machines. The
    machine (simulated by an LED) should turn on when the 'Start'
    button is pressed, and remain on until the 'Stop' button is
    pressed.

2.  Describe what happens in the Start/Stop program, above, if both
    pushbuttons are held? Is the machine (LED) on, or off? Describe
    what the program is doing.

3.  Modify the program in activity 1, to only turn the LED on if the
    'Start' button is pressed while the 'Stop' button is released.
    
4.  Modify the program in activity 1, above, to light the LED only
    after the 'Start' button is held for longer than one second.

5.  Create a program that uses each pushbutton to either display its
    own, unique lighting pattern using any combination of LEDs, or to
    play different tones (or even short tunes) when each button is
    pressed.

6.  Imagine that you're creating a turn signal circuit for a bicycle.
    The circuit design uses four LEDs mounted in a horizontal row
    under the rider's seat, and these will be controlled by two
    pushbuttons mounted on the bicycle's handlebars. Write a program
    to simulate the operation of the turn signal circuit using one
    or more of the LEDs to indicate a turn while its corresponding
    direction button is being held.

    For an extra challenge, add brake functionality or a bell/horn
    feature. Can you make the brake or horn operate while the turn
    signal is in operation? What makes doing this so difficult?
    
"""
