"""
================================================================================
Beginner Activity 10: Analog Output [Activity_B10_Analog_Output.py]
March 31, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPER_Nano.py board module file.

Analog jumper settings for this activity:
  JP3 - Enviro. (selects potentiometer RV1, if installed)
  JP4 - Enviro. (selects potentiometer RV2, if installed)
================================================================================
"""
# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32
import BEAPER_Nano as beaper

from machine import Pin, PWM
import time

# --- Program Configuration ------------
POTS_INSTALLED = False                # Set True if RV1 and RV2 are installed

# --- Program Constants ----------------
STEP_DELAY   = const(20)             # Main loop delay (ms) - ~50 iterations/sec
BRIGHT_STEP  = const(2000)           # LED2 brightness change per loop (SW3/SW4)
FADE_STEP    = const(500)            # LED3 brightness change per fade iteration
PWM_FREQ     = const(1000)           # PWM frequency for LEDs (Hz)

# --- Reconfigure LED pins as PWM outputs ---
# The board module defines LED pins as digital Pin objects for on/off control.
# Creating PWM objects on the same pins enables smooth analog brightness control.
# The pin number constants (LED2_PIN etc.) from the board module are used here
# rather than the Pin objects (LED2 etc.) - see GE2.
LED2_PWM = PWM(Pin(beaper.LED2_PIN), freq=PWM_FREQ, duty_u16=0)
LED3_PWM = PWM(Pin(beaper.LED3_PIN), freq=PWM_FREQ, duty_u16=0)
LED4_PWM = PWM(Pin(beaper.LED4_PIN), freq=PWM_FREQ, duty_u16=0)
LED5_PWM = PWM(Pin(beaper.LED5_PIN), freq=PWM_FREQ, duty_u16=0)

# --- Program Variables ----------------
led2_brightness = 0                  # Current LED2 brightness (0-65535)
led3_brightness = 0                  # Current LED3 brightness (0-65535)
fade_state = 0                       # LED3 fade: 1 = fading up, -1 = fading down, 0 = idle


# --- Program Functions ----------------

def set_brightness(pwm_led, brightness):
  # Set a PWM LED to a brightness level (0-65535).
  # Clamps the value to the valid range before setting.
  # Returns the clamped brightness so the caller can store it.
  brightness = max(0, min(65535, brightness))
  pwm_led.duty_u16(brightness)
  return brightness


# --- Main Program ---------------------

beaper.nano_led_on()
print("Activity 10: Analog Output")
print("SW3/SW4: dim/brighten LED2")
print("SW2: fade LED3 up to full  SW5: fade LED3 down to off")
if POTS_INSTALLED:
  print("RV1/RV2: control LED4/LED5 brightness")
print()

while True:
  # Update button states
  SW2_pressed = beaper.SW2.value() == 0
  SW3_pressed = beaper.SW3.value() == 0
  SW4_pressed = beaper.SW4.value() == 0
  SW5_pressed = beaper.SW5.value() == 0
  
  # SW3 dims LED2, SW4 brightens LED2 (one step per loop while held)
  if SW3_pressed:
    led2_brightness -= BRIGHT_STEP
    led2_brightness = set_brightness(LED2_PWM, led2_brightness)
  elif SW4_pressed:
    led2_brightness += BRIGHT_STEP
    led2_brightness = set_brightness(LED2_PWM, led2_brightness)
  print("LED2 brightness: ", led2_brightness)

  # SW2 triggers automatic fade up, SW5 triggers automatic fade down
  # Once triggered, the fade continues without the button being held
  if SW2_pressed and fade_state != 1:
    fade_state = 1                    # Begin fading up
  elif SW5_pressed and fade_state != -1:
    fade_state = -1                   # Begin fading down

  # Advance LED3 fade by one step per loop iteration
  if fade_state == 1:
    led3_brightness += FADE_STEP
    led3_brightness = set_brightness(LED3_PWM, led3_brightness)
    if led3_brightness >= 65535:
      fade_state = 0                  # Fade up complete
  elif fade_state == -1:
    led3_brightness -= FADE_STEP
    led3_brightness = set_brightness(LED3_PWM, led3_brightness)
    if led3_brightness <= 0:
      fade_state = 0                  # Fade down complete

  # RV1 and RV2 control LED4 and LED5 brightness directly (if installed)
  if POTS_INSTALLED:
    set_brightness(LED4_PWM, beaper.RV1_level())
    set_brightness(LED5_PWM, beaper.RV2_level())

  time.sleep_ms(STEP_DELAY)


"""
Guided Exploration

Activity 9 introduced analog input - reading continuously varying
physical quantities from sensors and converting raw ADC values into
meaningful numbers. This activity introduces the complementary
direction: analog output, using Pulse Width Modulation (PWM) to
produce continuously varying output levels from a digital signal.
The same 16-bit range used by the ADC in Activity 9 appears again
here as the duty cycle range, and the clamping pattern from
'set_brightness()' parallels the range-conversion pattern from
'map_range()'. By the end of this activity you will understand how
LEDs, motors, servos, and speakers are all controlled through the
same underlying PWM mechanism.

1.  All of the outputs used so far have been digital - fully on or
    fully off. Pulse Width Modulation (PWM) is a technique for
    producing an analog-like output using a digital signal. Rather
    than varying a voltage directly, PWM switches the output rapidly
    between HIGH and LOW. The proportion of time the signal spends
    HIGH is called the duty cycle.

    A duty cycle of 0% means the signal is always LOW - the LED is
    off. A duty cycle of 100% means the signal is always HIGH - the
    LED is at full brightness. A duty cycle of 50% means the signal
    spends equal time HIGH and LOW, and the LED appears at roughly
    half brightness because the eye averages the light energy over
    time, perceiving rapid switching as a steady intermediate level.

    The 'duty_u16' parameter used throughout this program represents
    the duty cycle as a 16-bit integer: 0 means 0% and 65535 means
    100%. Calculate the duty cycle percentage for these 'duty_u16'
    values: 0, 16384, 32768, 49152, 65535.

    Why is a 16-bit range (0-65535) used rather than simply 0-100?
    Think about how many distinct brightness levels each range
    provides and whether the difference would be visible to the eye.
    The Numeric Types sidebar explains why hardware ranges are
    expressed as powers of 2.

2.  The PWM objects for the LED pins are created using pin number
    constants from the board module:

  LED2_PWM = PWM(Pin(beaper.LED2_PIN), freq=PWM_FREQ, duty_u16=0)

    Open BEAPER_Nano.py and find where both 'LED2_PIN' and 'LED2'
    are defined. 'LED2_PIN' is an integer constant holding the GPIO
    pin number. 'LED2' is a Pin object created from that number,
    configured as a digital output.

    Why is 'beaper.LED2_PIN' used here rather than 'beaper.LED2'?
    What would happen if you passed the Pin object 'beaper.LED2'
    directly to 'PWM()' instead of wrapping the pin number in a
    new 'Pin()'? Try it and observe the result.

    This is the first time in the Activities that the program steps
    outside the board module's abstraction to configure hardware
    directly. The board module was designed anticipating this - the
    pin number constants are exposed precisely so that programs can
    create their own objects on those pins when needed.

3.  The PWM frequency (set to 1000 Hz by PWM_FREQ) determines how
    many times per second the signal switches on and off. At 1000 Hz
    the LED completes 1000 full on-off cycles per second, which
    appears perfectly steady to the eye.

    Try changing PWM_FREQ to different values and observe the LED
    during brightness changes with SW3/SW4:

  PWM_FREQ = const(10)      # Very low - clearly visible flicker
  PWM_FREQ = const(50)      # Low - flicker may be visible in motion
  PWM_FREQ = const(200)     # Borderline - depends on individual vision
  PWM_FREQ = const(1000)    # Standard - smooth appearance
  PWM_FREQ = const(10000)   # High - imperceptibly smooth

    Note that changing PWM_FREQ requires restarting the program,
    since PWM objects are created with the frequency at startup.
    You can update frequency on a running object using
    'LED2_PWM.freq(new_freq)' - try this in the console while the
    program is running.

    At what frequency does the flicker become invisible to you?
    Why do motor controllers typically use PWM frequencies of
    10 kHz or higher even though motors have no visual response?

4.  This program controls LED2 and LED3 in two fundamentally
    different ways, and the difference is important.

    Holding SW3 or SW4 dims or brightens LED2 by one BRIGHT_STEP
    value on every loop iteration while each button is held,
    providing direct, manual control.

    Pressing SW2 or SW5 triggers an automatic fade on LED3 that
    continues on its own until maximum or minimum brightness is
    reached. Look at the 'fade_state' variable: it is set to 1 or
    -1 when a button is pressed, and the main loop advances the
    fade by FADE_STEP on every iteration until the limit is hit.

    How are both the led2_brightness and led3_brightness values
    prevented from going below the minimum PWM value of 0 or
    above the maximum PWM value of 65535?

5.  The fade rate (how quickly LED3 changes) depends on two things:
    FADE_STEP and STEP_DELAY. Calculate how long a complete fade
    from 0 to 65535 takes with the current values. What FADE_STEP
    would make the fade take exactly 2 seconds?

    Now consider: what if the loop also needed to check a slow
    sensor taking 50ms per reading? The fade would slow down
    because each loop iteration takes longer. The fade rate is
    coupled to everything else in the loop. In Activity 11 you
    will learn a technique that gives each output its own
    independent update rate, solving this coupling problem.

6.  The 'POTS_INSTALLED' constant is a configuration flag - a
    boolean value set once at the top of the program to match the
    hardware, rather than something that changes during execution.

    This pattern is common in embedded firmware. Rather than the
    program trying to detect whether hardware is present (which
    can be unreliable for simple analog devices), the programmer
    declares the configuration explicitly, making assumptions
    visible and easy to change.

    If POTS_INSTALLED is False, what happens to LED4 and LED5?
    Are the PWM objects for those pins still created? What is
    their duty cycle if the 'if POTS_INSTALLED:' block never runs?

    Set POTS_INSTALLED to True (if your pots are installed) and
    observe LED4 and LED5 responding to RV1 and RV2. Notice that
    'RV1_level()' returns 0-65535 and 'duty_u16()' accepts 0-65535
    - the ranges match exactly so no scaling is needed. When would
    scaling be required?

7.  This program runs in a continuous 'while True:' loop, checking
    all inputs and updating all outputs on every iteration at a
    rate set by STEP_DELAY. This fixed-rate control loop is a
    fundamental embedded systems pattern - the program runs at a
    known rate, processing all inputs and producing all outputs
    in each pass.

    Count the total number of GPIO reads and PWM writes that
    happen in one loop iteration with POTS_INSTALLED = True and
    all buttons released. How many iterations per second does the
    program run at STEP_DELAY = 20ms?

    The fade and dimming behaviours share the same loop. What
    would happen to LED2's dimming responsiveness if FADE_STEP
    were very small, requiring thousands of iterations to complete
    a fade? Would LED2 still respond immediately to SW3 and SW4?
    This is the same coupling problem described in GE4, seen from
    a different angle.


Extension Activities

    The following activities each explore a specific area of analog
    output - sound, motor control, servos, or RGB colour. Each
    begins in a separate project file that sets up the hardware
    configuration and provides a partial program structure for you
    to complete. Open the relevant project file alongside this one.

    Choose the output type or types most relevant to your interests
    or project, or work through all of them. When opening a project
    file, refer to the guided exploration questions listed for that
    activity, as the project builds directly on them.

1.  Sound output using PWM
    Refer to: GE1, GE3
    Open: B10_Sound_Player_Project.py

2.  Motor control using PWM
    Refer to: GE1, GE2, GE3, GE4
    Open: B10_Motor_Controller_Project.py

3.  Servo control using PWM
    Refer to: GE1, GE3
    Open: B10_Servo_Controller_Project.py

4.  RGB colour output using PWM
    Refer to: GE1, GE2
    Open: B10_RGB_Controller_Project.py

"""