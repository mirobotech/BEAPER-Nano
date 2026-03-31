"""
================================================================================
Beginner Activity 2: Timing (Blocking) [Activity_B02_Timing.py]
March 30, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPER_Nano.py board module file.
================================================================================
"""
# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32
import BEAPER_Nano as beaper  # Set up BEAPER Nano I/O

import time

beaper.nano_led_on()

# Main loop - code indented below while True: repeats forever
while True:
  beaper.LED2.value(1)
  beaper.LED5.value(0)
  time.sleep(0.5)        # wait 0.5 seconds

  beaper.LED2.value(0)
  beaper.LED5.value(1)
  time.sleep(0.5)        # wait 0.5 seconds
  

"""
Guided Exploration

Timing is fundamental to microcontroller programs. Without delays, a
microcontroller executes instructions in microseconds — far too fast
for people to perceive. The time between actions is what makes blinking
LEDs, musical tones, and responsive controls possible, and managing
that time well is one of the most important skills in microcontroller
programming.

1.  Activity 1 imported the BEAPER_Nano.py board module to make
    BEAPER Nano's I/O devices available to this program:

import BEAPER_Nano as beaper  # Set up BEAPER Nano I/O

    If you open the BEAPER_Nano.py module in the editor, you'll see
    that it consists of ordinary MicroPython program code. The import
    statement includes all of its code into the current program — the
    contents of BEAPER_Nano.py won't be visible in this program's
    editor window, but everything it defines will be fully accessible.

    The 'import time' statement works the same way — it imports the
    functions built into MicroPython's time module into this program.
    Unlike the board module, we can't open the time module to view its
    source code, but we can look up its functions in the MicroPython
    documentation. We'll do that in GE2.

    It's useful to recognize that whenever a dot '.' appears in a
    MicroPython statement, it means the program is using something
    defined in a module. For now, just notice that:

beaper.LED2.value(1)  - sets the value of LED2 in the beaper module

time.sleep(0.5)       - calls the sleep function in the time module

    We'll explore modules, classes, and methods in more detail in
    later activities.

    What do you think will happen if a program tries to use sleep()
    without importing the time module first? Comment-out the
    'import time' statement and try to run the program. What happens?
    Restore the statement before moving on.

2.  Open the MicroPython documentation in a browser using this URL:

    https://docs.micropython.org/en/latest/library/time.html#module-time

    Look up the time.sleep() function. Read its description — what
    does the parameter passed to sleep() represent? What units does
    it use?

    Glancing through the page, you'll also see the other time
    functions available in MicroPython, including sleep_ms() and
    sleep_us(), which we'll use shortly. Getting comfortable finding
    and reading documentation like this is an important skill —
    most MicroPython modules and functions are documented here.

3.  Run the program if you haven't done so already. The LEDs should
    be alternating on and off with a short delay between each change.
    How long does each LED stay on? Does it match the delay value in
    the code?

    There is another way to accomplish the same result using the
    'time.sleep_ms()' function. Replace both time.sleep(0.5) calls
    in your program with:

    time.sleep_ms(500)

    and run the program again. The result should be exactly the same.
    Is it? Expressing the delay as an integer number of milliseconds
    rather than a decimal number of seconds is less error-prone —
    can you think of a mistake that would be easy to make with
    time.sleep() that couldn't happen with time.sleep_ms()?

4.  Stop the program from running. When the program stops, do all of
    the LEDs turn off, including the Arduino Nano ESP32's built-in LED?

    When stopping future programs that control different kinds of
    output devices, what might we need to be careful of?

5.  'sleep_us()' delays for the number of microseconds provided.
    While microsecond delays are much too short to see, they can be
    used to generate signals at audible frequencies — including sound
    waves! Some piezo speakers make a sound when powered on, but the
    speaker on BEAPER Nano needs to be rapidly switched on and off to
    create sound. Let's try it!

    First, add these two lines between the import statements and the
    main 'while True:' loop. The first imports Pin from the machine
    module, and the second configures the circuit's LS1 connection
    as a pin output called 'speaker':

from machine import Pin
speaker = Pin(beaper.LS1_PIN, Pin.OUT)

    Next, add this new 'while True:' loop above the existing one:

while True:
  speaker.value(1)
  time.sleep_us(1136)
  speaker.value(0)
  time.sleep_us(1136)

    Run the program. It should produce a 440Hz tone. Each half-cycle
    of the sound wave lasts 1136 microseconds, so the full period is
    1136 + 1136 = 2272 microseconds. Since frequency = 1 ÷ period,
    that gives 1,000,000 ÷ 2272 ≈ 440Hz — the musical note A4.

    Are the LEDs still flashing while the sound is playing? Stop the
    program to stop the tone, then think about what the program is
    actually doing. Explain what is happening and why the LEDs are
    no longer blinking.

6.  There is an easier and more flexible way to produce tones using
    the BEAPER_Nano.py board module's tone() and noTone() functions.

    Remove the 'from machine import Pin' statement, the 'speaker'
    definition, and the entire 'while True:' loop added in GE5.
    Then replace the sleep() calls in the original loop as shown:

while True:
  beaper.LED2.value(1)
  beaper.LED5.value(0)
  beaper.tone(440, 500)

  beaper.LED2.value(0)
  beaper.LED5.value(1)
  beaper.tone(523, 500)

    The first parameter in tone() is the frequency in Hz, and the
    second is the duration in milliseconds. So, 'beaper.tone(440, 500)'
    plays a 440Hz tone for 500ms. Notice that tone() also acts as a
    delay — the program waits for the tone to finish before moving to
    the next statement, just as sleep() did before.

    You can also call 'beaper.noTone()' at any point to stop a tone
    immediately. When you stop the program, the tone may continue
    playing because it runs on a hardware timer that keeps going
    independently of the program loop. Press the reset button, or
    call noTone(), to silence it.


Extension Activities

Notice that this program has two distinct sections: statements that
run once when the program starts, followed by statements inside the
'while True:' loop that repeat forever. This setup-then-loop pattern
appears in virtually every microcontroller program you will write —
use the setup section for anything that should happen only once at
startup, and the loop for everything that should keep running.

1.  Simulate a machine's start-up and operation by lighting one LED
    for two seconds after the program starts. After the two-second
    delay, have the program blink a second LED once per second.

2.  Create an animated light pattern using the four on-board LEDs. It
    could light and extinguish the four LEDs in sequence, chase a lit
    LED across the four positions or back-and-forth, or make a more
    unique or artistic pattern — it's up to you!

3.  Really old computers used lights to show binary values. Try to
    simulate a binary counting sequence using BEAPER Nano's LEDs.

4.  Create a musical sequence of tones or a short song that repeats
    after a short pause.

"""