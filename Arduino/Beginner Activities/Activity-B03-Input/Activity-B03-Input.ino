/* ================================================================================
Beginner Activity 3: Input [Activity-B03-Input]
February 11, 2026

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

    // Configure BEAPER Nano pushbuttons as inputs
    pinMode(SW2, INPUT_PULLUP);
    pinMode(SW3, INPUT_PULLUP);
    pinMode(SW4, INPUT_PULLUP);
    pinMode(SW5, INPUT_PULLUP);
}

// ---------------------------------------------------------------
// Loop runs forever
// ---------------------------------------------------------------
void loop()
{
    // Momentary button SW2
    if (digitalRead(SW2) == LOW)
    {
        digitalWrite(LED2, HIGH);
    }
    else
    {
        digitalWrite(LED2, LOW);
    }

    // Start a pattern
    if (digitalRead(SW5) == LOW)
    {
        digitalWrite(LED2, HIGH);
        delay(200);
        digitalWrite(LED3, HIGH);
        delay(200);
        digitalWrite(LED4, HIGH);
        delay(200);
        digitalWrite(LED5, HIGH);
        delay(200);
        digitalWrite(LED2, LOW);
        delay(200);
        digitalWrite(LED3, LOW);
        delay(200);
        digitalWrite(LED4, LOW);
        delay(200);
        digitalWrite(LED5, LOW);
        delay(200);
    }

    delay(20);  // Short delay for button debouncing
}


/*
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

    What value do you expect digitalRead(SW2) to return when SW2 is
    not pressed? What about when SW2 is pressed?

    Arduino's digitalRead() function is used to read the value of
    I/O pins, and it reads pins as being either HIGH or LOW (exactly
    like the values set using the digitalWrite() function). Let's
    look at the if-else structure in the program:

    // Momentary button SW2
    if (digitalRead(SW2) == LOW)
    {
        digitalWrite(LED2, HIGH);
    }
    else
    {
        digitalWrite(LED2, LOW);
    }

    The 'if' statement, known as an 'if condition', employs a similar
    structure to that used by the main loop(). That is, the program
    statements inside the if block will execute whenever the if
    condition is true. And, in this case the condition will be true
    when the value of the SW2 pin is equal to LOW (two equals signs
    are used to check and compare values, as opposed to one equals
    sign being used to set a value).

    This if condition also includes a complementary 'else' statement,
    which will logically be the opposite of if. When if is true, else
    will be false, and when if is false, else will become true.

    Looking at SW2's if-else condition, explain the program flow when
    SW2 is not pressed, and when SW2 is pressed. Which digitalWrite()
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

    if (digitalRead(SW3) == LOW)
    {
        tone(LS1, 440);
    }
    else
    {
        noTone(LS1);
    }

    What is the advantage of using an 'if-else' structure instead of
    using two separate if conditions - one to start the tone, and a
    second to stop the tone - to do the same thing?

4.  Let's try using a combination of two pushbuttons to turn on one
    LED. One way to accomplish this is by nesting one if-else
    condition inside another, like this:

    if (digitalRead(SW3) == LOW)
    {
        if (digitalRead(SW4) == LOW)
        {
            digitalWrite(LED3, HIGH);
        }
        else
        {
            digitalWrite(LED3, LOW);
        }
    }
    else
    {
        digitalWrite(LED3, LOW);
    }
    
    The nested if-else logic enables SW4 to turn the LED only if both
    it and SW3 are pressed. Try the code in your program to verify
    that it works as expected.

5.  A better way to use two buttons to turn on one LED is by using
    an '&&' (AND) logical operator in the if condition, like this:

    if (digitalRead(SW3) == LOW && digitalRead(SW4) == LOW)
    {
        digitalWrite(LED3, HIGH);
    }
    else
    {
        digitalWrite(LED3, LOW);
    }

    Try this code in your program to verify that it works. In what
    ways is this solution better than using nested if-else conditions?
    
6.  The logical '||' (OR) operator can also be used in conditional
    expressions. Describe when the LED would be lit if the SW3
    and SW4 pushbutton inputs in the activity were combined using a
    logical OR operator instead of the AND operator in the condition.


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

*/
