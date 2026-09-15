/* ================================================================================
Project: RGB Controller [B10_RGB_Controller_Project]
Version: 1.2
Updated: September 14, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPERNano.h header file

Before starting this project, re-read GE 1 and GE 2 from
Activity 10: Analog Output.

The Arduino Nano ESP32 module includes a built-in RGB LED driven
by three independent PWM channels - one each for red, green, and
blue. Mixing these three channels at different intensities produces
a wide range of colours.

Arduino's analogWrite() uses 8-bit values (0-255), so RGB
brightness values in this project range from 0 (off) to 255
(full brightness).

The RGB LED elements are active-LOW - a lower duty cycle
produces more light. The set_rgb() function handles this
inversion automatically so that 0 always means off and 255
always means full brightness.

Colour mixing reference:
  Red   only          = Red
  Green only          = Green
  Blue  only          = Blue
  Red + Green         = Yellow
  Red + Blue          = Magenta
  Green + Blue        = Cyan
  Red + Green + Blue  = White (or near-white)

Controls:
  RV1 - red channel brightness (if pots installed)
  RV2 - green channel brightness (if pots installed)
  SW2/SW3 - step red channel down/up (if no pots)
  SW4/SW5 - step green channel down/up (if no pots)
================================================================================*/
// IMPORTANT: Make sure that BEAPERNano.h is accessible as a tab in this project.
#include "BEAPERNano.h"

// ---- Program Configuration -----------
bool POTS_INSTALLED = false;          // Set true if RV1 and RV2 are installed

// ---- Program Constants ---------------
const int STEP_DELAY   = 20;          // Main loop delay (ms)
const int COLOUR_STEP  = 8;           // Brightness change per button press (0-255)

// ---- Program Variables ---------------
int red_brightness   = 0;            // Current red channel (0-255)
int green_brightness = 0;            // Current green channel (0-255)
int blue_brightness  = 0;            // Current blue channel (0-255)


// ---- Program Functions ---------------

void set_rgb(int red, int green, int blue)
{
    // Set the RGB LED to the given red, green, and blue brightness values.
    // Clamps each value to 0-255 and inverts for active-LOW hardware.
    red = constrain(red, 0, 255);
    // TODO: constrain green, blue to 0-255
    analogWrite(LED_RED, 255 - red);    // Invert for active-LOW
    // TODO: set green, blue RGB LED intensity (inverted, as above)
}

void rgb_off()
{
    // Turn off the RGB LED.
    set_rgb(0, 0, 0);
}


void setup()
{
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, HIGH);

    // Configure RGB LED pins as PWM outputs
    pinMode(LED_RED,   OUTPUT);
    pinMode(LED_GREEN, OUTPUT);
    pinMode(LED_BLUE,  OUTPUT);

    pinMode(SW2, INPUT_PULLUP);
    pinMode(SW3, INPUT_PULLUP);
    pinMode(SW4, INPUT_PULLUP);
    pinMode(SW5, INPUT_PULLUP);

    // Configure the ADC for 16-bit readings (0-65535), matching the
    // MicroPython board module's read_u16()-style scaling - see
    // Activity 10, GE1.
    analogReadResolution(16);

    Serial.begin(9600);
    delay(2000);                       // Give Serial Monitor time to
                                        // connect, without blocking
                                        // forever if it's never opened

    rgb_off();
    Serial.println("RGB Controller");
    if (POTS_INSTALLED)
        Serial.println("RV1: red   RV2: green");
    else
        Serial.println("SW2/SW3: red down/up   SW4/SW5: green down/up");
}

void loop()
{
    if (POTS_INSTALLED)
    {
        red_brightness = map(RV1_level(), 0, 65535, 0, 255);
        // TODO: set green_brightness or blue_brightness from RV2
    }
    else
    {
        if (digitalRead(SW2) == LOW)
            red_brightness -= COLOUR_STEP;
        else if (digitalRead(SW3) == LOW)
            red_brightness += COLOUR_STEP;
        // TODO: set green_brightness or blue_brightness using SW4/SW5

        red_brightness = constrain(red_brightness, 0, 255);
        // TODO: constrain green_brightness, blue_brightness to 0-255
    }

    set_rgb(red_brightness, green_brightness, blue_brightness);

    Serial.print("R: "); Serial.print(red_brightness);
    Serial.print("  G: "); Serial.print(green_brightness);
    Serial.print("  B: "); Serial.println(blue_brightness);

    delay(STEP_DELAY);
}


/* ================================================================================
Extension Activities
================================================================================

--------------------------------------------------------------------------------
EA 1 - Complete the skeleton
--------------------------------------------------------------------------------

Complete the set_rgb() function to constrain and set the green
and blue LED intensities. This program controls two of the three
red, green, and blue LED elements using either two potentiometers,
or two sets of up/down pushbuttons (EA 2, below, lets you configure
a method to control all three). Complete the missing sections of
loop() to control the green channel, as described in Controls
above.

--------------------------------------------------------------------------------
EA 2 - Add blue channel control
--------------------------------------------------------------------------------

Add blue channel control. With four buttons and two
potentiometers controlling only red and green, choose one
of these approaches for blue:

a) Derive blue automatically:

Example code:

blue_brightness = 255 - red_brightness - green_brightness;
blue_brightness = constrain(blue_brightness, 0, 255);

b) Add a mode toggle: pressing SW2 and SW5 together switches
   between (red + green) mode and (blue + brightness) mode.

c) If using potentiometers, use HSV mixing from EA 3, giving
   full colour control from two knobs.

--------------------------------------------------------------------------------
EA 3 - HSV colour mixing
--------------------------------------------------------------------------------

HSV (Hue-Saturation-Value) colour mixing is more intuitive
than direct RGB for many applications. Hue is expressed in
degrees around the colour wheel (0=red, 120=green, 240=blue,
360=red again). Saturation controls vividness as a percentage
(100=full colour, 0=white). Value controls overall brightness
as a percentage (0=off, 100=full brightness).

A ready-made 'hsvToRGB(h, s, v)' function is available in
colour.h - add '#include "colour.h"' near the top of your
program, alongside the existing '#include "BEAPERNano.h"'
line, to use it. It returns an 'RGB' structure with '.r',
'.g', and '.b' fields, using integer arithmetic throughout so
no float values are involved:

Example code:

#include "colour.h"

Use RV1 to sweep hue across the full colour wheel and RV2 to
control brightness, with saturation fixed at 100:

Example code:

int hue = map(RV1_level(), 0, 65535, 0, 360);
int val = map(RV2_level(), 0, 65535, 0, 100);
RGB colour = hsvToRGB(hue, 100, val);
set_rgb(colour.r, colour.g, colour.b);

Trace through 'hsvToRGB()' with h=0, h=120, and h=240 (all
with s=100, v=100) and verify that the expected primary colours
- red, green, and blue - appear on the LED.

Open colour.h and find the 'long' casts inside 'hsvToRGB()'.
Why are they necessary here even though 'h', 's', and 'v' are
declared as plain 'int' parameters? Consider the largest
possible value of an expression like 'v * (255 - s)' before
it is divided - does it fit within a 16-bit int's range? The
Numeric Types sidebar explains why this matters on some of the
boards this curriculum supports.

--------------------------------------------------------------------------------
EA 4 - fade_to() and a colour sequence
--------------------------------------------------------------------------------

Write a 'fade_to(int tr, int tg, int tb, int steps)' function
that smoothly transitions the RGB LED from its current colour
to a target. Use it to cycle through a sequence of preset colours
with smooth transitions, using an array of target colours:

Example code:

const int colours[][3] = {
  { 255,   0,   0 },   // Red
  { 255, 128,   0 },   // Orange
  { 255, 255,   0 },   // Yellow
  {   0, 255,   0 },   // Green
  {   0,   0, 255 },   // Blue
};

--------------------------------------------------------------------------------
EA 5 - NeoPixel preview
--------------------------------------------------------------------------------

NeoPixels (WS2812B addressable LEDs) also use 8-bit RGB values
(0-255), the same range as this project - and the same range
colour.h's functions already use, so no scaling is needed. The
Arduino NeoPixel library (Adafruit_NeoPixel) controls strips of
individually addressable LEDs using a single data wire. The
colour mixing and HSV concepts from this project apply directly
to NeoPixel programming.

Research 'Adafruit_NeoPixel' and note how colours are set using
setPixelColor(index, red, green, blue). The 'set_rgb()' function
you wrote here, and 'hsvToRGB()' from colour.h, will both work
with NeoPixels with only minor changes.

*/
