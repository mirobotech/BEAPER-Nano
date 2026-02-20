"""
================================================================================
Beginner Activity 8: Functions [Activity_B08_Functions.py]
February 20, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPER_Nano.py board module file.
================================================================================
"""
# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32
import BEAPER_Nano as beaper

import random
import time

# --- Program Constants ----------------
FLASH_DELAY = const(100)
STEP_DELAY = const(400)
MAX_ATTEMPTS = const(4)

# --- Program Variables ----------------
target = 0
attempts = 0


# --- Program Functions ----------------

def clear_leds():
  # Turn off all four LEDs.
  beaper.LED2.value(0)
  beaper.LED3.value(0)
  beaper.LED4.value(0)
  beaper.LED5.value(0)

def indicate_attempts(count):
  # Light LEDs to show remaining attempts: 4 lit = 4 remaining, etc.
  beaper.LED2.value(count >= 1)
  beaper.LED3.value(count >= 2)
  beaper.LED4.value(count >= 3)
  beaper.LED5.value(count >= 4)

def read_keypad():
  # Wait for any pushbutton to be pressed and released.
  # Returns the button number (2, 3, 4, or 5) when released.
  key = 0
  while key == 0:
    if beaper.SW2.value() == 0:
      key = 2
    elif beaper.SW3.value() == 0:
      key = 3
    elif beaper.SW4.value() == 0:
      key = 4
    elif beaper.SW5.value() == 0:
      key = 5
  while beaper.SW2.value() == 0 or beaper.SW3.value() == 0 or \
        beaper.SW4.value() == 0 or beaper.SW5.value() == 0:
    pass
  return key


# --- Main Program ---------------------

beaper.nano_led_on()
print("Button guessing game - find the secret button!")

while True:
  # Start a new round
  target = random.randint(2, 5)
  attempts = MAX_ATTEMPTS
  indicate_attempts(attempts)
  print("New round! Guess the secret button (SW2-SW5)...")

  # Play the round
  while attempts > 0:
    key = read_keypad()
    print("You pressed SW" + str(key))

    if key == target:
      print("Correct! You found it in", MAX_ATTEMPTS - attempts + 1, "guess(es)!")
      for _ in range(3):
        beaper.tone(4000, FLASH_DELAY)
        time.sleep_ms(FLASH_DELAY)
      clear_leds()
      time.sleep_ms(STEP_DELAY)
      attempts = 0           # Exit the inner loop to start a new round
    else:
      attempts -= 1
      beaper.tone(200, FLASH_DELAY)
      indicate_attempts(attempts)
      if attempts > 0:
        print("Wrong! ", attempts, "attempt(s) remaining.")
      else:
        print("Out of attempts! The secret button was SW" + str(target))
        time.sleep_ms(STEP_DELAY)
        clear_leds()


"""
Program Analysis Activities

1.  Every program in this curriculum has used functions. Every time
    you have written 'beaper.tone()', 'beaper.LED2.value()', or
    'time.sleep_ms()', you have been calling a function - passing
    it information (or nothing at all) and letting it do a job.

    A function is a named block of code that can be called from
    anywhere in a program. Functions can receive input values called
    arguments, and they can send back a result called a return value.

    Look at the three functions defined in this program before the
    main loop. They are introduced in order of increasing complexity:

  def clear_leds():              # No arguments, no return value
  def indicate_attempts(count):  # One argument, no return value
  def read_keypad():             # No arguments, returns a value

    Identify at least five other function calls already in this
    program - including 'random.randint(2, 5)' and calls to board
    module functions. For each one, note whether it receives
    arguments, returns a value, or both. Notice that 'random.randint()'
    is itself a function that takes two arguments and returns a value
    - the random number it generates.

2.  The 'def' keyword defines a function. The name that follows
    becomes the way to call it. Everything indented beneath the
    'def' line is the function body - the code that runs each time
    the function is called.

    Look at 'clear_leds()':

  def clear_leds():
    # Turn off all four LEDs.
    beaper.LED2.value(0)
    beaper.LED3.value(0)
    beaper.LED4.value(0)
    beaper.LED5.value(0)

    This function takes no arguments and returns no value - it simply
    performs a task. In MicroPython, a function that returns no value
    is sometimes called a void function (borrowing a term from C).

    Count how many times 'clear_leds()' is called in the main
    program. How many lines of code would the program contain if
    each call were replaced with the four individual LED statements?
    What does this tell you about the value of functions for
    reducing repetition?

3.  The 'indicate_attempts(count)' function receives one argument.
    The name 'count' in the function definition is called a parameter
    - it is a variable that holds whatever value is passed in when
    the function is called.

    Look at how 'count' is used inside the function body:

  def indicate_attempts(count):
    beaper.LED2.value(count >= 1)
    beaper.LED3.value(count >= 2)
    beaper.LED4.value(count >= 3)
    beaper.LED5.value(count >= 4)

    When the program starts a new round and calls
    'indicate_attempts(attempts)' with attempts equal to 4, all
    four LEDs light up. As wrong guesses reduce attempts, the
    function is called again and LEDs extinguish one by one.

    Trace through the function for each possible value of count
    (0 through 4) and describe which LEDs would be lit. What would
    the LEDs show if count were somehow 5 or greater? Verify your
    predictions by running the program.

    The parameter 'count' is a local variable - it only exists
    inside 'indicate_attempts()' and disappears when the function
    returns. What would happen if you tried to use 'count' in the
    main program loop? Try it and observe the result.

4.  The 'read_keypad()' function uses the 'return' statement to
    send a value back to the code that called it:

  key = read_keypad()

    After this line, 'key' holds whatever value 'read_keypad()'
    returned - the number of the button that was pressed (2, 3,
    4, or 5). The return value can then be used like any other
    variable.

    Look at the two while loops inside 'read_keypad()'. The first
    loop waits until a button is pressed and records which one.
    The second loop waits until all buttons are released before
    returning. Why are both loops necessary? What would happen if
    the second loop were removed and the function returned 'key'
    immediately after detecting a press? Think about how the main
    loop would behave on the very next call to 'read_keypad()'.

5.  Functions must be defined before they are called. In this
    program, all three functions are defined in the 'Program
    Functions' section, before the main loop that calls them.

    What would happen if you moved the 'def clear_leds():' block
    to after the main 'while True:' loop? Try it and observe the
    error message. What does the error tell you about how
    MicroPython processes a program file?

6.  The 'indicate_attempts()' function is a compact example of
    using a parameter as meaningful data rather than just a count.
    Each comparison in the function body produces True or False,
    which directly sets the LED state - the same technique used
    in the Part 2 and Part 3 loops in Activity 7.

    Rewrite 'indicate_attempts()' using four 'if'/'else' blocks
    instead of the comparison approach, and verify that the program
    still behaves identically. Which version do you find easier to
    read and why? What does this tell you about the relationship
    between a function's internal implementation and its external
    behaviour?

7.  The 'indicate_attempts()' function currently sets the LEDs
    directly, but the caller is responsible for turning them off
    at the right moment. A tidier design would have
    'indicate_attempts()' call 'clear_leds()' as its first action,
    so it always starts from a known state before lighting the
    appropriate LEDs.

    A function calling another function is called function
    composition - complex behaviour built from simpler named pieces.
    Modify 'indicate_attempts()' to call 'clear_leds()' as its
    first action, then remove the separate 'clear_leds()' call
    from the wrong-guess branch in the main loop. The program
    should behave identically.

    What does this change tell you about how behaviour can be
    moved into functions without affecting the visible result?
    What is the advantage of 'indicate_attempts()' managing its
    own cleanup rather than relying on the caller to do it?

8.  Open BEAPER_Nano.py and find the definition of the 'tone()'
    function. Read through its body carefully.

    What arguments does 'tone()' accept? Are any of them optional?
    How does the function use its arguments internally? Does it
    call any other functions - and if so, which ones?

    The optional 'duration' argument uses a Python feature called
    a default parameter value. When 'tone()' is called without a
    duration - as in 'beaper.tone(4000)' - the parameter takes
    its default value instead of requiring the caller to provide
    one. You have been using this feature throughout the curriculum
    without knowing it had a name.

    Look at 'noTone()' in the same file. Under what circumstances
    does 'tone()' call 'noTone()'? What would happen if you called
    'beaper.tone(440)' without a duration - would the tone ever
    stop on its own?

    This exercise is a preview of how the board module is
    structured - every helper function you have relied on is
    defined in exactly this way, using the same 'def', parameters,
    and return patterns you have been learning in this activity.
    You now have the tools to read and understand all of it.


Programming Activities

    As you write your programs, write a comment above each function
    definition describing what it does, what arguments it expects,
    and what it returns (if anything). This style of documentation
    is the standard way to communicate a function's purpose to
    anyone reading your code - including yourself later.

1.  Add a 'win_signal()' function and a 'lose_signal()' function
    to the starter program, each encapsulating the tone and LED
    behaviour for their respective outcomes. Replace the inline
    win and lose code in the main loop with calls to these functions.

    After this change, the inner 'while attempts > 0:' loop should
    read almost like plain English: get a key, check if it matches,
    call the appropriate signal function, update the display. How
    does moving the signal behaviour into named functions change
    the readability of the main loop?

2.  Write a 'flash_led(led, times)' function that flashes a
    specified LED a specified number of times with a short delay
    between each flash. The first argument should be an LED pin
    object (such as beaper.LED2) and the second should be the
    number of flashes.

    Use this function to create distinct win and lose signals
    that use different LEDs and flash counts, replacing the
    simpler tone-only signals from Programming Activity 1.

    This demonstrates that a single well-written function can
    produce several distinct outputs depending on its arguments.

3.  Modify 'read_keypad()' to also play a brief confirmation tone
    when a button press is detected - before the release loop.
    Each button should play a different frequency so the player
    can identify which button was pressed by sound alone:
    SW2=500Hz, SW3=750Hz, SW4=1000Hz, SW5=1250Hz (or choose
    your own frequencies).

    This adds behaviour to the function without changing its
    interface - the calling code still uses 'key = read_keypad()'
    and receives the same return values. What does this tell you
    about the advantage of encapsulating behaviour in functions?

4.  Write a 'choose_target()' function that uses 'random.randint()'
    to return a randomly chosen button number (2, 3, 4, or 5).
    Replace the direct 'random.randint(2, 5)' call in the main
    loop with a call to this new function.

    This may seem like a small change for little gain, but consider:
    if you later wanted to change the selection logic - weighting
    certain buttons more heavily, or avoiding the same button twice
    in a row - you would only need to change 'choose_target()',
    not every place in the program that picks a target. This is
    called encapsulating the selection logic, and it is one of the
    main reasons functions are used even for short tasks.

5.  Refactor the Activity 6 combination lock into a cleaner version
    using the three functions from this activity. The combination
    lock requires the player to press SW2, SW3, SW4, and SW5 in
    a specific order. Use:

    - 'read_keypad()' to get each button press
    - 'indicate_attempts(step)' to light LEDs showing how many
      steps of the sequence have been completed correctly
    - 'clear_leds()' to reset the display on a wrong press

    The main program logic should fit in around 15 lines. Compare
    this version with your Activity 6 combination lock program.
    What specifically did moving code into functions change about
    the structure and readability of the main loop?

    As an extension, add a second parameter to 'indicate_attempts()'
    so it can accept 'indicate_attempts(step, success)' where
    'success' is True or False. When success is False, flash the
    lit LEDs briefly before clearing, rather than clearing
    immediately. How does adding a second parameter change the
    function's interface, and what changes are needed wherever
    the function is called?

"""
