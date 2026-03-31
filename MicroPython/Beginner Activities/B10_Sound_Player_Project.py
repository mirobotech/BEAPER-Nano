"""
================================================================================
Project: Sound Player [B10_Sound_Player_Project.py]
March 31, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPER_Nano.py board module file.

Before starting this project, re-read GE1 and GE3
from Activity 10: Analog Output.

This skeleton sets up the BEAPER Nano's piezo speaker as a PWM
output with independent control over frequency and duty cycle.
Frequency determines pitch - higher values produce higher pitches.
Duty cycle determines the tone's character (timbre) - a 50% duty
cycle produces a clean square wave, while lower duty cycles produce
a thinner, more nasal sound.

Controls:
  SW2 - decrease frequency (lower pitch)
  SW5 - increase frequency (higher pitch)
  SW3 - decrease duty cycle (thinner sound)
  SW4 - increase duty cycle (fuller sound)
================================================================================
"""
# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32
import BEAPER_Nano as beaper

import time

# --- Program Constants ----------------
STEP_DELAY    = 20                    # Main loop delay (ms)
FREQ_MIN      = 100                   # Minimum frequency (Hz)
FREQ_MAX      = 8000                  # Maximum frequency (Hz)
FREQ_STEP     = 50                    # Frequency change per loop iteration
DUTY_MIN      = int(65535 * 0.01)     # Minimum duty cycle (~1%)
DUTY_MAX      = int(65535 * 0.50)     # Maximum duty cycle (50%)
DUTY_STEP     = 500                   # Duty cycle change per loop iteration

# --- Program Variables ----------------
frequency = 440                       # Current frequency in Hz (A4 = 440 Hz)
duty      = int(65535 * 0.50)         # Current duty cycle (start at 50%)


# --- Program Functions ----------------

def set_tone(freq, duty_u16):
  # Set the piezo speaker to the given frequency and duty cycle.
  # Clamps both values to their valid ranges before applying.
  # Complete the TODO below before relying on the returned duty value.
  freq = max(FREQ_MIN, min(FREQ_MAX, freq))
  # TODO: clamp duty_u16 to the range DUTY_MIN .. DUTY_MAX
  beaper.LS1.freq(freq)
  beaper.LS1.duty_u16(duty_u16)
  return freq, duty_u16

def beep(freq, duty_u16, duration_ms):
  # Play a tone at the given frequency and duty cycle for duration_ms
  # milliseconds, then silence the speaker.
  # TODO: call set_tone() to start the tone
  # TODO: use time.sleep_ms() to wait for duration_ms
  # TODO: set beaper.LS1.duty_u16(0) to silence the speaker
  pass


# --- Main Program ---------------------

beaper.nano_led_on()
print("Sound Player")
print("SW2/SW5: pitch down/up   SW3/SW4: duty cycle down/up")

# Start with the speaker playing at the initial settings
frequency, duty = set_tone(frequency, duty)
print("Frequency:", frequency, "Hz   Duty:", round(duty * 100 / 65535), "%")

while True:
  SW2_pressed = beaper.SW2.value() == 0
  SW3_pressed = beaper.SW3.value() == 0
  SW4_pressed = beaper.SW4.value() == 0
  SW5_pressed = beaper.SW5.value() == 0
  changed = False

  if SW2_pressed:
    frequency -= FREQ_STEP
    changed = True
  elif SW5_pressed:
    frequency += FREQ_STEP
    changed = True

  if SW3_pressed:
    duty -= DUTY_STEP
    changed = True
  elif SW4_pressed:
    duty += DUTY_STEP
    changed = True

  if changed:
    frequency, duty = set_tone(frequency, duty)
    print("Frequency:", frequency, "Hz   Duty:", round(duty * 100 / 65535), "%")

  time.sleep_ms(STEP_DELAY)


"""
Extension Activities

1.  Implement the 'beep()' function and use it to play a startup
    chime when the program begins - three rising tones of decreasing
    duration, for example. Call 'beep()' from before the main loop
    so the chime plays once on startup, then the interactive
    controls take over.

    After the chime, does the speaker resume at the correct
    frequency and duty cycle? What do you need to call after
    'beep()' to restore the continuous tone?

2.  A melody can be stored as a sequence of (frequency, duration_ms)
    pairs. Here is a short example using the first four notes of
    'Ode to Joy':

  melody = (
    (659, 400),   # E5
    (659, 400),   # E5
    (698, 400),   # F5
    (784, 400),   # G5
  )

    The following code plays the melody one note at a time using
    'beep()'. Add it after your startup chime:

  for note in melody:
    beep(note[0], duty, note[1])
    time.sleep_ms(50)             # Short gap between notes

    Extend the melody with more notes, or create your own. Change
    the gap between notes and observe how it affects the feel of
    the music. What happens if you change 'duty' to a low value
    like 'int(65535 * 0.05)' before playing the melody?

3.  Add a silence mode toggled by pressing SW2 and SW5 at the same
    time. When silent, 'beaper.LS1.duty_u16(0)' stops the tone
    without changing 'frequency' or 'duty'. Pressing either button
    alone while silent resumes the tone at the stored settings.
    How will you detect that two buttons are pressed simultaneously?

4.  Investigate how 'beaper.tone()' from the board module differs
    from directly setting 'beaper.LS1.freq()' and
    'beaper.LS1.duty_u16()'. Open BEAPER_Nano.py and read the
    'tone()' function. What duty cycle does it always use? Could
    you produce the full range of timbres available in this project
    using 'beaper.tone()' alone, or does exploring timbre require
    direct PWM access as used here?

"""