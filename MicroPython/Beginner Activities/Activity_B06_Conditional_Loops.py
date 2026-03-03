"""
================================================================================
Beginner Activity 6: Conditional Loops [Activity_B06_Conditional_Loops.py]
March 3, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPER_Nano.py board module file.
================================================================================
"""
# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32
import BEAPER_Nano as beaper

import time

# --- Program Constants ----------------
FLASH_DELAY = const(100)
COUNT_DELAY = const(500)

# --- Program Variables ----------------
SW5_pressed = False
count = 0

beaper.LED2.value(1)
beaper.LED3.value(1)
beaper.LED4.value(1)
beaper.LED5.value(1)

# Wait for SW5 to start the countdown
print("Press SW5 to start the countdown...")
while not SW5_pressed:
  beaper.nano_led_toggle()
  time.sleep_ms(FLASH_DELAY)
  SW5_pressed = (beaper.SW5.value() == 0)

# Ensure status LED stays on and set starting count
beaper.nano_led_on()
count = 4

# Count down using LEDs
while count > 0:
  if count >= 4:
    beaper.LED5.value(1)
  else:
    beaper.LED5.value(0)
  if count >= 3:
    beaper.LED4.value(1)
  else:
    beaper.LED4.value(0)
  if count >= 2:
    beaper.LED3.value(1)
  else:
    beaper.LED3.value(0)
  if count >= 1:
    beaper.LED2.value(1)
  else:
    beaper.LED2.value(0)
  print("count:", count)
  time.sleep_ms(COUNT_DELAY)
  count -= 1

# Countdown finished
print("Countdown complete!")
beaper.LED2.value(0)
time.sleep_ms(COUNT_DELAY)

# Beep and blink LED three times
beaper.LED2.value(1)
beaper.tone(4000, FLASH_DELAY)
beaper.LED2.value(0)
time.sleep_ms(FLASH_DELAY)
beaper.LED2.value(1)
beaper.tone(4000, FLASH_DELAY)
beaper.LED2.value(0)
time.sleep_ms(FLASH_DELAY)
beaper.LED2.value(1)
beaper.tone(4000, FLASH_DELAY)
beaper.LED2.value(0)
time.sleep_ms(FLASH_DELAY)


"""
Guided Exploration

Every program written so far has used 'while True:' as its main loop
- a loop that runs forever because its condition is always true. But
a while loop's condition can be any expression that evaluates to True
or False, and the loop will keep running only as long as that
expression remains true. This means a loop can exit when something
happens, or when a value reaches a target. Choosing the right loop
condition is a design decision, and this activity explores what the
options are and when each one is most useful.

1.  This program uses two while loops, each with a different
    condition. The first one:

  while not SW5_pressed:

    ...keeps running as long as SW5 is NOT pressed. The loop body
    toggles the status LED to let the user know the program is
    waiting. As soon as SW5 is pressed, SW5_pressed becomes True,
    'not SW5_pressed' becomes False, and the loop exits.

    The second loop:

  while count > 0:

    ...keeps running as long as 'count' is greater than zero. Each
    iteration of the loop decreases 'count' by 1, so the loop will
    exit after exactly four iterations.

    There is an important difference between these two loops. Can you
    describe what that difference is? Which one could you predict the
    exact number of iterations for before the program runs, and which
    one couldn't you? What does this tell you about when each type of
    condition is most useful?

2.  The variable 'count' plays three roles in the countdown loop: it
    is set to a starting value before the loop begins, it is checked
    in the loop's condition on every iteration, and it is changed
    inside the loop body. This combination - initialize, check, update
    - is the standard pattern for a loop control variable.

    Look at the countdown loop and identify where each of these three
    things happens:

  count = 4             # Initialize
  while count > 0:      # Check
    ...
    count -= 1          # Update

    What would happen if the 'count -= 1' line were missing? Try
    removing it from your program and running it. What do you observe?
    Why does this happen? Press the stop button to end the program,
    then restore the line before continuing.

3.  The first while loop doesn't count, but still needs to initialize,
    check, and update a variable to either continue looping or exit.
    Look at the loop and identify what variable it uses, where it gets
    initialized, where it is checked, and where it is updated as the
    loop runs.

4.  Notice that the program has code between and after the two while
    loops. The 'beaper.nano_led_on()' line runs after the first loop
    exits but before the second loop begins, and the countdown-
    complete signal runs only after both loops have finished.

    Most programs you have written so far have had all their code
    inside a 'while True:' loop, which means nothing placed after
    that loop ever runs. This program demonstrates that loops can
    exit, and that code placed after a loop runs exactly once when
    the loop finishes.

    The current program runs once and stops, but most microcontroller
    programs need to keep running forever. Modify the program to wrap
    everything - both while loops and all the code between and after
    them - inside an outer 'while True:' loop, just like your previous
    programs. After the countdown finishes and the done signal plays,
    the program should reset and wait for SW5 to be pressed again.
    What variable needs to be reset at the start of each outer loop
    cycle, and why?

5.  The 'while not SW5_pressed:' loop in this program is a common
    and useful pattern - a loop that simply waits until something
    happens before allowing the program to continue. It can be used
    any time a program needs to pause at a specific point until a
    condition is met.

    You have also seen 'not' used in if conditions in Activity 5.
    In both cases, 'not' inverts the truth value of whatever follows
    it. Here are three equivalent ways to write the same wait loop:

  while not SW5_pressed:          # While SW5 is NOT pressed
  while SW5_pressed == False:     # Same thing, more verbose
  while beaper.SW5.value() != 0:  # Reading the pin directly

    All three do the same thing. The third option reads the hardware
    pin directly rather than using a named variable - notice that it
    requires you to know whether the switch is active-low or
    active-high, while the first two options hide that detail behind
    a meaningful name. Which do you find most readable, and why?
    What does your answer tell you about the value of meaningful
    variable names?

6.  The print() statements in this program reveal what is happening
    inside the loops in the console. Run the program and observe the
    console output as the countdown progresses.

    Add a print statement inside the 'while not SW5_pressed:' loop
    to show that the waiting loop is running. What do you observe
    about how quickly the messages appear compared to the countdown
    loop's messages? What accounts for the difference in speed?

7.  A conditional loop whose condition never becomes false will run
    forever - exactly like 'while True:'. This is sometimes called
    an infinite loop, and is usually the result of a bug rather than
    intentional design.

    The countdown loop exits because 'count -= 1' eventually makes
    'count' reach zero. But what if the condition were 'while count
    != 0:' and count started at an odd number and decreased by 2
    each iteration? Would the loop ever exit? Try it:

  count = 5
  while count != 0:
    print("count:", count)
    time.sleep_ms(COUNT_DELAY)
    count -= 2

    What happens? Why? What would be a safer condition to use here?
    Press the stop button to end the program, then change the
    condition to 'while count > 0:' and verify that it now exits
    correctly.


Extension Activities

These activities use conditional loops as a core structural tool.
As you write each program, think carefully about what the loop's
exit condition should be before you start coding - the condition is
a design decision that determines when the program moves on, and
getting it right is just as important as getting the code inside
the loop right.

1.  Look at the 'Beep and blink LED three times' section at the end
    of the program. It works, but the three repetitions are written
    out manually - which is repetitive and would become impractical
    if you needed ten or twenty repetitions instead of three.

    Replace the three manual repetitions with a single while loop
    that produces the same beep-and-blink pattern exactly three
    times. You will need a loop control variable to count the
    repetitions and an exit condition that stops the loop after
    the third one.

    What is the minimum number of lines your while loop solution
    requires? How does it compare to the manual version?

2.  Write a program that waits in a loop for SW2 to be pressed, then
    waits in a second loop for SW2 to be released, then lights LED2
    to indicate the button was pressed and released. Use print
    statements to show each phase - waiting for a press, waiting for
    release, and done.

    Edge detection from Activity 5 catches the moment a button
    transitions from not pressed to pressed, but it does so by
    comparing the current and previous loop states on every cycle.
    This press-and-release approach is different - it explicitly
    waits in a dedicated loop for each transition to complete before
    moving on. When might you prefer one approach over the other?

3.  Write a program that uses a conditional loop to flash LED2 a
    number of times equal to the number of times SW3 was pressed
    before SW5 was pressed. The program should:

    - Wait in a loop for button presses, counting SW3 presses using
      edge detection and flashing LED2 momentarily on each press
    - Exit the waiting loop when SW5 is pressed
    - Flash LED3 once for each press that was counted, with a short
      pause between each flash

    This structure - an input phase that collects data in one loop,
    followed by an output phase that acts on that data in a second
    loop - is a useful program pattern that separates concerns
    clearly and makes each phase easier to reason about.

4.  Create a reaction timer program. The program should:

    - Display a brief 'get ready' signal by lighting LED2
    - Wait for a random delay between 2 and 5 seconds before
      lighting LED3 as the 'go' signal (use the hint below)
    - Wait in a loop for SW3 to be pressed, using a fixed
      time.sleep_ms(10) delay inside the loop so each iteration
      takes a known 10ms - this makes the iteration count a reliable
      measure of elapsed time
    - Display the result by lighting a different combination of LEDs
      depending on whether the count was low (fast), medium, or high
    - Use print to show the exact loop iteration count in the console

    Hint: MicroPython's built-in random number generator can be
    used to get a random integer in a range like this:

  import random
  delay_ms = random.randint(2000, 5000)
  time.sleep_ms(delay_ms)

5.  Re-create the two-player rapid-clicker game from Activity 5,
    but replace the 'if game_active:' block with a conditional while
    loop. The game loop should keep running while neither player has
    reached MAX_COUNT. When the loop exits, determine the winner
    and light the appropriate LED.

    How does restructuring the game around a while loop change the
    program compared to the Activity 5 version? Is the logic clearer
    or less clear? What are the trade-offs?

6.  Create a combination lock program that requires the user to press
    SW2, SW3, SW4, and SW5 in a specific order. The program should:

    - Wait in a loop for each button in the correct sequence
    - If the correct button is pressed, advance to the next step
      and flash LED2 momentarily to confirm
    - If the wrong button is pressed, flash LED5 to indicate an
      error and reset to the beginning of the sequence
    - When the full correct sequence is entered, light all LEDs
      and play a short celebratory tone sequence

    Hint: Use a step counter variable to track which position in
    the sequence the program is currently waiting for. When a correct
    button is pressed, increment the step counter. When a wrong button
    is pressed, reset it to zero. The loop can exit when the step
    counter reaches the length of the full sequence.

"""