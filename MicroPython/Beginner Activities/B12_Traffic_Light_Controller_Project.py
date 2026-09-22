# ================================================================================
# Project: Traffic Light Controller [B12_Traffic_Light_Controller_Project.py]
# Version: 1.2
# Updated: September 22, 2026
#
# Platform: mirobo.tech BEAPER Nano circuit (any configuration)
# Requires: BEAPER_Nano.py board module file
#
# Before starting this project, re-read GE 1 through GE 7 from
# Activity 12: State Machines. This skeleton reuses the same
# enter_state() and named-constant patterns as the combination lock,
# now applied to a four-state traffic light.
#
# State diagram:
#   RED --(RED_TIME elapsed, car_waiting)     --> ADV_GREEN
#   RED --(RED_TIME elapsed, not car_waiting) --> GREEN
#   ADV_GREEN --(ADV_GREEN_TIME elapsed)      --> GREEN
#   GREEN     --(effective green time elapsed)--> YELLOW
#   YELLOW    --(YELLOW_TIME elapsed)         --> RED
#
# Outputs per state:
#   RED:        LED5 on
#   ADV_GREEN:  LED5 on (cross traffic still stopped) + LED2 flashing
#               (protected left-turn arrow)
#   GREEN:      LED3 on
#   YELLOW:     LED4 on
#
# Simulated inputs (SW2/SW3 are only read during RED):
#   SW2: simulates a car waiting for the protected left turn -
#        sets 'car_waiting', which is checked once, when RED_TIME
#        elapses, to decide whether to enter ADV_GREEN or GREEN
#   SW3: simulates a pedestrian crossing request - sets
#        'walk_requested', which extends the following GREEN phase
#        by WALK_EXTENSION milliseconds
#
# Unlike the combination lock, where each button press needed to be
# counted individually, SW2 and SW3 here just need to be noticed at
# any point during RED - so this project checks them with the same
# plain 'beaper.SW2.value() == 0' comparison used since Activity 3,
# with no release-waiting required. A flag, once set, stays set until
# the state machine resets it on the next entry to RED.
# ================================================================================

# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32.
import BEAPER_Nano as beaper  # Set up BEAPER Nano I/O

import time

# --- State Constants ------------------
STATE_RED       = const(0)
STATE_ADV_GREEN = const(1)           # Protected left-turn arrow phase
STATE_GREEN     = const(2)
STATE_YELLOW    = const(3)

# --- Program Constants ----------------
LOOP_DELAY           = const(10)     # Main loop delay (ms)
RED_TIME             = const(3000)   # Minimum time spent in RED (ms)
ADV_GREEN_TIME       = const(2000)   # Protected left-turn arrow duration (ms)
GREEN_TIME           = const(4000)   # Base GREEN duration (ms)
YELLOW_TIME          = const(1500)   # YELLOW duration (ms)
WALK_EXTENSION       = const(2000)   # Extra GREEN time if a walk was requested (ms)
ARROW_FLASH_INTERVAL = const(200)    # Left-turn arrow flash toggle interval (ms)

# --- Program Variables ----------------
state           = STATE_RED
state_start     = 0
car_waiting     = False              # Set by SW2 during RED
walk_requested  = False              # Set by SW3 during RED
last_flash_time = 0                  # ADV_GREEN: last time the arrow toggled
arrow_on        = False              # ADV_GREEN: current arrow flash state


# --- Program Functions ----------------

def all_leds_off():
  beaper.LED2.value(0)
  beaper.LED3.value(0)
  beaper.LED4.value(0)
  beaper.LED5.value(0)

def calculate_green_time():
  # Return the GREEN duration for this cycle: the base GREEN_TIME,
  # extended by WALK_EXTENSION if a pedestrian requested a crossing
  # during the preceding RED phase. Written as its own function so
  # both places that need this value - entering GREEN, and checking
  # whether GREEN's time is up - always agree, rather than
  # recalculating the same expression twice and risking the two
  # copies drifting out of sync.
  if walk_requested:
    return GREEN_TIME + WALK_EXTENSION
  else:
    return GREEN_TIME

def enter_state(new_state, current_time, reason=""):
  # Transition to a new state: clear outputs, update state variable,
  # record transition time, and print a diagnostic message.
  global state, state_start, arrow_on
  all_leds_off()
  state = new_state
  state_start = current_time
  arrow_on = False

  state_names = {
    STATE_RED:       "RED",
    STATE_ADV_GREEN: "ADV_GREEN",
    STATE_GREEN:     "GREEN",
    STATE_YELLOW:    "YELLOW",
  }
  print("-->", state_names[new_state], end="")
  if reason:
    print(" (", reason, ")", sep="")
  else:
    print()


# --- Main Program ---------------------

beaper.nano_led_on()  # Status LED on
all_leds_off()
state_start = time.ticks_ms()

print("Traffic Light Controller")
print("SW2 (during RED): car waiting for left turn")
print("SW3 (during RED): pedestrian walk request")
print()

enter_state(STATE_RED, state_start, "startup")
beaper.LED5.value(1)

while True:
  current_time = time.ticks_ms()
  elapsed = time.ticks_diff(current_time, state_start)

  if state == STATE_RED:
    # TODO: if SW2 is pressed, set car_waiting = True
    # TODO: if SW3 is pressed, set walk_requested = True
    # TODO: once elapsed >= RED_TIME:
    #         if car_waiting: enter_state(STATE_ADV_GREEN, current_time)
    #                         turn on LED5 (still red for cross traffic)
    #                         reset car_waiting = False for the next cycle
    #         else:           enter_state(STATE_GREEN, current_time)
    #                         turn on LED3
    pass

  elif state == STATE_ADV_GREEN:
    # TODO: flash LED2 (the left-turn arrow) at ARROW_FLASH_INTERVAL,
    #       using last_flash_time and arrow_on the same way GE7's
    #       alarm flash timer works - remember LED5 needs to be lit
    #       again after each all_leds_off() inside enter_state(),
    #       since cross traffic is still stopped during this phase
    # TODO: once elapsed >= ADV_GREEN_TIME: enter_state(STATE_GREEN, current_time)
    #                                       turn on LED3
    pass

  elif state == STATE_GREEN:
    # TODO: once elapsed >= calculate_green_time():
    #         enter_state(STATE_YELLOW, current_time)
    #         turn on LED4
    pass

  elif state == STATE_YELLOW:
    # TODO: once elapsed >= YELLOW_TIME:
    #         enter_state(STATE_RED, current_time)
    #         turn on LED5
    #         reset walk_requested = False for the next cycle
    pass

  time.sleep_ms(LOOP_DELAY)


# ================================================================================
# Extension Activities
# ================================================================================
#
# --------------------------------------------------------------------------------
# EA 1 - Complete the skeleton
# --------------------------------------------------------------------------------
#
# Complete the four TODO sections above so the traffic light
# cycles correctly. Test each transition by watching the serial
# output and LEDs: does RED always last at least RED_TIME? Does
# holding SW2 during RED correctly route through ADV_GREEN? Does
# a walk request measurably lengthen the following GREEN phase?
#
# --------------------------------------------------------------------------------
# EA 2 - A second pedestrian button
# --------------------------------------------------------------------------------
#
# Add a second walk request button, SW4, for pedestrians crossing
# in the opposite direction, with its own 'walk_requested_2' flag.
# Either request should extend GREEN - but pressing both should
# not extend it twice. How will your condition check for "at
# least one of the two flags is set" without double-counting?
#
# --------------------------------------------------------------------------------
# EA 3 - All-red clearance interval
# --------------------------------------------------------------------------------
#
# Real traffic lights often include an all-red clearance interval
# - a brief period where every direction shows red, after YELLOW
# and before the next phase begins, to let the intersection fully
# clear before cross traffic gets a green light. Add a new
# ALL_RED state between YELLOW and RED, lasting ALL_RED_TIME
# milliseconds, with every LED off except LED5.
#
# Update your state diagram to include this new state and its
# transitions.
#
# --------------------------------------------------------------------------------
# EA 4 - Pedestrian countdown warning
# --------------------------------------------------------------------------------
#
# Add a pedestrian countdown warning: when GREEN has less than
# 3000ms of its calculated duration remaining, flash LED3 instead
# of holding it steady, to warn that the light is about to change.
# You will need to compare 'elapsed' against
# 'calculate_green_time() - 3000' rather than a fixed constant.
#
# --------------------------------------------------------------------------------
# EA 5 - Time-driven vs. event-driven transitions
# --------------------------------------------------------------------------------
#
# This traffic light and the combination lock both use
# 'enter_state()', named state constants, and 'time.ticks_diff()'
# for timing - but they differ in one significant way: the
# combination lock's transitions all depend on button presses,
# while most of this traffic light's transitions depend on
# elapsed time instead, with button presses only setting flags
# checked later.
#
# Look back at your state diagrams for both programs. Which
# transitions in each diagram are triggered by time, and which by
# an event? Is there a state in either program with more than one
# way to leave it?