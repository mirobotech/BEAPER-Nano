/* ================================================================================
Beginner Activity 8: Functions [Activity-B08-Functions]
March 17, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPERNano.h header file
=================================================================================*/
// IMPORTANT: Make sure that BEAPERNano.h is accessible as a tab in this project.
#include "BEAPERNano.h"   // Define BEAPER Nano I/O devices

// ---- Program Constants ----------------
const int FLASH_DELAY = 100;
const int STEP_DELAY = 400;
const int MAX_ATTEMPTS = 4;

// ---- Program Variables ----------------
int target = 0;
int attempts = 0;


// ---- Program Functions ----------------

void clear_leds()
{
    // Turn off all four LEDs.
    digitalWrite(LED2, LOW);
    digitalWrite(LED3, LOW);
    digitalWrite(LED4, LOW);
    digitalWrite(LED5, LOW);
}

void indicate_attempts(int count)
{
    // Light LEDs to show remaining attempts: 4 lit = 4 remaining, etc.
    digitalWrite(LED2, count >= 1 ? HIGH : LOW);
    digitalWrite(LED3, count >= 2 ? HIGH : LOW);
    digitalWrite(LED4, count >= 3 ? HIGH : LOW);
    digitalWrite(LED5, count >= 4 ? HIGH : LOW);
}

int read_keypad()
{
    // Wait for any pushbutton to be pressed and released.
    // Returns the button number (2, 3, 4, or 5) when released.
    int key = 0;
    while (key == 0)
    {
        if (digitalRead(SW2) == LOW) key = 2;
        else if (digitalRead(SW3) == LOW) key = 3;
        else if (digitalRead(SW4) == LOW) key = 4;
        else if (digitalRead(SW5) == LOW) key = 5;
    }
    while (digitalRead(SW2) == LOW || digitalRead(SW3) == LOW ||
           digitalRead(SW4) == LOW || digitalRead(SW5) == LOW) {}
    return key;
}


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
    randomSeed(analogRead(0));          // Seed random number generator

    Serial.println("Button guessing game - find the secret button!");
}

void loop()
{
    // Start a new round
    target = random(2, 6);              // Random number 2-5
    attempts = MAX_ATTEMPTS;
    indicate_attempts(attempts);
    Serial.println("New round! Guess the secret button (SW2-SW5)...");

    // Play the round
    while (attempts > 0)
    {
        int key = read_keypad();
        Serial.print("You pressed SW");
        Serial.println(key);

        if (key == target)
        {
            Serial.print("Correct! You found it in ");
            Serial.print(MAX_ATTEMPTS - attempts + 1);
            Serial.println(" guess(es)!");
            for (int i = 0; i < 3; i++)
            {
                tone(LS1, 4000, FLASH_DELAY);
                delay(FLASH_DELAY * 2);
            }
            clear_leds();
            delay(STEP_DELAY);
            attempts = 0;               // Exit the inner loop to start a new round
        }
        else
        {
            attempts--;
            tone(LS1, 200, FLASH_DELAY);
            indicate_attempts(attempts);
            if (attempts > 0)
            {
                Serial.print("Wrong! ");
                Serial.print(attempts);
                Serial.println(" attempt(s) remaining.");
            }
            else
            {
                Serial.print("Out of attempts! The secret button was SW");
                Serial.println(target);
                delay(STEP_DELAY);
                clear_leds();
            }
        }
    }
}


/*
Guided Exploration

Every program in this curriculum has used functions. Every time you
have written 'tone()', 'digitalWrite()', or 'delay()', you have been
calling a function - passing it information and letting it do a job.
'setup()' and 'loop()' are themselves functions, called automatically
by the Arduino runtime. This activity reveals how functions work and
shows you how to define your own. The three functions in this program
are introduced in order of increasing complexity, and together they
cover the three essential forms: a function with no arguments and no
return value, a function with an argument and no return value, and a
function with no arguments that returns a value.

1.  Functions are named blocks of code that can be called from
    anywhere in a program. They can receive input values called
    arguments, and they can send back a result called a return value.

    Look at the three functions defined before setup(). In Arduino C,
    every function must declare its return type before its name:
    'void' means the function returns nothing, and 'int' means it
    returns an integer. Their signatures show the three forms at
    a glance:

    void clear_leds()           // No arguments, no return value
    void indicate_attempts(int count)  // One argument, no return value
    int read_keypad()           // No arguments, returns an int

    Identify at least five other function calls already in this
    program. For each one, note whether it receives arguments,
    returns a value, or both. 'random(2, 6)' is a good starting
    point - it takes two arguments and returns the random number
    it generates.

2.  In Arduino C, a function definition has three parts: the return
    type, the function name, and the body in curly braces. Look at
    'clear_leds()':

    void clear_leds()
    {
        // Turn off all four LEDs.
        digitalWrite(LED2, LOW);
        digitalWrite(LED3, LOW);
        digitalWrite(LED4, LOW);
        digitalWrite(LED5, LOW);
    }

    The 'void' return type means this function performs a task but
    sends no value back. Everything between the curly braces is the
    function body - the code that runs each time the function is
    called.

    Count how many times 'clear_leds()' is called in the program.
    How many lines of code would the program contain if each call
    were replaced with the four individual digitalWrite() statements?

    The reduction in repeated lines is only part of the benefit.
    What would happen if you needed to add a fifth LED to the
    circuit? How many places in the program would need to change
    with the function, compared to without it? This single-point-
    of-change property is one of the most important reasons to use
    functions, even for short tasks.

3.  The 'indicate_attempts(int count)' function receives one
    argument. The declaration 'int count' in the function header
    means the function expects an integer argument and will refer
    to it internally as 'count'. This is called a parameter.

    Look at how 'count' is used inside the function body:

    void indicate_attempts(int count)
    {
        digitalWrite(LED2, count >= 1 ? HIGH : LOW);
        digitalWrite(LED3, count >= 2 ? HIGH : LOW);
        digitalWrite(LED4, count >= 3 ? HIGH : LOW);
        digitalWrite(LED5, count >= 4 ? HIGH : LOW);
    }

    When loop() calls 'indicate_attempts(attempts)' with attempts
    equal to 4, all four LEDs light up. As wrong guesses reduce
    attempts, the function is called again and LEDs extinguish
    one by one.

    Trace through the function for each possible value of count
    (0 through 4) and describe which LEDs would be lit. What would
    the LEDs show if count were somehow 5 or greater? Verify your
    predictions by running the program.

    The parameter 'count' is a local variable - it only exists
    inside 'indicate_attempts()' and is destroyed when the function
    returns. What would happen if you tried to use 'count' in loop()?
    Try it and observe the compiler error.

4.  The 'read_keypad()' function uses the 'return' statement to
    send a value back to the code that called it:

    int key = read_keypad();

    The 'int' before 'key' declares it as an integer variable, and
    it receives whatever value 'read_keypad()' returned - the number
    of the button that was pressed (2, 3, 4, or 5). That value is
    then assigned to 'key' and can be used like any other variable.
    The return type in the function header ('int read_keypad()') must
    match the type of the value being returned.

    Look at the two loops inside 'read_keypad()'. The first loop
    waits until a button is pressed and records which one. The second
    loop - with an empty body '{}' - waits until all buttons are
    released before returning. Why are both loops necessary? What
    would happen if the second loop were removed and the function
    returned 'key' immediately after detecting a press? Think about
    how loop() would behave on the very next call to 'read_keypad()'.

5.  In Arduino C, functions must be defined before they are called,
    or the compiler needs to know their full signature in advance.
    In this program, all three functions are defined before setup()
    and loop(), so the compiler encounters their definitions before
    any calls to them.

    Try moving the entire 'clear_leds()' function definition to
    after loop(). What happens when you try to compile? The error
    may mention 'was not declared in this scope'. What does this
    tell you about how the Arduino compiler processes a program file?

6.  The 'indicate_attempts()' function is a compact example of
    using a parameter as meaningful data rather than just a count.
    The ternary operator '?' selects HIGH or LOW based on a
    comparison - the same pattern used in the for loop displays
    in Activity 7.

    Rewrite 'indicate_attempts()' using four 'if'/'else' blocks
    instead of the ternary approach, and verify that the program
    still behaves identically. Which version do you find easier to
    read and why?

    This exercise illustrates an important principle: a function's
    external behaviour - what it does when called - is separate
    from its internal implementation - how it does it. Code that
    calls the function only sees the result; the implementation can
    be changed freely as long as the result stays the same.

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
    from the wrong-guess branch in loop(). The program should
    behave identically.

    What does this change tell you about how behaviour can be
    moved into functions without affecting the visible result?
    What is the advantage of 'indicate_attempts()' managing its
    own cleanup rather than relying on the caller to do it?

8.  Open BEAPERNano.h and read through the inline helper functions
    defined there - 'left_motor_forward()', 'light_level()', and
    others.

    Each inline function follows the same pattern you have been
    learning in this activity: a return type, a name, a parameter
    list (possibly empty), and a body. The 'inline' keyword is an
    instruction to the compiler to insert the function's code
    directly at each call site rather than making a traditional
    function call - a small efficiency improvement that has no
    effect on how you write or call the function.

    Choose any two inline functions from the header and answer
    these questions for each: What does it return? What arguments
    does it accept? What does its body do, and does it call any
    other functions?

    Arduino's built-in 'tone()' function accepts an optional third
    argument (duration). What would happen if you called
    'tone(LS1, 440)' without a duration - would the tone stop on
    its own? Try it: the hardware timer will keep the tone playing
    until 'noTone(LS1)' is called explicitly to stop it. Arduino C
    supports optional arguments through default parameter values,
    declared in the function header like this:

    void tone(pin, frequency, duration = 0);

    You have been relying on this behaviour throughout the curriculum.
    Which of the three functions you wrote in this activity could
    benefit from a default parameter value, and what would that
    default be?


Extension Activities

These activities build on the three functions already in the starter
program. As you add new functions, keep loop() focused on program
flow - it should read clearly as a sequence of named actions, with
the details handled inside the functions themselves.

1.  Add a 'win_signal()' function and a 'lose_signal()' function
    to the starter program, each encapsulating the tone and LED
    behaviour for their respective outcomes. Replace the inline
    win and lose code in loop() with calls to these functions.

    After this change, the inner 'while (attempts > 0)' loop should
    read almost like plain English: get a key, check if it matches,
    call the appropriate signal function, update the display. How
    does moving the signal behaviour into named functions change
    the readability of loop()?

2.  Write a 'flash_led(int led, int times)' function that flashes
    a specified LED a specified number of times with a short delay
    between each flash. In Arduino C, LED pin numbers are integers,
    so passing 'LED2' to the function passes the integer pin number
    defined in BEAPERNano.h - inside the function, 'led' can be
    used directly in digitalWrite() calls just like LED2 would be.

    Use this function to create distinct win and lose signals that
    use different LEDs and flash counts, replacing the simpler
    tone-only signals from EA1.

    This demonstrates that a single well-written function can
    produce several distinct outputs depending on its arguments.

3.  Modify 'read_keypad()' to also play a brief confirmation tone
    when a button press is detected - before the release loop.
    Each button should play a different frequency so the player
    can identify which button was pressed by sound alone:
    SW2=500Hz, SW3=750Hz, SW4=1000Hz, SW5=1250Hz (or choose
    your own frequencies).

    This adds behaviour to the function without changing its
    interface - the calling code still uses
    'int key = read_keypad()' and receives the same return values.
    What does this tell you about the advantage of encapsulating
    behaviour in functions?

4.  Write a 'choose_target()' function that uses 'random()' to
    return a randomly chosen button number (2, 3, 4, or 5).
    Replace the direct 'random(2, 6)' call in loop() with a call
    to this new function.

    This may seem like a small change for little gain, but consider:
    if you later wanted to change the selection logic - weighting
    certain buttons more heavily, or avoiding the same button twice
    in a row - you would only need to change 'choose_target()',
    not every place in the program that picks a target. This is
    called encapsulating the selection logic, and it is one of the
    main reasons functions are used even for short tasks.

5.  Refactor the combination lock from Activity 6 Extension Activity
    6 into a cleaner version using the three functions from this
    activity. The combination lock requires the player to press SW2,
    SW3, SW4, and SW5 in a specific order. Use:

    - 'read_keypad()' to get each button press
    - 'indicate_attempts(step)' to light LEDs showing how many
      steps of the sequence have been completed correctly
    - 'clear_leds()' to reset the display on a wrong press

    The main program logic in loop() should fit in around 15 lines.
    Compare this version with your Activity 6 combination lock
    program. What specifically did moving code into functions change
    about the structure and readability of loop()?

    As an extension, add a second parameter to 'indicate_attempts()'
    so it can accept 'indicate_attempts(int step, bool success)'
    where 'success' controls whether the LEDs flash briefly before
    clearing on a wrong entry. How does adding a second parameter
    change the function's interface, and what changes are needed
    wherever the function is called?

*/
