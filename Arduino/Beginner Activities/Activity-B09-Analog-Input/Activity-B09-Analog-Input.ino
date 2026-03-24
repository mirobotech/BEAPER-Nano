/* ================================================================================
Beginner Activity 9: Analog Input [Activity-B09-Analog-Input]
February 28, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPERNano.h header file

Analog jumper settings for this activity:
  JP1 - Enviro. (selects ambient light sensor Q4)
  JP2 - Enviro. (selects temperature sensor U4)
  JP3 - Enviro. (selects potentiometer RV1)
  JP4 - Enviro. (selects potentiometer RV2)
=================================================================================*/
// IMPORTANT: Make sure that BEAPERNano.h is accessible as a tab in this project.
#include "BEAPERNano.h"   // Define BEAPER Nano I/O devices

// ---- Program Constants ----------------
const int STEP_DELAY  = 100;          // Main loop delay (ms)
const int LIGHT_HIGH  = 750;          // Light threshold: LED turns on above this
const int LIGHT_LOW   = 550;          // Light threshold: LED turns off below this
const int TONE_MIN    = 200;          // Minimum theremin frequency (Hz)
const int TONE_MAX    = 4000;         // Maximum theremin frequency (Hz)

// ---- Program Variables ----------------
bool light_on = false;                // Hysteresis state for light threshold


// ---- Program Functions ----------------

float map_range(int value, int in_min, int in_max, int out_min, int out_max)
{
    // Map a value from one range to another, returning a float result.
    // Cast to float before dividing to avoid integer truncation.
    // Use (int)map_range(...) when an integer result is required.
    return out_min + (float)(value - in_min) * (out_max - out_min) / (in_max - in_min);
}

void show_bar(int level, int max_level)
{
    // Display a bar graph on LEDs 2-5 proportional to level out of max_level.
    // Thresholds are centred in each quarter so all LEDs can light fully.
    digitalWrite(LED2, level > max_level * 1 / 8 ? HIGH : LOW);
    digitalWrite(LED3, level > max_level * 3 / 8 ? HIGH : LOW);
    digitalWrite(LED4, level > max_level * 5 / 8 ? HIGH : LOW);
    digitalWrite(LED5, level > max_level * 7 / 8 ? HIGH : LOW);
}

float read_temp_c()
{
    // Read U4 analog temperature sensor and return temperature in degrees C.
    // Formula for MCP9700A: Temp(C) = (Voltage - 0.5V) / 0.01 V/C
    float voltage = (float)analogRead(U4) * 3.3 / 1023.0;
    return (voltage - 0.5) / 0.01;
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

    Serial.println("Activity 9: Analog Input");
    Serial.println("JP1=Enviro, JP2=Enviro, JP3=Enviro, JP4=Enviro");
    Serial.println();
}

void loop()
{
    // Part 1: Read potentiometer RV1 and display as bar graph and raw value
    int rv1 = analogRead(RV1);
    show_bar(rv1, 1023);
    Serial.print("RV1: "); Serial.print(rv1); Serial.print("  ");

    // Part 2: Read potentiometer RV2 and use it to control the tone frequency
    int rv2 = analogRead(RV2);
    int frequency = (int)map_range(rv2, 0, 1023, TONE_MIN, TONE_MAX);
    tone(LS1, frequency);
    Serial.print("RV2: "); Serial.print(rv2);
    Serial.print(" Freq: "); Serial.print(frequency);
    Serial.print(" Hz  ");

    // Part 3: Read sensors and convert to meaningful units
    int light = light_level();
    float temp = read_temp_c();
    Serial.print("Light: "); Serial.print(light);
    Serial.print(" Temp: "); Serial.print(temp, 1);
    Serial.print(" C  ");

    // Part 4: Threshold detection with hysteresis on light sensor
    if (light_on)
    {
        if (light < LIGHT_LOW)
        {
            light_on = false;
            digitalWrite(LED_BUILTIN, HIGH);  // Status LED on
        }
    }
    else
    {
        if (light > LIGHT_HIGH)
        {
            light_on = true;
            digitalWrite(LED_BUILTIN, LOW);   // Status LED off
        }
    }

    Serial.print("Light LED: "); Serial.println(light_on ? "ON" : "OFF");
    delay(STEP_DELAY);
}


/*
Guided Exploration

All of the programs so far have used digital I/O - inputs and outputs
that are either fully on or fully off. The real world is rarely that
simple: temperature, light, sound, and position all vary continuously
across a range of values. Microcontrollers read these continuously
varying physical quantities using an Analog to Digital Converter, or
ADC, which turns a voltage into a number the program can work with.
The three functions in this program apply the patterns from Activity
8 - parameters, return values, and encapsulation - to sensor data,
converting raw ADC readings into bar graph displays, musical tones,
and temperatures in degrees Celsius. This activity also works with
integer and float numeric types in detail - the Numeric Types sidebar
is a useful reference if you want to review how these types work.

1.  The Arduino Nano ESP32's ADC returns values from 0 to 1023 -
    a 10-bit range. This means the ADC divides the full input
    voltage range (0 to 3.3V) into 1024 steps, giving a resolution
    of about 3.2mV per step.

    When you turn RV1 fully anti-clockwise, 'analogRead(RV1)'
    returns approximately 0. Fully clockwise returns approximately
    1023. Observe the Serial Monitor while slowly rotating RV1
    from one extreme to the other. Is the change perfectly smooth,
    or do you notice any irregularities?

    Why does the ADC use a range of 0-1023 specifically, rather
    than 0-100 or 0-1000? Think about how 1024 relates to powers
    of 2 and the binary number system from Activity 7. The Numeric
    Types sidebar explains why integer sizes are always powers of 2.

2.  The 'map_range()' function converts a value from one numeric
    range to another:

    float map_range(int value, int in_min, int in_max,
                    int out_min, int out_max)
    {
        return out_min + (float)(value - in_min) *
               (out_max - out_min) / (in_max - in_min);
    }

    Trace through this formula with value=511 (approximately
    halfway), in_min=0, in_max=1023, out_min=200, out_max=4000.
    What frequency would this produce? Does it match what you
    would expect for a value halfway through the input range?

    Notice the '(float)' cast before '(value - in_min)'. In
    Arduino C, dividing two integers always produces an integer
    result - the remainder is discarded. The cast forces the
    calculation to use floating point arithmetic, preserving the
    decimal portion of the result.

    The main loop converts the result back to int before passing
    it to 'tone()':

    int frequency = (int)map_range(rv2, 0, 1023, TONE_MIN, TONE_MAX);

    Why is the '(int)' cast necessary here? In Activity 8 GE8
    you found that Arduino's 'tone()' function expects integer
    arguments. Try removing the cast and passing the float result
    directly - does the compiler warn you, or does the behaviour
    change at runtime?

    Arduino also provides a built-in 'map()' function that serves
    the same purpose. The key difference is that 'map()' uses
    integer arithmetic throughout, so it would truncate any
    fractional part of the result internally - before the explicit
    '(int)' cast in this program gets the chance to. For mapping
    ADC values to tone frequencies the final result is identical,
    but for output ranges that require fractional precision (such
    as displaying a sensor value as a percentage) 'map_range()'
    gives a more accurate result.

3.  The 'show_bar()' function divides the LED range into four
    bands, with thresholds centred in each quarter:

    digitalWrite(LED2, level > max_level * 1 / 8 ? HIGH : LOW);
    digitalWrite(LED3, level > max_level * 3 / 8 ? HIGH : LOW);
    digitalWrite(LED4, level > max_level * 5 / 8 ? HIGH : LOW);
    digitalWrite(LED5, level > max_level * 7 / 8 ? HIGH : LOW);

    The thresholds are at 1/8, 3/8, 5/8, and 7/8 of max_level -
    the midpoints of each quarter. This means each LED represents
    one quarter of the input range, and all four LEDs can light
    when the value is high enough.

    Trace through the function with max_level=1023 and these
    values of level: 0, 128, 384, 640, 896, 1023.
    Which LEDs are lit for each value?

    In Arduino C, dividing two integers always produces an integer
    result - any remainder is discarded. Integer division is exactly
    what is needed here: threshold values should be whole numbers
    since ADC results are integers. You will explore this further
    in GE5.

    Notice the operator precedence: 'max_level * 1 / 8' is
    evaluated left to right as '(max_level * 1) / 8'. What would
    happen if it were evaluated as 'max_level * (1 / 8)' instead?
    Calculate '1 / 8' as integer division and explain the effect.

    Compare 'show_bar()' with 'indicate_attempts()' from
    Activity 8. Both display a level on four LEDs, but
    'show_bar()' works with any maximum value, not just 4.
    What did making the function more general require, and what
    did it make possible?

4.  Part 2 maps RV2 to a tone frequency, creating a theremin-like
    instrument. The tone plays continuously because Arduino's
    'tone()' function, when called with only two arguments
    (pin and frequency), plays until 'noTone()' is called.

    The function 'read_keypad()' from Activity 8 is not suitable
    for use inside a loop that needs to keep updating sensor
    readings and tone frequency. What property of 'read_keypad()'
    would cause problems here? Think about what the function does
    while it is waiting for a button press.

    Modify loop() to silence the tone while SW5 is held down,
    using 'digitalRead(SW5) == LOW' as the check and
    'noTone(LS1)' to stop the sound. The tone should resume
    automatically on the next iteration when SW5 is released.

5.  In Arduino C, every variable and function has a declared type
    that determines what kind of value it can hold or return. The
    two most common numeric types are 'int' (whole numbers, no
    decimal point) and 'float' (numbers with a decimal point).
    Dividing two integers in Arduino C always truncates the result
    - any fractional part is silently discarded.

    Add these temporary print statements to loop() after the
    existing Serial.print calls, and observe the Serial Monitor:

    Serial.println((int)(3.3 / 2));      // Integer cast of float division
    Serial.println(3.3 / 2);            // Float division
    Serial.println(3 / 2);              // Integer division
    Serial.println((float)3 / 2);       // Cast forces float division

    What does each line print? Notice that '3 / 2' gives 1, not
    1.5 - the fractional part is silently discarded. This is why
    'read_temp_c()' uses '(float)analogRead(U4)' before dividing:
    without the cast, the division would be integer arithmetic and
    the temperature conversion would be significantly less accurate.

    Remove the temporary print statements once you have recorded
    your observations.

6.  The 'read_temp_c()' function converts the raw ADC reading to
    degrees Celsius using the MCP9700A temperature sensor's
    characteristics. The sensor outputs 0.5V at 0°C and increases
    by 10mV (0.01V) for every degree Celsius above zero.

    The conversion has two steps. First, the raw ADC value is
    converted to a voltage:

    float voltage = (float)analogRead(U4) * 3.3 / 1023.0;

    Why is the raw value multiplied by 3.3 and divided by 1023?
    Note that 1023.0 (with a decimal point) ensures float division
    even without an explicit cast - what would happen if it were
    written as 1023 instead?

    Then the voltage is converted to temperature:

    return (voltage - 0.5) / 0.01;

    Why is 0.5 subtracted before dividing? Why divide by 0.01
    rather than multiplying by 100 (which would give the same
    result mathematically)? At what raw ADC value would the
    sensor read exactly 0°C? Calculate it and verify by adding
    a temporary Serial.print inside 'read_temp_c()'.

    The board has been running for a while when you take a reading.
    Would you expect U4 to read exactly room temperature, or
    slightly warmer? What does this mean for how accurately U4
    measures the ambient temperature of the surrounding environment?

7.  Before tuning the threshold values for the hysteresis light
    detector, it helps to know the actual range of values the light
    sensor produces in your environment. Hysteresis is a technique
    that uses two thresholds - one to turn something on, and a lower
    one to turn it off - to prevent flickering when a reading hovers
    near a single boundary. GE8 covers this in detail; first, take
    some measurements to calibrate the thresholds to your environment.

    Temporarily add two variables to track the minimum and maximum
    light readings. Add them at the top of loop():

    static int light_min = 1023;
    static int light_max = 0;

    The 'static' keyword preserves a local variable's value between
    calls to loop() - without it, the variable would reset to its
    initial value on every iteration. Inside loop(), after reading
    'light', add:

    if (light < light_min) light_min = light;
    if (light > light_max) light_max = light;
    Serial.print("Min: "); Serial.print(light_min);
    Serial.print(" Max: "); Serial.println(light_max);

    Run the program and slowly cover Q4 completely with your
    finger, then uncover it fully and hold it near a bright light
    source. Record the minimum and maximum values you observe.
    These represent the practical range of your sensor in its
    current environment.

    Remove the tracking code once you have your readings. You
    will use these values to set appropriate LIGHT_HIGH and
    LIGHT_LOW thresholds in GE8.

8.  A single threshold would turn the status LED on when light
    exceeds it and off when light falls below it - but when the
    light level hovers near the boundary, the LED flickers
    rapidly as the reading crosses the threshold many times
    per second.

    Hysteresis solves this with two thresholds: the LED turns
    on only when light rises above LIGHT_HIGH, and turns off
    only when it falls below LIGHT_LOW. The gap between them
    creates a band of values where the LED holds its current
    state regardless of small fluctuations.

    The 'light_on' variable is declared before loop(), not inside
    it. Why is this essential to the hysteresis behaviour? What
    would happen if it were declared inside loop()?

    Using the minimum and maximum readings from GE7, set
    LIGHT_HIGH to approximately 75% of the way between your
    minimum and maximum, and LIGHT_LOW to approximately 25%.
    Slowly cover and uncover Q4 while watching the status LED.
    Does the LED respond without flickering near the transition?

    Reduce the gap between LIGHT_HIGH and LIGHT_LOW gradually
    until flickering begins. What is the minimum gap that prevents
    flickering under your lighting conditions? What happens if
    you set LIGHT_LOW higher than LIGHT_HIGH?

9.  The main loop prints all sensor readings using multiple
    Serial.print() calls followed by a final Serial.println()
    to end the line. This keeps each loop iteration on one line
    in the Serial Monitor, making it easier to observe all values
    changing together.

    Add a loop counter at the top of loop():

    static int loop_count = 0;
    loop_count++;

    Print 'loop_count' at the start of each line. The 'static'
    keyword preserves the count between calls to loop() - without
    it, loop_count would reset to 0 on every iteration.

    Observe the rate at which lines appear in the Serial Monitor.
    What STEP_DELAY value gives the best balance between a fast
    sensor update rate and output that is readable? Human perception
    has a limit of around 50-100ms - below that threshold, reducing
    STEP_DELAY further will not make the sensor response feel more
    immediate, but the Serial Monitor output will become harder
    to read.


Extension Activities

These activities build on the sensor-reading and function patterns
from the starter program. Use named constants for all threshold and
scaling values, and named functions for any reusable behaviour.

1.  Modify 'show_bar()' so that it accepts a third bool argument
    'invert' that defaults to false. When invert is true, the bar
    fills from right to left - LED5 lights first at low values,
    LED2 last at high values. Use this to display the light level
    inverted, so that a darker environment produces a fuller bar.

    In Arduino C, default parameter values are declared in the
    function header:

    void show_bar(int level, int max_level, bool invert = false);

    Call 'show_bar(light, 1023, true)' for the light display and
    verify it responds correctly. What does this tell you about
    how default parameters make functions more flexible without
    requiring changes to existing calls?

2.  Write a 'temp_trend()' function that compares the current
    temperature with the previous reading and returns an int:
    1 for rising, -1 for falling, 0 for steady. Store the
    previous reading in a static variable inside the function.
    Print a corresponding symbol ('+', '-', '=') alongside the
    temperature on each iteration.

    What threshold difference in degrees C makes a useful steady
    band that avoids constant switching due to sensor noise? The
    BEAPER Nano uses U4 as its only temperature sensor - how
    might the board's own heat output affect the readings over
    time, and what does this mean for measuring slow changes in
    ambient temperature?

3.  Create a data logger that records the minimum and maximum
    values seen for RV1, light level, and temperature since the
    program started. Print the current value, minimum, and maximum
    for each sensor on every iteration. When SW5 is pressed,
    reset all minimums and maximums to their starting values.

    Think carefully about initial values: what should the minimum
    start at so that the first real reading always replaces it?
    What should the maximum start at? What happens to your
    approach if the sensor range is not known in advance?

4.  Write a 'calibrate()' function that reads a given analog pin
    a specified number of times, discards the highest and lowest
    values, and returns the average of the remainder as a float.
    Use 'int pin' and 'int samples' as parameters.

    Call this function once in setup() for RV1 and the light
    sensor analog pins, storing the results as baseline values.
    In loop(), display the difference between the current reading
    and the baseline rather than the raw value.

    This technique - averaging after discarding the extremes - is
    called a trimmed mean, and it reduces the effect of occasional
    noisy readings on the result. What effect does the number of
    samples have on the startup time and on the noise reduction?

5.  Build a simple environmental monitor using all available analog
    inputs. Display temperature in degrees C and light as a
    percentage of the calibrated maximum. Use RV1 to set a
    temperature alarm threshold and RV2 to set a light alarm
    threshold. When either sensor exceeds its threshold, sound
    a distinctive alarm tone and flash the corresponding LED.

    Structure the program using functions for each major task:
    reading and converting each sensor, checking each threshold,
    and triggering each alarm. How does organising the program
    this way compare to writing it as a single sequential block?
    What would make it harder to add a third sensor later?

*/
