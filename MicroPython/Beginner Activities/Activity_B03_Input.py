"""
================================================================================
Beginner Activity 3: Digital Input [Activity_B03_Input.py]
February 26, 2026

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
Guided Exploration

From this activity onward, the main loop does more than just wait —
it continuously checks the state of inputs and responds to them. This
technique is called polling: the program repeatedly asks "is the
button pressed yet?" on every pass through the loop. Understanding
polling, and its limitations, is fundamental to writing responsive
microcontroller programs.

It also helps to know that BEAPER Nano's pushbuttons are wired as
active-low inputs — pressing a button connects its pin to ground,
making the pin read 0 rather than 1. Keep this in mind as you read
through the code and the questions below.

1.  The pushbuttons in the BEAPER Nano circuit are connected in what
    is known as a pull-up configuration, meaning one side of each
    pushbutton switch is wired in series with a resistor that is
    connected, or 'pulled up', to the power supply voltage. The other
    terminal of the pushbutton is connected to ground, and the
    microcontroller input pin sits in between the pull-up resistor and
    the switch, reading the voltage across the switch.

    The inactive voltage (when the pushbutton is not pressed) will be
    high due to the pull-up resistor's connection to the power supply,
    and the active voltage (when the pushbutton is pressed) will be 0V
    because the switch connects the pin directly to ground. This is
    what makes it an active-low input — the pin reads 0 when active.

    What value do you expect beaper.SW2.value() to return when SW2 is
    not pressed? What about when SW2 is pressed?

    MicroPython's value() method can be used without an argument to
    read the value of an I/O pin, like this:

  if beaper.SW2.value() == 0:

    Note that two equals signs '==' are used to compare values, while
    a single equals sign '=' is used to assign a value. Mixing these
    up is one of the most common beginner mistakes in programming —
    'beaper.SW2.value() = 0' would cause an error, while
    'beaper.SW2.value() == 0' checks whether SW2 is reading 0.

    The 'if' statement works similarly to the 'while' loop: program
    statements indented below it execute when the condition is true.
    This if condition also has a complementary 'else:' clause, which
    runs when the condition is false — so exactly one of the two
    branches always executes.

    Looking at SW2's if-else condition, explain the program flow when
    SW2 is not pressed, and when SW2 is pressed. Which LED2 value()
    call executes in each case?

2.  Press SW5 to start the light pattern. While the pattern is
    running, does pressing and holding SW2 turn LED2 on? Explain why
    or why not, and what you think is happening in the program.

    Think back to Activity 2's discussion of blocking delays — the
    Notes and Warnings in the delay() documentation pointed out that
    the microcontroller can't do anything else while a delay is
    running. How does that relate to what you're observing here?
    Can you think of a way to test and verify your explanation?

3.  Activity 2's Extension Activities demonstrated how to use tone()
    with both a frequency and a duration argument. Passing tone() only
    a frequency argument causes it to start playing until either
    another tone() call changes the frequency, or noTone() is called
    to stop it.

    An if-else condition is an ideal way to play a tone while a button
    is held and stop it when the button is released. Add this code to
    your program to try it out:

  if beaper.SW3.value() == 0:
    beaper.tone(440)
  else:
    beaper.noTone()

    What is the advantage of using an if-else structure here instead
    of two separate if conditions — one to start the tone and one to
    stop it?

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

    The nested if-else logic enables SW4 to turn the LED on only if
    both SW3 and SW4 are pressed. Try the code in your program to
    verify that it works as expected.

5.  A better way to use two buttons to turn on one LED is by using
    the 'and' logical operator in the if condition, like this:

  if beaper.SW3.value() == 0 and beaper.SW4.value() == 0:
    beaper.LED3.value(1)
  else:
    beaper.LED3.value(0)

    Try this code in your program to verify that it works. In what
    ways is this solution better than using nested if-else conditions?

6.  The logical 'or' operator can also be used in conditional
    expressions. Predict when the LED would be lit if the 'and'
    operator in GE5 were replaced with 'or'. Try it in your program
    to verify your prediction.


Extension Activities

Writing programs that respond to inputs is where microcontroller
programming starts to feel alive. As you write your own programs,
get into the habit of adding short comments to explain what each
section of your code does — a comment that explains *why* code is
written a certain way is often more valuable than one that just
describes *what* it does. Future you will thank present you.

1.  Create a program that simulates the separate 'Start' and 'Stop'
    buttons found on large industrial machines. The machine (simulated
    by an LED) should turn on when the 'Start' button is pressed and
    remain on until the 'Stop' button is pressed.

    What happens if both buttons are held at the same time? Is the
    machine (LED) on or off? Describe what the program is doing in
    that case.

    Using what you learned about the 'and' logical operator in GE5,
    modify your program so that the 'Start' button only turns the
    machine on when the 'Stop' button is not being held at the same
    time.

2.  Modify the program from EA1 to light the LED only after the
    'Start' button has been held for longer than one second.

3.  Create a program that uses each pushbutton to display its own
    unique lighting pattern using any combination of LEDs, or to
    play a different tone or short tune when each button is pressed.

4.  Imagine that you're creating a turn signal circuit for a bicycle.
    The circuit uses four LEDs in a row, controlled by two pushbuttons
    on the handlebars. Write a program to simulate the turn signal
    using one or more of BEAPER Nano's LEDs to indicate a left or
    right turn while the corresponding button is held.

    For an extra challenge, add brake functionality or a bell/horn
    feature. Can you make the brake or horn operate while the turn
    signal is active? What makes doing this so difficult?

"""