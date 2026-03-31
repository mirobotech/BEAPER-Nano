/* ================================================================================
Project: Sound Player [B10-Sound-Player-Project]
March 31, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPERNano.h header file

Before starting this project, re-read GE1 and GE3
from Activity 10: Analog Output.

This project controls the BEAPER Nano's piezo speaker using
Arduino's tone() function. Frequency (pitch) is fully controllable
with SW2 and SW5. Arduino's tone() always produces a 50% duty cycle
square wave - timbre control is not available through tone(). See
EA4 if you are interested in how timbre could be explored using
direct hardware timer access.

Controls:
  SW2 - decrease frequency (lower pitch)
  SW5 - increase frequency (higher pitch)
  SW3 - shift down one octave (halve frequency)
  SW4 - shift up one octave (double frequency)
================================================================================*/
// IMPORTANT: Make sure that BEAPERNano.h is accessible as a tab in this project.
#include "BEAPERNano.h"   // Define BEAPER Nano I/O devices

// ---- Program Constants ----------------
const int FREQ_MIN   = 100;           // Minimum frequency (Hz)
const int FREQ_MAX   = 8000;          // Maximum frequency (Hz)
const int FREQ_STEP  = 50;            // Frequency change per loop iteration
const int NOTE_GAP   = 30;            // Silent gap between notes (ms)

// ---- Program Variables ----------------
int frequency = 440;                  // Current frequency in Hz (A4 = 440 Hz)


// ---- Program Functions ----------------

void set_tone(int freq)
{
    // Play the piezo speaker at the given frequency.
    // Clamps the frequency to the valid range before applying.
    // NOTE: Arduino's tone() always uses a 50% duty cycle square wave.
    if (freq < FREQ_MIN) freq = FREQ_MIN;
    if (freq > FREQ_MAX) freq = FREQ_MAX;
    frequency = freq;
    tone(LS1, frequency);
}

void beep(int freq, int duration_ms)
{
    // Play a tone at the given frequency for duration_ms milliseconds,
    // then silence the speaker.
    // TODO: call set_tone() to start the tone at freq
    // TODO: use delay() to wait for duration_ms
    // TODO: call noTone(LS1) to silence the speaker
    // TODO: add a NOTE_GAP silent pause after the note
}


void setup()
{
    // Configure Arduino Nano ESP32 status LED as output
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, HIGH);  // Status LED on

    // Configure BEAPER Nano pushbuttons as inputs
    pinMode(SW2, INPUT_PULLUP);
    pinMode(SW3, INPUT_PULLUP);
    pinMode(SW4, INPUT_PULLUP);
    pinMode(SW5, INPUT_PULLUP);

    Serial.begin(9600);
    while (!Serial);                  // Wait for serial port to be ready

    Serial.println("Sound Player");
    Serial.println("SW2/SW5: pitch down/up   SW3/SW4: octave down/up");

    // Start with the speaker playing at the initial frequency
    set_tone(frequency);
    Serial.print("Frequency: "); Serial.print(frequency); Serial.println(" Hz");
}

void loop()
{
    bool changed = false;

    if (digitalRead(SW2) == LOW)
    {
        set_tone(frequency - FREQ_STEP);
        changed = true;
    }
    else if (digitalRead(SW5) == LOW)
    {
        set_tone(frequency + FREQ_STEP);
        changed = true;
    }

    if (digitalRead(SW3) == LOW)
    {
        set_tone(frequency / 2);      // Shift down one octave (halve frequency)
        changed = true;
        delay(200);                   // Debounce octave shift
    }
    else if (digitalRead(SW4) == LOW)
    {
        set_tone(frequency * 2);      // Shift up one octave (double frequency)
        changed = true;
        delay(200);                   // Debounce octave shift
    }

    if (changed)
    {
        Serial.print("Frequency: "); Serial.print(frequency); Serial.println(" Hz");
    }

    delay(20);
}


/*
Extension Activities

1.  Implement the 'beep()' function and use it to play a startup
    chime when the program begins - three rising tones of decreasing
    duration, for example. Call 'beep()' from setup() after
    Serial.println() so the chime plays once on startup, then the
    interactive controls take over.

    After the chime, does the speaker resume at the correct
    frequency? What do you need to call after 'beep()' to restore
    the continuous tone?

2.  A melody can be stored as a two-dimensional array of
    {frequency, duration_ms} pairs. Here is a short example using
    the first four notes of 'Ode to Joy':

  const int melody[][2] = {
    { 659, 400 },   // E5
    { 659, 400 },   // E5
    { 698, 400 },   // F5
    { 784, 400 },   // G5
  };
  const int MELODY_LENGTH = sizeof(melody) / sizeof(melody[0]);

    Play the melody using 'beep()' in a for loop, with a short
    gap between notes:

  for (int i = 0; i < MELODY_LENGTH; i++)
  {
    beep(melody[i][0], melody[i][1]);
  }

    Extend the melody with more notes, or create your own. Change
    the gap value inside 'beep()' and observe how it affects the
    feel of the music.

3.  Add a silence mode toggled by pressing SW2 and SW5 at the same
    time. When silent, 'noTone(LS1)' stops the tone without changing
    'frequency'. Pressing either button alone while silent resumes
    the tone at the stored frequency. How will you detect that two
    buttons are pressed simultaneously?

4.  Arduino's tone() function always produces a 50% duty cycle
    square wave - the signal spends equal time HIGH and LOW on every
    cycle. Changing the duty cycle is not possible through
    'analogWrite()' on the speaker pin, because 'analogWrite()'
    changes the duty cycle but not the frequency, and 'tone()'
    takes control of the timer and ignores 'analogWrite()'.

    The Arduino Nano ESP32's hardware has a dedicated LEDC (LED
    Control) peripheral that can set both frequency and duty cycle
    independently. Research 'ledcAttach()', 'ledcWriteTone()', and
    'ledcWrite()' in the ESP32 Arduino documentation. How would you
    use these functions to produce the same pitch at different duty
    cycles? What timbre change do you hear when the duty cycle
    is very low (say, 5% of 255)?

*/
