"""
================================================================================
Beginner Activity 7: Counted Loops [Activity_B07_Counted_Loops.py]
March 10, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPER_Nano.py board module file.
================================================================================
"""
# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32
import BEAPER_Nano as beaper

import time

# --- Program Constants ----------------
FLASH_DELAY = const(100)
STEP_DELAY = const(300)

# --- Program Variables ----------------
SW5_pressed = False

beaper.nano_led_on()

# Wait for SW5 to begin
print("Press SW5 to begin...")
while not SW5_pressed:
  beaper.nano_led_toggle()
  time.sleep_ms(FLASH_DELAY)
  SW5_pressed = (beaper.SW5.value() == 0)

beaper.nano_led_on()
print("Starting!")

# Part 1: Repeat a done signal three times using a for loop
print("Part 1: for loop repeat")
for i in range(3):
  beaper.LED2.value(1)
  beaper.tone(4000, FLASH_DELAY)
  beaper.LED2.value(0)
  time.sleep_ms(FLASH_DELAY)

time.sleep_ms(STEP_DELAY)

# Part 2: Count up through LEDs using the loop variable
print("Part 2: count up")
for i in range(2, 6):
  print("  i =", i)
  beaper.LED2.value(i >= 2)
  beaper.LED3.value(i >= 3)
  beaper.LED4.value(i >= 4)
  beaper.LED5.value(i >= 5)
  time.sleep_ms(STEP_DELAY)

time.sleep_ms(STEP_DELAY)

# Part 3: Count down through LEDs using a negative step
print("Part 3: count down")
for i in range(5, 1, -1):
  print("  i =", i)
  beaper.LED2.value(i >= 2)
  beaper.LED3.value(i >= 3)
  beaper.LED4.value(i >= 4)
  beaper.LED5.value(i >= 5)
  time.sleep_ms(STEP_DELAY)

# All LEDs off
beaper.LED2.value(0)
beaper.LED3.value(0)
beaper.LED4.value(0)
beaper.LED5.value(0)
print("Done!")


"""
Guided Exploration

In Activity 6, Extension Activity 1 asked you to replace three manual
repetitions with a while loop. It worked, but it required you to
manage a loop control variable yourself - initialize it, check it in
the condition, and update it inside the loop body. MicroPython has a
loop structure designed specifically for situations where the number
of iterations is known in advance: the for loop. It handles the
initialize, check, and update steps automatically, leaving you to
focus on what the loop body should do. This activity explores three
forms of the for loop - range(n), range(start, stop), and
range(start, stop, step) - and when to use each one.

1.  Look at Part 1 of this program:

  for i in range(3):
    beaper.LED2.value(1)
    beaper.tone(4000, FLASH_DELAY)
    beaper.LED2.value(0)
    time.sleep_ms(FLASH_DELAY)

    The 'for i in range(3):' line tells MicroPython to run the loop
    body three times, automatically managing a loop variable called
    'i'. The range(3) function produces the sequence of values 0, 1,
    2 - one for each iteration. On the first iteration i is 0, on
    the second i is 1, and on the third i is 2.

    Add a print statement inside the Part 1 loop to print the value
    of i on each iteration:

  for i in range(3):
    print("i =", i)
    beaper.LED2.value(1)
    ...

    Run the program and observe the console output. Does i have the
    values you expected? Compare this for loop with the while loop
    solution you wrote in Activity 6 Extension Activity 1. What
    does the for loop handle automatically that your while loop
    required you to do manually?

2.  You may have noticed that range(3) produces 0, 1, 2 rather than
    1, 2, 3. This is intentional - MicroPython (and most programming
    languages) count from zero by default. The value in range(n) is
    the number of iterations, not the last value produced.

    One way to remember it: range(n) always produces exactly n
    values, starting from 0, and stopping before n. You can verify
    this with any range:

  for i in range(5):
    print(i)

    How many values does this print? What is the first? What is
    the last? Does range(5) ever produce the value 5?

3.  Part 2 of the program uses a two-argument form of range():

  for i in range(2, 6):

    This tells MicroPython to start at 2 and stop before 6, producing
    the values 2, 3, 4, 5. This is useful when the loop variable
    needs to start at a value other than 0.

    Look at how i is used inside the Part 2 loop body:

  beaper.LED2.value(i >= 2)
  beaper.LED3.value(i >= 3)
  beaper.LED4.value(i >= 4)
  beaper.LED5.value(i >= 5)

    Here, i is not just being counted - it is being used as meaningful
    data. Each comparison produces True or False, which directly sets
    the LED state. When i is 2, only LED2 is lit. When i is 4, LED2,
    LED3, and LED4 are all lit. Trace through all four values of i
    and describe what you would expect to see on the LEDs for each one.

    Run the program to verify your prediction. Was it correct?

4.  Part 3 uses a three-argument form of range():

  for i in range(5, 1, -1):

    The third argument is the step - the amount added to i after each
    iteration. A step of -1 counts downward. This produces the values
    5, 4, 3, 2 - stopping before reaching 1.

    Why does the sequence stop at 2 and not at 1? What would you
    change to make it include 1 as well?

    Try replacing the step with -2 in Part 3:

  for i in range(5, 0, -2):

    What values does i take? What do the LEDs show? Add a print
    statement to verify.

5.  The loop variable in a for loop doesn't have to be named 'i'.
    That name is just a convention - any valid variable name works.
    In fact, if you don't need to use the loop variable at all (as
    in Part 1, where only the number of repetitions matters), Python
    convention is to use an underscore '_' as the variable name to
    signal that the value is intentionally ignored:

  for _ in range(3):
    beaper.LED2.value(1)
    beaper.tone(4000, FLASH_DELAY)
    beaper.LED2.value(0)
    time.sleep_ms(FLASH_DELAY)

    Replace 'i' with '_' in the Part 1 loop and verify that the
    program still works identically. When would you choose to use
    a meaningful name like 'i' or 'count' instead of '_'?

    As a preview of something you'll explore in the intermediate
    activities: MicroPython's for loop can iterate over any sequence,
    not just a range of numbers. The BEAPER_Nano.py board module
    defines a list of LED objects called LEDS, so you can write:

  for led in beaper.LEDS:
    led.value(1)
    time.sleep_ms(STEP_DELAY)

    ...and the loop will visit each LED in turn without needing a
    range or an index variable at all. Lists and iteration over
    sequences are covered fully in the intermediate activities.

6.  A for loop and a while loop can often solve the same problem.
    Here is the Part 1 for loop rewritten as a while loop:

  count = 0
  while count < 3:
    beaper.LED2.value(1)
    beaper.tone(4000, FLASH_DELAY)
    beaper.LED2.value(0)
    time.sleep_ms(FLASH_DELAY)
    count += 1

    And here is a while loop equivalent for the Part 2 for loop:

  i = 2
  while i < 6:
    beaper.LED2.value(i >= 2)
    beaper.LED3.value(i >= 3)
    beaper.LED4.value(i >= 4)
    beaper.LED5.value(i >= 5)
    time.sleep_ms(STEP_DELAY)
    i += 1

    Both approaches produce identical results. When would you choose
    a for loop over a while loop, and when would a while loop be the
    better choice? Think about what each one communicates to someone
    reading your code.

7.  A for loop can be placed inside another for loop - this is called
    nesting. Here is a simple example to try:

  for led in range(2, 6):
    for flash in range(led - 1):
      beaper.LED2.value(led >= 2)
      beaper.LED3.value(led >= 3)
      beaper.LED4.value(led >= 4)
      beaper.LED5.value(led >= 5)
      time.sleep_ms(FLASH_DELAY)
      beaper.LED2.value(0)
      beaper.LED3.value(0)
      beaper.LED4.value(0)
      beaper.LED5.value(0)
      time.sleep_ms(FLASH_DELAY)
    time.sleep_ms(STEP_DELAY)

    Before running it, trace through the loop values and predict what
    you will see. For each value of 'led', how many times does the
    inner loop run? What does the pattern look like?

    Run the program to check your prediction. Print both loop
    variables to the console to help verify your understanding of
    what is happening at each step.


Extension Activities

For loops are the right tool when the number of iterations is known
in advance. Before starting each program below, think about which
loop type fits each part of the problem - a for loop where the count
is fixed, and a while loop where the program needs to wait for
something to happen or respond to changing conditions.

1.  Rewrite the Activity 6 starter program, replacing only the parts
    that are naturally expressed as counted loops. The wait-for-SW5
    loop should remain a while loop - explain in a comment why it
    cannot be replaced with a for loop. The countdown should become
    a for loop using range() with a negative step, and the done
    signal should become a for loop using range(3).

    How much shorter is the rewritten version compared to the
    Activity 6 original? Which version do you find easier to read?

2.  Create an LED bar graph that fills from left to right and then
    empties from right to left, repeating continuously. Use two for
    loops - one to fill and one to empty - and adjust the step delay
    to find a speed that looks smooth.

    Extend the program so that SW4 speeds up the animation and SW3
    slows it down, using a variable delay that changes with each
    button press. What minimum and maximum values make sense?

3.  Use nested for loops to create a structured LED display. The
    outer loop should select each LED in sequence (LED2 through LED5),
    and the inner loop should flash that LED a number of times equal
    to its position in the sequence (LED2 flashes once, LED3 flashes
    twice, LED4 three times, LED5 four times). Add a short pause
    between each LED's flashes and a longer pause between LEDs.

    Once this works, add a second pass in reverse order using a
    second pair of nested loops, so the full sequence goes 1-2-3-4
    flashes and then 4-3-2-1 flashes before repeating.

4.  Create a binary counter that uses the four LEDs to display the
    binary representation of numbers from 0 to 15. Use a for loop
    to count from 0 to 15, and for each value light the LEDs to
    show its binary representation:

    - LED2 represents the 1s place (bit 0)
    - LED3 represents the 2s place (bit 1)
    - LED4 represents the 4s place (bit 2)
    - LED5 represents the 8s place (bit 3)

    Hint: MicroPython's bitwise AND operator '&' and right-shift
    operator '>>' can help extract individual bits from a number:

  for i in range(16):
    beaper.LED2.value((i >> 0) & 1)  # bit 0
    beaper.LED3.value((i >> 1) & 1)  # bit 1
    beaper.LED4.value((i >> 2) & 1)  # bit 2
    beaper.LED5.value((i >> 3) & 1)  # bit 3
    time.sleep_ms(STEP_DELAY)

    Use print to display each number's decimal value and its binary
    representation in the console alongside the LED display. What
    is the highest number the four LEDs can represent?

5.  Write a program that produces a Morse code output for a short
    word or phrase of your choice. Represent each dot as a short LED
    flash and tone, and each dash as a longer one. Use a for loop to
    iterate over a list of dot/dash patterns for each letter.

    You will learn how lists work in full detail in the intermediate
    activities - but even without fully understanding them yet, you
    can use the pattern in the hint below to produce some interesting
    results. This is a preview of how for loops are used more broadly
    in MicroPython beyond just iterating over ranges of numbers.

    Hint: A for loop can iterate directly over a list, visiting each
    item in turn. The tone() function blocks for the duration of the
    tone, so the sleep_ms() call that follows adds a gap after the
    sound ends:

  morse_s = ['.', '.', '.']        # S = dot dot dot
  morse_o = ['-', '-', '-']        # O = dash dash dash

  for symbol in morse_s:
    if symbol == '.':
      beaper.tone(800, 100)        # Short tone for dot
    else:
      beaper.tone(800, 300)        # Long tone for dash
    time.sleep_ms(100)             # Gap between symbols

    Try spelling 'SOS' by iterating over morse_s, morse_o, and
    morse_s in sequence. By convention, the gap between letters
    should be three times the dot duration - add a time.sleep_ms()
    between each letter's loop to observe the difference it makes.
    Experiment with different frequencies and durations to improve
    the sound.

"""