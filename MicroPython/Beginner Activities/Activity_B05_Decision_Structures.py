"""
================================================================================
Beginner Activity 5: Decision Structures [Activity_B05_Decision_Structures.py]
February 26, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPER_Nano.py board module file.
================================================================================
"""
# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32
import BEAPER_Nano as beaper

import time

# --- Program Constants ----------------
MAX_COUNT = const(50)

# --- Program Variables ----------------
SW2_pressed = False
SW3_pressed = False
SW4_pressed = False
SW5_pressed = False
SW3_presses = 0
SW4_presses = 0
SW3_last = False
SW4_last = False

beaper.nano_led_on()

while True:
  # Read pushbuttons
  SW2_pressed = (beaper.SW2.value() == 0)
  SW3_pressed = (beaper.SW3.value() == 0)
  SW4_pressed = (beaper.SW4.value() == 0)
  SW5_pressed = (beaper.SW5.value() == 0)

  if SW3_pressed:
    beaper.LED2.value(1)
  else:
    beaper.LED2.value(0)

  time.sleep_ms(20)


"""
Guided Exploration

Real programs rarely make simple yes/no decisions. Most interesting
behaviour comes from choosing between multiple possibilities based
on changing conditions and values. This activity introduces the
if/elif chain - a way of expressing multi-way decisions - along with
comparison operators, counting variables, and edge detection. These
tools, combined with the named variables and Boolean logic from
Activity 4, make it possible to write programs that respond to what
has happened, not just what is happening right now.

1.  This program's button variables (SW3_pressed, SW4_pressed, etc.)
    hold True or False Boolean values, which means they can be
    combined using the Boolean logical operators 'and', 'or', and
    'not'. For example, changing the if condition in the program to:

  if SW3_pressed and SW4_pressed:

    ...will light LED2 only when both SW3 and SW4 are pressed at the
    same time. Modify the if condition in your program to match this
    example and verify that it works as expected.

2.  Replace the 'and' operator in the if condition with 'or' and run
    the program again. Does it work the way you would expect it to?

3.  It's just as easy to invert an input to its opposite state using
    the logical 'not' operator. Predict how you think this conditional
    expression will behave:

  if SW3_pressed and not SW4_pressed:

    Try the condition in your program to verify your prediction.

4.  Let's make the program count the number of times SW3 is pressed.
    Start by reverting the if condition back to reading only the state
    of SW3. Next, add the 'SW3_presses += 1' compound operation inside
    the if block to accumulate SW3 presses. This is shorthand for
    'SW3_presses = SW3_presses + 1' - it adds 1 to the current value
    and stores the result back into the same variable:

  if SW3_pressed:
    beaper.LED2.value(1)
    SW3_presses += 1
  else:
    beaper.LED2.value(0)

    Add a print statement inside the if block to display the count
    in the console each time SW3 is pressed:

  if SW3_pressed:
    beaper.LED2.value(1)
    SW3_presses += 1
    print("SW3_presses:", SW3_presses)

    Run the program, open the console, and press SW3 a few times.
    How quickly does the count increase? Does the count go up once
    per press, or faster? What do you think is happening?

5.  Previous programs have used the '==' (equal to) conditional
    operator to check if two values are the same. MicroPython supports
    six comparison operators that can be used in if conditions:

    ==  equal to
    !=  not equal to
    <   less than
    >   greater than
    <=  less than or equal to
    >=  greater than or equal to

    Now add this set of if/elif conditions below the SW3 if block to
    display the count using the LEDs:

  # Light LEDs for different numbers of presses
  if SW3_presses >= 1:
    beaper.LED3.value(1)
  elif SW3_presses >= 10:
    beaper.LED4.value(1)
  elif SW3_presses >= MAX_COUNT:
    beaper.LED5.value(1)

    The if/elif structure is a chain of conditional decisions. Starting
    with the first if, each condition is evaluated in turn until the
    first true condition is found. Once a true condition is found, its
    code runs and the rest of the chain is skipped entirely.

    Run the program and press SW3. LED3 should light after the first
    press - does it? Does LED4 light after ten presses? Using what
    you now know about how the chain works, can you explain why?

    Re-arrange the conditions so that the chain evaluates from the
    largest value down to the smallest, and add a reset block for SW5:

  # Light LEDs for different numbers of presses
  if SW3_presses >= MAX_COUNT:
    beaper.LED5.value(1)
  elif SW3_presses >= 10:
    beaper.LED4.value(1)
  elif SW3_presses >= 1:
    beaper.LED3.value(1)

  # Reset the count
  if SW5_pressed:
    SW3_presses = 0
    beaper.LED3.value(0)
    beaper.LED4.value(0)
    beaper.LED5.value(0)

    Test the updated program. Does the LED behaviour now match what
    you would expect? Press SW5 to reset the count and confirm that
    all three LEDs turn off.

6.  You may have noticed that the counter increases very quickly -
    much faster than you are actually pressing the button. This is
    because the button state is read every loop cycle, so holding SW3
    for even a fraction of a second registers dozens of counts.

    The solution is edge detection - counting a press only when the
    button transitions from not pressed to pressed. The program
    already declares SW3_last for exactly this purpose:

  # Detect a new SW3 press (not pressed to pressed transition)
  if SW3_pressed and not SW3_last:
    SW3_presses += 1
    beaper.LED2.value(1)
  else:
    beaper.LED2.value(0)

    SW3_last must be updated at the end of each loop cycle, after all
    the button logic has run, so it correctly holds the previous
    loop's button state:

  # Save button states for next loop
  SW3_last = SW3_pressed

    Add both of these changes to your program. The print statement
    from GE4 will now show exactly one count per press in the console,
    regardless of how long the button is held. This is a good example
    of using print() to verify that a fix is working correctly - once
    you are satisfied, the print statement can be removed or commented
    out.

    The SW4_last variable is also already declared for the same
    purpose. Can you add edge detection for SW4 as well?

7.  Remove the print statement from your program and run it to confirm
    everything still works correctly. Now think back to the program
    in Activity 4's Exploration file, where pressing a button during
    the light pattern had no effect until the pattern finished. How
    is the approach in this activity different, and what makes edge
    detection better suited to counting presses accurately?


Extension Activities

The activities below build directly on the counting and edge detection
techniques from the Guided Exploration. Use named variables and
constants throughout, and use print() to help develop and debug your
programs - removing or commenting out debugging output once you are
satisfied that everything works correctly.

1.  Modify the press-counting program from the Guided Exploration so
    that pressing SW4 increases the count and pressing SW3 decreases
    it. Clamp the count so that it can never go below zero or above
    MAX_COUNT. Use the LEDs to display four ranges of the count value
    (off, low, medium, and high).

2.  Create a program that uses SW3 and SW4 as 'back' and 'forward'
    buttons to scroll through four different LED patterns, one per
    button press. Pressing SW4 should advance to the next pattern, and
    pressing SW3 should go back to the previous one. The sequence
    should wrap around - going past the last pattern returns to the
    first, and going before the first returns to the last.

3.  Create a two-player rapid-clicker game in which the first player
    to reach MAX_COUNT wins. Here is how the game should work:

    - Player 1 uses SW3, and LED2 flashes briefly on each of their clicks
    - Player 2 uses SW4, and LED5 flashes briefly on each of their clicks
    - The first player to reach MAX_COUNT wins
    - If Player 1 wins, LED3 lights up and stays on
    - If Player 2 wins, LED4 lights up and stays on
    - Once a player has won, additional button presses from either
      player should be blocked until the game is reset
    - Pressing SW5 resets both counters, turns off all LEDs, and
      restarts the game

    Use edge detection from GE6 for both SW3 and SW4 so that each
    physical press is counted exactly once. You will need a Boolean
    variable to track whether the game is still active - start with
    something like:

SW3_presses = 0
SW4_presses = 0
SW3_last = False
SW4_last = False
game_active = True

    Wrap all of the player input and win-checking logic inside an
    'if game_active:' block, and handle the SW5 reset outside of it
    so that the reset always works regardless of game state.

    While developing your game, use print() to track both counters
    at once:

    print("P1:", SW3_presses, "P2:", SW4_presses)

    Once your game is working correctly, remove or comment out the
    print statement - debugging output left in a finished program
    clutters the console and can be confusing.

"""