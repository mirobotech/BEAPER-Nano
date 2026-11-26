/* ================================================================================
Reach-Ahead: Reaction Time Game with LCD Display [BEAPERNano-Reaction-Game-LCD]
Version: 1.2
Updated: November 24, 2026

Platform: mirobo.tech BEAPER Nano circuit with optional 1.54" LCD
Requires: BEAPERNano_v1_2.h header file, Adafruit_GFX library, Adafruit_ST7789
  library (install both via the Arduino Library Manager)

A preview of what an LCD display can add to a program you already
know well - this is a complete, working version of the Reaction
Time Game capstone, with its result screen shown on an LCD instead
of only printed to the Serial Monitor. It uses a handful of drawing
functions you have not seen before (fillRect(), setCursor(), print())
in the same way you already call functions like tone() or delay() -
as tools to use, not something you need to understand the inner
workings of yet.

Game modes and rules are unchanged from the original Reaction Time
Game capstone - see that file for the full design discussion. This
version fills in all of that capstone's TODOs so you have a
complete, working reference to read alongside your own attempt.

--------------------------------------------------------------------------------
IMPORTANT - hardware verification needed:

This program has not been tested against real BEAPER Nano hardware
and has two genuine unknowns that only testing on the actual board
can resolve:

  1. setRotation() - the value below (2) is a starting guess, not a
     confirmed match for BEAPER Nano's physical LCD mounting. If the
     display appears upside-down or sideways, try values 0, 1, or 3
     instead.

  2. Panel offset - the mirobo.tech MicroPython LCD driver (LCD.py)
     uses a custom rotation table with non-zero pixel offsets for
     two of its four rotations, which suggests this specific 240x240
     panel's addressable driver memory may be larger than the
     visible area (a common situation for ST7789 panels sold as
     240x240 that are internally addressed as part of a larger
     240x320 memory map). Adafruit_ST7789's generic init(240, 240)
     may not automatically apply the same offset. If the image
     appears shifted, cropped, or wrapped, check the Adafruit_ST7789
     library documentation for setColRowStart() or an equivalent
     offset-configuration call.

--------------------------------------------------------------------------------
Hardware used:
  SW1          - Start a round / react during a round
  SW2 / SW3    - Cycle game mode (only while at the menu)
  SW4          - Cancel the current round, return to the menu
  LS1          - Piezo speaker (stimulus/target beep, result tones)
  On-board LED - On during an active round
  LCD          - Shows the result of each round
=================================================================================*/
// IMPORTANT: Make sure that BEAPERNano_v1_2.h is accessible as a tab in this project.
#include "BEAPERNano_v1_2.h"      // Define BEAPER Nano I/O devices
#include <Adafruit_GFX.h>    // Core graphics library
#include <Adafruit_ST7789.h> // Hardware-specific library for ST7789
#include <SPI.h>

// ---- LCD Pin Configuration -----------------
// Matches LCDconfig_Nano.py's SPI(2, sck=48, mosi=38, ...) configuration.
// No reset pin - BEAPER Nano's LCD reset is hard-wired to the RESET
// button circuit, not a separate GPIO, so -1 (unused) is passed below.
const int TFT_CS   = 21;
const int TFT_DC   = 18;
const int TFT_SCLK = 48;
const int TFT_MOSI = 38;

SPIClass *tftSPI = NULL;
Adafruit_ST7789 *tft = NULL;

// ---- LCD Colors (RGB565) -------------------
// Matching LCD.py's pre-computed values exactly, rather than
// recomputing them from RGB and risking a rounding difference.
const uint16_t COLOR_WHITE    = 0xFFFF;
const uint16_t COLOR_WHITE50  = 0x4208;
const uint16_t COLOR_CYAN75   = 0x05FB;
const uint16_t COLOR_GREEN75  = 0x05E0;
const uint16_t COLOR_RED75    = 0xB800;
const uint16_t COLOR_YELLOW75 = 0xBDE0;
const uint16_t COLOR_BLUE50   = 0x0004;
const uint16_t COLOR_GREY     = 0x2104;
const uint16_t COLOR_BLACK    = 0x0000;

// ---- State Constants -------------------
const int STATE_MENU    = 0;         // Selecting a mode, waiting to start
const int STATE_WAITING = 1;         // SIMPLE only: waiting out the random delay
const int STATE_REACT   = 2;         // SIMPLE only: stimulus is showing, timing the press
const int STATE_CHASING = 3;         // TIMING only: chase pattern running
const int STATE_RESULT  = 4;         // Showing the result of the last round

const char* STATE_NAMES[] = { "MENU", "WAITING", "REACT", "CHASING", "RESULT" };

// ---- Mode Constants -----------------------
const int MODE_SIMPLE = 0;
const int MODE_TIMING = 1;
const int NUM_MODES   = 2;

const char* MODE_NAMES[] = { "SIMPLE", "TIMING" };

// ---- Simple Reaction Time Configuration ---
const int REACT_LED   = LED1;        // The single stimulus LED for SIMPLE mode
const int MIN_WAIT_MS = 1500;        // Shortest possible random delay before the stimulus
const int MAX_WAIT_MS = 4000;        // Longest possible random delay before the stimulus

// ---- Timing/Anticipation Configuration -----
const int CHASE_LEDS[]      = { LED1, LED2, LED3, LED4 };
const int CHASE_INTERVAL_MS = 300;   // Time the chase spends on each LED
const int TARGET_POSITION   = 2;     // Index into CHASE_LEDS - 2 = LED3

// ---- Timing Constants -----------------------
const int RESULT_DISPLAY_MS = 2500;  // Minimum time a result is shown before advancing
const int LOOP_DELAY        = 1;     // Main loop delay (ms) - kept short for timing precision

// ---- LCD Layout Constants ----------------
const int SCREEN_WIDTH  = 240;
const int SCREEN_HEIGHT = 240;
const int HEADER_H      = 40;
const int BAR_X         = 20;
const int BAR_Y         = 170;
const int BAR_WIDTH     = 200;
const int BAR_HEIGHT    = 26;
const int MAX_BAR_MS    = 1000;      // Values at or above this fill the whole bar

// ---- Program Variables -----------------------
int  state             = STATE_MENU;
unsigned long state_start = 0;

int current_mode = MODE_SIMPLE;

// ---- SIMPLE mode variables ----
unsigned long wait_duration      = 0;
unsigned long stimulus_time      = 0;
unsigned long reaction_time      = 0;
unsigned long best_reaction_time = 999999;
bool false_start = false;

// ---- TIMING mode variables ----
int  chase_position          = 0;
unsigned long last_chase_step      = 0;
unsigned long last_target_lit_time = 0;
unsigned long timing_error         = 0;
unsigned long best_timing_error    = 999999;

// ---- SW2/SW3 edge detection (menu mode cycling) ----
int sw2_last = 1;
int sw3_last = 1;

// ---- Result tracking (for the LCD screen) ----
bool result_shown        = false;
bool result_was_new_best = false;
unsigned long result_value = 0;
bool result_failed       = false;
const char* result_fail_message = "";


// ---- Program Functions -----------------------

void all_choice_leds_off()
{
    for (int i = 0; i < 4; i++)
        digitalWrite(CHASE_LEDS[i], LOW);   // CHASE_LEDS[0] is REACT_LED (LED1)
}

void enter_state(int new_state, unsigned long current_time, const char* reason = "")
{
    state       = new_state;
    state_start = current_time;
    Serial.print("--> ");
    Serial.print(STATE_NAMES[new_state]);
    if (reason[0] != '\0')
    {
        Serial.print(" (");
        Serial.print(reason);
        Serial.println(")");
    }
    else
    {
        Serial.println();
    }
}

void start_round(unsigned long current_time)
{
    digitalWrite(LED_BUILTIN, HIGH);
    all_choice_leds_off();
    result_shown = false;
    if (current_mode == MODE_SIMPLE)
    {
        wait_duration = random(MIN_WAIT_MS, MAX_WAIT_MS + 1);   // +1: random() excludes its upper bound
        false_start   = false;
        enter_state(STATE_WAITING, current_time, "round start");
    }
    else if (current_mode == MODE_TIMING)
    {
        chase_position   = 0;
        last_chase_step  = current_time;
        digitalWrite(CHASE_LEDS[0], HIGH);
        if (TARGET_POSITION == 0)
            last_target_lit_time = current_time;
        enter_state(STATE_CHASING, current_time, "round start");
    }
}

// print_centered() wraps the three-call GFX pattern for centred text
// (getTextBounds() to measure the string, setCursor() to position it,
// print() to draw it) into a single reusable call - the same role
// LCD.py's text16_width() played for centring in the MicroPython
// version, adapted to how Adafruit_GFX actually measures text.
void print_centered(const char* str, int y, uint16_t color, uint8_t size)
{
    int16_t x1, y1;
    uint16_t w, h;
    tft->setTextSize(size);
    tft->getTextBounds(str, 0, 0, &x1, &y1, &w, &h);
    tft->setCursor((SCREEN_WIDTH - w) / 2, y);
    tft->setTextColor(color);
    tft->print(str);
}

void draw_menu()
{
    tft->fillScreen(COLOR_BLACK);
    tft->fillRect(0, 0, SCREEN_WIDTH, HEADER_H, COLOR_BLUE50);
    print_centered("Reaction Game", 12, COLOR_WHITE, 2);
    print_centered(MODE_NAMES[current_mode], 100, COLOR_CYAN75, 2);
    print_centered("SW1: play  SW2/3: mode", 210, COLOR_WHITE50, 1);
}

void draw_result()
{
    tft->fillScreen(COLOR_BLACK);
    tft->fillRect(0, 0, SCREEN_WIDTH, HEADER_H, COLOR_BLUE50);
    print_centered(MODE_NAMES[current_mode], 12, COLOR_WHITE, 2);

    if (result_failed)
    {
        print_centered(result_fail_message, 100, COLOR_RED75, 2);
    }
    else
    {
        uint16_t color = result_was_new_best ? COLOR_GREEN75 : COLOR_CYAN75;
        char value_str[16];
        sprintf(value_str, "%lu ms", result_value);
        print_centered(value_str, 70, color, 2);

        if (result_was_new_best)
            print_centered("NEW BEST!", 100, COLOR_YELLOW75, 2);

        // Bar chart: filled portion shows this round's time, scaled so a
        // time at or above MAX_BAR_MS fills the whole bar. This is the
        // same "multiply then divide" scaling used for PWM brightness in
        // Activity 10 and analog sensor thresholds throughout this
        // curriculum, applied here to a time value instead.
        unsigned long capped_value = min(result_value, (unsigned long)MAX_BAR_MS);
        int bar_fill = capped_value * BAR_WIDTH / MAX_BAR_MS;
        tft->drawRect(BAR_X, BAR_Y, BAR_WIDTH, BAR_HEIGHT, COLOR_GREY);
        tft->fillRect(BAR_X, BAR_Y, bar_fill, BAR_HEIGHT, color);

        // Best-time marker - skipped on the very first successful round of
        // a session, when no best has been set yet (still at its 999999
        // sentinel value).
        unsigned long best_value = (current_mode == MODE_SIMPLE) ? best_reaction_time : best_timing_error;
        if (best_value != 999999)
        {
            unsigned long capped_best = min(best_value, (unsigned long)MAX_BAR_MS);
            int best_x = BAR_X + capped_best * BAR_WIDTH / MAX_BAR_MS;
            tft->drawFastVLine(best_x, BAR_Y - 6, BAR_HEIGHT + 12, COLOR_YELLOW75);
        }
    }

    print_centered("SW1: again  SW4: menu", 210, COLOR_WHITE50, 1);
}


void setup()
{
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, LOW);

    for (int i = 0; i < 4; i++)
        pinMode(CHASE_LEDS[i], OUTPUT);

    pinMode(SW1, INPUT_PULLUP);
    pinMode(SW2, INPUT_PULLUP);
    pinMode(SW3, INPUT_PULLUP);
    pinMode(SW4, INPUT_PULLUP);

    Serial.begin(9600);
    delay(2000);

    randomSeed(millis());

    // Set up the LCD on a custom hardware SPI peripheral (matching
    // LCDconfig_Nano.py's SPI(2, sck=48, mosi=38, ...) configuration) -
    // NOT the default SPI pins, so the hardware-SPI-with-custom-pins
    // constructor is needed rather than the simpler default-pins one.
    tftSPI = new SPIClass(HSPI);
    tftSPI->begin(TFT_SCLK, -1, TFT_MOSI, TFT_CS);   // sck, miso (unused), mosi, ss
    tft = new Adafruit_ST7789(tftSPI, TFT_CS, TFT_DC, -1);   // -1: no reset pin
    tft->init(240, 240);
    tft->setRotation(2);   // See the hardware verification note at the top of this file
    tft->setTextWrap(false);

    all_choice_leds_off();
    Serial.println("Reaction Time Game with LCD Display");
    Serial.println("SW2/SW3: change mode   SW1: start / react   SW4: cancel");
    Serial.println();

    state_start = millis();
    enter_state(STATE_MENU, state_start, "startup");
    draw_menu();
}

void loop()
{
    unsigned long current_time = millis();
    unsigned long elapsed      = current_time - state_start;

    // ---- Cancel (SW4) - checked before all state logic, except at the menu ----
    if (digitalRead(SW4) == LOW && state != STATE_MENU && state != STATE_RESULT)
    {
        all_choice_leds_off();
        digitalWrite(LED_BUILTIN, LOW);
        enter_state(STATE_MENU, current_time, "cancelled");
        draw_menu();
    }

    // ---- State: Menu ----
    else if (state == STATE_MENU)
    {
        int sw2_current = digitalRead(SW2);
        int sw3_current = digitalRead(SW3);
        if ((sw2_current == LOW && sw2_last == HIGH) || (sw3_current == LOW && sw3_last == HIGH))
        {
            current_mode = (current_mode + 1) % NUM_MODES;
            Serial.print("Mode: "); Serial.println(MODE_NAMES[current_mode]);
            draw_menu();
        }
        sw2_last = sw2_current;
        sw3_last = sw3_current;

        if (digitalRead(SW1) == LOW)
            start_round(current_time);
    }

    // ---- State: Waiting (SIMPLE mode - random delay before stimulus) ----
    else if (state == STATE_WAITING)
    {
        if (digitalRead(SW1) == LOW)
        {
            false_start = true;
            enter_state(STATE_RESULT, current_time, "false start");
        }
        else if (elapsed >= wait_duration)
        {
            digitalWrite(REACT_LED, HIGH);
            tone(LS1, 880, 100);
            stimulus_time = current_time;
            enter_state(STATE_REACT, current_time);
        }
    }

    // ---- State: React (SIMPLE mode - stimulus is showing) ----
    else if (state == STATE_REACT)
    {
        if (digitalRead(SW1) == LOW)
        {
            reaction_time = current_time - stimulus_time;
            if (reaction_time < best_reaction_time)
                best_reaction_time = reaction_time;
            digitalWrite(REACT_LED, LOW);
            enter_state(STATE_RESULT, current_time);
        }
    }

    // ---- State: Chasing (TIMING mode) ----
    else if (state == STATE_CHASING)
    {
        if ((current_time - last_chase_step) >= (unsigned long)CHASE_INTERVAL_MS)
        {
            digitalWrite(CHASE_LEDS[chase_position], LOW);
            chase_position = (chase_position + 1) % 4;
            digitalWrite(CHASE_LEDS[chase_position], HIGH);
            last_chase_step = current_time;
            if (chase_position == TARGET_POSITION)
            {
                last_target_lit_time = current_time;
                tone(LS1, 660, 80);
            }
        }

        if (digitalRead(SW1) == LOW)
        {
            timing_error = abs((long)(current_time - last_target_lit_time));
            if (timing_error < best_timing_error)
                best_timing_error = timing_error;
            all_choice_leds_off();
            enter_state(STATE_RESULT, current_time);
        }
    }

    // ---- State: Result ----
    else if (state == STATE_RESULT)
    {
        if (!result_shown)
        {
            result_shown = true;
            digitalWrite(LED_BUILTIN, LOW);

            if (current_mode == MODE_SIMPLE && false_start)
            {
                result_failed = true;
                result_fail_message = "Too soon!";
                Serial.println("Too soon!");
                tone(LS1, 220, 300);
            }
            else
            {
                result_failed = false;
                if (current_mode == MODE_SIMPLE)
                {
                    result_value = reaction_time;
                    result_was_new_best = (reaction_time == best_reaction_time);
                }
                else
                {
                    result_value = timing_error;
                    result_was_new_best = (timing_error == best_timing_error);
                }

                Serial.print(MODE_NAMES[current_mode]);
                Serial.print(" result: "); Serial.print(result_value); Serial.print(" ms");
                Serial.println(result_was_new_best ? " (new best!)" : "");

                if (result_was_new_best)
                {
                    tone(LS1, 660, 100);
                    delay(120);
                    tone(LS1, 880, 150);
                }
                else
                {
                    tone(LS1, 440, 150);
                }
            }

            draw_result();
        }

        if (elapsed >= (unsigned long)RESULT_DISPLAY_MS)
        {
            if (digitalRead(SW1) == LOW)
            {
                start_round(current_time);
            }
            else if (digitalRead(SW4) == LOW)
            {
                enter_state(STATE_MENU, current_time, "SW4 pressed");
                draw_menu();
            }
        }
    }

    delay(LOOP_DELAY);
}
