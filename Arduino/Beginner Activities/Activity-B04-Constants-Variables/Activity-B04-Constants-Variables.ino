/* ================================================================================
Beginner Activity 4: Constants and Variables [Activity-B04-Constants-Variables]
February 26, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPERNano.h header file
=================================================================================*/
// IMPORTANT: Make sure that BEAPERNano.h is accessible as a tab in this project.
#include "BEAPERNano.h"   // Define BEAPER Nano I/O devices

// ---- Program Constants ----------------
const int BLINK_DELAY = 200;

// ---- Program Variables ----------------
bool SW2_pressed;
bool display_pattern = false;

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
    SW2_pressed = (digitalRead(SW2) == LOW);

    // Start pattern with SW2 press
    if (SW2_pressed)
    {
        display_pattern = true;
    }

    // LED pattern
    if (display_pattern)
    {
        digitalWrite(LED2, HIGH);
        delay(BLINK_DELAY);
        digitalWrite(LED3, HIGH);
        delay(BLINK_DELAY);
        digitalWrite(LED4, HIGH);
        delay(BLINK_DELAY);
        digitalWrite(LED5, HIGH);
        delay(BLINK_DELAY);
        digitalWrite(LED2, LOW);
        delay(BLINK_DELAY);
        digitalWrite(LED3, LOW);
        delay(BLINK_DELAY);
        digitalWrite(LED4, LOW);
        delay(BLINK_DELAY);
        digitalWrite(LED5, LOW);
        delay(BLINK_DELAY);
        display_pattern = false;
    }
}


/*
Guided Exploration

Good programs are written for two audiences: the computer that runs
them and the people who read them. Constants, variables, and
meaningful names are how programmers communicate intent — not just
what the code does, but why it does it. The concepts introduced in
this activity will make your programs easier to read, easier to
change, and easier to debug.

1.  There are several new concepts in this program, so let's start
    with the simplest one — program constants:

// ---- Program Constants ----------------
const int BLINK_DELAY = 200;

    A program constant is a named, unchanging value used in place of
    a number in a program. Here, 'BLINK_DELAY' is defined as a
    constant integer ('const' meaning constant, 'int' meaning a whole
    number) with a value of 200. This value will not change while the
    program runs. (The names of constants are written in ALL_CAPS by
    convention, to distinguish them from variables.)

    Using a named constant instead of a bare number provides two
    important benefits. First, the name 'BLINK_DELAY' is descriptive
    — it tells anyone reading the program what 200 actually means.
    Second, every part of the program that uses BLINK_DELAY can be
    updated simply by changing one line at the top.

    Run the program and observe the blink rate. Then change
    BLINK_DELAY to 100 and run it again, then try 50. Think about
    how much longer it would take to update every delay() call
    individually.

    This program uses two types: 'int' for integer (whole number)
    values, and 'bool' for Boolean (true/false) values. A third
    common type, 'float', is used for numbers with decimal parts
    (for example, 3.14159). Unlike MicroPython, which infers the
    type of a value automatically, Arduino C requires every constant
    and variable to be declared with an explicit type — which is why
    'const int' and 'bool' appear in this program's declarations.

2.  The second concept introduced here is the use of Boolean
    variables. Variables are named like constants, but their values
    are expected to change as the program runs. This program defines
    two:

// ---- Program Variables ----------------
bool SW2_pressed;
bool display_pattern = false;

    Notice that SW2_pressed is declared without being assigned a
    value — it is uninitialized. In Arduino C, reading an
    uninitialized variable can produce unpredictable results, but
    this program writes to SW2_pressed at the start of every loop
    cycle before reading it, so it is always defined when used.
    display_pattern is initialized to false so it starts in a known
    state before the loop begins.

    Both variables will switch between true and false while the
    program runs. Boolean variables have a useful shortcut in if
    conditions. Instead of writing:

    if (display_pattern == true)

    the program uses:

    if (display_pattern)

    Both mean the same thing — the second simply uses the variable's
    own true or false state directly, without needing to compare it
    to anything. This works because a Boolean variable already is
    the result of a true/false test.

    Explain which part of the program sets display_pattern to true,
    and which part resets it to false.

3.  Sometimes you need to see what your program is thinking — the
    current value of a variable at a specific moment in time.
    Arduino's Serial.print() and Serial.println() functions send text
    to the Serial Monitor in the Arduino IDE (opened from the Tools
    menu, or Ctrl+Shift+M), making them essential tools for
    understanding and debugging programs. The Serial.begin(9600) call
    in setup() initializes the serial connection — make sure the
    Serial Monitor is set to the same baud rate (9600).

    Add these lines inside the 'if (SW2_pressed)' block to print the
    value of display_pattern each time SW2 is pressed:

    if (SW2_pressed)
    {
        display_pattern = true;
        Serial.print("display_pattern: ");
        Serial.println(display_pattern);
    }

    Run the program, open the Serial Monitor, and press SW2. Do you
    see the output you expected? Note that Serial.println() prints
    Boolean values as 1 (true) or 0 (false).

    Now add a Serial.println() call inside the 'if (display_pattern)'
    block, just before 'display_pattern = false', to show the moment
    it resets:

        Serial.println("display_pattern reset to: false");

    You'll see Serial.print() used again in the next activity. Get
    comfortable with it — revealing variable state at key moments is
    one of the most practical debugging techniques you'll use.

4.  The SW2_pressed variable is assigned using this statement:

    SW2_pressed = (digitalRead(SW2) == LOW);

    SW2 is read and compared with LOW because it is wired as an
    active-low input. If SW2 reads LOW, the expression evaluates to
    true and SW2_pressed becomes true — enabling it to be used
    directly in any if condition.

    The name SW2_pressed carries meaning: it will be true only when
    SW2 is actually being pressed. This makes the if condition that
    follows it clear and unambiguous:

    if (SW2_pressed)

    A programmer reading this code doesn't need to know whether the
    switch is active-high or active-low — that detail is handled once,
    at the top of the loop, and hidden behind a meaningful name.

    Could the program use a similar approach to detect a button being
    released? Write an appropriate variable name and expression that
    would be true only when SW2 is not being pressed.

5.  The program so far uses a single constant and two Boolean
    variables. The next file, B04-Constants-Variables-Exploration,
    extends these ideas with multiple constants, multiple named button
    variables, and a variable delay that changes at runtime.

    Before loading and running that program, read through its code
    and try to predict what each button will do and how the program
    works. Which parts of the code made your prediction easier?


Extension Activities

The programs you write from here on should use named constants and
variables from the start — choose names that describe what a value
represents, not just what type it is. A name like 'SW2_pressed' tells
a reader far more than 'button' or 'b2'. Treat naming as part of the
design, not an afterthought.

1.  Re-create the Start-Stop pushbutton program from Activity 3
    using named button variables and a logical variable for the
    machine state.

    Create a program that simulates the 'Start' and 'Stop' buttons
    found on large industrial machines. The machine (simulated by an
    LED) should turn on when the 'Start' button is pressed and remain
    on until the 'Stop' button is pressed. Ensure that the machine
    cannot be turned on while the Stop button is being pressed.

2.  Create the code for a toggle button — a type of switch behaviour
    that uses a single button to alternately turn a device on and off.
    The output should only change when the button transitions from
    not pressed to pressed, so holding the button should not cause
    repeated toggling.

    You will need three variables: one for the current LED state, one
    for the current button state, and one for the previous button
    state. Start a new program with something like:

bool LED2_on = false;
bool toggle_pressed = false;
bool toggle_last = false;

    Each loop, save the current value of toggle_pressed into
    toggle_last before reading the new button state. A toggle should
    only happen when toggle_pressed is true and toggle_last was false
    — meaning a new press has just occurred.

3.  Extend the toggle button program from EA2 so that each pushbutton
    toggles its corresponding LED, allowing any combination of LEDs
    to be set simply by pressing the individual buttons.

4.  Re-create the bicycle turn signal circuit from Activity 3 using
    named button variables and logical variables for the turn signal
    state.

    The circuit uses four LEDs in a row, controlled by two pushbuttons
    on the handlebars. Write a program to simulate the turn signal
    using one or more of BEAPER Nano's LEDs to indicate a left or
    right turn while the corresponding button is held.

    For an extra challenge, add brake functionality or a bell/horn
    feature. Can you make the brake or horn operate while the turn
    signal is active? What makes doing this so difficult?

*/
