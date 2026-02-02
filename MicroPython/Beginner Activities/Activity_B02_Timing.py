"""
================================================================================
Beginner Activity 2: Timing (Blocking) [Activity_B02_Timing.py]
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
  beaper.LED2.value(1)
  beaper.LED5.value(0)
  time.sleep(0.5)        # wait 0.5 seconds

  beaper.LED2.value(0)
  beaper.LED5.value(1)
  time.sleep(0.5)        # wait 0.5 seconds
  

"""
Program Analysis Activities

1.  In the previous activity you learned that BEAPER_Nano.py is a 
    board module file that defines all of BEAPER Nano's I/O devices.
    (You can open it in the editor and view its contents!) So, what
    does the 'import BEAPER_Nano as beaper' statement actually do?

    Modules like BEAPER_Nano.py consist of ordinary MicroPython
    program code, and the import statement simply includes that code
    into the current program – but invisibly. The contents of the file
    won't appear in the program editor, but will still be accessible
    by the program that includes them.

    The 'import time' statement in this program does the same thing – 
    it imports the functions built into MicroPython's time module into
    our program. We can't open the time module to view its functions
    as we can with the BEAPER_Nano.py board module, but we can look up
    the time module's functions in the MicroPython documentation, here:
    
    https://docs.micropython.org/en/latest/

    Open the MicroPython documentation website in a browswer and search
    for 'time'. Then, click the link 'time - time related functions' – 
    or, use this URL to navigate there directly:
    
    https://docs.micropython.org/en/latest/library/time.html#module-time )
    
    Glancing through the time module's functions, you will see that
    there are a number of different time functions available, including
    the 'time.sleep()' function called by this program.
    
    It's important to recognize that whenever a dot '.' appears in a
    MicroPython program statement, it simply means that it's using
    some function or class or method in a module (we'll learn more
    about all of these specific terms in later actvities). For now,
    just realize that:
    
    beaper.LED2.value(1) - sets the value of LED2 in the beaper module
    
    and
    
    time.sleep(0.5) - sets the duration of sleep in the time module.
    
    What do you think will happen if a program tries to use the sleep()
    function without importing the time module first? Comment-out or
    remove the 'import time' statement from your program and try to
    run it. What happens?
    
2.  Ensure that the 'import time' statement is put back into the
    program code and run the program if you haven't done so already!
    Ooh, look, we can make lights blink by telling the microcontroller
    to sleep for a short time between changing its LED values!
    
    Look up the time.sleep() function in the MicroPython documentation.
    Is it working as expected? Does the microcontroller sleep for 0.5
    seconds after turning one of the LEDs on or off?
    
    There is another way to accomplish the same thing by using the
    'time.sleep_ms()' function. Replace the time.sleep(0.5) function
    in your program with:
    
    time.sleep_ms(500)
    
    and run the program again. The result should be exactly the same.
    Is it? Is there any advantage to using time.sleep_ms() function
    instead of the time.sleep() function?
    
3.  Stop the program from running. When the program stops, do all of
    the LEDs turn off, including the Arduino Nano ESP32's built-in LED?

    When stopping future programs controlling different kinds of
    output devices, what might we need to be careful of? 
    
4.  'sleep_us()' is another sleep function that delays for the number
    of microseconds provided. While microsecond delays are much too
    short to see, they can be used to make other signals including
    sound waves! Some piezo speakers make a sound when powered on,
    but the speaker used on BEAPER Nano needs to be rapidly turned on
    and off to create audible frequencies. Let's try it!

    First, add this line between the import statements and the main
    'while True:' loop:

speaker = Pin(beaper.LS1_PIN, Pin.OUT)

    This statement re-defines the circuit's LS1 connection as a pin
    output called 'speaker'. Next, add this new 'while True:' function
    above the existing while True: loop in the program:

while True:
  speaker.value(1)
  time.sleep_us(1136)
  speaker.value(0)
  time.sleep_us(1136)

    Run the program. It should be producing a 440Hz tone because the
    two time delays between changing the value of the speaker output
    pin will add up to create the 2272 microsecond time period of a
    440Hz sound wave.
    
    Hey, are the LEDs still flashing while the sound is playing? Stop
    the program to stop the tone, and then ponder what the program is
    actually doing. Explain what is happening and why you think the
    LEDs are no longer blinking.

5.  There is an easier and more flexible way way to produce sound
    frequencies by using the BEAPER_Nano.py board module's tone() and
    noTone() functions. 

    Remove both the 'speaker' definition statement and the entire
    'while True:' loop added in the previous activity step. Next,
    replace the sleep() functions in the existing loop with the
    tone() functions as shown below:

while True:
  beaper.LED2.value(1)
  beaper.LED5.value(0)
  beaper.tone(440, 500)

  beaper.LED2.value(0)
  beaper.LED5.value(1)
  beaper.tone(523, 500)

    The first parameter in the tone function is the frequency in Hz,
    and the second is the tone duration in milliseconds. So, the
    statement 'beaper.tone(440, 500)' plays a 440Hz tone for 500ms.

    When you stop the program, the tone may continue playing. Press
    the reset button to stop the tone from playing.


Programming Activities

1.  Simulate a machine's start-up and operation by lighting one LED
    for two seconds after the program starts. After the two second
    delay finishes, have the program blink a second LED at a 1Hz rate.

2.  Create an animated light pattern using the four on-board LEDs. It
    could light and extinguish the four LEDs in sequence, or chase a
    lit LED across the four positions in sequence or back-and-forth,
    or make a more unique or artistic pattern - it's up to you!

3.  Really old computers used lights to show binary values. Try to
    simulate a binary count on BEAPER Nano's LEDs.
    
4.  Create a musical sequence of tones that repeats after a pause. 
    
"""
