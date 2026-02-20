/* ================================================================================
Beginner Activity 4: Constants and Variables [Activity-B04-Constants-Variables]
February 19, 2026

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

    Serial.begin(9600);     // Initialize serial output for debugging
    while (!Serial);        // Wait for the serial port to start
}

void loop()
{
    SW2_pressed = (digitalRead(SW2) == LOW);

    // Check button state
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
Program Analysis Activities

1.  There are a lot of new and important concepts to cover in this
    program, so let's start at the top with the simplest one: program
    constants:

// ---- Program Constants ----------------
const int BLINK_DELAY = 200;

    A program constant is simply an un-changing, named value used
    instead of a number in a program. In this program, 'BLINK_DELAY'
    is defined as an integer constant ('const' meaning constant, and
    'int' meaning an integer, or whole number) with a value of 200.
    This value won't change while the program runs. (The names of
    constants are often written in ALL_CAPS to distinguish them
    from variables -- which we'll learn about, below.) 

    The extra work of writing BLINK_DELAY instead of 200 provides
    two important benefits. First, the name 'BLINK_DELAY' is
    descriptive, and provides more meaning to anyone reading the
    program than the number 200 would.

    Second, all of the parts of the program that make use of the
    BLINK_DELAY constant can now be changed simply by editing one
    line at the top of the program. 

    Run the program and watch its blink rate. Then, change the
    value of the BLINK_DELAY constant to 100 and run the program
    again. Then, change it to 50 and run it again. Imagine how much
    longer it would have taken to change every single delay statement
    instead of just changing the constant.

2.  The second important concept introduced in this program is the
    use of variables to store simple true/false values. Variables
    are named, just like constants, but their values are expected to
    change as the program runs. This program defines two variables:

// ---- Program Variables ----------------
bool SW2_pressed;
bool display_pattern = false;

    The 'bool' type refers to 'Boolean', or true/false logic, and
    'SW2_pressed' is defined as an uninitialized variable - that
    is, it hasn't been assigned a value of true or false yet. (This
    can lead to unexpected behaviour if it's read without being
    assigned first, but this program will write to it first.) The
    second variable, 'display_pattern' is initialized to be false
    before the main program loop runs, and will switch between
    being true and false as the user interacts with the program.
    
    What's special about Boolean variables is not just that they
    can change state between true and false, but that they also
    enable if conditions to use a clever short-cut. Instead of
    checking the value of the display_pattern variable with this
    typical if expression:

    if (display_pattern == true)

    The program instead uses this shorter if condition:
    
    if (display_pattern)

    In the first case the microcontroller evaluates the expression
    (display_pattern == true) to produce either a true or false
    result that will determine the program flow either into or
    around the code in the if structure.

    Since the expression '(display_pattern == true)' can only be
    true if the display_pattern variable itself is true, the second
    case simply uses the state of the display_pattern variable 
    itself (true/false) to determine the path of program execution.

    Explain which part of the program sets the display_pattern
    variable to true, and which part resets it to false.

    LEDs show you what your program is doing, but sometimes you need
    to see what your program is thinking - that is, the current value
    of a variable at a specific moment. Arduino's Serial.print() and
    Serial.println() functions send text to the Serial Monitor in the
    Arduino IDE (opened from the Tools menu, or Ctrl+Shift+M), making
    them essential tools for understanding and debugging programs. The
    Serial.begin(9600) call in setup() initializes the serial
    connection at 9600 baud - make sure the Serial Monitor is set to
    the same speed.

    Add this line inside the 'if (SW2_pressed)' block to print the
    value of display_pattern each time SW2 is pressed:

    if (SW2_pressed)
    {
        display_pattern = true;
        Serial.print("display_pattern: ");
        Serial.println(display_pattern);
    }

    Run the program, open the Serial Monitor, and press SW2. Do you
    see the output you expected? Now try adding a Serial.println()
    call inside the 'if (display_pattern)' block, just before
    'display_pattern = false', to show the moment it resets:

        Serial.println("display_pattern reset to: false");

    Using Serial.print() to reveal the state of variables at key
    points in your program is one of the most useful debugging
    techniques you will use as a programmer. You'll see it put to
    use again in the next activity.

3.  The third important concept introduced in this program blends
    the features and benefits of the previous two. The SW2_pressed 
    variable is a Boolean variable, just like display_pattern. It
    is assigned a value using this statement:
    
    SW2_pressed = (digitalRead(SW2) == LOW);
  
    The SW2 pin is read and compared with LOW because SW2 is
    connected in an active-low resistor pull-up circuit. If the SW2
    pin is LOW, the SW2_pressed variable will be true, enabling it
    to determine the path of any if condition it's used in.

    And, just like the name BLINK_DELAY, the variable name SW2_pressed
    also carries meaning. The variable SW2_pressed will be true only
    when SW2 is actually pressed.

    Could the program use a similar statement to check for a pushbutton
    being released? Create both an appropriate variable name and an
    expression that could be used to detect if the SW2 pushbutton is
    in an un-pressed state.
    
4.  The last new concept introduced in this program demonstrates a
    method of ensuring that input state remains consistent for the
    duration of each main loop cycle in the program.

    Doing this is not a critical requirement for this program, but it
    does become important in a large, complex program loop. Imagine if
    the state of SW2 needs to be evaluated multiple times, and each
    time SW2 is read using a typical input expression: 

    if (digitalRead(SW2) == LOW)

    There is no guarantee that every read of SW2 during the same
    program loop will produce the same, consistent value. A solution
    to this problem is to store SW2's state in a variable just once
    during each program cycle, and then to have any other parts of
    the program that need to use SW2's state read the value of the
    variable instead of the switch itself:
    
    SW2_pressed = (digitalRead(SW2) == LOW);
    
    The SW2 state now remains consistent for the duration of each main
    loop cycle and, as a bonus, conditional expressions reading the 
    variable now read logically and can be more helpful to anyone
    trying to understand the code:

    if (SW2_pressed)

    This conditional expression is simple, short, meaningful, and
    unambiguous. A programmer trying to understand or add features
    to the code won't have to think about whether the switch is
    active-high or active-low (although somebody had to, earlier),
    making code maintenance easier. Because this method is so clear
    and useful, you'll see it used more in future learning activities.

    Notice the connection between meaningful names and meaningful
    comments - both are forms of communication to future readers.
    Good variable names and constants can make code nearly
    self-explanatory, reducing the need for comments. But comments
    remain valuable for explaining the reasoning behind decisions
    that aren't obvious from the code itself. Aim for both: names
    that describe what a value is, and comments that explain why
    it's used the way it is.

5.  Let's make some extensive changes to the program, with the goal
    of replacing the BLINK_DELAY constant with a blink_delay_ms
    variable, defined in the new program as shown:
    
int blink_delay_ms = 200;

    The blink_delay_ms variable is defined as an 'int' (integer),
    but the lack of the 'const' qualifier means that it will be
    able to change as the program runs.

    Replace all of the existing program code with the new program
    code below, starting from the 'Program Constants' comment down 
    to the closing brace of the loop() function:

*/

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

/*

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

void loop()
{
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

    Can you predict what the program will do and how it works? 
    Which characteristics of the new program code helped you to
    make your prediction or helped you to understand the code?

    As you test the program, try adding Serial.print() statements to
    display the values of blink_delay_ms and display_pattern in the
    Serial Monitor. Which button sets which delay? Can you see
    display_pattern cycling between 1 (true) and 0 (false) as the
    pattern runs?

6.  How does the compiler know that BLINK_DELAY is a constant,
    and that blink_delay_ms is a variable?

7.  Predict what will happen in the above program if two buttons are
    pressed at the same time. Try it! Was your prediction correct?
    Explain why you think this happens.


Programming Activities

1.  Re-create the Start-Stop pushbutton program from Activity B03
    using named buttons and logical variables. (The details are
    repeated below.)

    Create a program that simulates the separate 'Start' and 'Stop'
    buttons that would be found on large, industrial machines. The
    machine (simulated by an LED) should turn on when the 'Start'
    button is pressed, and remain on until the 'Stop' button is
    pressed. Ensure that the machine cannot be turned on while the
    Stop button is being pressed.

2.  Create the code for a 'toggle' button, a type of switch behaviour
    that uses a single button to alternately turn a device or feature
    on and off. In order to do this, the previous state of the button
    must be compared with its current state, and the output should
    only change when the button state changes from not being pressed
    to being pressed. Each new press of the toggle button should
    alternately turn a single LED on or off. Ensure that the LED state
    doesn't change if the toggle button is held for any length of time.

    Hint: You will need three variables - one to store the current LED
    state, one to store the current button state, and one to store the
    previous button state. Start with something like:

bool LED2_on = false;
bool SW2_pressed;
bool SW2_last = false;

    Each loop, save the current SW2_pressed value into SW2_last before
    reading the new button state. A toggle should only happen when
    SW2_pressed is true and SW2_last was false (a new press).

3.  Extend the toggle button program you created, above, so that each
    pushbutton on your circuit toggles a corresponding LED, allowing
    a user to set any light pattern on the circuit simply by pressing
    buttons.

4.  Re-create the bicycle turn signal circuit from Activity B03 using
    named buttons and logical variables. (The details are repeated
    below.)

    Imagine that you're creating a turn signal circuit for a bicycle.
    The circuit design uses four LEDs mounted in a horizontal row
    under the rider's seat, and these will be controlled by two
    pushbuttons mounted on the bicycle's handlebars. Write a program
    to simulate the operation of the turn signal circuit using one
    or more of the LEDs to indicate a turn while its corresponding
    direction button is being held.

    For an extra challenge, add brake functionality or a bell/horn
    feature. Can you make the brake or horn operate while the turn
    signal is in operation? 

*/
