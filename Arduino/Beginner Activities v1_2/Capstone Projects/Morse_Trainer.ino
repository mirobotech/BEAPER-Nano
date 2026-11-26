/* ================================================================================
Capstone Project: Morse Code Trainer [BEAPERNano-Capstone-Morse-Trainer]
Version: 1.2
Updated: November 24, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPERNano_v1_2.h header file

Practice sending and receiving Morse code using a single button.
Hold SW1 briefly for a dot, longer for a dash - the same tap/hold
timing idea from Activity 11, applied to classify each press rather
than just detecting a hold.

Two modes, selected with SW2/SW3 at the menu:

  TRANSMIT - Free practice. Tap out letters at your own pace; each
             completed letter is decoded and printed as soon as you
             pause. No pressure, no scoring - just practice forming
             correct dot/dash patterns.

  RECEIVE  - The program picks a random letter and sends it back to
             you (LED1 flashes, LS1 beeps - a dot is a short flash,
             a dash is three times as long). You then tap the same
             letter back using the identical tap interface, and the
             program checks whether it matches.

Both modes rely on the exact same underlying mechanism - reading
taps, classifying each as a dot or dash, and detecting when a
letter is complete from the pause that follows it. That shared
logic lives in one function, read_tap(), that both modes call.

Hardware used:
  SW1          - Tap button (hold briefly for a dot, longer for a dash)
  SW2 / SW3    - Cycle mode (only while at the menu)
  SW4          - Start / return to menu
  LED1         - Lights while SW1 is held, and during RECEIVE's playback
  LS1          - Piezo speaker (tap tone, playback tone)

Compatible with all BEAPER Nano configurations. No additional
hardware or jumper changes required.

--------------------------------------------------------------------------------
Timing (see Development Guide Step 1 for calibration):
  DOT_MAX_MS    - a press shorter than this is a dot; longer is a dash
  LETTER_GAP_MS - a pause longer than this after a release, with no
                  new press, means the letter is complete

Real Morse timing uses fixed ratios: a dash is three dot-durations
long, the gap between letters is three dot-durations, and the gap
between words is seven. This trainer uses similar proportions but
with more forgiving absolute values, since tapping accurately by
hand is harder than a machine sending at a fixed rate.

--------------------------------------------------------------------------------
Trainer behaviour:
  MENU           - Select mode with SW2/SW3. Press SW4 to begin.
  TRANSMIT       - Continuous free-form tapping and decoding.
                   Press SW4 to return to the menu.
  RECEIVE_SEND   - The program sends a random letter.
  RECEIVE_LISTEN - Your turn - tap back the same letter.
  RECEIVE_RESULT - Shows whether you matched it, then starts
                   another round automatically.

Before you begin - complete your capstone plan using the Capstone
Preparation Guide: a plain-English description of each mode, a
state diagram, your constants and variables, and your testing plan.
=================================================================================*/
// IMPORTANT: Make sure that BEAPERNano_v1_2.h is accessible as a tab in this project.
#include "BEAPERNano_v1_2.h"   // Define BEAPER Nano I/O devices
#include <string.h>       // strcmp(), strcpy(), strlen() - see the note in read_tap()

// ---- State Constants -------------------
const int STATE_MENU           = 0;  // Selecting a mode
const int STATE_TRANSMIT       = 1;  // Free-form tapping and decoding
const int STATE_RECEIVE_SEND   = 2;  // Program is sending the target letter
const int STATE_RECEIVE_LISTEN = 3;  // Player taps the letter back
const int STATE_RECEIVE_RESULT = 4;  // Showing whether it matched

const char* STATE_NAMES[] = { "MENU", "TRANSMIT", "RECEIVE_SEND", "RECEIVE_LISTEN", "RECEIVE_RESULT" };

// ---- Mode Constants -----------------------
const int MODE_TRANSMIT = 0;
const int MODE_RECEIVE  = 1;
const int NUM_MODES     = 2;

const char* MODE_NAMES[] = { "TRANSMIT", "RECEIVE" };

// ---- Morse Code Lookup Table ---------------
// Two parallel arrays, indexed together - the same pattern used
// throughout this curriculum's capstones, here holding the full
// alphabet. MORSE_LETTERS[i] and MORSE_CODES[i] together describe
// one letter: MORSE_LETTERS[0] is 'A' (a single char, not a string -
// every letter is exactly one character), MORSE_CODES[0] is its
// dot/dash pattern ".-" (a C-string, since these vary in length).
const char  MORSE_LETTERS[] = { 'A','B','C','D','E','F','G','H','I','J','K','L','M',
                                 'N','O','P','Q','R','S','T','U','V','W','X','Y','Z' };
const char* MORSE_CODES[]   = { ".-","-...","-.-.","-..",".","..-.","--.","....","..",
                                 ".---","-.-",".-..","--","-.","---",".--.","--.-",
                                 ".-.","...","-","..-","...-",".--","-..-","-.--","--.." };
const int NUM_LETTERS = 26;

// ---- Tap Timing Configuration -------------
const int DOT_MAX_MS    = 300;       // Press shorter than this = dot; longer = dash
const int LETTER_GAP_MS = 700;       // Pause this long after a release = letter complete

// ---- Receive Mode Playback Configuration ---
const int SYMBOL_GAP_MS     = 200;   // Silent gap between symbols within one letter
const int DASH_MULTIPLIER   = 3;     // A dash is played this many times as long as a dot
const int RESULT_DISPLAY_MS = 2000;  // How long the RECEIVE result is shown

// ---- Program Variables -----------------------
int  state             = STATE_MENU;
unsigned long state_start = 0;

int current_mode = MODE_TRANSMIT;

// ---- Shared tap-reading state (used by read_tap(), see below) ----
// current_sequence is the ACTIVE buffer, appended to on every tap.
// completed_sequence is a separate, STABLE snapshot copied out of it
// only when a letter finishes - keeping these separate means the
// pointer read_tap() returns stays valid (pointing at data that will
// not change) even after later taps continue modifying
// current_sequence. Returning a pointer into current_sequence
// directly would risk the caller reading stale or half-updated data
// if it did not use the result immediately.
bool sw1_was_pressed   = false;
unsigned long press_start = 0;
char current_sequence[20]   = "";    // Symbols accumulated for the letter in progress
int  current_sequence_length = 0;
char completed_sequence[20] = "";    // Stable copy of the most recently completed sequence
unsigned long last_release_time = 0;
bool letter_pending = false;         // True when at least one symbol is waiting on a gap

// ---- SW2/SW3 edge detection (menu mode cycling) ----
int sw2_last = 1;
int sw3_last = 1;

// ---- Receive mode variables ----
char target_letter = ' ';
const char* target_code = "";
int  symbol_index = 0;               // Which symbol of target_code is being sent/was just sent
bool sending_on    = false;          // True while LED1/LS1 are active for the current symbol
unsigned long symbol_start = 0;
bool received_correct = false;


// ---- Program Functions -----------------------

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

char decode_letter(const char* sequence)
{
    // Look up the letter matching a completed dot/dash sequence.
    // Returns '?' if the sequence does not match any known letter -
    // this happens naturally from mistimed taps and is not an error.
    for (int i = 0; i < NUM_LETTERS; i++)
    {
        if (strcmp(MORSE_CODES[i], sequence) == 0)
            return MORSE_LETTERS[i];
    }
    return '?';
}

const char* encode_letter(char letter)
{
    // Look up the dot/dash sequence for a given letter.
    for (int i = 0; i < NUM_LETTERS; i++)
    {
        if (MORSE_LETTERS[i] == letter)
            return MORSE_CODES[i];
    }
    return "";
}

const char* read_tap(unsigned long current_time)
{
    // Read SW1, classify each press as a dot or dash by its duration,
    // and accumulate symbols into current_sequence. Call this every
    // loop iteration while tap input should be accepted (both
    // STATE_TRANSMIT and STATE_RECEIVE_LISTEN do this).
    //
    // Returns a pointer to the completed sequence (a C-string of '.'
    // and '-') once a LETTER_GAP_MS pause follows the most recent
    // release with no new press - this is the signal that the player
    // has finished a letter and moved on. Returns NULL on every call
    // where nothing new has completed yet.
    //
    // TODO: implement this function using the following steps:
    //
    // 1. Read SW1's current state (digitalRead(SW1) == LOW means
    //    pressed). Compare it against sw1_was_pressed (tracking the
    //    PREVIOUS reading) to detect edges - the same pattern used
    //    for SW2/SW3 in STATE_MENU below.
    //
    // 2. On a press edge (was not pressed, now is): record
    //    press_start = current_time. Update sw1_was_pressed.
    //
    // 3. On a release edge (was pressed, now is not): calculate how
    //    long the press lasted (current_time - press_start). If
    //    shorter than (unsigned long)DOT_MAX_MS, append '.' to
    //    current_sequence; otherwise append '-'. Appending means:
    //    current_sequence[current_sequence_length] = symbol;
    //    current_sequence_length++;
    //    current_sequence[current_sequence_length] = '\0';
    //    (the '\0' keeps it a valid, correctly-terminated C-string
    //    after every append). Record last_release_time = current_time
    //    and set letter_pending = true. Update sw1_was_pressed.
    //
    // 4. Regardless of the above, check: if letter_pending is true
    //    AND SW1 is not currently pressed AND the time since
    //    last_release_time is at least (unsigned long)LETTER_GAP_MS,
    //    the letter is complete. Copy current_sequence into
    //    completed_sequence with strcpy(completed_sequence,
    //    current_sequence), then reset current_sequence[0] = '\0',
    //    current_sequence_length = 0, and letter_pending = false.
    //    Return completed_sequence.
    //
    // 5. If none of the above produced a completed sequence, return
    //    NULL.
    //
    // Think carefully about step 4's ordering relative to steps 2-3 -
    // should the gap check happen before or after processing a
    // press/release edge that occurs on the very same call?
    return NULL;
}


void setup()
{
    pinMode(LED1, OUTPUT);
    digitalWrite(LED1, LOW);

    pinMode(SW1, INPUT_PULLUP);
    pinMode(SW2, INPUT_PULLUP);
    pinMode(SW3, INPUT_PULLUP);
    pinMode(SW4, INPUT_PULLUP);

    Serial.begin(9600);
    delay(2000);                       // Give Serial Monitor time to
                                        // connect, without blocking
                                        // forever if it's never opened

    randomSeed(millis());              // Seed the random number generator

    Serial.println("Morse Code Trainer");
    Serial.println("SW2/SW3: change mode   SW4: start / menu   SW1: tap");
    Serial.println();

    state_start = millis();
    enter_state(STATE_MENU, state_start, "startup");
    Serial.print("Mode: "); Serial.println(MODE_NAMES[current_mode]);
}

void loop()
{
    unsigned long current_time = millis();
    unsigned long elapsed      = current_time - state_start;

    // ---- State: Menu ----
    if (state == STATE_MENU)
    {
        int sw2_current = digitalRead(SW2);
        int sw3_current = digitalRead(SW3);
        if ((sw2_current == LOW && sw2_last == HIGH) || (sw3_current == LOW && sw3_last == HIGH))
        {
            current_mode = (current_mode + 1) % NUM_MODES;
            Serial.print("Mode: "); Serial.println(MODE_NAMES[current_mode]);
        }
        sw2_last = sw2_current;
        sw3_last = sw3_current;

        if (digitalRead(SW4) == LOW)
        {
            if (current_mode == MODE_TRANSMIT)
            {
                Serial.println("Tap away - pause to complete a letter. SW4 to return to menu.");
                enter_state(STATE_TRANSMIT, current_time, "start");
            }
            else
            {
                target_letter = MORSE_LETTERS[random(0, NUM_LETTERS)];
                target_code   = encode_letter(target_letter);
                symbol_index  = 0;
                sending_on    = true;
                symbol_start  = current_time;
                digitalWrite(LED1, HIGH);
                tone(LS1, 440);
                enter_state(STATE_RECEIVE_SEND, current_time, "start");
            }
        }
    }

    // ---- State: Transmit ----
    else if (state == STATE_TRANSMIT)
    {
        if (digitalRead(SW4) == LOW)
        {
            enter_state(STATE_MENU, current_time, "SW4 pressed");
        }
        else
        {
            // TODO: call read_tap(current_time). If it returns non-NULL,
            //       decode it with decode_letter() and print both the
            //       sequence and the decoded letter, e.g.:
            //       "-.-.  ->  C"
        }
    }

    // ---- State: Receive - Send (fully worked - see Development Guide Step 3) ----
    else if (state == STATE_RECEIVE_SEND)
    {
        unsigned long symbol_duration = (target_code[symbol_index] == '.') ? DOT_MAX_MS : (DOT_MAX_MS * DASH_MULTIPLIER);
        unsigned long symbol_elapsed  = current_time - symbol_start;

        if (sending_on && symbol_elapsed >= symbol_duration)
        {
            digitalWrite(LED1, LOW);
            noTone(LS1);
            sending_on = false;
            symbol_start = current_time;
        }
        else if (!sending_on && symbol_elapsed >= (unsigned long)SYMBOL_GAP_MS)
        {
            symbol_index++;
            if (symbol_index >= (int)strlen(target_code))
            {
                Serial.print("Your turn - tap back: "); Serial.println(target_letter);
                enter_state(STATE_RECEIVE_LISTEN, current_time, "sent");
            }
            else
            {
                digitalWrite(LED1, HIGH);
                tone(LS1, 440);
                sending_on = true;
                symbol_start = current_time;
            }
        }
    }

    // ---- State: Receive - Listen ----
    else if (state == STATE_RECEIVE_LISTEN)
    {
        // TODO: call read_tap(current_time). If it returns non-NULL,
        //       compare it against target_code with strcmp():
        //       - set received_correct = (strcmp(sequence, target_code) == 0)
        //       - print what the player sent and whether it was correct
        //       - play a distinct confirmation or "incorrect" tone
        //       - enter_state(STATE_RECEIVE_RESULT, current_time)
    }

    // ---- State: Receive - Result ----
    else if (state == STATE_RECEIVE_RESULT)
    {
        if (elapsed >= (unsigned long)RESULT_DISPLAY_MS)
        {
            if (digitalRead(SW4) == LOW)
            {
                enter_state(STATE_MENU, current_time, "SW4 pressed");
            }
            else
            {
                // Start another round automatically
                target_letter = MORSE_LETTERS[random(0, NUM_LETTERS)];
                target_code   = encode_letter(target_letter);
                symbol_index  = 0;
                sending_on    = true;
                symbol_start  = current_time;
                digitalWrite(LED1, HIGH);
                tone(LS1, 440);
                enter_state(STATE_RECEIVE_SEND, current_time, "next round");
            }
        }
    }

    delay(1);
}


/* ================================================================================
Development Guide
================================================================================

Work through these steps in order.

--------------------------------------------------------------------------------
Step 1 - Calibrate the timing constants
--------------------------------------------------------------------------------

Before implementing anything, get a feel for DOT_MAX_MS and
LETTER_GAP_MS by tapping naturally on SW1 while printing raw press
durations. Temporarily add this loop after pinMode(SW4,
INPUT_PULLUP) in setup():

Example code:

while (true)
{
    if (digitalRead(SW1) == LOW)
    {
        unsigned long press_start = millis();
        while (digitalRead(SW1) == LOW) { }
        Serial.print("press duration: ");
        Serial.print(millis() - press_start);
        Serial.println(" ms");
    }
}

Tap several short presses and several deliberately longer ones.
Choose a DOT_MAX_MS value comfortably between your typical short
and long presses - not guessed, measured. Remove the test loop
once you have a value that feels right.

--------------------------------------------------------------------------------
Step 2 - Implement read_tap()
--------------------------------------------------------------------------------

This is the core mechanism the whole trainer depends on - both
modes call it. Implement it following the TODO steps in its
definition. Test it in isolation before moving on: temporarily call
it every loop iteration from STATE_MENU and print whatever it
returns (only when it is not NULL), then tap out a few letters by
hand and confirm the raw sequences look right (dots and dashes in
the order and count you expect) before worrying about whether they
decode to the correct letter.

--------------------------------------------------------------------------------
Step 3 - Understand RECEIVE_SEND
--------------------------------------------------------------------------------

STATE_RECEIVE_SEND is already complete - read through it before
implementing RECEIVE_LISTEN. It uses the same flash-then-gap
sub-phase pattern as Rock-Paper-Scissors's countdown: sending_on
tracks whether LED1/LS1 are currently active for the symbol at
symbol_index, and symbol_duration is calculated per-symbol (a dash
takes DASH_MULTIPLIER times as long as a dot to send) rather than
being a single fixed value. strlen(target_code) tells the loop how
many symbols are in the current letter, since target_code is a
C-string whose length varies letter to letter.

Run the program, select RECEIVE, and press SW4. Confirm a random
letter is sent - watch and listen for a pattern of short and long
flashes with gaps between them, and check the Serial Monitor for
which letter was chosen so you can verify what you saw matches.

--------------------------------------------------------------------------------
Step 4 - Transmit mode
--------------------------------------------------------------------------------

Implement the TODO in STATE_TRANSMIT. Test by selecting TRANSMIT
and tapping out several different letters, confirming each is
decoded correctly after you pause. Deliberately tap an invalid
sequence (five dots in a row, for example) and confirm it prints
'?' rather than crashing or hanging.

--------------------------------------------------------------------------------
Step 5 - Receive listening and comparison
--------------------------------------------------------------------------------

Implement the TODO in STATE_RECEIVE_LISTEN. Test by selecting
RECEIVE and correctly tapping back several letters the program
sends, then deliberately tapping the wrong letter back at least
once, confirming both outcomes are detected and reported correctly.

--------------------------------------------------------------------------------
Step 6 - Full session
--------------------------------------------------------------------------------

Play several RECEIVE rounds in a row and confirm each automatically
starts the next after RESULT_DISPLAY_MS, and that pressing SW4
during RECEIVE_RESULT returns to the menu instead. Switch between
TRANSMIT and RECEIVE at the menu and confirm both still work
correctly after switching back and forth.

*/


/* ================================================================================
Extension Activities
================================================================================

--------------------------------------------------------------------------------
EA 1 - External Morse key
--------------------------------------------------------------------------------

A real Morse key (a straight key, specifically - the classic
spring-loaded lever switch) is far more tactile and authentic to
practice on than a small tactile button. Wire one to H1 as a second
momentary switch input (H1 also carries I2C/QWIIC SDA on BEAPER
Nano - not a conflict for this capstone, which does not use I2C,
but worth knowing if you extend the project further):

Example code:

pinMode(H1, INPUT_PULLUP);

Rather than choosing between SW1 or the external key, let both work
at once - replace every digitalRead(SW1) == LOW check inside
read_tap() with a call to a small helper function:

Example code:

bool tap_pressed()
{
    return digitalRead(SW1) == LOW || digitalRead(H1) == LOW;
}

This sidesteps needing any kind of input-source setting entirely.
With no external key wired up, H1 simply reads HIGH permanently via
its own pull-up, so nothing breaks or needs toggling - SW1 keeps
working exactly as before. With a key connected, either one taps out
dots and dashes interchangeably, even switching between them
mid-session.

--------------------------------------------------------------------------------
EA 2 - Full words and phrases
--------------------------------------------------------------------------------

Add a third mode where RECEIVE sends a whole word instead of a
single letter - each letter of the word sent in turn, with a
WORD_GAP_MS-length pause (rather than SYMBOL_GAP_MS) marking the
boundary between letters within the word so the player can tell
where one letter ends and the next begins. Build your own word list
(a simple array of short, all-uppercase C-strings works well - add
your own words to it) and pick one at random the same way
target_letter is currently chosen from MORSE_LETTERS. The player
must tap back the entire word, letter by letter, matching
read_tap()'s per-letter completion against the word's letters in
order.

--------------------------------------------------------------------------------
EA 3 - Numbers and punctuation
--------------------------------------------------------------------------------

Extend MORSE_LETTERS and MORSE_CODES with entries for 0-9 (and
punctuation, if you like) rather than building a separate lookup
mechanism - the existing decode_letter()/encode_letter() functions
work unchanged with a longer table, since they already search the
whole array rather than assuming exactly 26 entries. Remember to
update NUM_LETTERS to match the new table length.

--------------------------------------------------------------------------------
EA 4 - Adjustable speed (WPM)
--------------------------------------------------------------------------------

Morse speed is conventionally measured in words per minute (WPM),
based on a standard word length. Add a speed setting (adjustable
with SW2/SW3 at the menu, similar to how mode is currently
selected) that scales DOT_MAX_MS, LETTER_GAP_MS, SYMBOL_GAP_MS, and
RECEIVE_SEND's dot duration all together from one WPM value, rather
than as independent constants. What relationship between WPM and
dot duration would you use? (Hint: research the standard "PARIS"
timing method real operators use to define WPM precisely.)

--------------------------------------------------------------------------------
EA 5 - SOS recognition
--------------------------------------------------------------------------------

Real operators send SOS as a single continuous prosign - three
dots, three dashes, three dots, with no letter-gap pauses between
the S, O, and S - rather than as three separately-decoded letters.
In read_tap()'s terms, this means the full sequence "...---..."
arrives as ONE completed sequence, not three. Add a check (in
either TRANSMIT or RECEIVE, or both) for this exact sequence with
strcmp(sequence, "...---...") == 0, and trigger a distinct,
attention-grabbing alarm response when detected - reusing Alarm
System's aesthetic seems fitting for something that is, after all,
the universal distress signal.

--------------------------------------------------------------------------------
EA 6 - Audio-only or visual-only practice
--------------------------------------------------------------------------------

Real Morse operators work by sound alone - add a setting (cycled
at the menu alongside mode) that makes RECEIVE_SEND use only LS1,
only LED1, or both together, letting a player practice pure audio
reception once they no longer need the visual flash as a crutch.

*/
