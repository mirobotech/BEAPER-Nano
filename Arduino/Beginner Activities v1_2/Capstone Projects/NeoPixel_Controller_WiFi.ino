/* ================================================================================
Reach-Ahead: WiFi NeoPixel Controller [BEAPERNano-Reaction-NeoPixel-WiFi]
Version: 1.2
Updated: November 24, 2026

Platform: mirobo.tech BEAPER Nano circuit (robot configuration with
  voltage regulator U1 and 74HCT541 buffer/level shifter U2 is needed
  to run short 5V NeoPixel sticks or rings)
Requires: BEAPERNano_v1_2.h header file, colour.h conversion header,
  Adafruit_NeoPixel library (install via Arduino Library Manager)

A preview of what WiFi can add to a program you already know well -
this is a complete, working version of the NeoPixel Controller
capstone (with all of its modes filled in as a reference), plus a
second way to control it: a web page served directly from the
BEAPER Nano itself. Connect a phone or laptop to the BEAPER Nano's
own WiFi network, open a web browser, and control the strip from
there - at the same time as the physical buttons, which keep
working exactly as before.

This program creates its own WiFi network (an "access point") -
there is no need for an existing WiFi router, a network password
you don't know, or an internet connection. The BEAPER Nano's
built-in ESP32-S3 WiFi radio does all of this without any extra
hardware. This program uses the Arduino ESP32 core's built-in
WebServer library, which handles the details of parsing an HTTP
request and routing it to the right handler function - a genuinely
easier tool for this job than manually parsing raw text, the same
way beaper.tone() is easier than generating a square wave by hand.
A future intermediate-course activity covers networking in depth;
this program does not attempt to teach that here.

Hardware used:
  SW1        - Cycle parameter up within the current mode (hold to repeat)
  SW2        - Previous animation mode (cycles backward)
  SW3        - Next animation mode (cycles forward)
  SW4        - Toggle strip on/off (remembers the last active mode)
  LS1        - Piezo speaker (mode-change confirmation beep)
  On-board LED - On while a mode is active

  NeoPixel strip (data input connects to PIXEL_PIN - see strip setup, below)

--------------------------------------------------------------------------------
Connecting to the web interface:

  1. Run this program. Watch the Serial Monitor for a line like:
       Connect to WiFi network: BEAPER-NeoPixel  (password: beaper123)
       Then browse to: http://192.168.4.1/
  2. On your phone or laptop, open WiFi settings and connect to the
     "BEAPER-NeoPixel" network using the password shown.
  3. Open a web browser and go to the address shown. You do not need
     an internet connection - you are connecting directly to the
     BEAPER Nano.
  4. Tap a mode link to switch modes. Once a mode is active, drag the
     slider to adjust that mode's parameter (hue for SOLID and PULSE,
     speed or rate for the others) - this offers smoother, direct
     control than SW1's one-step-at-a-time button press, and either
     control method can be used at any time, even switching back and
     forth.

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
Animation modes (selected with SW2/SW3 or the web page):
  OFF      - Strip dark. SW4 toggles between OFF and the last active mode.
  SOLID    - All pixels set to a single colour.
  CHASE    - One lit pixel travels along the strip.
  THEATRE  - Every third pixel lit, pattern advances each frame.
  RAINBOW  - Full spectrum gradient slowly rotates along the strip.
  PULSE    - All pixels fade in and out; hue advances each cycle.
=================================================================================*/
// IMPORTANT: Make sure that BEAPERNano_v1_2.h and colour.h are accessible as tabs
// in this project.
#include "BEAPERNano_v1_2.h"        // Define BEAPER Nano I/O devices
#include "colour.h"            // HSV-to-RGB colour conversion - see colour.h
#include <Adafruit_NeoPixel.h>
#include <WiFi.h>
#include <WebServer.h>

// =============================================================================
// Strip configuration - set these to match your hardware
// =============================================================================

const int NUM_LEDS = 30;
const int MAX_BRIGHTNESS = 32;
bool STRIP_IS_RGBW = false;
const int PIXEL_PIN = H5;
Adafruit_NeoPixel strip(NUM_LEDS, PIXEL_PIN, NEO_GRB + NEO_KHZ800);

// =============================================================================
// WiFi Access Point configuration
// =============================================================================

const char* AP_SSID     = "BEAPER-NeoPixel";
const char* AP_PASSWORD = "beaper123";        // Must be at least 8 characters for WPA2
IPAddress AP_IP(192, 168, 4, 1);
IPAddress AP_GATEWAY(192, 168, 4, 1);
IPAddress AP_SUBNET(255, 255, 255, 0);

WebServer server(80);

// =============================================================================
// Mode constants
// =============================================================================

const int MODE_OFF     = 0;
const int MODE_SOLID   = 1;
const int MODE_CHASE   = 2;
const int MODE_THEATRE = 3;
const int MODE_RAINBOW = 4;
const int MODE_PULSE   = 5;

const int NUM_MODES = 6;

const char* MODE_NAMES[] = { "OFF", "SOLID", "CHASE", "THEATRE", "RAINBOW", "PULSE" };

// =============================================================================
// Timing constants
// =============================================================================

const int LOOP_DELAY     = 1;
const int FRAME_INTERVAL = 20;
const int ADJUST_FIRST   = 500;
const int ADJUST_REPEAT  = 80;

// =============================================================================
// Animation parameter defaults
// =============================================================================

const int DEFAULT_HUE           = 0;
const int DEFAULT_CHASE_SPEED   = 1;
const int DEFAULT_THEATRE_RATE  = 3;
const int DEFAULT_RAINBOW_SPEED = 2;
const int PULSE_STEP            = 2;

// =============================================================================
// Program variables
// =============================================================================

int mode = MODE_OFF;

int hue = DEFAULT_HUE;

int chase_pos   = 0;
int chase_speed = DEFAULT_CHASE_SPEED;

int theatre_offset = 0;
int theatre_rate   = DEFAULT_THEATRE_RATE;
int theatre_frames = 0;

int rainbow_offset = 0;
int rainbow_speed  = DEFAULT_RAINBOW_SPEED;

int  pulse_bright = 0;
bool pulse_up     = true;

unsigned long last_frame_time = 0;

bool sw1_held           = false;
unsigned long sw1_held_start  = 0;
unsigned long sw1_last_repeat = 0;

int sw2_last = 1;
int sw3_last = 1;
int sw4_last = 1;

int last_active_mode = MODE_SOLID;


// =============================================================================
// Helper functions
// =============================================================================

RGB scale_colour(uint8_t r, uint8_t g, uint8_t b, uint8_t brightness)
{
    float factor = brightness / 255.0;
    RGB result;
    result.r = (uint8_t)(r * factor);
    result.g = (uint8_t)(g * factor);
    result.b = (uint8_t)(b * factor);
    return result;
}

void set_pixel(int i, uint8_t r, uint8_t g, uint8_t b)
{
    if (STRIP_IS_RGBW)
        strip.setPixelColor(i, r, g, b, 0);
    else
        strip.setPixelColor(i, r, g, b);
}

void fill_strip(uint8_t r, uint8_t g, uint8_t b)
{
    for (int i = 0; i < NUM_LEDS; i++)
        set_pixel(i, r, g, b);
    strip.show();
}

void clear_strip()
{
    fill_strip(0, 0, 0);
}

void enter_mode(int new_mode)
{
    // Transition to a new mode. Both the physical buttons and the web
    // interface (via the /mode/... routes below) call this same
    // function, so the two control methods always stay in sync.
    mode           = new_mode;
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

void adjust_parameter()
{
    // Advance the current mode's adjustable parameter by one step -
    // SW1's (physical) behaviour. See set_parameter() for the web
    // slider's direct-set equivalent - both act on the same
    // underlying variables.
    if (mode == MODE_SOLID || mode == MODE_PULSE)
    {
        hue = (hue + 10) % 360;
        Serial.print("    hue: "); Serial.println(hue);
    }
    else if (mode == MODE_CHASE)
    {
        chase_speed = chase_speed % 20 + 1;
        Serial.print("    chase speed: "); Serial.println(chase_speed);
    }
    else if (mode == MODE_THEATRE)
    {
        theatre_rate = theatre_rate % 20 + 1;
        Serial.print("    theatre rate: "); Serial.println(theatre_rate);
    }
    else if (mode == MODE_RAINBOW)
    {
        rainbow_speed = rainbow_speed % 20 + 1;
        Serial.print("    rainbow speed: "); Serial.println(rainbow_speed);
    }
}

void set_parameter(int value)
{
    // Directly set the current mode's adjustable parameter to a
    // specific value - the web slider's behaviour. Clamped to each
    // parameter's valid range, since the value arrives as text from
    // the network and should not be trusted to already be in range.
    if (mode == MODE_SOLID || mode == MODE_PULSE)
    {
        // A plain value % 360 could still be negative if a malformed
        // request ever sent a negative number (C's % keeps the
        // dividend's sign, unlike Python's) - adding 360 before the
        // second % guarantees a non-negative result in the 0-359
        // range regardless.
        hue = ((value % 360) + 360) % 360;
    }
    else if (mode == MODE_CHASE)
        chase_speed = max(1, min(20, value));
    else if (mode == MODE_THEATRE)
        theatre_rate = max(1, min(20, value));
    else if (mode == MODE_RAINBOW)
        rainbow_speed = max(1, min(20, value));
}

bool check_sw2(unsigned long current_time)
{
    int sw1_current = digitalRead(SW1);
    if (sw1_current == LOW)
    {
        if (!sw1_held)
        {
            sw1_held        = true;
            sw1_held_start  = current_time;
            sw1_last_repeat = current_time;
            return true;
        }
        else if ((current_time - sw1_held_start) >= (unsigned long)ADJUST_FIRST &&
                 (current_time - sw1_last_repeat) >= (unsigned long)ADJUST_REPEAT)
        {
            sw1_last_repeat = current_time;
            return true;
        }
    }
    else
    {
        sw1_held = false;
    }
    return false;
}


// =============================================================================
// Web server
// =============================================================================

String buildSliderSection()
{
    if (mode == MODE_OFF)
        return "";

    String label, minVal, maxVal, value;
    if (mode == MODE_SOLID || mode == MODE_PULSE)
    {
        label = "Hue"; minVal = "0"; maxVal = "359"; value = String(hue);
    }
    else if (mode == MODE_CHASE)
    {
        label = "Chase Speed"; minVal = "1"; maxVal = "20"; value = String(chase_speed);
    }
    else if (mode == MODE_THEATRE)
    {
        label = "Theatre Rate"; minVal = "1"; maxVal = "20"; value = String(theatre_rate);
    }
    else if (mode == MODE_RAINBOW)
    {
        label = "Rainbow Speed"; minVal = "1"; maxVal = "20"; value = String(rainbow_speed);
    }

    String html = "<p>" + label + "</p>";
    html += "<input type=\"range\" id=\"param\" min=\"" + minVal + "\" max=\"" + maxVal +
            "\" value=\"" + value + "\" oninput=\"sendUpdate()\">";
    return html;
}

String buildHtml()
{
    // Built fresh on every request, so it always shows the current
    // state - including changes made from the physical buttons, not
    // just from the web page itself.
    String html = "<!DOCTYPE html><html><head><meta charset=\"UTF-8\">";
    html += "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">";
    html += "<title>NeoPixel Controller</title><style>";
    html += "body { font-family: sans-serif; text-align: center; margin-top: 30px; background: #222; color: #eee; }";
    html += "input[type=range] { width: 80%; }";
    html += "a { color: #6cf; margin: 0 6px; text-decoration: none; }";
    html += "</style></head><body>";
    html += "<h2>BEAPER NeoPixel Controller</h2>";
    html += "<p style=\"font-size:1.2em;\">Mode: " + String(MODE_NAMES[mode]) + "</p>";
    html += "<p>";
    html += "<a href=\"/mode/off\">Off</a> | ";
    html += "<a href=\"/mode/solid\">Solid</a> | ";
    html += "<a href=\"/mode/chase\">Chase</a> | ";
    html += "<a href=\"/mode/theatre\">Theatre</a> | ";
    html += "<a href=\"/mode/rainbow\">Rainbow</a> | ";
    html += "<a href=\"/mode/pulse\">Pulse</a>";
    html += "</p>";
    html += buildSliderSection();
    html += "<script>";
    html += "let updatePending = false;";
    html += "function sendUpdate() {";
    html += "  if (updatePending) return;";
    html += "  updatePending = true;";
    html += "  setTimeout(function() {";
    html += "    let value = document.getElementById('param').value;";
    html += "    fetch(`/update?value=${value}`).finally(function() { updatePending = false; });";
    html += "  }, 100);";
    html += "}";
    html += "</script></body></html>";
    return html;
}

void handleRoot()
{
    server.send(200, "text/html", buildHtml());
}

void handleMode()
{
    // server.uri() gives the full request path, e.g. "/mode/chase" -
    // this one handler is registered for all six /mode/... routes
    // below, so it dispatches based on which path was actually
    // requested.
    String path = server.uri();
    if (path == "/mode/off")          enter_mode(MODE_OFF);
    else if (path == "/mode/solid")   enter_mode(MODE_SOLID);
    else if (path == "/mode/chase")   enter_mode(MODE_CHASE);
    else if (path == "/mode/theatre") enter_mode(MODE_THEATRE);
    else if (path == "/mode/rainbow") enter_mode(MODE_RAINBOW);
    else if (path == "/mode/pulse")   enter_mode(MODE_PULSE);

    server.send(200, "text/html", buildHtml());
}

void handleUpdate()
{
    if (server.hasArg("value"))
        set_parameter(server.arg("value").toInt());
    server.send(200, "text/plain", "OK");
}

void handleNotFound()
{
    // Any unrecognized path (including a browser's automatic request
    // for /favicon.ico) just shows the current status page, the same
    // as requesting "/" directly.
    server.send(200, "text/html", buildHtml());
}


void setup()
{
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, LOW);

    pinMode(SW1, INPUT_PULLUP);
    pinMode(SW2, INPUT_PULLUP);
    pinMode(SW3, INPUT_PULLUP);
    pinMode(SW4, INPUT_PULLUP);

    Serial.begin(9600);
    delay(2000);

    strip.begin();
    strip.show();

    WiFi.softAP(AP_SSID, AP_PASSWORD);
    WiFi.softAPConfig(AP_IP, AP_GATEWAY, AP_SUBNET);

    server.on("/", handleRoot);
    server.on("/mode/off", handleMode);
    server.on("/mode/solid", handleMode);
    server.on("/mode/chase", handleMode);
    server.on("/mode/theatre", handleMode);
    server.on("/mode/rainbow", handleMode);
    server.on("/mode/pulse", handleMode);
    server.on("/update", handleUpdate);
    server.onNotFound(handleNotFound);
    server.begin();

    Serial.println("WiFi NeoPixel Controller");
    Serial.print("Strip type: "); Serial.println(STRIP_IS_RGBW ? "RGBW" : "RGB");
    Serial.println();
    Serial.print("Connect to WiFi network: "); Serial.print(AP_SSID);
    Serial.print("  (password: "); Serial.print(AP_PASSWORD); Serial.println(")");
    Serial.print("Then browse to: http://"); Serial.print(WiFi.softAPIP()); Serial.println("/");
    Serial.println();
    Serial.println("SW2/SW3: previous/next mode   SW1: adjust parameter   SW4: on/off");
    Serial.println();

    last_frame_time = millis();
    enter_mode(MODE_OFF);
}

void loop()
{
    unsigned long current_time = millis();

    server.handleClient();   // Non-blocking - processes any pending web request

    // ---- Button: SW2 - previous mode -------------------------------------
    int sw2_current = digitalRead(SW2);
    if (sw2_current == LOW && sw2_last == HIGH)
    {
        if (mode != MODE_OFF)
            enter_mode((mode - 2 + (NUM_MODES - 1)) % (NUM_MODES - 1) + 1);
    }
    sw2_last = sw2_current;

    // ---- Button: SW3 - next mode -------------------------------------------
    int sw3_current = digitalRead(SW3);
    if (sw3_current == LOW && sw3_last == HIGH)
    {
        if (mode != MODE_OFF)
            enter_mode(mode % (NUM_MODES - 1) + 1);
    }
    sw3_last = sw3_current;

    // ---- Button: SW4 - toggle strip on/off ---------------------------------
    int sw4_current = digitalRead(SW4);
    if (sw4_current == LOW && sw4_last == HIGH)
    {
        if (mode == MODE_OFF)
        {
            enter_mode(last_active_mode);
        }
        else
        {
            last_active_mode = mode;
            enter_mode(MODE_OFF);
        }
    }
    sw4_last = sw4_current;

    // ---- SW1: cycle mode parameter (hold to repeat) ------------------------
    if (check_sw2(current_time))
        adjust_parameter();

    // ---- Animation frame (non-blocking, rate-limited by FRAME_INTERVAL) ---
    if ((current_time - last_frame_time) >= (unsigned long)FRAME_INTERVAL)
    {
        last_frame_time = current_time;

        if (mode == MODE_SOLID)
        {
            RGB raw    = hsvToRGB(hue, 100, 100);
            RGB scaled = scale_colour(raw.r, raw.g, raw.b, MAX_BRIGHTNESS);
            fill_strip(scaled.r, scaled.g, scaled.b);
        }
        else if (mode == MODE_CHASE)
        {
            RGB raw    = hsvToRGB(hue, 100, 100);
            RGB scaled = scale_colour(raw.r, raw.g, raw.b, MAX_BRIGHTNESS);
            clear_strip();
            set_pixel(chase_pos, scaled.r, scaled.g, scaled.b);
            strip.show();
            chase_pos = (chase_pos + chase_speed) % NUM_LEDS;
        }
        else if (mode == MODE_THEATRE)
        {
            RGB raw    = hsvToRGB(hue, 100, 100);
            RGB scaled = scale_colour(raw.r, raw.g, raw.b, MAX_BRIGHTNESS);
            for (int i = 0; i < NUM_LEDS; i++)
            {
                if (i % 3 == theatre_offset)
                    set_pixel(i, scaled.r, scaled.g, scaled.b);
                else
                    set_pixel(i, 0, 0, 0);
            }
            strip.show();
            theatre_frames++;
            if (theatre_frames >= theatre_rate)
            {
                theatre_frames = 0;
                theatre_offset = (theatre_offset + 1) % 3;
            }
        }
        else if (mode == MODE_RAINBOW)
        {
            for (int i = 0; i < NUM_LEDS; i++)
            {
                int pixel_hue = (rainbow_offset + i * 360 / NUM_LEDS) % 360;
                RGB raw    = hsvToRGB(pixel_hue, 100, 100);
                RGB scaled = scale_colour(raw.r, raw.g, raw.b, MAX_BRIGHTNESS);
                set_pixel(i, scaled.r, scaled.g, scaled.b);
            }
            strip.show();
            rainbow_offset = (rainbow_offset + rainbow_speed) % 360;
        }
        else if (mode == MODE_PULSE)
        {
            RGB raw    = hsvToRGB(hue, 100, 100);
            RGB scaled = scale_colour(raw.r, raw.g, raw.b, pulse_bright);
            fill_strip(scaled.r, scaled.g, scaled.b);
            if (pulse_up)
            {
                pulse_bright = min(pulse_bright + PULSE_STEP, MAX_BRIGHTNESS);
                if (pulse_bright == MAX_BRIGHTNESS)
                    pulse_up = false;
            }
            else
            {
                pulse_bright = max(pulse_bright - PULSE_STEP, 0);
                if (pulse_bright == 0)
                {
                    pulse_up = true;
                    hue = (hue + 30) % 360;
                }
            }
        }
    }

    delay(LOOP_DELAY);
}
