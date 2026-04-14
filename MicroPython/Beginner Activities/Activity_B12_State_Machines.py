"""
================================================================================
Beginner Activity 12: State Machines [Activity_B12_State_Machines.py]
April 14, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPER_Nano.py board module file.

This program implements a traffic light controller as a state machine.
The traffic light cycles through green, yellow, and red states. A car
sensor (SW2) can register a waiting vehicle during red, triggering an
advanced green turn signal before the regular green phase. A walk
request (SW5) registered during red extends the subsequent green phase
and lights the on-board LED as a walk signal.

Traffic light LED assignments:
  LED2        - Left turn signal (advanced green, flashing)
  LED3        - Straight through / regular green
  LED4        - Yellow
  LED5        - Red (stays lit during advanced green phase)
  On-board LED - Walk signal (active during extended green)
================================================================================
"""
# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32
import BEAPER_Nano as beaper

import time

# --- State Constants ------------------
# Each state is given a named integer constant. Using names rather
# than raw numbers makes the code read like the state diagram.
STATE_ADV_GREEN = const(0)           # Advanced green: left turn flashing
STATE_GREEN     = const(1)           # Regular green: straight through
STATE_YELLOW    = const(2)           # Yellow: prepare to stop
STATE_RED       = const(3)           # Red: all stopped

# --- Program Constants ----------------
LOOP_DELAY      = const(1)           # Main loop delay (ms)

ADV_GREEN_TIME  = const(5000)        # Advanced green phase duration (ms)
GREEN_TIME      = const(6000)        # Regular green phase duration (ms)
YELLOW_TIME     = const(2000)        # Yellow phase duration (ms)
RED_TIME        = const(5000)        # Red phase duration (ms)
FLASH_INTERVAL  = const(400)         # Advanced green flash toggle interval (ms)
WALK_EXTENSION  = const(4000)        # Extra green time for pedestrian crossing (ms)

# --- Program Variables ----------------
state           = STATE_RED          # Current state (start at red)
state_start     = 0                  # Time current state began
last_flash_time = 0                  # Last time advanced green LED toggled
flash_on        = False              # Current flash LED state
car_waiting     = False              # Car sensor triggered during red
walk_requested  = False              # Walk signal requested during red
effective_green = GREEN_TIME         # Green duration (extended if walk requested)


# --- Program Functions ----------------

def all_leds_off():
  beaper.LED2.value(0)
  beaper.LED3.value(0)
  beaper.LED4.value(0)
  beaper.LED5.value(0)

def enter_state(new_state, current_time, reason=""):
  # Transition to a new state: turn off all LEDs, set the new state,
  # record the transition time, and print a diagnostic message.
  global state, state_start, flash_on
  all_leds_off()
  beaper.nano_led_off()              # Clear walk signal on any transition
  state = new_state
  state_start = current_time
  flash_on = False

  state_names = {
    STATE_ADV_GREEN: "ADV_GREEN",
    STATE_GREEN:     "GREEN",
    STATE_YELLOW:    "YELLOW",
    STATE_RED:       "RED",
  }
  print("-->", state_names[new_state], end="")
  if reason:
    print(" (", reason, ")", sep="")
  else:
    print()


# --- Main Program ---------------------

all_leds_off()
beaper.nano_led_off()                # On-board LED reserved for walk signal
print("Activity 12: State Machines - Traffic Light Controller")
print("SW2: car sensor (advanced green request during red)")
print("SW5: walk signal request (during red)")
print()

# Enter the initial state
state_start = time.ticks_ms()
last_flash_time = time.ticks_ms()
print("--> RED (initial)")
beaper.LED5.value(1)

while True:
  current_time = time.ticks_ms()
  elapsed = time.ticks_diff(current_time, state_start)

  # --- State: Advanced Green ---
  if state == STATE_ADV_GREEN:
    # Red stays lit during advanced green (cross traffic still stopped)
    # Flash LED2 at FLASH_INTERVAL while state persists
    if time.ticks_diff(current_time, last_flash_time) >= FLASH_INTERVAL:
      flash_on = not flash_on
      beaper.LED2.value(flash_on)
      last_flash_time = current_time

    # Transition to regular green after ADV_GREEN_TIME
    if elapsed >= ADV_GREEN_TIME:
      # Apply walk extension if requested (request was held through adv. green)
      effective_green = GREEN_TIME + WALK_EXTENSION if walk_requested else GREEN_TIME
      enter_state(STATE_GREEN, current_time, "advanced green complete")
      beaper.LED3.value(1)
      if walk_requested:
        beaper.nano_led_on()
        print("    walk signal active (+", WALK_EXTENSION // 1000, "s extension)")

  # --- State: Green ---
  elif state == STATE_GREEN:
    if elapsed >= effective_green:
      walk_requested = False
      enter_state(STATE_YELLOW, current_time, "timed out")
      beaper.LED4.value(1)

  # --- State: Yellow ---
  elif state == STATE_YELLOW:
    if elapsed >= YELLOW_TIME:
      enter_state(STATE_RED, current_time, "timed out")
      beaper.LED5.value(1)

  # --- State: Red ---
  elif state == STATE_RED:
    # Check car sensor - record request but transition only when red elapses
    if beaper.SW2.value() == 0 and not car_waiting:
      car_waiting = True
      print("    car sensor: advanced green requested")

    # Check walk request - recorded here, processed on entering green
    if beaper.SW5.value() == 0 and not walk_requested:
      walk_requested = True
      print("    walk button: extended green requested")

    # Transition when red time elapses
    if elapsed >= RED_TIME:
      if car_waiting:
        car_waiting = False
        enter_state(STATE_ADV_GREEN, current_time, "car waiting")
        beaper.LED5.value(1)              # Red stays on during advanced green
        last_flash_time = current_time
      else:
        effective_green = GREEN_TIME + WALK_EXTENSION if walk_requested else GREEN_TIME
        enter_state(STATE_GREEN, current_time, "timed out")
        beaper.LED3.value(1)
        if walk_requested:
          beaper.nano_led_on()
          print("    walk signal active (+", WALK_EXTENSION // 1000, "s extension)")

  time.sleep_ms(LOOP_DELAY)


"""
Guided Exploration

Activities 9 through 11 focused on a single technical problem at a
time: analog input, output, then non-blocking timing. Each activity's
program grew more capable, but the overall structure stayed the same -
a loop that checks conditions and updates outputs. This works well
for independent controls, but becomes hard to manage when the program
needs to behave differently depending on what has happened before.

This activity introduces state machines: a way of organising a program
around a set of named states, with explicit rules for when to move
between them. The traffic light controller below has four states
(ADV_GREEN, GREEN, YELLOW, RED), each with its own outputs and its
own timing. The non-blocking timer patterns from Activity 11 appear
here too - state duration is tracked with a one-shot elapsed timer,
and the advanced green flash uses an independent repeating timer
inside the same state. The difference is that now those timers drive
transitions between program modes, not just individual outputs.

1.  A state machine can be described visually as a state diagram:
    circles represent states and arrows represent transitions between
    them. Each arrow is labelled with the event or condition that
    triggers the transition.

    Draw the state diagram for this traffic light program. Your
    diagram should have four circles (one per state) and arrows
    showing every possible transition. Label each arrow with its
    trigger - either a timing condition (e.g. "elapsed >= GREEN_TIME")
    or an event (e.g. "car_waiting == True").

    Compare your diagram to the program's 'while True:' loop. Can
    you find a direct correspondence between each arrow in your
    diagram and a specific 'if' statement in the code?

    Notice that the outputs of each state - which LEDs are on - are
    set when entering each state via 'enter_state()', not checked
    continuously every loop iteration. Why is this cleaner? What
    would happen if a noisy connection caused 'enter_state()' to
    be called a second time while already in a state?

    The red LED (LED5) stays on during the advanced green phase even
    though the state has changed. Where in the code is this handled,
    and why is it correct for cross-traffic safety?

2.  States are defined using named integer constants:

  STATE_ADV_GREEN = const(0)
  STATE_GREEN     = const(1)
  STATE_YELLOW    = const(2)
  STATE_RED       = const(3)

    The program could instead use raw numbers (0, 1, 2, 3) directly
    in the 'if' statements. What would be lost? Consider what happens
    if you need to add a new state between GREEN and YELLOW and must
    renumber the existing states.

    Named constants also make the serial output meaningful. The
    'enter_state()' function uses a dictionary to look up the
    state name for printing. What would the output look like if
    raw numbers were used instead of names?

    This naming principle applies beyond state machines. Any number
    in your program that represents a meaningful concept - a pin,
    a threshold, a mode - should have a name. Where else in this
    curriculum have you seen this principle applied?

3.  The program uses two flag variables to record sensor events
    during red: 'car_waiting' and 'walk_requested'. Both are set
    when their respective buttons are pressed during red, but
    neither triggers an immediate transition - they are checked
    only when the red duration elapses.

    Why is this design correct for 'car_waiting'? What would happen
    if the program transitioned to advanced green immediately when
    SW2 was pressed, regardless of how much red time remained?

    The walk request is treated differently from the car request:
    it does not change which state follows red, only how long green
    lasts and whether the walk signal lights. Trace through the
    program for this sequence of events and identify exactly where
    'walk_requested' affects the program's behaviour:

    - Red phase begins
    - SW5 pressed at t=2000ms into red
    - SW2 pressed at t=3000ms into red
    - Red elapses at t=5000ms

    Both flags are separate variables with separate responsibilities,
    even though they are both set during red and each cleared when
    the phase it governs ends. Why is it important that they are
    separate rather than combined into a single variable or checked
    in a single 'if' statement?

4.  The advanced green state contains two independent timers
    running simultaneously:

    - 'state_start' tracks how long the state has been active,
      used to determine when to leave the state.
    - 'last_flash_time' tracks when the LED last toggled, used
      to control the flash rate.

    These two timers are completely independent - the flash rate
    does not affect the state duration and vice versa. Trace
    through several iterations of the loop while in STATE_ADV_GREEN
    and verify that both timers advance independently.

    This is the multi-rate timing pattern from Activity 11, now
    applied inside a single state of a state machine: the state-
    duration timer is a one-shot elapsed timer (set once on entry,
    never reset), while the flash timer is a repeating interval
    timer (reset each time the LED toggles). What would happen to
    the flash rate if 'state_start' were reset each time the LED
    toggled? What would happen to the state duration?

5.  The 'enter_state()' function prints a diagnostic message every
    time a state transition occurs:

  --> GREEN (timed out)
  --> YELLOW (timed out)
  --> RED (timed out)
  --> ADV_GREEN (car waiting)
  --> GREEN (advanced green complete)

    This is serial output used as an engineering tool rather than
    as a user interface. By printing on transitions rather than
    every loop iteration, the output is concise and meaningful -
    each line tells you exactly what happened and why.

    Compare this to printing every loop iteration as some earlier
    activities did. How many lines per second would be printed at
    LOOP_DELAY = 1ms if every iteration printed a status message?
    Why would that be less useful than transition-only printing?

    Add a print statement inside the STATE_RED block that prints
    the elapsed time every 1000ms while waiting. How does this
    feel different from the transition prints? When would
    continuous printing be useful versus transition-only printing?


Extension Activities

    Extension Activities 1 and 2 extend the traffic light program
    you have been working with - add each feature directly to this
    file. EA3 opens a separate skeleton that uses the same state
    machine pattern to implement a completely different system.

1.  Train crossing mode: add a train crossing sensor (SW3) that
    forces the signal to yellow then red from any active green
    state, and holds red until the train has cleared.

    A real signal must transition through yellow before red so
    that drivers already committed to crossing have time to clear
    the intersection safely. Jumping directly to red could cause
    collisions.

    Draw the updated state diagram before writing any code. Then
    implement the following behaviour:

    - If SW3 is pressed while in STATE_ADV_GREEN or STATE_GREEN,
      immediately transition to STATE_YELLOW (interrupting the
      normal cycle)
    - Yellow then transitions normally to red after YELLOW_TIME
    - A 'train_crossing' flag distinguishes train-forced red from
      normal red, preventing the normal cycle from resuming while
      SW3 is held
    - After SW3 is released, a CLEARANCE_TIME delay elapses
      before returning to normal red and resuming the cycle

    You will need:
    - A 'train_crossing' boolean flag
    - A 'clearance_start' timestamp for the post-release delay
    - A check for SW3 at the top of the main loop, before the
      state logic, to catch it in any green state
    - Modified red state logic that checks 'train_crossing'
      before deciding whether to resume the normal cycle

    How many new transitions does train crossing add to the state
    diagram? Does the yellow-first requirement change how you
    structure the SW3 check relative to the existing yellow state
    logic?

2.  Crosswalk extension: the main program already processes a
    walk request (SW5) registered during red, extending the green
    phase and lighting the on-board LED as a walk signal. Extend
    this behaviour in two ways:

    a) Walk signal timeout: the on-board LED should turn off
       partway through the extended green phase (after WALK_TIME
       milliseconds) to indicate that the safe crossing window
       has closed, even though the light remains green. Add a
       'walk_start_time' timestamp set when entering the extended
       green, and turn off the on-board LED when WALK_TIME elapses.

    b) Walk request during green: currently a walk request pressed
       during green is ignored (the check only runs during red).
       Add handling so that SW5 pressed during green sets
       'walk_requested' and extends the current green phase by
       WALK_EXTENSION, starting the walk signal immediately.
       Guard against extending an already-extended phase.

    For part (b), how do you extend the current green phase
    without restarting the state timer? Consider using
    'effective_green' and 'walk_requested' together to calculate
    the remaining time correctly.

3.  Combination lock: implement a three-button combination lock
    as a standalone state machine.
    Open: B12_Combination_Lock_Project.py

    The correct combination is SW2, SW3, SW4 pressed in sequence.
    The lock has states for each step of the sequence, an unlocked
    state, and an alarm state triggered by any wrong button press.
    SW5 resets from any state.

    This state machine is event-driven rather than time-driven -
    transitions occur when buttons are pressed, not when timers
    elapse. Compare its structure to the traffic light's structure:
    what is the same and what is different?

"""