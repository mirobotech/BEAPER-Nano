"""
================================================================================
Beginner Activity 11: Non-Blocking Timing [Activity_B11_Non-Blocking_Timing.py]
April 7, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPER_Nano.py board module file.
================================================================================
"""
# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32
import BEAPER_Nano as beaper

import time

# --- Program Constants ----------------
LOOP_DELAY      = const(1)           # Main loop delay (ms) - see GE1
HOLD_TIME       = const(500)         # Button hold threshold (ms)
BLINK4_INTERVAL = const(200)         # LED4 blink toggle interval (ms)
BLINK5_INTERVAL = const(350)         # LED5 blink toggle interval (ms)

# --- Program Variables ----------------

# Part 1: Button hold detection
button_is_down = False               # True while SW2 is held
button_down_time = 0                 # Time SW2 was pressed (valid when button_is_down)
hold_fired = False                   # True after hold action fires this press

# Part 2: Multi-rate LED blinking
last_blink4_time = 0                 # Last time LED4 state was toggled
last_blink5_time = 0                 # Last time LED5 state was toggled
led4_state = False                   # Current LED4 on/off state
led5_state = False                   # Current LED5 on/off state


# --- Main Program ---------------------

beaper.nano_led_on()
beaper.LED2.value(0)
beaper.LED3.value(0)
beaper.LED4.value(0)
beaper.LED5.value(0)

print("Activity 11: Non-Blocking Timing")
print("SW2 tap: toggle LED2   SW2 hold: toggle LED3")
print("LED4 blinks at", 1000 // BLINK4_INTERVAL, "Hz")
print("LED5 blinks at", 1000 // BLINK5_INTERVAL, "Hz (approx)")
print()

# Initialise blink timestamps to current time
last_blink4_time = time.ticks_ms()
last_blink5_time = time.ticks_ms()

while True:
  current_time = time.ticks_ms()
  SW2_pressed = beaper.SW2.value() == 0

  # --- Part 1: Button hold detection ---

  if SW2_pressed:
    # Button is currently pressed
    if not button_is_down:
      # Button just went down - record the time and set flag
      button_is_down = True
      button_down_time = current_time
      hold_fired = False

    elif (not hold_fired and
          time.ticks_diff(current_time, button_down_time) >= HOLD_TIME):
      # Hold threshold reached - fire hold action once
      beaper.LED3.value(not beaper.LED3.value())
      hold_fired = True
      print("Hold: LED3 toggled")

  else:
    # Button is not pressed
    if button_is_down:
      # Button just released
      if not hold_fired:
        # No hold fired this press - treat as a tap
        beaper.LED2.value(not beaper.LED2.value())
        print("Tap: LED2 toggled")
      button_is_down = False
      hold_fired = False

  # --- Part 2: Multi-rate LED blinking ---

  if time.ticks_diff(current_time, last_blink4_time) >= BLINK4_INTERVAL:
    led4_state = not led4_state
    beaper.LED4.value(led4_state)
    last_blink4_time = current_time

  if time.ticks_diff(current_time, last_blink5_time) >= BLINK5_INTERVAL:
    led5_state = not led5_state
    beaper.LED5.value(led5_state)
    last_blink5_time = current_time

  time.sleep_ms(LOOP_DELAY)


"""
Guided Exploration

Activities 9 and 10 used a fixed 'STEP_DELAY' to control the main
loop rate, with all outputs - LED dimming, fading, pot reads - tied
to the same delay. This worked for simple programs, but GE5 and GE7
in Activity 10 identified a fundamental problem: if any part of the
loop slows down, every other part slows down with it. Adding a 50ms
sensor read would have made the LEDs dim and fade more slowly, and
there was no way to give different outputs different update rates
without restructuring the entire program.

This activity introduces non-blocking timing: rather than pausing
the whole program with 'sleep_ms()', the loop runs continuously and
checks timestamps to decide when each action is due. The technique
is demonstrated in two independent parts: Part 1 detects tap-versus-
hold on a single button, a task that is impossible with fixed delays,
and Part 2 blinks two LEDs at different rates simultaneously without
either one affecting the other. The same pattern appears in every
professional embedded program, from consumer electronics to
industrial controllers.

1.  Every program since Activity 3 has used 'time.sleep_ms()' to
    control how fast the main loop runs. In Activities 9 and 10,
    STEP_DELAY was set to 20ms, making the loop run approximately
    50 times per second.

    This activity sets LOOP_DELAY to 1ms - the loop runs
    approximately 1000 times per second. Why does this activity
    need a much faster loop rate than previous activities?

    Consider what would happen if LOOP_DELAY were set to 300ms
    with HOLD_TIME still at 500ms. How accurately could the
    program detect the hold threshold? At 300ms per iteration,
    what is the worst-case error in detecting a 500ms hold?

    More fundamentally: in Activity 10, the fade rate was coupled
    to STEP_DELAY. Look at this activity's loop - if you added a
    sensor read that takes 50ms to execute, would the blink rates
    be affected? Why? What would need to change to make the
    blink rates truly independent of all other code in the loop?

2.  The timing pattern used throughout this program follows the
    same structure every time:

  current_time = time.ticks_ms()
  if time.ticks_diff(current_time, last_event_time) >= INTERVAL:
    last_event_time = current_time
    # take action

    MicroPython provides 'time.ticks_diff()' rather than simply
    subtracting timestamps. To understand why, consider what
    happens to 'time.ticks_ms()' after the microcontroller has
    been running for a long time. The counter is stored as a
    fixed-size integer and eventually wraps back to zero. This
    is called counter rollover.

    Try evaluating these expressions in the MicroPython console,
    imagining that 'last_event_time' was recorded when the counter
    read 987654321 and 'current_time' is 100 (the counter has just
    rolled over):

  import time
  time.ticks_diff(100, 987654321)

    What result do you get? Now try plain subtraction:

  100 - 987654321

    'time.ticks_diff()' returns the correct positive elapsed time,
    accounting for rollover. Plain subtraction gives a large
    negative number, which would cause the '>= INTERVAL' check to
    never trigger, breaking all timing in the program.

    'time.ticks_diff(new, old)' is designed specifically to handle
    rollover correctly. Always use it instead of subtracting ticks
    values directly.

3.  The button hold detection uses three variables:
    'button_is_down', 'button_down_time', and 'hold_fired'.
    Trace through the program carefully for each of these three
    scenarios and record the state of all three variables at
    each step:

    Scenario A - Quick tap (button held less than HOLD_TIME):
    - Button goes down
    - Button released after 200ms

    Scenario B - Hold (button held longer than HOLD_TIME):
    - Button goes down
    - 500ms elapses
    - Button released after 800ms total

    Scenario C - Long hold (button held much longer than HOLD_TIME):
    - Button goes down
    - 500ms elapses (hold fires)
    - 1000ms elapses
    - Button released after 1500ms total

    Why are both 'button_is_down' and 'button_down_time' needed
    as separate variables? 'button_is_down' tells the program
    whether the button is currently held. 'button_down_time'
    records when it went down so the hold duration can be
    measured. Each variable has one clear responsibility.

    Why is 'hold_fired' necessary? What would happen in Scenario C
    if 'hold_fired' were not used and the hold action had no
    guard condition?

    Notice that in a tap, LED2 changes on button release rather
    than on button press. This is essential for tap-vs-hold
    detection - why? Could you detect a tap on button press
    instead, and what information would you need that is not
    available at that moment?

4.  Part 2 blinks LED4 and LED5 at different rates simultaneously.
    Both LEDs share the same main loop, but each has its own
    timestamp and interval constant.

    LED4 toggles every BLINK4_INTERVAL milliseconds (200ms),
    producing a 5 Hz blink rate. LED5 toggles every
    BLINK5_INTERVAL milliseconds (350ms), producing approximately
    2.9 Hz. These rates are not simple multiples of each other,
    so the LEDs drift in and out of phase - sometimes toggling
    close together, sometimes far apart.

    Calculate when LED4 and LED5 will next toggle at the same
    time (within one loop iteration), starting from the moment
    both are initialised. This is the least common multiple of
    their intervals. After this time, does the pattern repeat?

    The program uses '>=' rather than '==' to compare elapsed
    time against the interval. Explain why '==' would fail
    almost every time, even with a 1ms loop delay. What does
    this mean for the actual accuracy of the blink interval -
    if BLINK4_INTERVAL is 200ms and the loop runs every 1ms,
    what is the worst-case timing error for each toggle?

5.  Look at the two timing patterns side by side:

    Button hold detection:
    'button_down_time' is set once when the button goes down, and
    the elapsed time is checked every iteration while the button
    remains held.

    LED blinking:
    'last_blink4_time' is updated each time the LED toggles, and
    the elapsed time is checked every iteration unconditionally.

    Both use 'ticks_diff(current_time, last_time) >= THRESHOLD'
    but they serve different purposes. In the blink pattern the
    timestamp is reset to 'current_time' each time the action
    fires - the interval is measured from the last action. In the
    hold pattern the timestamp is set once when the button goes
    down and never reset - the interval is measured from a single
    past event.

    This distinction - repeating interval versus one-shot elapsed
    time - covers the vast majority of non-blocking timing needs
    in embedded programs. In Activity 12 you will see how these
    patterns combine with program state to produce more complex
    timed behaviours.

    Identify which pattern (repeating or one-shot) would be most
    appropriate for each of these timing needs:
    a) A status LED that blinks once per second indefinitely
    b) A timeout that triggers if no button is pressed for 30s
    c) A motor that runs for exactly 2 seconds when SW3 is pressed
    d) A sensor read every 500ms regardless of other activity


Extension Activities

    The following activities extend the program you have already
    been working with. Add each feature directly to this file
    rather than opening a new one, building on the timing patterns
    already in place. EA5 is the exception - it opens a separate
    skeleton file that reimplements Activity 10's analog output
    using the techniques from this activity.

1.  Add a debounced SW3 button using timing. Mechanical buttons
    produce multiple rapid transitions (bounces) when pressed,
    which can register as multiple presses. A software debounce
    ignores transitions that occur within DEBOUNCE_MS of the
    previous transition.

    Declare a 'last_sw3_change' timestamp and a 'sw3_state'
    variable to track the last stable state. In the main loop,
    check whether SW3's current reading differs from 'sw3_state'
    and whether enough time has elapsed since the last change:

  current_sw3 = beaper.SW3.value()
  if (current_sw3 != sw3_state and
      time.ticks_diff(current_time, last_sw3_change) >= DEBOUNCE_MS):
    sw3_state = current_sw3
    last_sw3_change = current_time
    if sw3_state == 0:
      print("SW3 debounced press")

    Try DEBOUNCE_MS values of 10, 50, and 200ms and observe the
    difference in responsiveness and reliability. What is the
    minimum debounce time that eliminates false triggers on your
    hardware?

2.  Implement an inactivity timeout. Declare a 'last_activity_time'
    timestamp that resets to 'current_time' whenever any button
    is pressed. If TIMEOUT_MS elapses with no button activity,
    dim all LEDs to a low brightness and print a timeout message.
    The next button press should restore normal operation and
    reset the timeout.

    What TIMEOUT_MS value feels natural for a bench instrument
    that should indicate it is idle? How does this pattern relate
    to the screen-off timers used in battery-powered devices?

3.  Implement a one-shot timed signal. When SW4 is pressed, LED2
    lights for exactly SIGNAL_MS milliseconds then turns off
    automatically, without using 'time.sleep_ms()'. If SW4 is
    pressed again while the signal is active, restart the timer
    from the new press time.

    You will need a 'signal_active' boolean and a
    'signal_start_time' timestamp. Each loop iteration checks
    whether the signal is active and whether SIGNAL_MS has
    elapsed:

  if signal_active:
    if time.ticks_diff(current_time, signal_start_time) >= SIGNAL_MS:
      signal_active = False
      beaper.LED2.value(0)

    Try SIGNAL_MS values of 100, 500, and 2000ms. Notice that
    at 2000ms the main loop continues running normally during
    the signal - SW2's tap-and-hold still works, and LED4 and
    LED5 continue blinking. This would be impossible with
    'time.sleep_ms(2000)'.

4.  Add independent timing for a slow sensor read alongside the
    fast timing already in the loop. Declare a 'last_temp_time'
    timestamp and a TEMP_INTERVAL constant of 2000ms. Each time
    TEMP_INTERVAL elapses, read 'beaper.temp_C()' and print the
    result.

    The button and blink timing should be completely unaffected
    by the sensor read. Verify this by observing the blink rates
    and hold detection while the temperature prints every 2
    seconds.

    Now temporarily add 'time.sleep_ms(50)' inside the temperature
    read block and observe what happens to the blink rates and hold
    sensitivity. This demonstrates concretely why blocking calls
    anywhere in the loop affect all timing in the loop.

5.  Re-implement Activity 10's analog output controls using
    independent non-blocking timers.
    Open: B11_Timed_Analog_Output.py

    This skeleton applies the timing patterns from this activity
    to the PWM brightness controls from Activity 10. Each control
    gets its own update rate, independent of the others - the
    dim rate for LED2, the fade step rate for LED3, and the
    pot-polling rate for LED4/LED5 can all be set separately.

"""