/* ================================================================================
Beginner Activity 7: Counted Loops [Activity-B07-Counted-Loops]
March 10, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPERNano.h header file
=================================================================================*/
// IMPORTANT: Make sure that BEAPERNano.h is accessible as a tab in this project.
#include "BEAPERNano.h"   // Define BEAPER Nano I/O devices

// ---- Program Constants ----------------
const int FLASH_DELAY = 100;
const int STEP_DELAY = 300;

// ---- Program Variables ----------------
bool SW5_pressed = false;

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

    Serial.begin(9600);
    while (!Serial);                    // Wait for serial port to be ready

    // Wait for SW5 to begin
    Serial.println("Press SW5 to begin...");
    while (!SW5_pressed)
    {
        digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));   // Toggle status LED
        delay(FLASH_DELAY);
        SW5_pressed = (digitalRead(SW5) == LOW);
    }
    digitalWrite(LED_BUILTIN, HIGH);
    Serial.println("Starting!");

    // Part 1: Repeat a done signal three times using a for loop
    Serial.println("Part 1: for loop repeat");
    for (int i = 0; i < 3; i++)
    {
        digitalWrite(LED2, HIGH);
        tone(LS1, 4000, FLASH_DELAY);
        delay(FLASH_DELAY);
        digitalWrite(LED2, LOW);
        delay(FLASH_DELAY);
    }

    delay(STEP_DELAY);

    // Part 2: Count up through LEDs using the loop variable
    Serial.println("Part 2: count up");
    for (int i = 2; i < 6; i++)
    {
        Serial.print("  i = ");
        Serial.println(i);
        digitalWrite(LED2, i >= 2 ? HIGH : LOW);
        digitalWrite(LED3, i >= 3 ? HIGH : LOW);
        digitalWrite(LED4, i >= 4 ? HIGH : LOW);
        digitalWrite(LED5, i >= 5 ? HIGH : LOW);
        delay(STEP_DELAY);
    }

    delay(STEP_DELAY);

    // Part 3: Count down through LEDs using a negative step
    Serial.println("Part 3: count down");
    for (int i = 5; i > 1; i--)
    {
        Serial.print("  i = ");
        Serial.println(i);
        digitalWrite(LED2, i >= 2 ? HIGH : LOW);
        digitalWrite(LED3, i >= 3 ? HIGH : LOW);
        digitalWrite(LED4, i >= 4 ? HIGH : LOW);
        digitalWrite(LED5, i >= 5 ? HIGH : LOW);
        delay(STEP_DELAY);
    }

    // All LEDs off
    digitalWrite(LED2, LOW);
    digitalWrite(LED3, LOW);
    digitalWrite(LED4, LOW);
    digitalWrite(LED5, LOW);
    Serial.println("Done!");
}

void loop()
{
    // Program completes in setup() for this activity.
    // See Extension Activity 1 to restructure using loop().
}


/*
Guided Exploration

In Activity 6, Extension Activity 1 asked you to replace three manual
repetitions with a while loop. It worked, but it required you to
manage a loop control variable yourself - declare and initialize it
before the loop, check it in the condition, and update it inside the
loop body. Arduino C has a loop structure designed specifically for
situations where the number of iterations is known in advance: the
for loop. It packages the initialize, check, and update steps into a
single header line, leaving you to focus on what the loop body should
do. This activity explores the for loop and the three standard ways
to control its range and direction.

1.  Look at Part 1 of this program:

    for (int i = 0; i < 3; i++)
    {
        digitalWrite(LED2, HIGH);
        tone(LS1, 4000, FLASH_DELAY);
        delay(FLASH_DELAY);
        digitalWrite(LED2, LOW);
        delay(FLASH_DELAY);
    }

    The for loop header 'for (int i = 0; i < 3; i++)' contains
    three parts separated by semicolons, each corresponding to one
    of the steps from Activity 6's loop control variable pattern:

    int i = 0    // Initialize: declare i and set it to 0
    i < 3        // Check: keep looping while i is less than 3
    i++          // Update: add 1 to i after each iteration

    The compiler runs the initialize step once before the loop starts,
    checks the condition before each iteration, and runs the update
    step after each iteration - automatically, without you having to
    place these steps in the right locations yourself.

    Add a Serial.println() inside the Part 1 loop to print the value
    of i on each iteration. Run the program and observe the Serial
    Monitor output. Does i have the values you expected? Compare this
    for loop with the while loop solution you wrote in Activity 6
    Extension Activity 1. What does the for loop handle automatically
    that your while loop required you to do manually?

2.  Notice that i starts at 0 and the loop runs while i < 3,
    producing the values 0, 1, 2. The loop body runs three times,
    but i never reaches 3. This is the standard C for loop pattern
    for repeating something n times: start at 0, stop before n.

    You can verify the values with any range. Try this loop:

    for (int i = 0; i < 5; i++)
    {
        Serial.println(i);
    }

    How many values does this print? What is the first? What is
    the last? Does i ever equal 5?

3.  Part 2 uses a for loop that starts at 2 instead of 0:

    for (int i = 2; i < 6; i++)

    This is useful when the loop variable needs to represent a
    meaningful value rather than just a count. The loop produces
    2, 3, 4, 5 - stopping before 6.

    Look at how i is used inside the Part 2 loop body. The ternary
    operator '?' is used here as a compact way to choose between
    HIGH and LOW based on a comparison - you will learn more about
    it in the intermediate activities, but for now you can read
    'i >= 2 ? HIGH : LOW' as meaning 'HIGH if i >= 2, otherwise LOW'.

    Trace through all four values of i (2, 3, 4, 5) and describe
    what you would expect to see on the LEDs for each value.

    Run the program to verify your prediction. Was it correct?

4.  Part 3 counts downward by changing the for loop header:

    for (int i = 5; i > 1; i--)

    Instead of i++ (which adds 1), this uses i-- (which subtracts 1).
    The condition i > 1 stops the loop before i reaches 1, producing
    the values 5, 4, 3, 2.

    Why does the sequence stop at 2 and not at 1? What would you
    change to make it include 1 as well?

    Try counting down in steps of 2 by replacing i-- with i -= 2,
    and changing the stop condition to i > 0:

    for (int i = 5; i > 0; i -= 2)

    What values does i take? What do the LEDs show? Add a
    Serial.println() inside the loop to verify.

5.  The loop variable in a for loop doesn't have to be named 'i'.
    That name is just a convention - any descriptive name works and
    is often preferable. In Part 2, naming the variable 'led' instead
    of 'i' would make the loop's purpose immediately clearer:

    for (int led = 2; led < 6; led++)

    Try renaming i to led in the Part 2 loop. Does the program still
    work identically? When would you choose a descriptive name like
    'led' or 'count' over the conventional 'i'?

    As a preview of something you'll explore in the intermediate
    activities: Arduino C supports arrays, which allow you to store
    multiple values under one name and access them by index. The
    BEAPERNano.h header file defines an array of LED pin numbers
    called LEDS[], so you can write:

    for (int i = 0; i < 4; i++)
    {
        digitalWrite(LEDS[i], HIGH);
        delay(STEP_DELAY);
    }

    ...and the loop will control each LED in turn without individual
    digitalWrite() calls for each one. Arrays and indexed access are
    covered fully in the intermediate activities.

6.  A for loop and a while loop can often solve the same problem.
    Here is the Part 1 for loop rewritten as a while loop:

    int count = 0;
    while (count < 3)
    {
        digitalWrite(LED2, HIGH);
        tone(LS1, 4000, FLASH_DELAY);
        delay(FLASH_DELAY);
        digitalWrite(LED2, LOW);
        delay(FLASH_DELAY);
        count++;
    }

    And here is a while loop equivalent for the Part 2 for loop:

    int i = 2;
    while (i < 6)
    {
        digitalWrite(LED2, i >= 2 ? HIGH : LOW);
        digitalWrite(LED3, i >= 3 ? HIGH : LOW);
        digitalWrite(LED4, i >= 4 ? HIGH : LOW);
        digitalWrite(LED5, i >= 5 ? HIGH : LOW);
        delay(STEP_DELAY);
        i++;
    }

    Both approaches produce identical results. When would you choose
    a for loop over a while loop, and when would a while loop be the
    better choice? Think about what each one communicates to someone
    reading your code.

7.  A for loop can be placed inside another for loop - this is called
    nesting. Here is a simple example to try in setup():

    for (int led = 2; led < 6; led++)
    {
        for (int flash = 0; flash < led - 1; flash++)
        {
            digitalWrite(LED2, led >= 2 ? HIGH : LOW);
            digitalWrite(LED3, led >= 3 ? HIGH : LOW);
            digitalWrite(LED4, led >= 4 ? HIGH : LOW);
            digitalWrite(LED5, led >= 5 ? HIGH : LOW);
            delay(FLASH_DELAY);
            digitalWrite(LED2, LOW);
            digitalWrite(LED3, LOW);
            digitalWrite(LED4, LOW);
            digitalWrite(LED5, LOW);
            delay(FLASH_DELAY);
        }
        delay(STEP_DELAY);
    }

    Before running it, trace through the loop values and predict what
    you will see. For each value of 'led', how many times does the
    inner loop run? What does the pattern look like?

    Run the program to check your prediction. Print both loop
    variables to the Serial Monitor to help verify your understanding
    of what is happening at each step.


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
    a for loop counting downward, and the done signal should become
    a for loop that repeats three times.

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

    Hint: Arduino C's bitwise AND operator '&' and right-shift
    operator '>>' can help extract individual bits from a number:

    for (int i = 0; i < 16; i++)
    {
        digitalWrite(LED2, (i >> 0) & 1 ? HIGH : LOW);  // bit 0
        digitalWrite(LED3, (i >> 1) & 1 ? HIGH : LOW);  // bit 1
        digitalWrite(LED4, (i >> 2) & 1 ? HIGH : LOW);  // bit 2
        digitalWrite(LED5, (i >> 3) & 1 ? HIGH : LOW);  // bit 3
        delay(STEP_DELAY);
    }

    Use Serial.print() to display each number's decimal value in the
    Serial Monitor alongside the LED display. What is the highest
    number the four LEDs can represent?

5.  Write a program that produces a Morse code output for a short
    word or phrase of your choice. Represent each dot as a short LED
    flash and tone, and each dash as a longer one.

    You will learn how arrays and strings work in full detail in the
    intermediate activities - but even without fully understanding
    them yet, you can use the pattern in the hint below to produce
    some interesting results. This is a preview of how for loops are
    used more broadly in Arduino C beyond just counting numbers.

    Hint: A for loop can step through each character in a string
    using the string's length as the loop bound. The tone() function
    blocks for the duration of the tone, so the delay() call that
    follows adds a gap after the sound ends:

    const char morse_s[] = "...";    // S = dot dot dot
    const char morse_o[] = "---";    // O = dash dash dash

    for (int i = 0; i < strlen(morse_s); i++)
    {
        if (morse_s[i] == '.')
            tone(LS1, 800, 100);     // Short tone for dot
        else
            tone(LS1, 800, 300);     // Long tone for dash
        delay(100);                  // Gap between symbols
    }

    Try spelling 'SOS' by sending morse_s, morse_o, and morse_s
    in sequence. By convention, the gap between letters should be
    three times the dot duration - add a delay() between each
    letter's loop to observe the difference it makes. Experiment
    with different frequencies and durations to improve the sound.

*/
