/* ================================================================================
Project: RGB Controller [B10-RGB-Controller-Project]
March 31, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPERNano.h header file

Before starting this project, re-read GE1 and GE2
from Activity 10: Analog Output.

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

Note: This project applies to BEAPER Nano only. BEAPER Pico and
ARPS-2 do not have on-board RGB LEDs. For those platforms, RGB
output can be achieved using a NeoPixel LED strip - see the
future NeoPixel activity.
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
    red   = constrain(red,   0, 255);
    green = constrain(green, 0, 255);
    blue  = constrain(blue,  0, 255);
    analogWrite(LED_RED,   255 - red);    // Invert for active-LOW
    analogWrite(LED_GREEN, 255 - green);
    analogWrite(LED_BLUE,  255 - blue);
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

    Serial.begin(9600);
    while (!Serial);

    rgb_off();
    Serial.println("RGB Controller");
    if (POTS_INSTALLED)
        Serial.println("RV1: red   RV2: green");
    else
        Serial.println("SW2/SW3: red down/up   SW4/SW5: green down/up");
    Serial.println("Blue channel is 0 - see Extension Activity 1");
}

void loop()
{
    if (POTS_INSTALLED)
    {
        red_brightness   = map(analogRead(RV1), 0, 1023, 0, 255);
        green_brightness = map(analogRead(RV2), 0, 1023, 0, 255);
    }
    else
    {
        if (digitalRead(SW2) == LOW)
            red_brightness -= COLOUR_STEP;
        else if (digitalRead(SW3) == LOW)
            red_brightness += COLOUR_STEP;

        if (digitalRead(SW4) == LOW)
            green_brightness -= COLOUR_STEP;
        else if (digitalRead(SW5) == LOW)
            green_brightness += COLOUR_STEP;

        red_brightness   = constrain(red_brightness,   0, 255);
        green_brightness = constrain(green_brightness, 0, 255);
    }

    set_rgb(red_brightness, green_brightness, blue_brightness);

    Serial.print("R: "); Serial.print(red_brightness);
    Serial.print("  G: "); Serial.print(green_brightness);
    Serial.print("  B: "); Serial.println(blue_brightness);

    delay(STEP_DELAY);
}


/*
Extension Activities

1.  Add blue channel control. With four buttons and two
    potentiometers controlling only red and green, choose one
    of these approaches for blue:

    a) Derive blue automatically:
       blue_brightness = 255 - red_brightness - green_brightness;
       blue_brightness = constrain(blue_brightness, 0, 255);

    b) Add a mode toggle: pressing SW2 and SW5 together switches
       between (red + green) mode and (blue + brightness) mode.

    c) If using potentiometers, use HSV mixing from Extension 2,
       giving full colour control from two knobs.

2.  HSV (Hue-Saturation-Value) colour mixing is more intuitive
    than direct RGB for many applications. Hue is expressed in
    degrees around the colour wheel (0=red, 120=green, 240=blue,
    360=red again). Saturation controls vividness as a percentage
    (100=full colour, 0=white). Value controls overall brightness
    as a percentage (0=off, 100=full brightness).

    Add this function to your sketch:

  void hsv_to_rgb(float h, float s, float v,
                  int &r, int &g, int &b)
  {
    // Convert HSV to RGB values (0-255).
    // h: hue in degrees (0-360)
    // s: saturation as a percentage (0-100)
    // v: brightness as a percentage (0-100)
    s /= 100.0;
    v /= 100.0;
    if (s == 0.0) { r = g = b = (int)(v * 255); return; }
    int i = (int)(h / 60) % 6;
    float f = (h / 60) - (int)(h / 60);
    int p = (int)(v * (1 - s) * 255);
    int q = (int)(v * (1 - s * f) * 255);
    int t = (int)(v * (1 - s * (1 - f)) * 255);
    int V = (int)(v * 255);
    switch (i) {
      case 0: r=V; g=t; b=p; break;
      case 1: r=q; g=V; b=p; break;
      case 2: r=p; g=V; b=t; break;
      case 3: r=p; g=q; b=V; break;
      case 4: r=t; g=p; b=V; break;
      case 5: r=V; g=p; b=q; break;
    }
  }

    Use RV1 to sweep hue across the full colour wheel and RV2 to
    control brightness, with saturation fixed at 100:

  float hue = analogRead(RV1) * 360.0 / 1023.0;
  float val = analogRead(RV2) * 100.0 / 1023.0;
  hsv_to_rgb(hue, 100, val,
             red_brightness, green_brightness, blue_brightness);
  set_rgb(red_brightness, green_brightness, blue_brightness);

    Trace through 'hsv_to_rgb()' with h=0, h=120, and h=240 (all
    with s=100, v=100) and verify that the expected primary colours
    - red, green, and blue - appear on the LED.

    The '&' in the function parameters means the variables are
    passed by reference - the function writes directly into
    'red_brightness', 'green_brightness', and 'blue_brightness'
    rather than returning values. This is a C++ technique that
    allows a function to produce multiple output values.

3.  Write a 'fade_to(int tr, int tg, int tb, int steps)' function
    that smoothly transitions the RGB LED from its current colour
    to a target. Use it to cycle through a sequence of preset colours
    with smooth transitions, using an array of target colours:

  const int colours[][3] = {
    { 255,   0,   0 },   // Red
    { 255, 128,   0 },   // Orange
    { 255, 255,   0 },   // Yellow
    {   0, 255,   0 },   // Green
    {   0,   0, 255 },   // Blue
  };

4.  NeoPixel preview: NeoPixels (WS2812B addressable LEDs) also
    use 8-bit RGB values (0-255), the same range as this project.
    The Arduino NeoPixel library (Adafruit_NeoPixel) controls
    strips of individually addressable LEDs using a single data
    wire. The colour mixing and HSV concepts from this project
    apply directly to NeoPixel programming.

    Research 'Adafruit_NeoPixel' and note how colours are set
    using setPixelColor(index, red, green, blue). The 'set_rgb()'
    and 'hsv_to_rgb()' functions you wrote here will work with
    NeoPixels with only minor changes.

*/
