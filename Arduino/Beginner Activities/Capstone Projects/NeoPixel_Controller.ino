/* ================================================================================
Capstone Project: NeoPixel Display Controller [BEAPERNano-Capstone-NeoPixel-Controller]
Version: 1.0
Updated: July 25, 2026

Platform: mirobo.tech BEAPER Nano circuit (robot configuration with
  voltage regulator U1 and 74HCT541 buffer/level shifter U2 is needed
  to run short 5V NeoPixel sticks or rings)
Requires: BEAPERNano.h header file, colour.h conversion header,
  Adafruit_NeoPixel library (install via Arduino Library Manager)

Hardware used:
  SW2        - Cycle parameter up within the current mode (hold to repeat)
  SW3        - Previous animation mode (cycles backward)
  SW4        - Next animation mode (cycles forward)
  SW5        - Toggle strip on/off (remembers the last active mode)
  LS1        - Piezo speaker (mode-change confirmation beep)
  On-board LED - On while a mode is active

  NeoPixel strip (data input connects to PIXEL_PIN - see strip setup, below)

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
  to 5V output header H5 (GPIO 11) and used at low brightness
  (MAX_BRIGHTNESS = 32 or less).

3.3V SK6812 LEDs only:
  Up to 10 SK6812 LEDs can be connected using the 3.3V side of
  header H1 (also GPIO 11). H1 and H5 share the same GPIO pin on
  the BEAPER Nano, so the data connection is identical for both
  strip types - only the strip's supply voltage differs.

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
This capstone uses colour.h, a separate reusable header, for HSV-to-RGB
colour conversion - make sure it is accessible as a tab in this project
alongside BEAPERNano.h. Keeping colour math in its own header (rather
than copied inline, as earlier drafts of this program did) means the
same conversion code can be reused by any future project that needs it,
without duplication.

Before you begin - complete your capstone plan:
  1. Write a plain-English description from the viewer's perspective.
  2. List all modes, what each displays, and what SW2 adjusts.
  3. Draw the state diagram showing mode transitions and the OFF state.
  4. List all constants and variables you will need.
  5. Write your testing plan - verify each step before moving to the next.
=================================================================================*/
// IMPORTANT: Make sure that BEAPERNano.h and colour.h are accessible as tabs
// in this project.
#include "BEAPERNano.h"        // Define BEAPER Nano I/O devices
#include "colour.h"            // HSV-to-RGB colour conversion - see colour.h
#include <Adafruit_NeoPixel.h>

// =============================================================================
// Strip configuration - set these to match your hardware
// =============================================================================

const int NUM_LEDS = 30;              // Number of pixels in your strip.

const int MAX_BRIGHTNESS = 32;        // Global brightness cap (0-255).
                                       // 32 is safe for USB power with a short strip.
                                       // Raise toward 255 only with an external supply.

// Strip type: false for WS2812B (RGB, 3-byte), true for SK6812 (RGBW, 4-byte).
bool STRIP_IS_RGBW = false;           // Change to true for SK6812 strips.

// Data pin: H5 (GPIO 11) for WS2812B (5V header).
//           H1 (GPIO 11) for SK6812  (3.3V header).
// H1 and H5 share GPIO 11 on the BEAPER Nano, so PIXEL_PIN is the same
// for both strip types. Only the strip supply voltage differs.
// NOTE: GPIO 11 is also used by the QWIIC I2C bus (SDA). Using this pin
// for the NeoPixel strip means QWIIC will be unavailable at the same time.
const int PIXEL_PIN = H5;

// NeoPixel strip object. NEO_GRB for WS2812B, NEO_GRBW for SK6812.
// Change to NEO_GRBW + NEO_KHZ800 when switching to SK6812.
Adafruit_NeoPixel strip(NUM_LEDS, PIXEL_PIN, NEO_GRB + NEO_KHZ800);

// How the strip object works - read this before writing any animation code!
//
// strip.setPixelColor(i, r, g, b) stores the red, green, and blue colour
// data for pixel i in memory, but does not change the LED immediately.
// (For RGBW strips, use the four-argument version:
// strip.setPixelColor(i, r, g, b, w).)
// Calling strip.show() sends the stored pixel data to all of the LEDs
// in the strip at once. This is known as a buffered output model.
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
// 3. Call strip.begin() once in setup() before any other strip
//    function - this is required by the Adafruit_NeoPixel library and
//    has no MicroPython equivalent (MicroPython's neopixel object is
//    ready to use as soon as it is constructed).
//
// strip.getPixelColor(i) returns the current colour of pixel i, packed
// into a single 32-bit value rather than separate r/g/b numbers. This
// is useful when you need to know the current colour of a pixel, for
// example when dimming a tail in the COMET extension - see that
// extension activity for how to unpack the individual components.


// =============================================================================
// Mode constants
// =============================================================================

const int MODE_OFF     = 0;   // Strip dark - starting state
const int MODE_SOLID   = 1;   // All pixels one colour
const int MODE_CHASE   = 2;   // Single pixel travelling along the strip
const int MODE_THEATRE = 3;   // Every third pixel lit, pattern advances
const int MODE_RAINBOW = 4;   // Full spectrum gradient rotating along the strip
const int MODE_PULSE   = 5;   // All pixels fading in and out

const int NUM_MODES = 6;

const char* MODE_NAMES[] = { "OFF", "SOLID", "CHASE", "THEATRE", "RAINBOW", "PULSE" };

// =============================================================================
// Timing constants
// =============================================================================

const int LOOP_DELAY     = 1;     // Main loop delay (ms) - keeps loop responsive
const int FRAME_INTERVAL = 20;    // Animation frame update interval (ms) - 50 fps
const int ADJUST_FIRST   = 500;   // Delay before SW2 auto-repeat begins (ms)
const int ADJUST_REPEAT  = 80;    // Auto-repeat interval while SW2 is held (ms)

// =============================================================================
// Animation parameter defaults
// (Each mode has one SW2-adjustable parameter - see loop().)
// =============================================================================

const int DEFAULT_HUE           = 0;   // Starting hue for SOLID, CHASE, PULSE (0-359 deg)
const int DEFAULT_CHASE_SPEED   = 1;   // Pixels advanced per frame in CHASE (1-20)
const int DEFAULT_THEATRE_RATE  = 3;   // Frames between THEATRE advances (1-20)
const int DEFAULT_RAINBOW_SPEED = 2;   // Hue degrees advanced per frame in RAINBOW (1-20)
const int PULSE_STEP            = 2;   // Brightness change per frame in PULSE

// =============================================================================
// Program variables
// =============================================================================

int  mode         = MODE_OFF;
bool mode_changed = true;         // Forces a display update on the first frame

// ---- SOLID / PULSE hue ----
int hue = DEFAULT_HUE;            // Current hue (0-359 degrees)

// ---- CHASE ----
int chase_pos   = 0;              // Current lit pixel position (0 to NUM_LEDS-1)
int chase_speed = DEFAULT_CHASE_SPEED;

// ---- THEATRE ----
int theatre_offset = 0;           // Which pixel in the group-of-3 is currently lit
int theatre_rate   = DEFAULT_THEATRE_RATE;
int theatre_frames = 0;           // Counts frames since the last advance

// ---- RAINBOW ----
int rainbow_offset = 0;           // Hue offset that rotates the gradient along the strip
int rainbow_speed  = DEFAULT_RAINBOW_SPEED;

// ---- PULSE ----
int  pulse_bright = 0;            // Current brightness (0 to MAX_BRIGHTNESS)
bool pulse_up     = true;         // true while brightness is increasing

// ---- Timing ----
unsigned long last_frame_time = 0;

// ---- SW2 hold-and-repeat (Activity 11 pattern) ----
bool sw2_held           = false;
unsigned long sw2_held_start  = 0;
unsigned long sw2_last_repeat = 0;

// ---- SW3/SW4/SW5 edge detection ----
int sw3_last = 1;
int sw4_last = 1;
int sw5_last = 1;

// ---- SW5 toggle state ----
int last_active_mode = MODE_SOLID;   // Mode to return to when SW5 turns the strip on


// =============================================================================
// Helper functions
// =============================================================================
//
// hsvToRGB() lives in colour.h, included at the top of this file, rather
// than being defined here - see the module-level comment above for why.

RGB scale_colour(uint8_t r, uint8_t g, uint8_t b, uint8_t brightness)
{
    // Scale an RGB colour by a brightness factor (0-255).
    // brightness=255 returns the colour unchanged.
    // brightness=128 returns half-brightness.
    // brightness=0   returns black.
    //
    // This stays in this file rather than moving to colour.h, since it
    // applies this program's MAX_BRIGHTNESS setting - a choice specific
    // to this circuit and power supply, not a general colour conversion
    // any project would need. All colour math uses full 0-255 values,
    // and scale_colour() dims them at the end.
    float factor = brightness / 255.0;
    RGB result;
    result.r = (uint8_t)(r * factor);
    result.g = (uint8_t)(g * factor);
    result.b = (uint8_t)(b * factor);
    return result;
}

void set_pixel(int i, uint8_t r, uint8_t g, uint8_t b)
{
    // Set pixel i to (r, g, b), or (r, g, b, 0) for RGBW strips.
    // Using set_pixel() throughout means all animation code works with
    // both strip types without any other changes. Note that this always
    // sets the white channel to 0 for RGBW strips - see Extension
    // Activity 'e' for hsvToRGBW() in colour.h, which extracts a genuine
    // white component from the colour instead.
    if (STRIP_IS_RGBW)
        strip.setPixelColor(i, r, g, b, 0);
    else
        strip.setPixelColor(i, r, g, b);
}

void fill_strip(uint8_t r, uint8_t g, uint8_t b)
{
    // Set every pixel on the strip to (r, g, b) and push to hardware.
    for (int i = 0; i < NUM_LEDS; i++)
        set_pixel(i, r, g, b);
    strip.show();
}

void clear_strip()
{
    // Turn off all pixels.
    fill_strip(0, 0, 0);
}

void enter_mode(int new_mode)
{
    // Transition to a new mode.
    // Clears the strip, resets all animation counters, plays a
    // mode-specific confirmation tone, and prints the mode name.
    // This is the same enter_state() pattern from Activity 12.
    mode           = new_mode;
    mode_changed   = true;
    chase_pos      = 0;
    theatre_offset = 0;
    theatre_frames = 0;
    rainbow_offset = 0;
    pulse_bright   = 0;
    pulse_up       = true;

    clear_strip();

    if (new_mode == MODE_OFF)
    {
        digitalWrite(LED_BUILTIN, LOW);
        noTone(LS1);
    }
    else
    {
        digitalWrite(LED_BUILTIN, HIGH);
        tone(LS1, 660 + new_mode * 80, 60);
    }

    Serial.print("--> ");
    Serial.println(MODE_NAMES[new_mode]);
}

bool check_sw2(unsigned long current_time)
{
    // Read SW2 with the Activity 11 hold-and-repeat pattern.
    // Returns true if a parameter increment step is due this iteration,
    // false otherwise. Fires once on first press, then repeatedly after
    // ADJUST_FIRST ms with ADJUST_REPEAT ms between repeats.
    int sw2_current = digitalRead(SW2);
    if (sw2_current == LOW)
    {
        if (!sw2_held)
        {
            sw2_held        = true;
            sw2_held_start  = current_time;
            sw2_last_repeat = current_time;
            return true;
        }
        else if ((current_time - sw2_held_start) >= (unsigned long)ADJUST_FIRST &&
                 (current_time - sw2_last_repeat) >= (unsigned long)ADJUST_REPEAT)
        {
            sw2_last_repeat = current_time;
            return true;
        }
    }
    else
    {
        sw2_held = false;
    }
    return false;
}


void setup()
{
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, LOW);

    pinMode(SW2, INPUT_PULLUP);
    pinMode(SW3, INPUT_PULLUP);
    pinMode(SW4, INPUT_PULLUP);
    pinMode(SW5, INPUT_PULLUP);

    Serial.begin(9600);
    delay(2000);                       // Give Serial Monitor time to
                                        // connect, without blocking
                                        // forever if it's never opened

    strip.begin();                     // Required once before any other strip call
    strip.show();                      // Push an initial all-off state

    Serial.println("NeoPixel Display Controller");
    Serial.print("Strip type: "); Serial.print(STRIP_IS_RGBW ? "RGBW" : "RGB");
    Serial.print("  Pixels: "); Serial.print(NUM_LEDS);
    Serial.print("  Max brightness: "); Serial.println(MAX_BRIGHTNESS);
    Serial.println("SW3/SW4: previous/next mode   SW2: adjust parameter   SW5: on/off");
    Serial.println();

    last_frame_time = millis();
    enter_mode(MODE_OFF);   // Also clears the strip - no separate clear_strip() needed here
}

void loop()
{
    unsigned long current_time = millis();

    // ---- Button: SW3 - previous mode -------------------------------------
    int sw3_current = digitalRead(SW3);
    if (sw3_current == LOW && sw3_last == HIGH)
    {
        if (mode != MODE_OFF)
        {
            // Cycles backward through modes 1..NUM_MODES-1 (OFF is excluded -
            // SW5 handles OFF separately). C's % operator returns a result
            // with the same sign as the dividend (unlike Python's, which
            // matches the divisor), so a negative intermediate value here
            // needs an explicit correction rather than relying on % alone.
            // Try tracing mode=1 (SOLID) by hand: (1 - 2) = -1, and in C,
            // -1 % 5 evaluates to -1, not 4 as it would in Python - so 5 is
            // added before the modulo to keep the result positive.
            enter_mode((mode - 2 + (NUM_MODES - 1)) % (NUM_MODES - 1) + 1);
        }
    }
    sw3_last = sw3_current;

    // ---- Button: SW4 - next mode -------------------------------------------
    int sw4_current = digitalRead(SW4);
    if (sw4_current == LOW && sw4_last == HIGH)
    {
        if (mode != MODE_OFF)
            enter_mode(mode % (NUM_MODES - 1) + 1);
    }
    sw4_last = sw4_current;

    // ---- Button: SW5 - toggle strip on/off ---------------------------------
    int sw5_current = digitalRead(SW5);
    if (sw5_current == LOW && sw5_last == HIGH)
    {
        if (mode == MODE_OFF)
        {
            enter_mode(last_active_mode);    // Return to the last active mode
        }
        else
        {
            last_active_mode = mode;         // Remember current mode before turning off
            enter_mode(MODE_OFF);
        }
    }
    sw5_last = sw5_current;

    // ---- SW2: cycle mode parameter (hold to repeat) ------------------------
    if (check_sw2(current_time))
    {
        if (mode == MODE_SOLID || mode == MODE_PULSE)
        {
            hue = (hue + 10) % 360;
            Serial.print("    hue: "); Serial.println(hue);
        }
        else if (mode == MODE_CHASE)
        {
            chase_speed = chase_speed % 20 + 1;   // Cycles 1->20->1
            Serial.print("    chase speed: "); Serial.print(chase_speed); Serial.println(" pixels/frame");
        }
        else if (mode == MODE_THEATRE)
        {
            theatre_rate = theatre_rate % 20 + 1;  // Cycles 1->20->1
            Serial.print("    theatre rate: "); Serial.print(theatre_rate); Serial.println(" frames/step");
        }
        else if (mode == MODE_RAINBOW)
        {
            rainbow_speed = rainbow_speed % 20 + 1;  // Cycles 1->20->1
            Serial.print("    rainbow speed: "); Serial.print(rainbow_speed); Serial.println(" deg/frame");
        }
    }

    // ---- Animation frame (non-blocking, rate-limited by FRAME_INTERVAL) ---
    if ((current_time - last_frame_time) >= (unsigned long)FRAME_INTERVAL)
    {
        last_frame_time = current_time;

        // --------------------------------------------------------------------
        // MODE_SOLID: all pixels set to a single colour.
        //
        // This mode is already complete and working - it shows how
        // hsvToRGB(), scale_colour(), and set_pixel() work together. Read
        // and understand this before implementing the other modes.
        // --------------------------------------------------------------------
        if (mode == MODE_SOLID)
        {
            RGB raw    = hsvToRGB(hue, 100, 100);
            RGB scaled = scale_colour(raw.r, raw.g, raw.b, MAX_BRIGHTNESS);
            fill_strip(scaled.r, scaled.g, scaled.b);
        }

        // --------------------------------------------------------------------
        // MODE_CHASE: one lit pixel travels along the strip.
        //
        // Concept: set_pixel(i, r, g, b) addresses a single pixel by index.
        // The lit pixel index is stored in chase_pos. Each frame:
        //   1. Clear the entire strip (all pixels off).
        //   2. Set the pixel at chase_pos to the current colour.
        //   3. Call strip.show() to push the change to the hardware.
        //   4. Advance chase_pos by chase_speed.
        //      Use % NUM_LEDS to wrap back to 0 after the last pixel.
        //
        // TODO: implement MODE_CHASE using the steps above.
        // --------------------------------------------------------------------
        else if (mode == MODE_CHASE)
        {
        }

        // --------------------------------------------------------------------
        // MODE_THEATRE: every third pixel is lit and the pattern advances.
        //
        // Concept: the modulo operator % tests whether a number is a
        // multiple of another. (i % 3 == 0) is true for i = 0, 3, 6, 9...
        // Adding theatre_offset shifts which pixels are lit:
        //   offset=0: pixels 0, 3, 6, 9...  are lit
        //   offset=1: pixels 1, 4, 7, 10... are lit
        //   offset=2: pixels 2, 5, 8, 11... are lit
        //
        // Each frame, count up theatre_frames. When theatre_frames reaches
        // theatre_rate, reset it to 0 and advance theatre_offset by 1
        // (wrapping at 3 with % 3). This controls how fast the pattern moves.
        //
        // TODO: use a for loop over i = 0 to NUM_LEDS-1. For each pixel i,
        //       call set_pixel(i, ...) with the colour if
        //       (i % 3 == theatre_offset), or (0, 0, 0) (off) otherwise.
        //       After the loop, call strip.show(). Then update
        //       theatre_frames and advance theatre_offset when
        //       theatre_frames reaches theatre_rate.
        // --------------------------------------------------------------------
        else if (mode == MODE_THEATRE)
        {
        }

        // --------------------------------------------------------------------
        // MODE_RAINBOW: a full colour spectrum is spread across the strip
        // and the gradient slowly rotates.
        //
        // Concept: each pixel is assigned a hue based on its position.
        // Pixel i gets the hue: (rainbow_offset + i * 360 / NUM_LEDS) % 360
        // This spreads 360 degrees of hue evenly across NUM_LEDS pixels.
        // Adding rainbow_offset (which increases each frame) rotates the
        // gradient along the strip.
        //
        // TODO: use a for loop over i = 0 to NUM_LEDS-1. For each pixel i,
        //       calculate pixel_hue using the formula above, convert it
        //       to a scaled colour using hsvToRGB() and scale_colour(),
        //       and assign it with set_pixel(). After the loop, call
        //       strip.show(). Then advance rainbow_offset by
        //       rainbow_speed, wrapping at 360 with % 360.
        // --------------------------------------------------------------------
        else if (mode == MODE_RAINBOW)
        {
        }

        // --------------------------------------------------------------------
        // MODE_PULSE: all pixels fade in and out together, and the hue
        // advances at the start of each new cycle.
        //
        // Concept: pulse_bright ramps from 0 up to MAX_BRIGHTNESS then
        // back down to 0. pulse_up tracks the direction (true = going up).
        // Each frame, fill the strip with hue at the current pulse_bright.
        // Note: use pulse_bright directly as the brightness argument to
        // scale_colour() - not MAX_BRIGHTNESS - because pulse_bright IS
        // the brightness for this mode.
        //
        // When pulse_bright reaches MAX_BRIGHTNESS, set pulse_up to false.
        // When pulse_bright reaches 0 going down, set pulse_up to true and
        // advance the hue by 30 degrees so each pulse is a different colour.
        //
        // TODO: implement MODE_PULSE using the description above.
        // Hint: the update logic looks like this:
        //   if (pulse_up) {
        //       pulse_bright = min(pulse_bright + PULSE_STEP, MAX_BRIGHTNESS);
        //       if (pulse_bright == MAX_BRIGHTNESS) pulse_up = false;
        //   } else {
        //       pulse_bright = max(pulse_bright - PULSE_STEP, 0);
        //       if (pulse_bright == 0) {
        //           pulse_up = true;
        //           hue = (hue + 30) % 360;
        //       }
        //   }
        // --------------------------------------------------------------------
        else if (mode == MODE_PULSE)
        {
        }
    }

    delay(LOOP_DELAY);
}


/* ================================================================================
Development Guide
================================================================================

Work through these steps in order. Complete and test each step before
moving to the next. Start with a short strip (8-10 LEDs) at low
brightness while the circuit is USB-powered.

--------------------------------------------------------------------------------
Step 1 - Hardware setup and first pixel
--------------------------------------------------------------------------------

Wire the strip: data input to PIXEL_PIN, strip GND to BEAPER Nano
GND, strip power to an external supply (or USB for a short test strip).
Before any animation code, verify the connection by temporarily adding
these lines right after strip.begin() in setup():

Example code:

set_pixel(0, 32, 0, 0);   // Red at low brightness
strip.show();
// Stop here to verify

If the first pixel does not light, check the data line connection,
power, and shared ground. If the pixel shows the wrong colour, the
strip may have a different colour order (GRB vs RGB) - try changing
NEO_GRB to NEO_RGB in the strip constructor.

For SK6812 strips, change the constructor to NEO_GRBW + NEO_KHZ800,
set STRIP_IS_RGBW = true, and connect data to H1, not H5.

--------------------------------------------------------------------------------
Step 2 - Verify hsvToRGB()
--------------------------------------------------------------------------------

hsvToRGB() converts a colour described in HSV (hue, saturation,
value) into an RGB struct with .r, .g, and .b fields that the strip
expects. Read the explanation in colour.h's comment block to
understand why HSV is used here before testing it.

Add these lines temporarily in setup(), after strip.begin():

Example code:

RGB test = hsvToRGB(0, 100, 100);
Serial.print(test.r); Serial.print(", ");
Serial.print(test.g); Serial.print(", ");
Serial.println(test.b);   // Expect 255, 0, 0 (red)

test = hsvToRGB(120, 100, 100);
Serial.print(test.r); Serial.print(", ");
Serial.print(test.g); Serial.print(", ");
Serial.println(test.b);   // Expect 0, 255, 0 (green)

Try hue values of 0 (red), 120 (green), 240 (blue), and 60 (yellow).
Try s=0 with any hue - this should always produce white (255, 255,
255), since zero saturation means no colour, only brightness.

If any result is wrong, check colour.h before continuing. Correct
colour output here is essential for every mode that follows.

--------------------------------------------------------------------------------
Step 3 - Verify scale_colour() and set_pixel()
--------------------------------------------------------------------------------

Test scale_colour() with temporary lines in setup():

Example code:

RGB scaled = scale_colour(255, 0, 0, 255);
Serial.print(scaled.r); Serial.print(", ");
Serial.print(scaled.g); Serial.print(", ");
Serial.println(scaled.b);   // Expect 255, 0, 0 (unchanged)

scaled = scale_colour(255, 0, 0, 128);
Serial.println(scaled.r);   // Expect 127 (half brightness)

scaled = scale_colour(255, 0, 0, 0);
Serial.println(scaled.r);   // Expect 0 (black)

scale_colour() works by multiplying each component by
brightness/255.0. At brightness=255 the factor is 1.0 (unchanged).
At brightness=128 the factor is 0.5 (half). At brightness=0 the
factor is 0 (black). This is why all colour calculations in this
program use full 0-255 values - scale_colour() applies the global
MAX_BRIGHTNESS cap at the end, just before the colour is sent to
the strip.

Understanding these functions is the key to all modes. Every
animation follows the same pattern:
  1. Choose a hue (or calculate one from pixel position)
  2. Convert to RGB:    RGB raw = hsvToRGB(hue, 100, 100);
  3. Apply brightness:  RGB scaled = scale_colour(raw.r, raw.g, raw.b, MAX_BRIGHTNESS);
  4. Send to a pixel:   set_pixel(i, scaled.r, scaled.g, scaled.b);
  5. Push to hardware:  strip.show();

--------------------------------------------------------------------------------
Step 4 - SOLID mode (reference implementation)
--------------------------------------------------------------------------------

SOLID is already complete and working. Run the program, press SW5
to turn the strip on, then press SW4 to enter SOLID mode. Confirm
the strip lights at a single colour. Press SW2 to step through hue
changes in 10-degree increments. Hold SW2 and confirm auto-repeat
kicks in after 500 ms.

Read the SOLID code carefully before continuing:

Example code:

RGB raw    = hsvToRGB(hue, 100, 100);
RGB scaled = scale_colour(raw.r, raw.g, raw.b, MAX_BRIGHTNESS);
fill_strip(scaled.r, scaled.g, scaled.b);

hsvToRGB() returns a struct - a single value containing three
named fields, .r, .g, and .b, accessed with a dot (raw.r, not
raw[0]). This is different from MicroPython's version of this
program, which returns a tuple and unpacks it directly into three
separate variables with Python's * operator - C has no equivalent
shortcut, so the struct's fields are accessed individually instead,
one at a time, wherever they are needed. Structs are a preview of a
technique covered more fully in the intermediate activities; for
now, just remember that a value with a dot after it (raw.r) means
"the r field stored inside raw."

--------------------------------------------------------------------------------
Step 5 - CHASE mode
--------------------------------------------------------------------------------

Implement MODE_CHASE following the TODO comment.

Key ideas:
- set_pixel(i, r, g, b) writes to a single pixel at index i.
- clear_strip() sets every pixel to (0, 0, 0) and calls strip.show().
- chase_pos % NUM_LEDS wraps the position back to 0 after the last
  pixel, producing smooth continuous motion.

Test by pressing SW4 twice from SOLID to reach CHASE (SOLID -> CHASE).
The single lit pixel should travel smoothly from pixel 0 to the last
pixel and wrap back to 0. Press SW2 and confirm the speed changes.

Question: what happens if you remove the clear_strip() call? Try it.
Why does the strip need to be cleared on every frame for CHASE?

--------------------------------------------------------------------------------
Step 6 - THEATRE mode
--------------------------------------------------------------------------------

Implement MODE_THEATRE following the TODO comment.

Key ideas:
- (i % 3 == theatre_offset) is true for every third pixel starting
  at theatre_offset. This is the same modulo operator (%) from the
  counted loop activities.
- theatre_frames counts how many animation frames have elapsed since
  the last pattern advance. When it reaches theatre_rate, reset it to
  0 and advance theatre_offset by 1 (% 3). This controls how fast the
  advance happens.
- Setting theatre_rate = 1 makes the pattern advance every frame.
  Setting it higher slows the advance.

Test by pressing SW4 once from CHASE to reach THEATRE. You should see
three evenly-spaced lit pixels. Press SW2 to change the advance
rate. At rate=1 the pattern moves quickly; at rate=20 it moves slowly.

--------------------------------------------------------------------------------
Step 7 - RAINBOW mode
--------------------------------------------------------------------------------

Implement MODE_RAINBOW following the TODO comment.

Key ideas:
- i * 360 / NUM_LEDS spreads the full colour spectrum (0-360 degrees)
  evenly across the strip. Pixel 0 gets hue 0, the middle pixel gets
  hue ~180, the last pixel gets hue close to 360. This is integer
  division - i, 360, and NUM_LEDS are all int, so the result is a
  whole number automatically.
- Adding rainbow_offset to every pixel's hue shifts the gradient along
  the strip. Incrementing rainbow_offset each frame makes it rotate.
- % 360 keeps the hue in the valid range as the offset grows.

Test: the strip should show a smooth continuous spectrum from red
through green, blue, and back to red. Pressing SW2 should increase
the rotation speed.

--------------------------------------------------------------------------------
Step 8 - PULSE mode
--------------------------------------------------------------------------------

Implement MODE_PULSE following the TODO comment.

Key ideas:
- pulse_bright is used directly as the brightness argument, not
  MAX_BRIGHTNESS. This is the key difference from SOLID, where the
  brightness is fixed at MAX_BRIGHTNESS.
- The ramp uses min() and max() to clamp pulse_bright within
  [0, MAX_BRIGHTNESS] rather than checking with if/else. Both
  approaches work - min/max is more concise.
- The hue advances by 30 degrees at the bottom of each cycle so each
  pulse is a slightly different colour.

Test: the strip should fade smoothly from black to full brightness and
back to black. Confirm true black is reached at the bottom (not just
very dim). Confirm the hue shifts slightly with each new cycle.

--------------------------------------------------------------------------------
Step 9 - Full integration
--------------------------------------------------------------------------------

Cycle through all modes with SW3 and SW4. Check:
- Each mode produces the expected animation
- SW2 adjusts the correct parameter in each mode (with hold-and-repeat)
- SW3 cycles backward (CHASE -> SOLID -> PULSE -> RAINBOW -> ...)
- SW5 turns the strip off and back on, returning to the last mode
- The strip clears cleanly when entering each new mode
- The confirmation beep fires once per mode press (not while holding)

Open the Serial Monitor and confirm mode transition messages print
correctly and that parameter adjustments print with the right values.

--------------------------------------------------------------------------------
Step 10 - RGBW strips (SK6812)
--------------------------------------------------------------------------------

To use an SK6812 RGBW strip instead of a WS2812B:

1. Change the strip constructor's NEO_GRB to NEO_GRBW
2. Change STRIP_IS_RGBW = false to STRIP_IS_RGBW = true
3. Connect the strip data input to H1 instead of H5 - H1 and H5
   share GPIO 11 on the BEAPER Nano, so the pin assignment in code
   does not change, only which physical header you wire to.

set_pixel() handles the rest: it automatically calls the four-argument
version of setPixelColor() with white set to 0 when STRIP_IS_RGBW is
true. All modes will work without any other changes.

To use the white channel deliberately rather than leaving it at 0,
see Extension Activity 'e', which uses hsvToRGBW() - a second
function in colour.h that extracts a genuine white component from a
colour, rather than always returning 0.

*/


/* ================================================================================
Extensions
================================================================================

--------------------------------------------------------------------------------
EA a - PULSE_STEP control
--------------------------------------------------------------------------------

Right now PULSE_STEP is a constant you define. Add it as a SW2
parameter in MODE_PULSE so students can adjust how fast the pulse
ramps. What range of values produces smooth fades vs. harsh flashing?

--------------------------------------------------------------------------------
EA b - COMET effect
--------------------------------------------------------------------------------

Modify CHASE to draw a short fading tail behind the lit pixel. Each
frame, instead of clearing the whole strip, dim every pixel by
reading back its current colour and multiplying by a fade factor < 1
(e.g. 0.7). strip.getPixelColor(i) returns the colour packed into a
single 32-bit value rather than separate r/g/b numbers - unpack it
with bit shifting:

Example code:

uint32_t packed = strip.getPixelColor(i);
uint8_t old_r = (packed >> 16) & 0xFF;
uint8_t old_g = (packed >> 8) & 0xFF;
uint8_t old_b = packed & 0xFF;

Then set the head pixel to full brightness. How does the tail length
change with the fade factor?

--------------------------------------------------------------------------------
EA c - THEATRE colour gradient
--------------------------------------------------------------------------------

Instead of all lit pixels being the same hue, assign each lit pixel
a hue based on its position (similar to RAINBOW). The pattern should
still advance each frame. How does this change the appearance of the
animation?

--------------------------------------------------------------------------------
EA d - Beat-reactive brightness
--------------------------------------------------------------------------------

Read an analog input (e.g. RV1_level() with JP2=Enviro., or an
external microphone on H1) and map the reading to MAX_BRIGHTNESS
using map(). This makes the strip brightness respond to the
potentiometer or to sound. Which mode looks best with a changing
brightness?

--------------------------------------------------------------------------------
EA e - White channel mood lamp
--------------------------------------------------------------------------------

For SK6812 strips only. Create a new mode that ignores the colour
channels and uses only the white channel, slowly pulsing between
warm-white and off.

colour.h provides a second conversion function, hsvToRGBW(), that is
more accurate than this file's own set_pixel() for RGBW strips:
rather than always setting white to 0, it extracts the brightness
shared by all three RGB channels as a genuine white component:

Example code:

RGBW colour = hsvToRGBW(hue, saturation, value);
// colour.r, colour.g, colour.b, colour.w

For a pure white-channel mood lamp specifically, an even simpler
approach works: call hsvToRGBW() with saturation=0, which produces
r=g=b=0 and puts all the brightness into w directly. Compare the
light quality to the PULSE mode running in white (hue=0,
saturation=0) using the RGB channels instead - white channel light
tends to look "warmer" and more neutral than mixing white from RGB.

--------------------------------------------------------------------------------
EA f - Star Wars light saber
--------------------------------------------------------------------------------

Press a button to grow the 'blade' from the hilt, and then shimmer
the brightness. Pressing the button again shrinks the blade back
down into the hilt. Use another button to change or cycle the
colour of the light saber blade.

*/
