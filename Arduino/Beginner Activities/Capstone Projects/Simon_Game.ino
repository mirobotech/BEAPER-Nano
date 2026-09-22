/* ================================================================================
Capstone Project: Simon Memory Game [BEAPERNano-Capstone-Simon-Game]
Version: 1.0
Updated: July 25, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPERNano.h header file

Hardware used:
  SW2 / LED2 - Button and LED 1 (e.g. green)
  SW3 / LED3 - Button and LED 2 (e.g. red)
  SW4 / LED4 - Button and LED 3 (e.g. yellow)
  SW5 / LED5 - Button and LED 4 (e.g. blue)
  LS1        - Piezo speaker (one distinct tone per button)

Compatible with all BEAPER Nano configurations. No additional
hardware or jumper changes required.

--------------------------------------------------------------------------------
Game rules:
  The game plays back a growing sequence of flashing LEDs with tones.
  The player repeats the sequence by pressing the matching buttons.
  Each correct round adds one more step to the sequence.
  A wrong button press or timeout ends the game.
  Completing the maximum sequence length (MAX_LENGTH) wins the game.
  Press any button during the idle animation to start a new game.

--------------------------------------------------------------------------------
This capstone uses two kinds of array: const (fixed, read-only) and
non-const (values can change after creation). Read the Development
Guide's Step 1 before starting, since every other step depends on
understanding this distinction.

Before you begin - complete your capstone plan using the Capstone
Preparation Guide: project description, state diagram, state
details table, constants and variables, and testing plan.
=================================================================================*/
// IMPORTANT: Make sure that BEAPERNano.h is accessible as a tab in this project.
#include "BEAPERNano.h"   // Define BEAPER Nano I/O devices

// ---- State Constants -------------------
const int STATE_IDLE      = 0;       // Attract animation, waiting for player to start
const int STATE_PLAYBACK  = 1;       // Showing current sequence step (LED + tone)
const int STATE_GAP       = 2;       // Silent pause between playback steps
const int STATE_WAITING   = 3;       // Player's turn - waiting for button press
const int STATE_CORRECT   = 4;       // Brief correct-press feedback before next step
const int STATE_GAME_OVER = 5;       // Wrong press, timeout, or MAX_LENGTH reached

// State names, indexed by the constants above - used for Serial output
const char* STATE_NAMES[] = { "IDLE", "PLAYBACK", "GAP", "WAITING", "CORRECT", "GAME_OVER" };

// ---- Hardware Maps -----------------------
// const arrays: fixed-size, read-only collections. Good for grouping a
// fixed set of related values - here, one entry per Simon colour,
// indexed 0-3. See Development Guide Step 1 before relying on these.
const int BUTTONS[] = { SW2,  SW3,  SW4,  SW5  };
const int LEDS[]    = { LED2, LED3, LED4, LED5 };
const int TONES[]   = { 659,  554,  440,  330  };   // Hz, one per button

// ---- Game Constants -----------------------
const int MAX_LENGTH    = 16;        // Maximum sequence length (traditional Simon = 16)
const int SHOW_TIME     = 400;       // How long each sequence step is shown (ms)
const int GAP_TIME      = 150;       // Silent gap between playback steps (ms)
const int PRESS_TIME    = 300;       // How long a correct press lights the LED (ms)
const int TIMEOUT_MS    = 5000;      // Player must press within this time (ms)
const int IDLE_INTERVAL = 300;       // Attract animation step interval (ms)

// ---- Game Variables -----------------------
int  state           = STATE_IDLE;
unsigned long state_start = 0;       // Time current state began

// Non-const array: like the const arrays above, but individual
// elements CAN be changed after creation - see Development Guide
// Step 1. Declaring 'int sequence[MAX_LENGTH]' reserves 16 slots;
// add_step() below fills them in one at a time as the game grows.
int  sequence[MAX_LENGTH];           // The generated sequence (button indices 0-3)
int  seq_length      = 0;            // Current length of the active sequence
int  play_index      = 0;            // Which step is currently being played back
int  input_index      = 0;           // Which step the player is currently entering
int  score           = 0;            // Highest sequence length completed this session

int  idle_step       = 0;            // Current step in attract animation
unsigned long last_idle = 0;         // Last time idle animation advanced


// ---- Program Functions -----------------------

void all_leds_off()
{
    for (int i = 0; i < 4; i++)
        digitalWrite(LEDS[i], LOW);
    digitalWrite(LED_BUILTIN, LOW);
}

void enter_state(int new_state, unsigned long current_time, const char* reason = "")
{
    all_leds_off();
    noTone(LS1);
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

void show_step(int index)
{
    // Light the LED and play the tone for sequence step at 'index'.
    int button_index = sequence[index];
    digitalWrite(LEDS[button_index], HIGH);
    tone(LS1, TONES[button_index]);
}

int read_button()
{
    // Return the index (0-3) of any currently pressed button, or -1 if none.
    for (int i = 0; i < 4; i++)
    {
        if (digitalRead(BUTTONS[i]) == LOW)
            return i;
    }
    return -1;
}

bool add_step()
{
    // Append a new random step to the sequence, if there is room.
    // Returns true if a step was added, false if the sequence is
    // already at MAX_LENGTH (the player has won).
    if (seq_length >= MAX_LENGTH)
        return false;
    sequence[seq_length] = random(0, 4);   // random(0, 4) returns 0-3
    seq_length++;
    return true;
}

void display_score(int final_score)
{
    // Flash LEDs to indicate the score - one flash per level completed.
    // TODO: implement a visual or serial score display of your choice.
    // Ideas: flash LED2-LED5 as a bar (1-4 flashes = 1-4 LEDs lit),
    //        print the score to the Serial Monitor, or blink the
    //        on-board LED 'score' times with a pause between groups.
    Serial.print("Score: ");
    Serial.print(final_score);
    Serial.println(" steps completed");
}


void setup()
{
    // Configure Arduino Nano ESP32 status LED as output
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, LOW);

    // Configure BEAPER Nano LEDs as outputs
    for (int i = 0; i < 4; i++)
        pinMode(LEDS[i], OUTPUT);

    // Configure BEAPER Nano pushbuttons as inputs
    for (int i = 0; i < 4; i++)
        pinMode(BUTTONS[i], INPUT_PULLUP);

    Serial.begin(9600);
    delay(2000);                       // Give Serial Monitor time to
                                        // connect, without blocking
                                        // forever if it's never opened

    randomSeed(millis());              // Seed the random number generator

    all_leds_off();
    digitalWrite(LED_BUILTIN, HIGH);
    Serial.println("Simon Memory Game");
    Serial.println("Press any button to start");
    Serial.println();

    state_start = millis();
    last_idle   = millis();
}

void loop()
{
    unsigned long current_time = millis();
    unsigned long elapsed      = current_time - state_start;
    int pressed = read_button();

    // ---- State: Idle (attract animation) ----
    if (state == STATE_IDLE)
    {
        // TODO: cycle a simple animation across LED2-LED5 using idle_step and
        //       last_idle with IDLE_INTERVAL timing (pattern from Activity 11).
        //       Hint: light LEDS[idle_step % 4] and advance idle_step each interval.

        // Start a new game when any button is pressed
        if (pressed != -1)
        {
            seq_length  = 0;
            input_index = 0;
            play_index  = 0;
            add_step();
            enter_state(STATE_PLAYBACK, current_time, "game start");
            show_step(0);
        }
    }

    // ---- State: Playback (showing one sequence step) ----
    else if (state == STATE_PLAYBACK)
    {
        // TODO: when SHOW_TIME elapses, turn off the LED and tone then
        //       transition to STATE_GAP. After the gap, either show the
        //       next step (transition back to PLAYBACK) or, if all steps
        //       have been shown, transition to STATE_WAITING.
        //       Use play_index to track which step is currently showing.
    }

    // ---- State: Gap (silent pause between steps) ----
    else if (state == STATE_GAP)
    {
        // TODO: when GAP_TIME elapses, check if there are more steps to show.
        //       If play_index < seq_length, show the next step and enter PLAYBACK.
        //       If all steps have been shown, enter WAITING (player's turn).
    }

    // ---- State: Waiting (player's turn) ----
    else if (state == STATE_WAITING)
    {
        // TODO: if TIMEOUT_MS elapses with no button press, enter GAME_OVER.
        // TODO: if a button is pressed:
        //       - if it matches sequence[input_index], enter CORRECT
        //         (light the pressed LED and play its tone for PRESS_TIME)
        //       - if it does not match, enter GAME_OVER
    }

    // ---- State: Correct press feedback ----
    else if (state == STATE_CORRECT)
    {
        // TODO: when PRESS_TIME elapses, turn off LED and tone, then:
        //       - increment input_index
        //       - if input_index == seq_length, the full sequence was entered
        //         correctly:
        //           - update score if seq_length > score
        //           - call add_step(). If it returns false, the sequence has
        //             reached MAX_LENGTH - the player has won! Enter
        //             STATE_GAME_OVER with reason "you win!" (consider a
        //             distinct victory tone in that state, different from
        //             the failure tone).
        //           - otherwise, reset play_index and input_index to 0 and
        //             begin STATE_PLAYBACK of the new, longer sequence
        //       - if input_index < seq_length, remain in WAITING for the
        //         next button press
    }

    // ---- State: Game over ----
    else if (state == STATE_GAME_OVER)
    {
        // TODO: play a distinctive failure sound and flash all LEDs briefly.
        //       (Consider storing a separate 'won' boolean when entering
        //       this state, if you want a different sound for winning
        //       MAX_LENGTH versus losing, rather than trying to inspect
        //       the reason string later.)
        //       After the feedback duration, call display_score() and enter IDLE.
        //       Hint: use elapsed to time the failure animation, then transition.
    }

    delay(1);
}


/* ================================================================================
Development Guide
================================================================================

Work through these steps in order. Complete each step and test it
before moving on to the next.

--------------------------------------------------------------------------------
Step 1 - Understanding const and non-const arrays
--------------------------------------------------------------------------------

Every activity up to this point stored related values in separate
named variables - Activity 12's combination lock used entered_1,
entered_2, entered_3, entered_4 for a four-digit code. That works
well for a small, fixed number of values, but Simon's sequence can
grow up to MAX_LENGTH (16) steps. Writing entered_1 through
entered_16, with a 16-way if/else chain to read the right one, would
be unwieldy - and would need rewriting entirely if MAX_LENGTH ever
changed. This capstone uses arrays instead.

An array is a collection of values of the same type, indexed
starting at 0:

Example code:

const int BUTTONS[] = { SW2, SW3, SW4, SW5 };

BUTTONS[0] is SW2, BUTTONS[1] is SW3, and so on. The 'const' keyword
means the array's contents cannot be changed after it is created -
BUTTONS[0] = SW3 would fail to compile. This program uses three
const arrays - BUTTONS, LEDS, and TONES - as parallel lookups:
button index 2 (SW4) always corresponds to LEDS[2] (LED4) and
TONES[2] (440 Hz). This is a natural fit for a const array, because
the mapping between buttons, LEDs, and tones never changes while the
program runs. You have already seen this exact pattern, without the
name - STATE_NAMES[] near the top of this file is also a const
array, indexed by the same state numbers used throughout this
program.

An array without 'const' looks similar but its elements CAN be
changed after creation:

Example code:

int sequence[16];

This reserves 16 slots for integers, initially containing whatever
values happen to already be in that memory (not necessarily zero -
unlike Python's [0] * MAX_LENGTH, C does not automatically clear a
new array). Unlike the const arrays above, individual elements of
'sequence' are written throughout the game:

Example code:

sequence[seq_length] = random(0, 4);

This is the core reason Simon's sequence needs a non-const array
rather than a const one: each round, a new random step is written
into the next available position. A const array could not do this.
Use const when a fixed collection of values will not change; leave
off const when individual elements need to be updated after
creation.

Both are read the same way - square brackets with an index:
BUTTONS[i], LEDS[i], sequence[i]. Trace through 'add_step()' and
'show_step()' and confirm you can predict what each line does
before continuing.

--------------------------------------------------------------------------------
Step 2 - Idle animation
--------------------------------------------------------------------------------

Implement the attract animation in STATE_IDLE. The pattern should
cycle through the four LEDs using idle_step and the IDLE_INTERVAL
timer. Test that pressing any button transitions to the first
playback state and stops the animation.

--------------------------------------------------------------------------------
Step 3 - Single step playback
--------------------------------------------------------------------------------

Implement STATE_PLAYBACK and STATE_GAP for a sequence of length 1.
Verify that pressing the correct button produces a correct-press
flash, and that pressing the wrong button transitions to GAME_OVER.
Check the Serial Monitor to confirm state transitions are printing
correctly.

--------------------------------------------------------------------------------
Step 4 - Full playback sequence
--------------------------------------------------------------------------------

Extend the playback logic to handle sequences longer than 1. Use
play_index to advance through the sequence. After all steps are
shown, transition to STATE_WAITING with input_index = 0.

--------------------------------------------------------------------------------
Step 5 - Player input and correct sequence
--------------------------------------------------------------------------------

Implement STATE_WAITING and STATE_CORRECT. After each correct press
advance input_index. When input_index reaches seq_length, the round
is complete - call add_step() and begin playback of the longer
sequence, unless add_step() returns false (MAX_LENGTH reached).

--------------------------------------------------------------------------------
Step 6 - Winning and losing
--------------------------------------------------------------------------------

Implement STATE_GAME_OVER with a clear failure sound/animation that
is distinct from the correct-press feedback - and a distinct sound
for winning (reaching MAX_LENGTH) versus losing (wrong press or
timeout). Test both endings deliberately: losing is easy to test by
pressing a wrong button, but reaching MAX_LENGTH requires either
genuine skill or temporarily lowering MAX_LENGTH for testing.
Implement display_score() in a way that makes the score clear.
Return to STATE_IDLE afterward.

--------------------------------------------------------------------------------
Step 7 - Difficulty and polish
--------------------------------------------------------------------------------

Once the core game works end to end, move on to the Extension
Activities below for ideas on making the game more challenging or
more polished.

*/


/* ================================================================================
Extension Activities
================================================================================

--------------------------------------------------------------------------------
EA 1 - Adjustable speed
--------------------------------------------------------------------------------

Decrease SHOW_TIME and GAP_TIME as the sequence grows longer, making
later rounds harder. How will you calculate the speed from the
current sequence length?

--------------------------------------------------------------------------------
EA 2 - High score
--------------------------------------------------------------------------------

Track the best score across multiple games in a variable that
persists between STATE_GAME_OVER and STATE_IDLE. Display it at the
start of each game.

--------------------------------------------------------------------------------
EA 3 - Strict mode
--------------------------------------------------------------------------------

Add a penalty for pressing a button at the wrong time (during
playback). How does this affect your state machine? Which states
need to check for unexpected button presses?

--------------------------------------------------------------------------------
EA 4 - Sound design
--------------------------------------------------------------------------------

Are the four tones clearly distinguishable on your hardware? Try
adjusting TONES to find four pitches that sound natural together.
The traditional Simon tones are E4, C#5, A3, and E3, but these have
been moved up an octave to E5, C#5, A4, and E4 (659 Hz, 554 Hz,
440 Hz, 330 Hz) so they sound better when played on the circuit's
small piezo speaker.

*/
