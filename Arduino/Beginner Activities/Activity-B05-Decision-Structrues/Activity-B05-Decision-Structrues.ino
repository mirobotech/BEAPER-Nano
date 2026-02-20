/* ================================================================================
Beginner Activity 5: Decision Structures [Activity-B05-Decision-Structures]
February 19, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPERNano.h header file
=================================================================================*/
// IMPORTANT: Make sure that BEAPERNano.h is accessible as a tab in this project.
#include "BEAPERNano.h"   // Define BEAPER Nano I/O devices

// ---- Program Constants ----------------
const int MAX_COUNT = 50;

// ---- Program Variables ----------------
bool SW2_pressed;
bool SW3_pressed;
bool SW4_pressed;
bool SW5_pressed;
int SW3_presses = 0;
int SW4_presses = 0;
bool SW3_last = false;
bool SW4_last = false;

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

    Serial.begin(9600);     // Initialize serial output for debugging
    while (!Serial);        // Wait for the serial port to start
}

void loop()
{
    // Read pushbuttons
    SW2_pressed = (digitalRead(SW2) == LOW);
    SW3_pressed = (digitalRead(SW3) == LOW);
    SW4_pressed = (digitalRead(SW4) == LOW);
    SW5_pressed = (digitalRead(SW5) == LOW);

    if (SW3_pressed)
    {
        digitalWrite(LED2, HIGH);
    }
    else
    {
        digitalWrite(LED2, LOW);
    }

    delay(20);  // Short delay for button debouncing
}


/*
Program Analysis Activities

1.  This program's 'switch pressed' variables (e.g. SW3_pressed) use
    true or false (Boolean) logic states. Logic states allow multiple
    switch inputs to be combined using the Boolean logical operators
    '&&' (AND), '||' (OR), and '!' (NOT). For example, changing the
    conditional expression in the program to:

    if (SW3_pressed && SW4_pressed)

    ... will light LED2 only when both SW3 and SW4 are pressed at the
    same time. Modify the if condition in your program to match this
    example and verify its operation.

2.  Replace the '&&' operator in the if condition with '||' and run
    the program again. Does it work the way you would expect it to?

3.  It's just as easy to invert an input to its opposite state using
    the '!' (NOT) logical operator. Predict how you think this
    conditional expression will act:

    if (SW3_pressed && !SW4_pressed)

    Try the condition in your program to verify your prediction.

4.  Let's make the program count the number of times SW3 is pressed.
    Start by reverting the if condition back to only reading the
    state of pushbutton SW3. Next, add the 'SW3_presses++' increment
    operation to accumulate SW3 presses (it performs the same function
    as 'SW3_presses = SW3_presses + 1', but in a shorter statement):

    if (SW3_pressed)
    {
        digitalWrite(LED2, HIGH);
        SW3_presses++;
    }
    else
    {
        digitalWrite(LED2, LOW);
    }

    Next, add this set of if/else if conditions to display the number
    of times SW3 has been pressed using the LEDs:

    // Light LEDs for different numbers of presses
    if (SW3_presses >= 1)
    {
        digitalWrite(LED3, HIGH);
    }
    else if (SW3_presses >= 10)
    {
        digitalWrite(LED4, HIGH);
    }
    else if (SW3_presses >= MAX_COUNT)
    {
        digitalWrite(LED5, HIGH);
    }

    How do you think it will work? Run the program and try it. Each
    press of SW3 should light LED2 momentarily, and LED3 should remain
    lit after the first press. Does it? Does LED4 turn on after ten
    presses? Can you explain why?

5.  Previous programs have used the '==' (equal to) conditional
    operator to check if two values are the same. This program uses
    the '>=' (greater than or equal to) conditional operator to check
    if the value of SW3_presses is the same or larger than three
    different fixed numbers.

    In Arduino C, any of these six conditional operators can be
    used in if conditions:

    ==  equal to
    !=  not equal to
    <   less than
    >   greater than
    <=  less than or equal to
    >=  greater than or equal to

    The other new feature introduced in the previous step is the
    if/else if structure - a chain of multiple conditional decisions.
    Starting with the first if, each condition is evaluated in turn
    until the first true condition is found. Once a true condition is
    found, its code runs and the rest of the chain is skipped. If
    none of the conditions are true, the entire chain is bypassed.

    With a better understanding of how the chain works, can you
    explain why LED4 didn't turn on after ten presses in the previous
    step? Re-arrange the conditions in the correct order to light LED3
    after the first press, LED4 after 10 presses, and LED5 after the
    maximum number of presses:

    // Light LEDs for different numbers of presses
    if (SW3_presses >= MAX_COUNT)
    {
        digitalWrite(LED5, HIGH);
    }
    else if (SW3_presses >= 10)
    {
        digitalWrite(LED4, HIGH);
    }
    else if (SW3_presses >= 1)
    {
        digitalWrite(LED3, HIGH);
    }

    Also add a block of code to reset the SW3_presses count and turn
    off the LEDs when SW5 is pressed:

    // Reset the count
    if (SW5_pressed)
    {
        SW3_presses = 0;
        digitalWrite(LED3, LOW);
        digitalWrite(LED4, LOW);
        digitalWrite(LED5, LOW);
    }

    Try these new code blocks in your program. To see exactly what
    is happening, add a Serial.print() statement inside the
    'if (SW3_pressed)' block to display the count in the Serial
    Monitor:

    if (SW3_pressed)
    {
        digitalWrite(LED2, HIGH);
        SW3_presses++;
        Serial.print("SW3_presses: ");
        Serial.println(SW3_presses);
    }

    Watch the Serial Monitor output while pressing and holding SW3.
    How quickly does the count increase? Does this help explain the
    LED behaviour you observed?

6.  You may have noticed in the previous step that the counter
    increases very quickly - much faster than you're actually
    pressing the button. This is because the button state is read
    every loop, so holding SW3 for even a fraction of a second will
    register dozens of counts.

    The solution is edge detection - only counting a new press when
    the button transitions from not-pressed to pressed. The program
    already declares SW3_last for exactly this purpose. Here is how
    to use it:

    // Detect a new SW3 press (not-pressed to pressed transition)
    if (SW3_pressed && !SW3_last)
    {
        SW3_presses++;
        digitalWrite(LED2, HIGH);
    }
    else
    {
        digitalWrite(LED2, LOW);
    }

    The key is that SW3_last must be updated at the end of each loop
    cycle, after all the button logic has run, so it correctly holds
    the previous loop's button state:

    // Save button states for next loop
    SW3_last = SW3_pressed;

    Add both of these changes to your program. The Serial.print()
    statement from the previous step will now show exactly one count
    per press in the Serial Monitor, regardless of how long the button
    is held. This is a good example of using serial output to verify
    that a fix is working correctly - once you're satisfied, the
    Serial.print() calls can be removed or commented out.

    The SW4_last variable is also already declared for the same
    purpose. Can you add edge detection for SW4 as well?


Programming Activities

1.  Modify the press-counting program from the analysis activities
    so that pressing SW3 increases the count and pressing SW4
    decreases it, with the count clamped so that it can never go
    below zero or above MAX_COUNT. Use the LEDs to show four ranges
    of the count value (off, low, medium, high).

2.  Create a program that uses SW3 and SW4 as 'up' and 'down' buttons
    to scroll through four different LED patterns, one per button
    press. Pressing SW3 should advance to the next pattern, and
    pressing SW4 should go back to the previous one. The sequence
    should wrap around (going past the last pattern returns to the
    first, and going before the first returns to the last).

3.  Create a two-player rapid-clicker game in which the first player
    to reach MAX_COUNT clicks wins. Here is how the game should work:

    - Player 1 uses SW3, and LED2 flashes momentarily on each of their clicks
    - Player 2 uses SW4, and LED5 flashes momentarily on each of their clicks
    - The first player to reach MAX_COUNT wins
    - If Player 1 wins, LED3 lights up and stays on
    - If Player 2 wins, LED4 lights up and stays on
    - Once a player has won, additional button presses from either
      player should be blocked until the game is reset
    - Pressing SW5 resets both counters, turns off all LEDs, and
      restarts the game

    Hint: You will need to track whether the game is still active so
    that you can block input once a winner is found. A Boolean
    variable works well for this. Start with something like:

int SW3_presses = 0;
int SW4_presses = 0;
bool SW3_last = false;
bool SW4_last = false;
bool game_active = true;

    Use edge detection (from Analysis Q6) for both SW3 and SW4 so
    that each physical press is counted exactly once. Wrap all of the
    player input and win-checking logic inside an 'if (game_active)'
    block, and handle the SW5 reset outside of it so that the reset
    always works.

    While developing and testing your game, Serial.print() statements
    are a useful way to track both counters at once without needing to
    watch the LEDs:

    Serial.print("P1: ");
    Serial.print(SW3_presses);
    Serial.print("  P2: ");
    Serial.println(SW4_presses);

    Once your game is working correctly, remove or comment out any
    Serial.print() calls so they don't slow down the program. To
    comment out a line in Arduino C, add '//' at the start:

    // Serial.println(SW4_presses);

*/
