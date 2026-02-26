/* ================================================================================
Beginner Activity 2: Timing (Blocking) [Activity-B02-Timing]
February 26, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPERNano.h header file
=================================================================================*/
// IMPORTANT: Make sure that BEAPERNano.h is accessible as a tab in this project.
#include "BEAPERNano.h"   // Define BEAPER Nano I/O devices

// ---------------------------------------------------------------
// Setup runs once at power-up
// ---------------------------------------------------------------
void setup()
{
    // Configure Arduino Nano ESP32 status LED as output
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, HIGH);    // Status LED on

    // Configure BEAPER Nano LEDs as outputs
    pinMode(LED2, OUTPUT);
    pinMode(LED3, OUTPUT);
    pinMode(LED4, OUTPUT);
    pinMode(LED5, OUTPUT);
}

// ---------------------------------------------------------------
// Loop runs forever
// ---------------------------------------------------------------
void loop()
{
    digitalWrite(LED2, HIGH);
    digitalWrite(LED5, LOW);
    delay(500);                 // Wait 0.5 seconds

    digitalWrite(LED2, LOW);
    digitalWrite(LED5, HIGH);
    delay(500);                 // Wait 0.5 seconds
}


/*
Guided Exploration

Timing is fundamental to microcontroller programs. Without delays, a
microcontroller executes instructions in microseconds — far too fast
for people to perceive. The time between actions is what makes blinking
LEDs, musical tones, and responsive controls possible, and managing
that time well is one of the most important skills in microcontroller
programming.

1.  In Activity 1 you learned that the BEAPERNano.h header file
    defines all of BEAPER Nano's I/O devices. (You can open the file
    in the editor and view its contents!)

    If the header file describes the hardware, is there something
    similar that describes the software functions? How can we know,
    for example, that 'delay(500)' really delays for 0.5 seconds?

    Each Arduino software function is described in the Arduino
    Language Reference, found online here:

    https://docs.arduino.cc/language-reference/

    Open the Language Reference in a browser and look up the delay()
    function, or navigate directly to it using this URL:

    https://docs.arduino.cc/language-reference/en/functions/time/delay/

    Whenever you see a statement with brackets in an Arduino program
    — such as 'digitalWrite(LED2, HIGH)' or 'delay(500)' — it is
    calling an Arduino software function that is documented in the
    Language Reference. Getting comfortable finding and reading
    documentation like this is an important skill.

2.  Read both the Description and the Notes and Warnings sections of
    the delay() documentation. What does delay() actually do? What
    is the microcontroller doing while delay() is running? Why could
    this be a problem for some programs?

3.  Arduino also has a 'delayMicroseconds()' function. Look it up
    in the Language Reference. Would it be a good idea to use it to
    replace the 0.5 second delay in this program? Why or why not?

4.  What do you think would happen if both 'delay(500)' statements
    in the program were replaced with 'delayMicroseconds(500)'?
    Try it! Run the program and describe what the LEDs are doing.

5.  While microsecond delays are much too short to see, they can be
    used to generate signals at audible frequencies — including sound
    waves! Some piezo speakers make a sound when powered on, but the
    speaker on BEAPER Nano needs to be rapidly switched on and off to
    create sound. Let's try it!

    First, add this statement to the setup() function to configure
    the pin connected to piezo speaker LS1 as an output:

    pinMode(LS1, OUTPUT);

    Next, replace the entire loop() function with this one:

void loop()
{
    digitalWrite(LS1, HIGH);
    delayMicroseconds(1136);
    digitalWrite(LS1, LOW);
    delayMicroseconds(1136);
}

    Run the program. It should produce a 440Hz tone. Each half-cycle
    of the sound wave lasts 1136 microseconds, so the full period is
    1136 + 1136 = 2272 microseconds. Since frequency = 1 ÷ period,
    that gives 1,000,000 ÷ 2272 ≈ 440Hz — the musical note A4.

    Are the LEDs still flashing while the sound is playing? Stop the
    program to stop the tone, then think about what the program is
    actually doing. Explain what is happening and why the LEDs are
    no longer blinking.

6.  There is an easier and more flexible way to produce tones using
    Arduino's built-in tone() and noTone() functions.

    Replace the loop() function added in GE5 with this one, which
    restores the LED blinking and adds tone() calls:

void loop()
{
    digitalWrite(LED2, HIGH);
    digitalWrite(LED5, LOW);
    tone(LS1, 440, 500);
    delay(500);                 // Wait 0.5 seconds

    digitalWrite(LED2, LOW);
    digitalWrite(LED5, HIGH);
    tone(LS1, 523, 500);
    delay(500);                 // Wait 0.5 seconds
}

    Look up the tone() function in the Language Reference. What do
    its three parameters represent? Notice that tone() specifies a
    duration — do you think the separate delay() call is still
    needed, or does tone() already handle the timing? Try removing
    one of the delay() calls to find out.

    You can call noTone(LS1) at any point to stop a tone immediately.
    When you stop the program, the tone may continue playing because
    it runs on a hardware timer that keeps going independently of the
    program loop. Press the reset button, or call noTone(), to
    silence it.


Extension Activities

Notice that this program has two distinct sections: statements inside
setup() that run once at power-up, followed by statements inside
loop() that repeat forever. This setup-then-loop pattern appears in
virtually every Arduino program you will write — use setup() for
anything that should happen only once at startup, such as configuring
pins and turning on status indicators, and loop() for everything that
should keep running.

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

*/
