/* ================================================================================
Activity 11 Extension: LED Controller [B11_LED_Controller_Project]
Version: 1.2
Updated: September 16, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPERNano.h header file

Before starting, re-read GE 2, GE 4, and GE 5 from Activity 11:
Non-Blocking Timing.

This sketch reimplements Activity 10's analog output controls
using independent, non-blocking timers rather than a single shared
loop delay. Each control now has its own update rate:

  LED2 dim rate:  how often SW3/SW4 change brightness (ms per step)
  LED3 fade rate: how often the automatic fade advances (ms per step)
  LED4/5 rate:    how often pot readings update LED brightness (ms)

In Activity 10, all of these were coupled to STEP_DELAY - changing
one changed all of them. Here, each rate is set independently.

Controls (same as Activity 10):
  SW3/SW4 - dim/brighten LED2 (at DIM_RATE ms per step)
  SW2     - trigger automatic fade up on LED3
  SW5     - trigger automatic fade down on LED3
  RV1/RV2 - control LED4/LED5 brightness (if POTS_INSTALLED)
=================================================================================*/
// IMPORTANT: Make sure that BEAPERNano.h is accessible as a tab in this project.
#include "BEAPERNano.h"

// ---- Program Configuration -----------
bool POTS_INSTALLED = false;          // Set true if RV1 and RV2 are installed

// ---- Program Constants ---------------
const int LOOP_DELAY  = 1;            // Main loop delay (ms)

const int DIM_RATE    = 20;           // ms between each LED2 brightness step
const int FADE_RATE   = 10;           // ms between each LED3 fade step
const int POT_RATE    = 50;           // ms between pot reads for LED4/LED5

const int BRIGHT_STEP = 5;            // LED2 brightness change per dim step (0-255)
const int FADE_STEP   = 2;            // LED3 brightness change per fade step (0-255)

// ---- Program Variables ---------------
int  led2_brightness = 0;
int  led3_brightness = 0;
int  fade_state      = 0;             // 1 = fading up, -1 = fading down, 0 = idle

// TODO: declare timestamp variables for each timer
// unsigned long last_dim_time  = 0;
// unsigned long last_fade_time = 0;
// unsigned long last_pot_time  = 0;


// ---- Program Functions ---------------

int set_brightness(int led_pin, int brightness)
{
    // Set a PWM LED pin to a brightness level (0-255).
    // Clamps the value to the valid range before setting.
    // Returns the clamped brightness so the caller can store it.
    brightness = constrain(brightness, 0, 255);
    analogWrite(led_pin, brightness);
    return brightness;
}


void setup()
{
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, HIGH);

    pinMode(LED2, OUTPUT);
    pinMode(LED3, OUTPUT);
    pinMode(LED4, OUTPUT);
    pinMode(LED5, OUTPUT);

    pinMode(SW2, INPUT_PULLUP);
    pinMode(SW3, INPUT_PULLUP);
    pinMode(SW4, INPUT_PULLUP);
    pinMode(SW5, INPUT_PULLUP);

    Serial.begin(9600);             // Initialize serial output for debugging
    delay(2000);                    // Give the Serial Monitor time to connect

    Serial.println("LED Lighting Controller");
    Serial.println("SW3/SW4: dim/brighten LED2   SW2/SW5: fade LED3 up/down");

    // TODO: initialise all timestamp variables to millis()
}

void loop()
{
    unsigned long current_time = millis();

    // ---- LED2 dimming timer ----
    // TODO: check if DIM_RATE ms has elapsed since last_dim_time
    //       if so: check SW3/SW4 and update led2_brightness
    //              update last_dim_time = current_time

    // ---- LED3 fade timer ----
    // TODO: check if FADE_RATE ms has elapsed since last_fade_time
    //       if so: check SW2/SW5 to set fade_state
    //              advance fade by FADE_STEP if fade_state != 0
    //              update last_fade_time = current_time

    // ---- Pot polling timer (if installed) ----
    // TODO: check if POT_RATE ms has elapsed since last_pot_time
    //       if so: read RV1/RV2, scale to 0-255, update LED4/LED5
    //              update last_pot_time = current_time

    delay(LOOP_DELAY);
}


/* ================================================================================
Extension Activities
================================================================================

--------------------------------------------------------------------------------
EA 1 - Independent rates
--------------------------------------------------------------------------------

Activity 10 used a single STEP_DELAY = 20ms for everything.
This sketch uses three separate rate constants: DIM_RATE,
FADE_RATE, and POT_RATE. What does this make possible that
Activity 10's version could not do?

Try setting DIM_RATE = 5 and FADE_RATE = 100. In Activity 10
these two values were the same constant. Describe the
difference in feel between the two controls.

--------------------------------------------------------------------------------
EA 2 - Separating step size from step rate
--------------------------------------------------------------------------------

In Activity 10, the fade step size and the fade rate were
combined into a single effect: FADE_STEP=2 brightness units
every STEP_DELAY=20ms. Here they are separated: FADE_STEP
controls how much the brightness changes each step, and
FADE_RATE controls how often steps occur.

What combination of FADE_STEP and FADE_RATE produces the
same overall fade speed as Activity 10's FADE_STEP=2 with
STEP_DELAY=20ms? Is there more than one combination that
produces the same speed? What does each combination feel
like differently?

--------------------------------------------------------------------------------
EA 3 - Polling and idle work
--------------------------------------------------------------------------------

With LOOP_DELAY = 1ms, this program's loop runs approximately
20 times faster than Activity 10's. Does it actually do 20
times as much work? What is the processor doing on the
iterations where no timer threshold is met?

This is the key efficiency insight of non-blocking timing:
the processor checks conditions continuously but only does
meaningful work periodically. On a battery-powered device,
this idle checking still consumes power, which is why advanced
embedded systems use hardware interrupts or sleep modes instead
of polling. Interrupts are an important future concept that
will be introduced in the intermediate activities.

--------------------------------------------------------------------------------
EA 4 - Refactor a program with non-blocking timing
--------------------------------------------------------------------------------

Did one of your previous programs present timing challenges
that can now easily be implemented using non-blocking timing?

Refactoring is the process of rewriting some parts of a program
to simplify or refine their operation, or to improve their
readability (and likely its extensibility), while maintaining the
program's pre-existing functionality. While the goal of a refactor
is not to add new program features and functions, an effective
refactoring may make it simpler to extend the program in the future.
Remember when you made changes to the function code in Activity 8?
These changes added capabilities to the functions while they helped
to simplify the main program.

Identify a previous program that required a careful balance of
function timing and loop timing, and refactor the program to use
non-blocking timing. After you finish, reflect on whether the
refactored program ended up being longer or shorter than the
original, and whether the changes improved its readability or
future extensibility.

*/
