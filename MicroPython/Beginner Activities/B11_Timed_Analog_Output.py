"""
================================================================================
Activity 11 Extension: Timed Analog Output [B11_Timed_Analog_Output.py]
April 7, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPER_Nano.py board module file.

Before starting, re-read GE2, GE4, and GE5 from
Activity 11: Non-Blocking Timing.

This skeleton reimplements Activity 10's analog output controls
using independent non-blocking timers rather than a single shared
loop delay. Each control now has its own update rate:

  LED2 dim rate:  how often SW3/SW4 change brightness (ms per step)
  LED3 fade rate: how often the automatic fade advances (ms per step)
  LED4/5 rate:    how often pot readings update LED brightness (ms)

In Activity 10, all of these were coupled to STEP_DELAY - changing
one changed all of them. Here, each rate is set independently.

Controls (same as Activity 10):
  SW3/SW4 - dim/brighten LED2 (at DIM_RATE ms per step)
  SW2     - trigger automatic fade up on LED3
  SW5     - trigger automatic fade down on LED3
  RV1/RV2 - control LED4/LED5 brightness (if POTS_INSTALLED)
================================================================================
"""
# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32
import BEAPER_Nano as beaper

from machine import Pin, PWM
import time

# --- Program Configuration ------------
POTS_INSTALLED = False                # Set True if RV1 and RV2 are installed

# --- Program Constants ----------------
LOOP_DELAY  = const(1)               # Main loop delay (ms)
PWM_FREQ    = const(1000)            # PWM frequency for LEDs (Hz)

DIM_RATE    = const(20)              # ms between each LED2 brightness step
FADE_RATE   = const(10)              # ms between each LED3 fade step
POT_RATE    = const(50)              # ms between pot reads for LED4/LED5

BRIGHT_STEP = const(2000)            # LED2 brightness change per dim step
FADE_STEP   = const(500)             # LED3 brightness change per fade step

# --- Reconfigure LED pins as PWM outputs ---
LED2_PWM = PWM(Pin(beaper.LED2_PIN), freq=PWM_FREQ, duty_u16=0)
LED3_PWM = PWM(Pin(beaper.LED3_PIN), freq=PWM_FREQ, duty_u16=0)
LED4_PWM = PWM(Pin(beaper.LED4_PIN), freq=PWM_FREQ, duty_u16=0)
LED5_PWM = PWM(Pin(beaper.LED5_PIN), freq=PWM_FREQ, duty_u16=0)

# --- Program Variables ----------------
led2_brightness = 0
led3_brightness = 0
fade_state = 0                       # 1 = fading up, -1 = fading down, 0 = idle

# TODO: declare timestamp variables for each timer
# last_dim_time  = 0
# last_fade_time = 0
# last_pot_time  = 0


# --- Program Functions ----------------

def set_brightness(pwm_led, brightness):
  brightness = max(0, min(65535, brightness))
  pwm_led.duty_u16(brightness)
  return brightness


# --- Main Program ---------------------

beaper.nano_led_on()
print("Timed Analog Output")
print("SW3/SW4: dim/brighten LED2   SW2/SW5: fade LED3 up/down")

# TODO: initialise all timestamp variables to time.ticks_ms()

while True:
  current_time = time.ticks_ms()

  # --- LED2 dimming timer ---
  # TODO: check if DIM_RATE ms has elapsed since last_dim_time
  #       if so: check SW3/SW4 and update led2_brightness
  #              update last_dim_time = current_time

  # --- LED3 fade timer ---
  # TODO: check if FADE_RATE ms has elapsed since last_fade_time
  #       if so: check SW2/SW5 to set fade_state
  #              advance fade by FADE_STEP if fade_state != 0
  #              update last_fade_time = current_time

  # --- Pot polling timer (if installed) ---
  # TODO: check if POT_RATE ms has elapsed since last_pot_time
  #       if so: read RV1/RV2 and update LED4/LED5 brightness
  #              update last_pot_time = current_time

  time.sleep_ms(LOOP_DELAY)


"""
Extension Questions

1.  Activity 10 used a single STEP_DELAY = 20ms for everything.
    This skeleton uses three separate rate constants: DIM_RATE,
    FADE_RATE, and POT_RATE. What does this make possible that
    Activity 10's version could not do?

    Try setting DIM_RATE = 5 and FADE_RATE = 100. In Activity 10,
    these two values were the same constant. Describe the
    difference in feel between the two controls.

2.  In Activity 10, the fade step size and the fade rate were
    combined into a single effect: FADE_STEP brightness units
    every STEP_DELAY milliseconds. Here they are separated:
    FADE_STEP controls how much the brightness changes each step,
    and FADE_RATE controls how often steps occur.

    What combination of FADE_STEP and FADE_RATE produces the
    same overall fade speed as Activity 10's FADE_STEP=500 with
    STEP_DELAY=20ms? Is there more than one combination that
    produces the same speed? What does each combination feel
    like differently?

3.  With LOOP_DELAY = 1ms, this program's loop runs approximately
    20 times faster than Activity 10's. Does it actually do 20
    times as much work? What is the processor doing on the
    iterations where no timer threshold is met?

    This is the key efficiency insight of non-blocking timing:
    the processor checks conditions continuously but only does
    meaningful work periodically. On a battery-powered device,
    this idle checking still consumes power - which is why
    advanced embedded systems use hardware interrupts or sleep
    modes instead of polling. That is a topic for Year 2.

"""