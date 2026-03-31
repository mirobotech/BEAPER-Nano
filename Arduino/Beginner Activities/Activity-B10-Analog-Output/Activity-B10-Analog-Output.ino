/* ================================================================================
Beginner Activity 10: Analog Output [BEAPERNano-Activity-B10-Analog-Output]
March 31, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPERNano.h header file

Analog jumper settings for this activity:
  JP3 - Enviro. (selects potentiometer RV1, if installed)
  JP4 - Enviro. (selects potentiometer RV2, if installed)
=================================================================================*/
// IMPORTANT: Make sure that BEAPERNano.h is accessible as a tab in this project.
#include "BEAPERNano.h"   // Define BEAPER Nano I/O devices

// ---- Program Configuration ------------
const bool POTS_INSTALLED = false;    // Set true if RV1 and RV2 are installed

// ---- Program Constants ----------------
const int STEP_DELAY  = 20;           // Main loop delay (ms) - ~50 iterations/sec
const int BRIGHT_STEP = 8;            // LED2 brightness change per loop (SW3/SW4)
const int FADE_STEP   = 2;            // LED3 brightness change per fade iteration

// ---- Program Variables ----------------
int led2_brightness = 0;              // Current LED2 brightness (0-255)
int led3_brightness = 0;              // Current LED3 brightness (0-255)
int fade_state = 0;                   // LED3 fade: 1 = fading up, -1 = fading down, 0 = idle


// ---- Program Functions ----------------

int set_brightness(int pin, int brightness)
{
    // Set a PWM LED pin to a brightness level (0-255).
    // Clamps the value to the valid range before setting.
    // Returns the clamped brightness so the caller can store it.
    if (brightness < 0)   brightness = 0;
    if (brightness > 255) brightness = 255;
    analogWrite(pin, brightness);
    return brightness;
}


void setup()
{
    // Configure Arduino Nano ESP32 status LED as output
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, HIGH);  // Status LED on

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
    while (!Serial);                  // Wait for serial port to be ready

    Serial.println("Activity 10: Analog Output");
    Serial.println("SW3/SW4: dim/brighten LED2");
    Serial.println("SW2: fade LED3 up to full  SW5: fade LED3 down to off");
    if (POTS_INSTALLED)
        Serial.println("RV1/RV2: control LED4/LED5 brightness");
    Serial.println();
}

void loop()
{
    // Update button states
    bool SW2_pressed = digitalRead(SW2) == LOW;
    bool SW3_pressed = digitalRead(SW3) == LOW;
    bool SW4_pressed = digitalRead(SW4) == LOW;
    bool SW5_pressed = digitalRead(SW5) == LOW;

    // SW3 dims LED2, SW4 brightens LED2 (one step per loop while held)
    if (SW3_pressed)
    {
        led2_brightness -= BRIGHT_STEP;
        led2_brightness = set_brightness(LED2, led2_brightness);
    }
    else if (SW4_pressed)
    {
        led2_brightness += BRIGHT_STEP;
        led2_brightness = set_brightness(LED2, led2_brightness);
    }
    Serial.print("LED2 brightness: "); Serial.print(led2_brightness);

    // SW2 triggers automatic fade up, SW5 triggers automatic fade down
    // Once triggered, the fade continues without the button being held
    if (SW2_pressed && fade_state != 1)
        fade_state = 1;                   // Begin fading up
    else if (SW5_pressed && fade_state != -1)
        fade_state = -1;                  // Begin fading down

    // Advance LED3 fade by one step per loop iteration
    if (fade_state == 1)
    {
        led3_brightness += FADE_STEP;
        led3_brightness = set_brightness(LED3, led3_brightness);
        if (led3_brightness >= 255)
            fade_state = 0;               // Fade up complete
    }
    else if (fade_state == -1)
    {
        led3_brightness -= FADE_STEP;
        led3_brightness = set_brightness(LED3, led3_brightness);
        if (led3_brightness <= 0)
            fade_state = 0;               // Fade down complete
    }
    Serial.print("  LED3 brightness: "); Serial.println(led3_brightness);

    // RV1 and RV2 control LED4 and LED5 brightness directly (if installed)
    if (POTS_INSTALLED)
    {
        set_brightness(LED4, RV1_level() / 4);
        set_brightness(LED5, RV2_level() / 4);
    }

    delay(STEP_DELAY);
}


/*
Guided Exploration

Activity 9 introduced analog input - reading continuously varying
physical quantities from sensors and converting raw ADC values into
meaningful numbers. This activity introduces the complementary
direction: analog output, using Pulse Width Modulation (PWM) to
produce continuously varying output levels from a digital signal.
The same concepts from Activity 9 - scaling values between ranges,
clamping to valid bounds, and encapsulating hardware access in
functions - reappear here on the output side. By the end of this
activity you will understand how LEDs, motors, servos, and speakers
are all controlled through the same underlying PWM mechanism.

1.  All of the outputs used so far have been digital - fully on or
    fully off. Pulse Width Modulation (PWM) is a technique for
    producing an analog-like output using a digital signal. Rather
    than varying a voltage directly, PWM switches the output rapidly
    between HIGH and LOW. The proportion of time the signal spends
    HIGH is called the duty cycle.

    A duty cycle of 0% means the signal is always LOW - the LED is
    off. A duty cycle of 100% means the signal is always HIGH - the
    LED is at full brightness. A duty cycle of 50% means the signal
    spends equal time HIGH and LOW, and the LED appears at roughly
    half brightness because the eye averages the light energy over
    time, perceiving rapid switching as a steady intermediate level.

    Arduino's 'analogWrite()' function accepts a value from 0 to 255
    - an 8-bit range where 0 means 0% duty cycle and 255 means 100%.
    Calculate the duty cycle percentage for these 'analogWrite()'
    values: 0, 64, 128, 191, 255.

    Why is an 8-bit range (0-255) used rather than simply 0-100?
    Think about how many distinct brightness levels each range
    provides. The Numeric Types sidebar explains why hardware ranges
    are expressed as powers of 2.

2.  In Arduino, 'analogWrite()' works directly on any PWM-capable pin
    using the pin constant from the board header - no separate object
    is needed:

    analogWrite(LED2, brightness);   // Set LED2 PWM duty cycle

    Open BEAPERNano.h and find where 'LED2' is defined. It is a
    'const uint8_t' constant holding the GPIO pin number. The same
    pin constant used for 'digitalWrite()' in earlier activities is
    used here for 'analogWrite()' - the function call determines
    whether the pin behaves as a digital or PWM output.

    This is the first time in the Activities that the program uses
    a pin for analog output. Which other pins in BEAPERNano.h could
    be used with 'analogWrite()'? Look for pins that are shared with
    PWM-capable hardware in the header comments or in the Arduino
    Nano ESP32 datasheet.

3.  Arduino's 'analogWrite()' uses a fixed PWM frequency set by the
    hardware timer for each pin.

    The default PWM frequency on the Arduino Nano ESP32 is typically
    in the range of 1-5 kHz, which appears steady to the eye for LED
    dimming. To observe the effect of PWM switching directly, try
    waving a PWM-dimmed LED quickly through the air in a darkened
    room - at a lower duty cycle you should see a dotted trail rather
    than a solid line, which reveals the rapid on-off switching.

    Why do motor controllers typically use PWM frequencies of
    10 kHz or higher even though motors have no visual response?
    What would you hear if a motor were driven at 500 Hz?

4.  This program controls LED2 and LED3 in two fundamentally
    different ways, and the difference is important.

    Holding SW3 or SW4 dims or brightens LED2 by one BRIGHT_STEP
    value on every loop() iteration while each button is held,
    providing direct, manual control.

    Pressing SW2 or SW5 triggers an automatic fade on LED3 that
    continues on its own until maximum or minimum brightness is
    reached. Look at the 'fade_state' variable: it is set to 1 or
    -1 when a button is pressed, and the main loop advances the
    fade by FADE_STEP on every iteration until the limit is hit.

    Preventing a value from exceeding its bounds is known as
    'clamping'. How are both led2_brightness and led3_brightness
    clamped, or prevented from going below the minimum value of
    0 or above the maximum value of 255 for the 'analogWrite()'
    fuction? What do you notice about the way the statements
    implementing the clamping operation have been written?

5.  The fade rate (how quickly LED3 changes) depends on two things:
    FADE_STEP and STEP_DELAY. Calculate how long a complete fade
    from 0 to 255 takes with the current values. What FADE_STEP
    would make the fade take exactly 2 seconds?

    Now consider: what if the loop also needed to check a slow
    sensor taking 50ms per reading? The fade would slow down
    because each loop iteration takes longer. The fade rate is
    coupled to everything else in the loop. In Activity 11 you
    will learn a technique that gives each output its own
    independent update rate, solving this coupling problem.

6.  The 'POTS_INSTALLED' constant is a configuration flag - a
    boolean value set once at the top of the program to match the
    hardware, rather than something that changes during execution.

    This pattern is common in embedded firmware. Rather than the
    program trying to detect whether hardware is present (which
    can be unreliable for simple analog devices), the programmer
    declares the configuration explicitly, making assumptions
    visible and easy to change.

    If POTS_INSTALLED is false, what happens to LED4 and LED5?
    Their pins are still configured as outputs in setup(). What
    is their state when the POTS_INSTALLED block never runs?

    When POTS_INSTALLED is true, 'RV1_level()' returns 0-1023 but
    'analogWrite()' accepts 0-255. The program scales the reading
    with a simple integer division:

    set_brightness(LED4, RV1_level() / 4);

    Why does dividing by 4 work here? What is the maximum value of
    'RV1_level() / 4', and does it fit within the 0-255 range?
    When would 'map()' be needed instead of a division by 4?

7.  This program runs in a continuous loop() function, checking all
    inputs and updating all outputs on every iteration at a rate set
    by STEP_DELAY. This fixed-rate control loop is a fundamental
    embedded systems pattern - the program runs at a known rate,
    processing all inputs and producing all outputs in each pass.

    Count the total number of pin reads and 'analogWrite()' calls
    that happen in one loop() iteration with POTS_INSTALLED = true
    and all buttons released. How many iterations per second does
    the program run at STEP_DELAY = 20ms?

    The fade and dimming behaviours share the same loop. What
    would happen to LED2's dimming responsiveness if FADE_STEP
    were very small, requiring thousands of iterations to complete
    a fade? Would LED2 still respond immediately to SW3 and SW4?
    This is the same coupling problem described in GE4, seen from
    a different angle.


Extension Activities

    The following activities each explore a specific area of analog
    output - sound, motor control, servos, or RGB colour. Each
    begins in a separate project file that sets up the hardware
    configuration and provides a partial program structure for you
    to complete. Open the relevant project file alongside this one.

    Choose the output type or types most relevant to your interests
    or project, or work through all of them. When opening a project
    file, refer to the guided exploration questions listed for that
    activity, as the project builds directly on them.

1.  Sound output using PWM
    Refer to: GE1, GE3
    Open: B10-Sound-Player-Project

2.  Motor control using PWM
    Refer to: GE1, GE2, GE3, GE4
    Open: B10-Motor-Controller-Project

3.  Servo control using PWM
    Refer to: GE1, GE3
    Open: B10-Servo-Controller-Project

4.  RGB colour output using PWM
    Refer to: GE1, GE2
    Open: B10-RGB-Controller-Project

*/
