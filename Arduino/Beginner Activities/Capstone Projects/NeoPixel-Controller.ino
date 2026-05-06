/* ================================================================================
Capstone Project: NeoPixel Display Controller [NeoPixel-Controller]
May 4, 2026

Platform: mirobo.tech BEAPER Nano circuit (robot configuration with
  voltage regulator U1 and 74HCT541 buffer/level shifter U2 is needed
  to run short 5V NeoPixel sticks or rings)
Requires: BEAPERNano.h header file
Requires: Adafruit NeoPixel library (install via Arduino Library Manager:
  search for "Adafruit NeoPixel" and install the latest version)

Hardware used:
  SW2        - Cycle parameter up within the current mode (hold to repeat)
  SW3        - Previous animation mode (cycles backward)
  SW4        - Next animation mode (cycles forward)
  SW5        - Toggle strip on/off (remembers the last active mode)
  LS1        - Piezo speaker (mode-change confirmation beep)
  LED_BUILTIN - On while a mode is active

  NeoPixel strip (data input connects to DATA_PIN - see strip setup, below)

--------------------------------------------------------------------------------
* Connecting a large NeoPixel strip *

WARNING: A 60 LED strip at full brightness draws up to 3.6A (60ma
  per pixel at white). Connect the strip's power and GND directly
  to an external 5V power supply rated for at least 10% more than
  the highest expected current. Connect the BEAPER Nano GND to
  the external power supply GND (shared ground), and run the data
  wire from the BEAPER Nano to the Din pin on the strip.

* Connecting short NeoPixel sticks, rings, or strips *

5V WS2812B or SK6812 LEDs:
  Power BEAPER Nano with an external power supply (6-12V) connected
  to screw terminal CON1. Up to 30 WS2812B LEDs can be connected
  to 5V output header H5 and used at low brightness
  (MAX_BRIGHTNESS = 32 or less).

3.3V SK6812 LEDs only:
  Up to 10 SK6812 LEDs can be connected using 3.3V header H1. H1
  and H5 share the same pin on the Arduino Nano ESP32 , so the data
  connection is identical for both strip types.

--------------------------------------------------------------------------------
Animation modes (selected with SW3 / SW4):
  OFF      - Strip dark. SW5 toggles between OFF and the last active mode.
  SOLID    - All pixels set to a single colour.
             SW2: step hue by 10 degrees.
  CHASE    - One lit pixel travels along the strip.
             SW2: cycle speed (pixels per frame).
  THEATRE  - Every third pixel lit, pattern advances each frame.
             SW2: cycle advance rate.
  RAINBOW  - Full spectrum gradient slowly rotates along the strip.
             SW2: cycle rotation speed.
  PULSE    - All pixels fade in and out; hue advances each cycle.
             SW2: step hue by 10 degrees.
--------------------------------------------------------------------------------
Before you begin - complete your capstone plan:
  1. Write a plain-English description from the viewer's perspective.
  2. List all modes, what each displays, and what SW2 adjusts.
  3. Draw the state diagram showing mode transitions and the OFF state.
  4. List all constants and variables you will need.
  5. Write your testing plan - verify each step before moving to the next.
================================================================================*/
// IMPORTANT: Make sure that BEAPERNano.h is accessible as a tab in this project.
#include "BEAPERNano.h"
#include <Adafruit_NeoPixel.h>

// =============================================================================
// Strip configuration - set these to match your hardware
// =============================================================================

const int NUM_PIXELS     = 30;    // Number of pixels in your strip.

const int MAX_BRIGHTNESS = 32;    // Global brightness cap (0-255).
                                  // 32 is safe for USB power with a short strip.
                                  // Raise toward 255 only with an external supply.

// Strip type: 0 for WS2812B RGB (3-byte), 1 for SK6812 RGBW (4-byte).
// Change STRIP_TYPE and the strip constructor below to switch types.
const int STRIP_TYPE = 0;         // 0 = RGB (WS2812B),  1 = RGBW (SK6812)

// Data pin: H5 for WS2812B (5V header, for short or long 5V strips)
//           H1 for SK6812 (3.3V header, for short 3.3V strips only!)
// H1 and H5 share pin A4 on the BEAPER Nano, so DATA_PIN is the same
// for both strip types. Only the strip supply voltage differs. The
// Adafruit NeoPixel library uses native ESP32 pin numbers (A4 = 11).
// NOTE: A4 is also used by the I2C SDA line (Wire library). Using
// NeoPixel on this pin means I2C/Wire is unavailable at the same time.
const int DATA_PIN = 11;          // H1/H5 (Adafruit NeoPixel library 
                                  // uses native ESP32 pin numbers)

// NeoPixel strip object.
// NEO_GRB  + NEO_KHZ800 for WS2812B (RGB,  3-byte).
// NEO_GRBW + NEO_KHZ800 for SK6812  (RGBW, 4-byte).
// Change NEO_GRB to NEO_GRBW when switching to SK6812.
Adafruit_NeoPixel strip(NUM_PIXELS, DATA_PIN, NEO_GRB + NEO_KHZ800);

// How the strip object works - read this before writing any animation code!
//
// Writing strip.setPixelColor(i, color) stores the colour data for pixel i
// in memory, but does not change the LED immediately. Calling strip.show()
// sends the stored pixel data to all of the LEDs in the strip at once.
// This is known as a buffered output model.
//
// This means your program should:
//
// 1. Call strip.show() to update the LEDs after setting pixel values.
//    (Forgetting strip.show() is the most common mistake when working
//    with NeoPixels.)
//
// 2. Call strip.show() once at the end of a loop, instead of during
//    every loop, when setting multiple pixels in a loop. (Calling
//    strip.show() inside the loop works but will be much slower, since
//    the full strip data would be sent to the LEDs after every step.)
//
// strip.getPixelColor(i) returns the packed colour currently stored for
// pixel i. This is useful when you need the current colour of a pixel,
// for example when dimming a tail in the COMET extension.


// =============================================================================
// Mode constants
// =============================================================================

const int MODE_OFF     = 0;  // Strip dark - starting state
const int MODE_SOLID   = 1;  // All pixels one colour
const int MODE_CHASE   = 2;  // Single pixel travelling along the strip
const int MODE_THEATRE = 3;  // Every third pixel lit, pattern advances
const int MODE_RAINBOW = 4;  // Full spectrum gradient rotating along the strip
const int MODE_PULSE   = 5;  // All pixels fading in and out

const int NUM_MODES    = 6;

const char* MODE_NAMES[] = { "OFF", "SOLID", "CHASE", "THEATRE", "RAINBOW", "PULSE" };


// =============================================================================
// Timing constants
// =============================================================================

const int LOOP_DELAY    = 1;    // Main loop delay (ms)
const int FRAME_INTERVAL= 20;   // Animation frame update interval (ms) - 50 fps
const int ADJUST_FIRST  = 500;  // Delay before SW2 auto-repeat begins (ms)
const int ADJUST_REPEAT = 80;   // Auto-repeat interval while SW2 is held (ms)


// =============================================================================
// Animation parameter defaults
// (Each mode has one SW2-adjustable parameter - see the main loop.)
// =============================================================================

const int DEFAULT_HUE           = 0;   // Starting hue (0-359 degrees)
const int DEFAULT_CHASE_SPEED   = 1;   // Pixels advanced per frame (1-20)
const int DEFAULT_THEATRE_RATE  = 3;   // Frames between THEATRE advances (1-20)
const int DEFAULT_RAINBOW_SPEED = 2;   // Hue degrees advanced per frame (1-20)


// =============================================================================
// Program variables
// =============================================================================

int mode         = MODE_OFF;
bool modeChanged = true;

// --- SOLID / PULSE hue ---
int hue = DEFAULT_HUE;

// --- CHASE ---
int chasePos   = 0;
int chaseSpeed = DEFAULT_CHASE_SPEED;

// --- THEATRE ---
int theatreOffset = 0;
int theatreRate   = DEFAULT_THEATRE_RATE;
int theatreFrames = 0;

// --- RAINBOW ---
int rainbowOffset = 0;
int rainbowSpeed  = DEFAULT_RAINBOW_SPEED;

// --- PULSE ---
int  pulseBright = 0;
bool pulseUp     = true;

// --- Timing ---
unsigned long lastFrameTime = 0;

// --- SW2 hold-and-repeat ---
bool          sw2Held       = false;
unsigned long sw2HeldStart  = 0;
unsigned long sw2LastRepeat = 0;

// --- SW3/SW4/SW5 edge detection ---
int sw3Last = HIGH;
int sw4Last = HIGH;
int sw5Last = HIGH;

// --- SW5 toggle ---
int lastActiveMode = MODE_SOLID;  // Mode to return to when SW5 turns strip on


// =============================================================================
// Helper functions
// =============================================================================

uint32_t hsvToColor(int h, int s, int v)
{
    // Convert a colour from HSV to a packed Adafruit NeoPixel colour.
    // h: hue 0-359 degrees
    // s: saturation 0-100 (0 = grey, 100 = fully saturated)
    // v: value (brightness) 0-100 (0 = black, 100 = full brightness)
    // Returns a uint32_t suitable for strip.setPixelColor() and makeColor().
    //
    // HSV describes colours as a position on a colour wheel using:
    //  - Hue - the colour, where each colour is represented by its
    //    angle in degrees around a circle. (red is hue=0, green is hue=120,
    //    and blue is hue=240)
    //  - Saturation - how vivid the colour is from 0 (no colour) to 100
    //    (full colour).
    //  - Value - how bright the colour is from 0 (black) to 100 (bright)
    //
    // Using HSV, cycling hue from 0 to 359 displays every colour in the
    // spectrum - red, orange, yellow, green, cyan, blue, violet, and back
    // to red - without touching saturation or brightness. This makes smooth
    // colour animations easier than trying to simultaneously adjust
    // individual RGB values up and down to mix colours.
    if (s == 0)
    {
        int c = (int)((long)v * 255 / 100);
        return strip.Color(c, c, c);
    }
    float sf = s / 100.0f;
    float vf = v / 100.0f;
    int   i  = (h / 60) % 6;
    float f  = (h / 60.0f) - (int)(h / 60);
    int   p  = (int)(vf * (1 - sf) * 255);
    int   q  = (int)(vf * (1 - f * sf) * 255);
    int   t  = (int)(vf * (1 - (1 - f) * sf) * 255);
    int   vi = (int)(vf * 255);
    switch (i)
    {
        case 0: return strip.Color(vi, t,  p);
        case 1: return strip.Color(q,  vi, p);
        case 2: return strip.Color(p,  vi, t);
        case 3: return strip.Color(p,  q,  vi);
        case 4: return strip.Color(t,  p,  vi);
        default:return strip.Color(vi, p,  q);
    }
}


uint32_t scaleColor(uint32_t color, int brightness)
{
    // Scale a packed colour by a brightness factor (0-255).
    // brightness=255 returns the colour unchanged.
    // brightness=128 returns approximately half-brightness.
    // brightness=32  returns 1/8 brightness.
    // brightness=0   returns black.
    //
    // This is used to apply MAX_BRIGHTNESS globally - all colour math
    // uses full 0-255 values, and scaleColor() dims them at the end.
    uint8_t r = (uint8_t)(color >> 16);
    uint8_t g = (uint8_t)(color >>  8);
    uint8_t b = (uint8_t)(color      );
    r = (uint8_t)((uint16_t)r * brightness / 255);
    g = (uint8_t)((uint16_t)g * brightness / 255);
    b = (uint8_t)((uint16_t)b * brightness / 255);
    if (STRIP_TYPE == 1)
    {
        uint8_t w = (uint8_t)(color >> 24);
        w = (uint8_t)((uint16_t)w * brightness / 255);
        return strip.Color(r, g, b, w);
    }
    return strip.Color(r, g, b);
}


uint32_t makeColor(int r, int g, int b)
{
    // Build a packed colour value for the current strip type.
    // For RGB strips  (STRIP_TYPE = 0): returns strip.Color(r, g, b)
    // For RGBW strips (STRIP_TYPE = 1): returns strip.Color(r, g, b, 0)
    //
    // Using makeColor() throughout means all animation code works with
    // both strip types without any other changes.
    if (STRIP_TYPE == 1)
        return strip.Color(r, g, b, 0);
    return strip.Color(r, g, b);
}


void fillStrip(uint32_t color)
{
    // Set every pixel to color and push to hardware.
    strip.fill(color, 0, NUM_PIXELS);
    strip.show();
}


void clearStrip()
{
    // Turn off all pixels.
    strip.clear();
    strip.show();
}


void enterMode(int newMode)
{
    // Transition to a new mode.
    // Clears the strip, resets all animation counters, plays a
    // mode-specific confirmation tone, and prints the mode name.
    // This is the same enter_state() pattern from Activity 12.
    mode         = newMode;
    modeChanged  = true;
    chasePos     = 0;
    theatreOffset = 0;
    theatreFrames = 0;
    rainbowOffset = 0;
    pulseBright  = 0;
    pulseUp      = true;

    clearStrip();

    if (newMode == MODE_OFF)
    {
        digitalWrite(LED_BUILTIN, LOW);
        noTone(LS1);
    }
    else
    {
        digitalWrite(LED_BUILTIN, HIGH);
        tone(LS1, 660 + newMode * 80, 60);
    }
    Serial.print("--> ");
    Serial.println(MODE_NAMES[newMode]);
}


bool checkSW2(unsigned long currentTime)
{
    // Read SW2 with the Activity 11 hold-and-repeat pattern.
    // Returns true if a parameter increment step is due this iteration.
    int sw2Current = digitalRead(SW2);
    if (sw2Current == LOW)
    {
        if (!sw2Held)
        {
            sw2Held       = true;
            sw2HeldStart  = currentTime;
            sw2LastRepeat = currentTime;
            return true;
        }
        else if ((currentTime - sw2HeldStart)  >= (unsigned long)ADJUST_FIRST &&
                 (currentTime - sw2LastRepeat) >= (unsigned long)ADJUST_REPEAT)
        {
            sw2LastRepeat = currentTime;
            return true;
        }
    }
    else
    {
        sw2Held = false;
    }
    return false;
}


// =============================================================================
// Setup
// =============================================================================

void setup()
{
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, LOW);

    pinMode(SW2, INPUT_PULLUP);
    pinMode(SW3, INPUT_PULLUP);
    pinMode(SW4, INPUT_PULLUP);
    pinMode(SW5, INPUT_PULLUP);

    pinMode(LED2, OUTPUT);
    pinMode(LED3, OUTPUT);
    pinMode(LED4, OUTPUT);
    pinMode(LED5, OUTPUT);

    strip.begin();
    strip.show();  // Clear all pixels on startup

    Serial.begin(115200);
    delay(2000);

    Serial.println("NeoPixel Display Controller");
    Serial.print("Strip type: ");
    Serial.print(STRIP_TYPE == 0 ? "RGB (WS2812B)" : "RGBW (SK6812)");
    Serial.print("  Pixels: "); Serial.print(NUM_PIXELS);
    Serial.print("  Max brightness: "); Serial.println(MAX_BRIGHTNESS);
    Serial.println("SW3/SW4: previous/next mode   SW2: adjust parameter   SW5: on/off");
    Serial.println();

    lastFrameTime = millis();
    enterMode(MODE_OFF);
}


// =============================================================================
// Main loop
// =============================================================================

void loop()
{
    unsigned long currentTime = millis();

    // ---- Button: SW3 - previous mode ----------------------------------------
    int sw3Current = digitalRead(SW3);
    if (sw3Current == LOW && sw3Last == HIGH)
    {
        if (mode != MODE_OFF)
            enterMode(((mode - 1 - 1) % (NUM_MODES - 1) + (NUM_MODES - 1)) % (NUM_MODES - 1) + 1);
    }
    sw3Last = sw3Current;

    // ---- Button: SW4 - next mode --------------------------------------------
    int sw4Current = digitalRead(SW4);
    if (sw4Current == LOW && sw4Last == HIGH)
    {
        if (mode != MODE_OFF)
            enterMode(mode % (NUM_MODES - 1) + 1);
    }
    sw4Last = sw4Current;

    // ---- Button: SW5 - toggle strip on/off ----------------------------------
    int sw5Current = digitalRead(SW5);
    if (sw5Current == LOW && sw5Last == HIGH)
    {
        if (mode == MODE_OFF)
            enterMode(lastActiveMode);
        else
        {
            lastActiveMode = mode;
            enterMode(MODE_OFF);
        }
    }
    sw5Last = sw5Current;

    // ---- SW2: cycle mode parameter (hold to repeat) -------------------------
    if (checkSW2(currentTime))
    {
        if (mode == MODE_SOLID || mode == MODE_PULSE)
        {
            hue = (hue + 10) % 360;
            Serial.print("    hue: "); Serial.println(hue);
        }
        else if (mode == MODE_CHASE)
        {
            chaseSpeed = chaseSpeed % 20 + 1;
            Serial.print("    chase speed: "); Serial.print(chaseSpeed);
            Serial.println(" pixels/frame");
        }
        else if (mode == MODE_THEATRE)
        {
            theatreRate = theatreRate % 20 + 1;
            Serial.print("    theatre rate: "); Serial.print(theatreRate);
            Serial.println(" frames/step");
        }
        else if (mode == MODE_RAINBOW)
        {
            rainbowSpeed = rainbowSpeed % 20 + 1;
            Serial.print("    rainbow speed: "); Serial.print(rainbowSpeed);
            Serial.println(" deg/frame");
        }
    }

    // ---- Animation frame (non-blocking, rate-limited by FRAME_INTERVAL) -----
    if ((currentTime - lastFrameTime) >= (unsigned long)FRAME_INTERVAL)
    {
        lastFrameTime = currentTime;

        // ----------------------------------------------------------------------
        // MODE_SOLID: all pixels set to a single colour.
        //
        // This mode is already complete and working - it shows how
        // hsvToColor(), scaleColor(), and makeColor() work together.
        // Read and understand this before implementing the other modes.
        // ----------------------------------------------------------------------
        if (mode == MODE_SOLID)
        {
            fillStrip(scaleColor(hsvToColor(hue, 100, 100), MAX_BRIGHTNESS));
        }

        // ----------------------------------------------------------------------
        // MODE_CHASE: one lit pixel travels along the strip.
        //
        // Concept: strip.setPixelColor(i, color) addresses a single pixel
        // by index. The lit pixel index is stored in chasePos. Each frame:
        //   1. Clear the strip (all pixels off) with strip.clear().
        //   2. Set pixel chasePos to the current colour.
        //   3. Call strip.show() to push the change to the hardware.
        //   4. Advance chasePos by chaseSpeed.
        //      Use % NUM_PIXELS to wrap back to 0 after the last pixel.
        //
        // TODO: implement MODE_CHASE using the steps above.
        // ----------------------------------------------------------------------
        else if (mode == MODE_CHASE)
        {
        }

        // ----------------------------------------------------------------------
        // MODE_THEATRE: every third pixel is lit and the pattern advances.
        //
        // Concept: the modulo operator % tests whether a number is a
        // multiple of another. (i % 3 == 0) is True for i = 0, 3, 6, 9...
        // Adding theatreOffset shifts which pixels are lit:
        //   offset=0: pixels 0, 3, 6, 9...  are lit
        //   offset=1: pixels 1, 4, 7, 10... are lit
        //   offset=2: pixels 2, 5, 8, 11... are lit
        //
        // Each frame, count up theatreFrames. When theatreFrames reaches
        // theatreRate, reset it to 0 and advance theatreOffset by 1
        // (wrapping at 3 with % 3). This controls how fast the pattern moves.
        //
        // TODO: use a for loop over NUM_PIXELS. For each pixel i, call
        //       strip.setPixelColor(i, color) if (i % 3 == theatreOffset),
        //       or strip.setPixelColor(i, 0) (off) otherwise. After the
        //       loop, call strip.show(). Then update theatreFrames and
        //       advance theatreOffset when theatreFrames reaches theatreRate.
        // ----------------------------------------------------------------------
        else if (mode == MODE_THEATRE)
        {
        }

        // ----------------------------------------------------------------------
        // MODE_RAINBOW: a full colour spectrum is spread across the strip
        // and the gradient slowly rotates.
        //
        // Concept: each pixel is assigned a hue based on its position.
        // Pixel i gets the hue: (rainbowOffset + i * 360 / NUM_PIXELS) % 360
        // This spreads 360 degrees of hue evenly across NUM_PIXELS pixels.
        // Adding rainbowOffset (which increases each frame) rotates the
        // gradient along the strip.
        //
        // TODO: use a for loop over NUM_PIXELS. For each pixel i, calculate
        //       pixelHue using the formula above, convert to a scaled colour
        //       using hsvToColor() and scaleColor(), and assign to pixel i
        //       via makeColor(). After the loop, call strip.show(). Then
        //       advance rainbowOffset by rainbowSpeed, wrapping at 360.
        // ----------------------------------------------------------------------
        else if (mode == MODE_RAINBOW)
        {
        }

        // ----------------------------------------------------------------------
        // MODE_PULSE: all pixels fade in and out together, and the hue
        // advances at the start of each new cycle.
        //
        // Concept: pulseBright ramps from 0 up to MAX_BRIGHTNESS then
        // back down to 0. pulseUp tracks the direction (true = going up).
        // Each frame, fill the strip with hue at the current pulseBright.
        // Note: use pulseBright directly as the brightness argument to
        // scaleColor() - not MAX_BRIGHTNESS - because pulseBright IS
        // the brightness for this mode.
        //
        // When pulseBright reaches MAX_BRIGHTNESS, set pulseUp to false.
        // When pulseBright reaches 0 going down, set pulseUp to true and
        // advance the hue by 30 degrees so each pulse is a different colour.
        //
        // TODO: implement MODE_PULSE using the description above.
        // Add PULSE_STEP as a constant (try 2 as a starting value).
        // ----------------------------------------------------------------------
        else if (mode == MODE_PULSE)
        {
        }
    }

    delay(LOOP_DELAY);
}


/*
Capstone Development Guide

Work through these steps in order. Complete and test each step before
moving to the next. Start with a short strip (8-10 LEDs) at low
brightness while the circuit is USB-powered.

Step 1 - Hardware setup and first pixel
  Wire the strip: data input to DATA_PIN, strip GND to BEAPER Nano GND,
  strip power to an external supply (or USB for a short test strip).
  Install the Adafruit NeoPixel library via the Arduino Library Manager
  (search for "Adafruit NeoPixel"). Verify the connection by temporarily
  adding these lines at the end of setup():

      strip.setPixelColor(0, makeColor(32, 0, 0));  // Red at low brightness
      strip.show();

  If the first pixel does not light, check the data line connection,
  power, and shared ground. If the pixel shows the wrong colour, the
  strip may have a different colour order (GRB vs RGB). WS2812B and
  SK6812 strips both typically use GRB ordering - the Adafruit NeoPixel
  library handles this internally with the NEO_GRB / NEO_GRBW type flag.

  For SK6812 strips, change NEO_GRB to NEO_GRBW in the strip constructor
  and set STRIP_TYPE = 1 before testing. Connect data to H1 (3.3V side)
  instead of H5 (5V side) - they share pin A4 on the BEAPER Nano.

Step 2 - Verify hsvToColor()
  The hsvToColor() function converts a colour described in HSV (hue,
  saturation, value) into the packed uint32_t colour that the strip
  expects. Read the explanation in the function's comment block above
  to understand why HSV is used before testing it.

  Unlike the MicroPython version, Arduino C functions cannot be tested
  directly in a console. Add temporary Serial.println() calls at the
  end of setup() to verify the output:

      Serial.println(hsvToColor(0,   100, 100), HEX);  // FF0000 red
      Serial.println(hsvToColor(120, 100, 100), HEX);  // 00FF00 green
      Serial.println(hsvToColor(240, 100, 100), HEX);  // 0000FF blue
      Serial.println(hsvToColor(60,  100, 100), HEX);  // FFFF00 yellow
      Serial.println(hsvToColor(0,   0,   100), HEX);  // FFFFFF white (s=0)

  Open the Serial Monitor (9600 baud) and confirm the hex values match.
  The Adafruit NeoPixel library packs colours as 0x00RRGGBB in memory.
  If any result is wrong, check the function logic before continuing.

Step 3 - Verify scaleColor() and makeColor()
  Add temporary Serial.println() calls to test these functions:

      Serial.println(scaleColor(makeColor(255, 0, 0), 255), HEX); // FF0000
      Serial.println(scaleColor(makeColor(255, 0, 0), 128), HEX); // approx 7F0000
      Serial.println(scaleColor(makeColor(255, 0, 0),  32), HEX); // approx 200000
      Serial.println(scaleColor(makeColor(255, 0, 0),   0), HEX); // 000000

  scaleColor() works by extracting each component byte from the packed
  colour, multiplying by brightness/255, and repacking. At brightness=255
  the factor is 1.0 (unchanged). At brightness=0 the factor is 0 (black).

  For STRIP_TYPE = 1 (SK6812), makeColor(255, 0, 0) should return a
  packed value with the white channel set to 0. Verify by checking that
  the high byte of the result is 0x00 (printed as 8 hex digits).

  Understanding these three functions is the key to all modes. Every
  animation follows the same pattern:
    1. Choose a hue (or calculate one from pixel position)
    2. Convert to colour:  uint32_t c = hsvToColor(hue, 100, 100)
    3. Apply brightness:   uint32_t sc = scaleColor(c, MAX_BRIGHTNESS)
    4. Send to hardware:   strip.setPixelColor(i, sc); strip.show()

Step 4 - SOLID mode (reference implementation)
  SOLID is already complete and working. Upload the sketch, press SW5
  to turn the strip on, then press SW4 to enter SOLID mode. Confirm
  the strip lights at a single colour. Press SW2 to step through hue
  changes in 10-degree increments. Hold SW2 and confirm auto-repeat
  kicks in after 500 ms.

  Read the SOLID code carefully before continuing:

      fillStrip(scaleColor(hsvToColor(hue, 100, 100), MAX_BRIGHTNESS));

  Breaking this apart to understand it:
    - hsvToColor(hue, 100, 100) converts the current hue to a packed colour
      at full saturation and full brightness.
    - scaleColor(..., MAX_BRIGHTNESS) dims the result to MAX_BRIGHTNESS.
    - fillStrip() sets every pixel to that colour and calls strip.show().

  Packed uint32_t colours are used throughout rather than separate r, g, b
  variables. The functions are designed to chain: the output of hsvToColor()
  feeds directly into scaleColor(), which feeds directly into fillStrip()
  or setPixelColor().

Step 5 - CHASE mode
  Implement MODE_CHASE following the TODO comment.

  Key ideas:
  - strip.setPixelColor(i, color) writes to a single pixel at index i.
  - strip.clear() sets every pixel to 0 (black) without calling show().
  - chasePos % NUM_PIXELS wraps the position back to 0 after the last pixel.
  - Call strip.show() once after setting the one lit pixel - not inside
    any inner loop.

  Test: press SW4 twice from SOLID to reach CHASE (SOLID -> CHASE).
  The single lit pixel should travel smoothly and wrap back to 0.
  Press SW2 and confirm the speed changes.

  Question: what happens if you remove strip.clear() from the loop?
  Try it. Why does the strip need to be cleared on every frame?

Step 6 - THEATRE mode
  Implement MODE_THEATRE following the TODO comment.

  Key ideas:
  - (i % 3 == theatreOffset) is true for every third pixel starting
    at theatreOffset. This is the same modulo operator from the counted
    loop activities.
  - theatreFrames counts frames since the last pattern advance. When it
    reaches theatreRate, reset it to 0 and advance theatreOffset by 1
    (% 3 to wrap back to 0 after 2).
  - Pass 0 (not makeColor(0,0,0)) to turn a pixel off - setPixelColor(i,0)
    is the standard way to clear a single pixel without clearing the strip.

  Test: press SW4 once from CHASE to reach THEATRE. You should see
  three evenly-spaced lit pixels advancing along the strip. Press SW2
  to change the advance rate.

  Question: change (i % 3 == theatreOffset) to (i % 4 == theatreOffset)
  and update the wrap from % 3 to % 4. What changes? Restore to % 3.

Step 7 - RAINBOW mode
  Implement MODE_RAINBOW following the TODO comment.

  Key ideas:
  - i * 360 / NUM_PIXELS spreads the full colour spectrum (0-360 degrees)
    evenly across the strip using integer division.
  - Adding rainbowOffset to every pixel's hue shifts the gradient along
    the strip. Incrementing rainbowOffset each frame makes it rotate.
  - % 360 keeps the hue in the valid range as the offset grows.

  Test: the strip should show a smooth continuous spectrum. Press SW2
  to increase the rotation speed.

  Question: what happens if you subtract rainbowOffset instead of
  adding it? What does a negative speed feel like? Try it.

Step 8 - PULSE mode
  Implement MODE_PULSE following the TODO comment.

  Key ideas:
  - pulseBright is used directly as the brightness argument to scaleColor(),
    not MAX_BRIGHTNESS. This is the key difference from SOLID.
  - The ramp uses constrain(pulseBright + PULSE_STEP, 0, MAX_BRIGHTNESS)
    to keep pulseBright within bounds.
  - Advance the hue by 30 degrees at the bottom of each cycle so each
    pulse is a slightly different colour.

  Test: the strip should fade smoothly to true black and back. Confirm
  the hue shifts with each new cycle.

Step 9 - Full integration
  Upload and cycle through all modes with SW3 and SW4. Check:
  - Each mode produces the expected animation
  - SW2 adjusts the correct parameter in each mode (with hold-and-repeat)
  - SW3 cycles backward (CHASE -> SOLID -> PULSE -> RAINBOW -> ...)
  - SW5 turns the strip off and back on, returning to the last mode
  - The strip clears cleanly when entering each new mode
  - The confirmation beep fires once per mode press (not while holding)

  Open the Serial Monitor and confirm state transition messages print
  correctly and parameter adjustments print with the right values.

Step 10 - RGBW strips (SK6812)
  To use an SK6812 RGBW strip instead of a WS2812B:

  1. Change STRIP_TYPE = 0 to STRIP_TYPE = 1
  2. Change NEO_GRB to NEO_GRBW in the Adafruit_NeoPixel constructor
  3. The data pin does not change: H1 and H5 share pin A4 on the BEAPER
     Nano. Connect the SK6812 data input to the H1 header (3.3V side)
     instead of H5 (5V side) - same pin, different voltage

  makeColor() and scaleColor() handle the rest: makeColor() automatically
  adds a fourth white channel byte (set to 0) when STRIP_TYPE = 1, and
  scaleColor() correctly scales all four channels.

  To use the white channel deliberately, modify makeColor() to accept an
  optional white parameter:

      uint32_t makeColor(int r, int g, int b, int w = 0) {
          if (STRIP_TYPE == 1) return strip.Color(r, g, b, w);
          return strip.Color(r, g, b);
      }

  Experiment: in SOLID mode, set the white channel to a low value (e.g.
  w=32) while keeping the colour channels non-zero. Compare the appearance
  to pure-colour output. White channel light tends to look "warmer" and
  more neutral than mixing white from RGB channels.

Extensions

  a) PULSE_STEP control: add PULSE_STEP as a SW2 parameter in MODE_PULSE
     so the pulse speed is adjustable at runtime. What range of values
     produces smooth fades vs. harsh flashing?

  b) COMET effect: modify CHASE to draw a short fading tail behind the
     lit pixel. Each frame, instead of clearing the whole strip, dim every
     pixel by extracting its components from strip.getPixelColor(i) and
     multiplying by a factor less than 1 (e.g. 0.7). Then set the head
     pixel to full brightness. How does the tail length change with the
     fade factor?

  c) THEATRE colour gradient: instead of all lit pixels being the same
     hue, assign each lit pixel a hue based on its position. The pattern
     should still advance each frame. How does this change the animation?

  d) Beat-reactive brightness: read an analog input (e.g. RV1_level()
     with JP3=Enviro., or an external microphone on H1) using analogRead()
     and map the reading to MAX_BRIGHTNESS. Which mode looks best with
     a changing brightness?

  e) White channel mood lamp: for SK6812 strips only. Create a new mode
     that ignores the colour channels and uses only the white channel,
     slowly pulsing between warm-white and off. Compare the light quality
     to the PULSE mode running in white (hue=0, saturation=0).

  f) Star Wars light saber: press a button to grow the 'blade' from the
     hilt, and then shimmer the brightness. Pressing the button again
     shrinks the blade back down into the hilt. Use another button to
     change or cycle the colour of the light saber blade.

*/
