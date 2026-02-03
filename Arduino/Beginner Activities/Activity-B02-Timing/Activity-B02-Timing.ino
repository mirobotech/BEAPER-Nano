/* ================================================================================
Beginner Activity 2: Timing (Blocking) [Activity-B02-Timing]
February 3, 2026

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

    // Configure ARPS2 LEDs as outputs
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
Program Analysis Activities

1.  In the previous activity you learned that the BEAPERNano.h
    header file defines all of BEAPER Nano's I/O devices. (You
    can open the file in the editor and view its contents!)
    
    So, if BEAPERNano.h describes the hardware, is there a
    similar file that describes the software? How can we know,
    for example, that the 'delay(500);' statement in the program
    above really delays for 0.5 seconds?

    Each one of Arduino's software functions is described in 
    the Arduino Language Reference, found online here:

    https://docs.arduino.cc/language-reference/

    Open the Language Reference website in a browser and scroll
    down the page to find the 'Time' functions. In the 'Time' 
    section, click on 'delay()' to find out more about the
    delay function, or use this URL to navigate there directly:

    https://docs.arduino.cc/language-reference/en/functions/time/delay/

    Whenever you see an Arduino program statement that includes
    brackets, such as 'digitalWrite(LED2, HIGH);' or 'delay(500);',
    you should understand that (for these first few activities at
    least) these statements are Arduino software functions that
    are described in the Language Reference. This makes it easy
    to find out what they do and how they work.

    Take a look at both the Description, and the Notes and Warnings
    section of the delay() function's documentation. What does the
    delay() function actually do? What does the micorcontroller do
    while it's executing the delay() function? Why could this be
    a problem for some programs?
    
2.  Arduino also has a delay function called 'delayMicroseconds()'.

    Look up the delayMicroseconds() function in the Language
    Reference. Do you think it would be a good idea to use to
    replace the 0.5 second delay in this program? Why or why not?

3.  What do you think would happen if the 'delay(500);' statements
    in the program were replaced with 'delayMicroseconds(500);'
    statements? Try it! Change both delay functions in the
    program to delayMicroseconds(500) and describe what run the
    program. Describe what the LEDs are doing.
    
4.  While microsecond delays are much too short to see, they can
    be used to make other signals including sound waves! Some
    piezo speakers make a sound when powered on, but the speaker
    used on BEAPER Nano needs to be rapidly turned on and off to
    create audible frequencies. Let's try it!

    First, add this statement to the setup() function:

    pinMode(LS1, OUTPUT);

    This statement dewfines the microcontroller's pin connecting
    to piezo speaker LS1 as an output. Next, replace the entire
    loop() function in the existing program with the new loop
    function, below:

void loop()
{
    digitalWrite(LS1, HIGH);
    delayMicroseconds(1136);
    digitalWrite(LS1, LOW);
    delayMicroseconds(1136);
}

    Run the program. It should produce a 440Hz tone because the
    two time delays in between changing the value of the speaker
    output pin will add up to create the 2272 microsecond time 
    period of a 440Hz sound wave.

5.  There is an easier and more flexible way way to produce sound
    frequencies by using Arduino's tone() and  noTone() functions. 

    Remove all of the loop code added in the previous activity
    step. Next, replace it with this one, which is very much like
    the original loop function, but now adds a tone() function
    before each delay() function:

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

    Look up the tone() function in the Arduino Language Reference.

    What do the three parameters inside its brackets represent?


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
    
*/