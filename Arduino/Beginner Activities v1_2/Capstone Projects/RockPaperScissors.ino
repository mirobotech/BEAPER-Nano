/* ================================================================================
Capstone Project: Rock-Paper-Scissors [BEAPERNano-Capstone-Rock-Paper-Scissors]
Version: 1.2
Updated: November 24, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPERNano_v1_2.h header file

A single-player Rock-Paper-Scissors game against the computer.
Press SW4 to begin a round: a 3-2-1 countdown flashes and beeps,
speeding up as it counts down, then a short window opens for you
to make your choice. Miss the window and it counts as too slow -
no result is compared.

Hardware used:
  SW1 - Rock
  SW2 - Paper
  SW3 - Scissors
  SW4 - Start a round
  LS1 - Piezo speaker (countdown beeps, "go" tone, outcome tones)

Compatible with all BEAPER Nano configurations. No additional
hardware or jumper changes required.

--------------------------------------------------------------------------------
Game behaviour:
  IDLE      - Waiting. Press SW4 to begin.
  COUNTDOWN - 3-2-1, LED1-LED3 flash together with a beep on each
              count. The gap between counts shrinks as it
              progresses - see COUNTDOWN_INTERVALS below.
  CHOOSING  - A short window opens (CHOOSE_WINDOW_MS). Press SW1,
              SW2, or SW3 for your choice. No press before the
              window closes counts as too slow.
  REVEAL    - The computer's choice is generated, compared against
              yours, and the result (win/lose/tie/too slow) is
              announced with a distinct tone pattern and printed to
              the Serial Monitor. Session totals (wins/losses/ties)
              are tracked throughout.

Before you begin - complete your capstone plan using the Capstone
Preparation Guide: a plain-English description from the player's
perspective, a state diagram, your constants and variables, and
your testing plan.
=================================================================================*/
// IMPORTANT: Make sure that BEAPERNano_v1_2.h is accessible as a tab in this project.
#include "BEAPERNano_v1_2.h"   // Define BEAPER Nano I/O devices

// ---- State Constants -------------------
const int STATE_IDLE      = 0;       // Waiting - press SW4 to start
const int STATE_COUNTDOWN = 1;       // 3-2-1 countdown, LEDs flashing
const int STATE_CHOOSING  = 2;       // Choice window open - press SW1/SW2/SW3
const int STATE_REVEAL    = 3;       // Showing the result of the round

const char* STATE_NAMES[] = { "IDLE", "COUNTDOWN", "CHOOSING", "REVEAL" };

// ---- Choice Constants -------------------
const int CHOICE_ROCK     = 0;
const int CHOICE_PAPER    = 1;
const int CHOICE_SCISSORS = 2;
const int CHOICE_NONE     = -1;      // Sentinel: no choice made (too slow)

const char* CHOICE_NAMES[] = { "Rock", "Paper", "Scissors" };   // Indexed 0-2 only; CHOICE_NONE handled separately

const int CHOICE_LEDS[] = { LED1, LED2, LED3 };   // Indexed by CHOICE_ROCK/PAPER/SCISSORS

// ---- Countdown Configuration -------------
// Three parallel const arrays, indexed together - the same pattern
// used for Simon Game's BUTTONS/LEDS/TONES. COUNTDOWN_INTERVALS[i]
// is the total time (ms) count i occupies; COUNTDOWN_TONES[i] is
// the pitch played at the start of count i. Intervals shrink and
// pitch rises as the countdown progresses, building tension toward
// "go."
const int COUNTDOWN_INTERVALS[] = { 800, 600, 400 };     // ms per count - gets faster
const int COUNTDOWN_TONES[]     = { 330, 415, 523 };     // Hz per count - gets higher (E4, G#4, C5)
const int GO_TONE               = 660;   // Distinct tone marking the choice window opening
const int FLASH_TIME            = 150;   // ms the LEDs stay lit within each count

// ---- Choosing/Reveal Configuration -------
const int CHOOSE_WINDOW_MS  = 3000;  // How long the player has to choose
const int RESULT_DISPLAY_MS = 2500;  // How long the result is shown before returning to IDLE

// ---- Program Variables -----------------------
int  state             = STATE_IDLE;
unsigned long state_start = 0;

// ---- Countdown sub-phase tracking ----
int  countdown_index = 0;            // Which count we're on (0, 1, 2)
unsigned long phase_start = 0;       // Time the CURRENT count began
bool flashing = false;               // True while LEDs are lit within the current count

// ---- Round variables ----
int player_choice   = CHOICE_NONE;
int computer_choice = CHOICE_NONE;

// ---- Session totals ----
int win_count  = 0;
int loss_count = 0;
int tie_count  = 0;


// ---- Program Functions -----------------------

void all_choice_leds_on()
{
    for (int i = 0; i < 3; i++)
        digitalWrite(CHOICE_LEDS[i], HIGH);
}

void all_choice_leds_off()
{
    for (int i = 0; i < 3; i++)
        digitalWrite(CHOICE_LEDS[i], LOW);
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
    // Begin a new round: reset countdown tracking, start the first
    // count immediately, and enter STATE_COUNTDOWN.
    countdown_index = 0;
    phase_start     = current_time;
    flashing        = true;
    player_choice   = CHOICE_NONE;
    computer_choice = CHOICE_NONE;
    all_choice_leds_on();
    tone(LS1, COUNTDOWN_TONES[0]);
    enter_state(STATE_COUNTDOWN, current_time, "round start");
}


void setup()
{
    // Configure Arduino Nano ESP32 status LED as output
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, LOW);

    // Configure BEAPER Nano LEDs as outputs
    for (int i = 0; i < 3; i++)
        pinMode(CHOICE_LEDS[i], OUTPUT);

    // Configure BEAPER Nano pushbuttons as inputs
    pinMode(SW1, INPUT_PULLUP);
    pinMode(SW2, INPUT_PULLUP);
    pinMode(SW3, INPUT_PULLUP);
    pinMode(SW4, INPUT_PULLUP);

    Serial.begin(9600);
    delay(2000);                       // Give Serial Monitor time to
                                        // connect, without blocking
                                        // forever if it's never opened

    randomSeed(millis());              // Seed the random number generator

    all_choice_leds_off();
    Serial.println("Rock-Paper-Scissors");
    Serial.println("SW1: Rock   SW2: Paper   SW3: Scissors   SW4: start round");
    Serial.println();

    state_start = millis();
    enter_state(STATE_IDLE, state_start, "startup");
}

void loop()
{
    unsigned long current_time = millis();
    unsigned long elapsed      = current_time - state_start;

    // ---- State: Idle ----
    if (state == STATE_IDLE)
    {
        if (digitalRead(SW4) == LOW)
            start_round(current_time);
    }

    // ---- State: Countdown (fully worked - see Development Guide Step 1) ----
    else if (state == STATE_COUNTDOWN)
    {
        unsigned long count_elapsed = current_time - phase_start;

        if (flashing && count_elapsed >= (unsigned long)FLASH_TIME)
        {
            all_choice_leds_off();
            noTone(LS1);
            flashing = false;
        }

        if (count_elapsed >= (unsigned long)COUNTDOWN_INTERVALS[countdown_index])
        {
            countdown_index++;
            phase_start = current_time;
            if (countdown_index >= 3)
            {
                tone(LS1, GO_TONE, 200);
                enter_state(STATE_CHOOSING, current_time, "go!");
            }
            else
            {
                all_choice_leds_on();
                tone(LS1, COUNTDOWN_TONES[countdown_index]);
                flashing = true;
            }
        }
    }

    // ---- State: Choosing ----
    else if (state == STATE_CHOOSING)
    {
        // TODO: if SW1/SW2/SW3 is pressed, set player_choice to the
        //       matching CHOICE_ROCK/PAPER/SCISSORS constant and
        //       enter_state(STATE_REVEAL, current_time, "chose").
        //
        // TODO: if elapsed >= (unsigned long)CHOOSE_WINDOW_MS with no press, the
        //       player was too slow - player_choice stays CHOICE_NONE
        //       (its default). enter_state(STATE_REVEAL, current_time,
        //       "too slow").
    }

    // ---- State: Reveal ----
    else if (state == STATE_REVEAL)
    {
        // TODO: on the first iteration of this state (hint: elapsed will
        //       be 0 or very small on the very first pass), determine and
        //       announce the result:
        //
        //       if (player_choice == CHOICE_NONE)
        //       {
        //           Serial.println("Too slow!");
        //       }
        //       else
        //       {
        //           computer_choice = random(0, 3);   // random() excludes its upper bound - 0,1,2
        //           Serial.print("You chose: "); Serial.println(CHOICE_NAMES[player_choice]);
        //           Serial.print("Computer chose: "); Serial.println(CHOICE_NAMES[computer_choice]);
        //           if (player_choice == computer_choice)
        //           {
        //               tie_count++;
        //               Serial.println("Tie!");
        //           }
        //           else if ((player_choice == CHOICE_ROCK && computer_choice == CHOICE_SCISSORS) ||
        //                    (player_choice == CHOICE_PAPER && computer_choice == CHOICE_ROCK) ||
        //                    (player_choice == CHOICE_SCISSORS && computer_choice == CHOICE_PAPER))
        //           {
        //               win_count++;
        //               Serial.println("You win!");
        //           }
        //           else
        //           {
        //               loss_count++;
        //               Serial.println("You lose!");
        //           }
        //           Serial.print("Score - wins: "); Serial.print(win_count);
        //           Serial.print("  losses: "); Serial.print(loss_count);
        //           Serial.print("  ties: "); Serial.println(tie_count);
        //       }
        //
        //       Play a distinct tone pattern for each outcome - for
        //       example an ascending two-note beep for a win, a single
        //       low buzz for a loss, and a single mid tone for a tie.
        //       Light CHOICE_LEDS[player_choice] to show what you picked
        //       (skip this if player_choice is CHOICE_NONE).
        //
        // TODO: once elapsed >= (unsigned long)RESULT_DISPLAY_MS, turn off all
        //       CHOICE_LEDS and enter_state(STATE_IDLE, current_time).
    }

    delay(1);
}


/* ================================================================================
Development Guide
================================================================================

Work through these steps in order.

--------------------------------------------------------------------------------
Step 1 - Understand the countdown
--------------------------------------------------------------------------------

STATE_COUNTDOWN is already complete and working - read through it
before starting on the TODOs elsewhere. It uses two nested timers:
an outer one (count_elapsed vs COUNTDOWN_INTERVALS[countdown_index])
tracking how long the CURRENT count has been running in total, and
an inner one (the same count_elapsed vs FLASH_TIME) tracking only
how long the LEDs should stay lit within that count. This is the
same non-blocking repeating-timer pattern from Activity 11, applied
twice at once - once for the overall count duration, once for the
shorter flash within it.

Run the program and press SW4. Confirm the countdown flashes three
times, getting visibly faster and higher-pitched each time, then
plays a distinct "go" tone and transitions to CHOOSING (check the
Serial Monitor for the state transition, since nothing is
implemented in CHOOSING yet).

--------------------------------------------------------------------------------
Step 2 - Reading the player's choice
--------------------------------------------------------------------------------

Implement the button-reading TODO in STATE_CHOOSING. Test that
pressing SW1, SW2, or SW3 during the choosing window correctly
records player_choice and transitions to STATE_REVEAL - check the
Serial Monitor's state transition message for each.

--------------------------------------------------------------------------------
Step 3 - Timeout handling
--------------------------------------------------------------------------------

Implement the timeout TODO in STATE_CHOOSING. Test by starting a
round and simply waiting without pressing anything - confirm it
transitions to STATE_REVEAL after CHOOSE_WINDOW_MS with
player_choice still CHOICE_NONE.

--------------------------------------------------------------------------------
Step 4 - Determining the winner
--------------------------------------------------------------------------------

Implement the TODO in STATE_REVEAL. Test all nine possible
combinations of player choice vs. computer choice deliberately -
this is easiest by temporarily hardcoding computer_choice to a
fixed value instead of using random() while you test each of your
three choices against it, then restoring the random version once
you have confirmed the win/lose/tie logic is correct for every
combination.

--------------------------------------------------------------------------------
Step 5 - Outcome feedback and return to idle
--------------------------------------------------------------------------------

Add the tone patterns and LED feedback described in the TODO, and
implement the return-to-idle timing. Confirm a full round - start,
countdown, choose, reveal, and return to idle - works correctly
several times in a row, and that win_count/loss_count/tie_count
accumulate correctly across multiple rounds without resetting.

*/


/* ================================================================================
Extension Activities
================================================================================

--------------------------------------------------------------------------------
EA 1 - Best-of-N match
--------------------------------------------------------------------------------

Layer a "match" concept on top of individual rounds: track a match
score separately from the session totals, and end the match (with
a distinct fanfare) once either the player or the computer reaches
a set number of wins (best of 5, for example). What should happen
to the match score when SW4 starts a new round after a match has
already ended?

--------------------------------------------------------------------------------
EA 2 - Elegant win-determination refactor
--------------------------------------------------------------------------------

The if/else chain in STATE_REVEAL checks three specific winning
combinations explicitly. There is a more compact way to determine
the same result using modular arithmetic: with choices numbered
0, 1, 2 (Rock, Paper, Scissors), the player wins whenever
(player_choice - computer_choice + 3) % 3 == 1, and loses whenever
it equals 2 (0 means a tie). Note the "+ 3" before the modulo - in
C, unlike Python, the % operator can return a negative result when
its left-hand operand is negative (player_choice - computer_choice
is negative whenever the player's choice number is lower - Rock(0)
vs Paper(1), for example), so 3 is added first to guarantee a
non-negative result before taking % 3. Verify this produces
identical results to your existing if/else chain for all nine
combinations before replacing it - why does this formula work?
(Hint: consider what each choice "beats" as you move one step
forward through the cycle Rock -> Paper -> Scissors -> Rock.)

--------------------------------------------------------------------------------
EA 3 - Adaptive computer opponent
--------------------------------------------------------------------------------

Instead of choosing randomly every time, track how many times the
player has chosen each of Rock/Paper/Scissors across the session
(three counters, similar to win_count/loss_count/tie_count) and
bias the computer's choice toward whichever counters the player's
most frequent pick. This is a simple introduction to
pattern-based prediction rather than pure randomness - does it
actually make the computer harder to beat once you have played
enough rounds for a pattern to emerge? How would a player adapt
their own strategy once they suspect the computer is doing this?

--------------------------------------------------------------------------------
EA 4 - Escalating time pressure
--------------------------------------------------------------------------------

Reuse Simon Game's "difficulty increases with progress" idea:
shrink CHOOSE_WINDOW_MS by a fixed amount after each round within
a session (with a reasonable minimum so it never becomes
impossible), so the game gets tenser to play the longer a session
continues. Should the window reset to its original length after a
"too slow" round, or keep shrinking regardless of outcome?

*/
