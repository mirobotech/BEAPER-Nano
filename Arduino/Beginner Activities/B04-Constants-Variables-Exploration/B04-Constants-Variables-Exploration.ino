/* ================================================================================
Beginner Activity 4 Exploration: Constants and Variables
[B04-Constants-Variables-Exploration]
February 26, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPERNano.h header file
=================================================================================*/
// IMPORTANT: Make sure that BEAPERNano.h is accessible as a tab in this project.
#include "BEAPERNano.h"   // Define BEAPER Nano I/O devices

// ---- Program Constants ----------------
const int SLOW_DELAY = 200;
const int MEDIUM_DELAY = 100;
const int FAST_DELAY = 50;
const int LUDICROUS_DELAY = 25;

// ---- Program Variables ----------------
bool slow_button;
bool medium_button;
bool fast_button;
bool ludicrous_button;
bool display_pattern = false;
int blink_delay_ms = 200;

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

    Serial.begin(9600);                 // Initialize serial output for debugging
}

void loop()
{
    // Check pushbuttons
    slow_button = (digitalRead(SW2) == LOW);
    medium_button = (digitalRead(SW3) == LOW);
    fast_button = (digitalRead(SW4) == LOW);
    ludicrous_button = (digitalRead(SW5) == LOW);

    if (slow_button)
    {
        blink_delay_ms = SLOW_DELAY;
        display_pattern = true;
    }

    if (medium_button)
    {
        blink_delay_ms = MEDIUM_DELAY;
        display_pattern = true;
    }

    if (fast_button)
    {
        blink_delay_ms = FAST_DELAY;
        display_pattern = true;
    }

    if (ludicrous_button)
    {
        blink_delay_ms = LUDICROUS_DELAY;
        display_pattern = true;
    }

    // LED pattern
    if (display_pattern)
    {
        digitalWrite(LED2, HIGH);
        delay(blink_delay_ms);
        digitalWrite(LED3, HIGH);
        delay(blink_delay_ms);
        digitalWrite(LED4, HIGH);
        delay(blink_delay_ms);
        digitalWrite(LED5, HIGH);
        delay(blink_delay_ms);
        digitalWrite(LED2, LOW);
        delay(blink_delay_ms);
        digitalWrite(LED3, LOW);
        delay(blink_delay_ms);
        digitalWrite(LED4, LOW);
        delay(blink_delay_ms);
        digitalWrite(LED5, LOW);
        delay(blink_delay_ms);
        display_pattern = false;
    }
}


/*
Guided Exploration

This program extends the concepts from Activity-B04-Constants-Variables
— multiple constants, multiple named button variables, and a variable
delay that changes at runtime. If you haven't already read through
the code above and made a prediction about what each button does,
do that before running the program.

1.  Run the program and press each button. Does the behaviour match
    your prediction? Which characteristics of the code made the
    program's behaviour easiest to predict before running it?

    Add Serial.print() statements to display the values of
    blink_delay_ms and display_pattern at key points in the loop —
    for example, each time a button is pressed and each time the
    pattern starts and finishes. Open the Serial Monitor and observe
    the output as you press different buttons.

    Can you see display_pattern cycling between 1 (true) and 0
    (false) as the pattern runs? Which button sets which delay value?

2.  blink_delay_ms is declared as 'int' without the 'const'
    qualifier. How does the compiler know that SLOW_DELAY and the
    other similarly declared names are constants, while blink_delay_ms
    is a variable? What does 'const' actually tell the compiler, and
    what would happen if you tried to assign a new value to SLOW_DELAY
    while the program was running?

3.  Predict what will happen if two buttons are pressed at the same
    time. Try it! Was your prediction correct? Trace through the
    program code to explain why this happens.

    When you are done exploring this program, return to
    Activity-B04-Constants-Variables for the Extension Activities.

*/
