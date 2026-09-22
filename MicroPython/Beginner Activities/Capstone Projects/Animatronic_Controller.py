# ================================================================================
# Capstone Project: Animatronic Servo Controller [Animatronic_Controller.py]
# Version: 1.0
# Updated: July 25, 2026
#
# Platform: mirobo.tech BEAPER Nano circuit (any configuration)
# Requires: BEAPER_Nano.py board module file
#
# A three-servo animatronic puppet that plays back a pre-authored
# sequence of poses, looping continuously. The example sequence below
# animates a simple head - panning left and right, tilting, and
# opening and closing a jaw - but the same structure works for any
# combination of servos: a waving arm, blinking eyelids, a wagging
# tail. Adapt the example sequence to your own puppet design.
#
# Hardware used:
#   SW2          - Start playback
#   SW5          - Emergency stop (halts playback, holds current pose)
#   LS1          - Piezo speaker (start beep) - see EA3 for animated sound
#   On-board LED - On while playing
#
#   Servo 1 on H5 - Example: head pan (left/right)
#   Servo 2 on H6 - Example: head tilt (up/down)
#   Servo 3 on H7 - Example: jaw/mouth (open/close)
#
# NOTE: H5, H6, and H7 are pin aliases of H1, H4, and H2 respectively
# (see BEAPER_Nano.py). If you extend this project with an external
# sensor or switch on H1, H2, or H4, it will conflict with whichever
# servo shares that pin.
#
# --------------------------------------------------------------------------------
# How the animation sequence works:
#
# Four lists, indexed together, describe the sequence - the same
# parallel-list pattern from Simon Game's BUTTONS/LEDS/TONES, extended
# from three lists to four. Frame i of the animation is described by
# ANIM_SERVO1[i], ANIM_SERVO2[i], ANIM_SERVO3[i], and ANIM_HOLD[i]
# together:
#
#   ANIM_SERVO1[i] - servo 1's angle during frame i
#   ANIM_SERVO2[i] - servo 2's angle during frame i
#   ANIM_SERVO3[i] - servo 3's angle during frame i
#   ANIM_HOLD[i]   - how long frame i is held before advancing (ms)
#
# Playback moves all three servos to frame i's angles, waits
# ANIM_HOLD[i] milliseconds, then advances to frame i+1 - wrapping
# back to frame 0 after the last frame, so the sequence loops
# continuously. See Development Guide Step 1 before editing the
# sequence.
#
# --------------------------------------------------------------------------------
# Animatronic controller behaviour:
#   IDLE    - Servos at HOME_ANGLE. Press SW2 to begin playback.
#   PLAYING - Cycling through the animation sequence, looping forever.
#   STOPPED - Playback halted, servos hold their current pose exactly
#             where they were. Press SW2 to return to IDLE (servos
#             then move to HOME_ANGLE).
#
# Before you begin - complete your capstone plan using the Capstone
# Preparation Guide: a plain-English description of your puppet and
# what it does, a list of your servos and what each one moves, your
# planned sequence of poses, and your testing plan.
# ================================================================================

# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32.
import BEAPER_Nano as beaper  # Set up BEAPER Nano I/O

import time
from machine import Pin, PWM

# --- State Constants -------------------
STATE_IDLE    = const(0)             # Servos at rest - waiting for start
STATE_PLAYING = const(1)             # Cycling through the animation sequence
STATE_STOPPED = const(2)             # Halted - servos hold their current pose

STATE_NAMES = {
  STATE_IDLE:    "IDLE",
  STATE_PLAYING: "PLAYING",
  STATE_STOPPED: "STOPPED",
}

# --- Servo Configuration ----------------
HOME_ANGLE = 45                      # Neutral/rest angle for all servos (0-90)

# BEAPER_Nano.py's SERVO1-4 constants are commented out, since H5-H8
# share pins with H1-H4 and I2C - only uncomment the ones you are
# using. This project constructs three directly instead.
SERVO1 = PWM(Pin(beaper.H5_PIN), freq=50, duty_u16=4915)   # Example: head pan
SERVO2 = PWM(Pin(beaper.H6_PIN), freq=50, duty_u16=4915)   # Example: head tilt
SERVO3 = PWM(Pin(beaper.H7_PIN), freq=50, duty_u16=4915)   # Example: jaw/mouth

# --- Animation Sequence -----------------
# Four parallel lists - see the header comment above for how they fit
# together. Frame 0 is (ANIM_SERVO1[0], ANIM_SERVO2[0], ANIM_SERVO3[0],
# ANIM_HOLD[0]), frame 1 is index 1 across all four lists, and so on.
# Replace these with your own puppet's poses - angles are 0-90 degrees.
ANIM_SERVO1 = [45, 20, 20, 70, 70, 45]   # Head pan:  centre, left, left, right, right, centre
ANIM_SERVO2 = [45, 45, 45, 45, 30, 45]   # Head tilt: centre, centre, centre, centre, down, centre
ANIM_SERVO3 = [30, 30, 60, 60, 30, 30]   # Jaw:       closed, closed, open, open, closed, closed
ANIM_HOLD   = [500, 700, 400, 700, 500, 800]   # Hold time per frame (ms)
NUM_FRAMES  = 6                          # Must match the length of the lists above

# --- Timing Constants -------------------
LOOP_DELAY = const(10)                # Main loop delay (ms)

# --- Program Variables ------------------
state           = STATE_IDLE
state_start     = 0

current_frame   = 0                   # Which frame is currently being held
frame_start     = 0                   # Time the current frame's hold period began


# --- Program Functions ------------------

def set_pose(servo1_angle, servo2_angle, servo3_angle):
  # Move all three servos to the given angles immediately.
  beaper.set_servo(SERVO1, servo1_angle)
  beaper.set_servo(SERVO2, servo2_angle)
  beaper.set_servo(SERVO3, servo3_angle)

def enter_state(new_state, current_time, reason=""):
  global state, state_start
  state       = new_state
  state_start = current_time
  print("-->", STATE_NAMES[new_state], end="")
  if reason:
    print(" (", reason, ")", sep="")
  else:
    print()


# --- Main Program ---------------------

set_pose(HOME_ANGLE, HOME_ANGLE, HOME_ANGLE)
beaper.nano_led_off()

print("Animatronic Servo Controller")
print("Sequence length:", NUM_FRAMES, "frames")
print("SW2: start playback")
print("SW5: emergency stop")
print()

state_start = time.ticks_ms()
enter_state(STATE_IDLE, state_start, "startup")

while True:
  current_time = time.ticks_ms()
  elapsed      = time.ticks_diff(current_time, state_start)

  # --- Emergency stop (SW5) - checked before all state logic ---
  if beaper.SW5.value() == 0 and state == STATE_PLAYING:
    beaper.nano_led_off()
    enter_state(STATE_STOPPED, current_time, "emergency stop")
    # Servos are NOT moved here - they simply hold whatever pose they
    # were in when the stop was triggered.

  # --- State: Idle ---
  elif state == STATE_IDLE:
    if beaper.SW2.value() == 0:
      beaper.tone(880, 100)
      beaper.nano_led_on()
      # TODO: start playback from the beginning of the sequence:
      #       - set current_frame = 0
      #       - call set_pose() with frame 0's angles
      #         (ANIM_SERVO1[0], ANIM_SERVO2[0], ANIM_SERVO3[0])
      #       - record frame_start = current_time
      #       - enter_state(STATE_PLAYING, current_time, "SW2 pressed")
      pass

  # --- State: Playing ---
  elif state == STATE_PLAYING:
    # TODO: non-blocking sequence playback, reusing the Activity 11
    #       repeating-timer pattern:
    #       - if elapsed since frame_start >= ANIM_HOLD[current_frame]:
    #           - advance current_frame by 1, wrapping back to 0 after
    #             the last frame with % NUM_FRAMES, so the sequence
    #             loops continuously
    #           - call set_pose() with the new current_frame's angles
    #             from ANIM_SERVO1/ANIM_SERVO2/ANIM_SERVO3
    #           - reset frame_start = current_time
    pass

  # --- State: Stopped ---
  elif state == STATE_STOPPED:
    if beaper.SW2.value() == 0:
      set_pose(HOME_ANGLE, HOME_ANGLE, HOME_ANGLE)
      enter_state(STATE_IDLE, current_time, "SW2 pressed")

  time.sleep_ms(LOOP_DELAY)


# ================================================================================
# Development Guide
# ================================================================================
#
# Work through these steps in order. Test each servo individually
# before combining them into a sequence.
#
# --------------------------------------------------------------------------------
# Step 1 - Understanding the parallel-list sequence
# --------------------------------------------------------------------------------
#
# This capstone reuses the parallel-list pattern from Simon Game's
# BUTTONS, LEDS, and TONES - three separate lists, indexed together,
# where index i across all three lists describes one complete "thing"
# (one button/LED/tone combination). Here, four lists play the same
# role for one animation frame instead:
#
# Example code:
#
# ANIM_SERVO1[2]  # servo 1's angle during frame 2
# ANIM_SERVO2[2]  # servo 2's angle during frame 2
# ANIM_SERVO3[2]  # servo 3's angle during frame 2
# ANIM_HOLD[2]    # how long frame 2 is held (ms)
#
# All four values at index 2 together describe "frame 2" of the
# animation, the same way BUTTONS[2], LEDS[2], and TONES[2] together
# described "Simon colour 2." An alternative design could combine
# each frame into a single tuple - (servo1, servo2, servo3, hold) -
# stored in one list of tuples instead of four separate lists. Both
# work; four parallel lists keeps each individual list simple and
# reuses exactly the pattern Simon Game already introduced, without
# adding a new nested structure on top of it.
#
# Trace through frame 2 in the example sequence by hand: what angle
# is each servo at, and how long is that pose held before the
# sequence moves on to frame 3?
#
# --------------------------------------------------------------------------------
# Step 2 - Servo wiring and range verification
# --------------------------------------------------------------------------------
#
# Verify each servo moves correctly and confirm which physical
# movement each angle produces for your specific puppet mechanism.
# Temporarily add these lines after set_pose(HOME_ANGLE, HOME_ANGLE,
# HOME_ANGLE) near the top of the program:
#
# Example code:
#
# time.sleep_ms(1000)
# beaper.set_servo(SERVO1, 0)
# time.sleep_ms(1000)
# beaper.set_servo(SERVO1, 90)
# time.sleep_ms(1000)
# beaper.set_servo(SERVO1, HOME_ANGLE)
#
# Repeat for SERVO2 and SERVO3. Note which angle corresponds to which
# physical position (e.g. "20 degrees = head fully left") - you will
# need these reference points when designing your own sequence in
# Step 5. Remove the test lines once you have confirmed all three
# servos move as expected.
#
# --------------------------------------------------------------------------------
# Step 3 - Playback from IDLE
# --------------------------------------------------------------------------------
#
# Implement the TODO in STATE_IDLE. Test that pressing SW2 correctly
# moves all three servos to frame 0's pose and transitions to
# STATE_PLAYING. Check the Serial Monitor for the state transition.
#
# --------------------------------------------------------------------------------
# Step 4 - Sequence playback
# --------------------------------------------------------------------------------
#
# Implement the TODO in STATE_PLAYING. Test that the puppet cycles
# through all six example frames in order, holding each for the
# correct duration, and loops back to frame 0 after the last frame.
# Test the emergency stop (SW5) mid-sequence and confirm the servos
# freeze in place rather than snapping to any other position. Test
# that pressing SW2 from STOPPED returns to HOME_ANGLE and IDLE.
#
# --------------------------------------------------------------------------------
# Step 5 - Design your own sequence
# --------------------------------------------------------------------------------
#
# Using the angle reference points you recorded in Step 2, design and
# write your own ANIM_SERVO1/ANIM_SERVO2/ANIM_SERVO3/ANIM_HOLD lists
# for your own puppet concept. Remember to update NUM_FRAMES to match
# the new list lengths - what happens if NUM_FRAMES does not match?
# Test your sequence and adjust hold times and angles until the
# motion looks the way you intend.


# ================================================================================
# Extension Activities
# ================================================================================
#
# --------------------------------------------------------------------------------
# EA 1 - Smooth motion between poses
# --------------------------------------------------------------------------------
#
# The base sequence snaps instantly from one pose to the next, which
# can look mechanical. Implement smooth motion instead: rather than
# calling set_pose() once per frame, step each servo gradually from
# its previous angle to the new frame's angle over a short
# TRANSITION_TIME, using the same "elapsed time since last step ->
# advance by a small amount" repeating-timer pattern used elsewhere
# in this curriculum (Activity 12's alarm flash, for example). You
# will need to track each servo's current angle separately from its
# target angle. Does smooth motion change how long each frame's total
# hold time should be?
#
# --------------------------------------------------------------------------------
# EA 2 - Fourth servo
# --------------------------------------------------------------------------------
#
# Add a fourth servo (H8) and a fifth parallel list, ANIM_SERVO4,
# following the same pattern as the first three. What did you need
# to change in how many places to add one more servo? At what number
# of servos would you want a different structure - see Analog
# Monitor's EA5 for a similar tradeoff in a different context.
#
# --------------------------------------------------------------------------------
# EA 3 - Synchronized sound
# --------------------------------------------------------------------------------
#
# Add a fifth parallel list, ANIM_TONE, giving each frame a tone
# frequency (or 0 for silence). Play the tone (or call
# beaper.noTone()) each time a new frame begins, alongside the servo
# movement. Try syncing a tone with the jaw-open frames in the
# example sequence for a simple "talking" effect. Real animatronic
# characters often go further, syncing individual mouth shapes to
# recorded speech - what would be needed to approximate that with
# only two mouth positions (open/closed)?
#
# --------------------------------------------------------------------------------
# EA 4 - Interactive recording
# --------------------------------------------------------------------------------
#
# Add a RECORDING state where SW3/SW4 adjust the angle of a
# currently-selected servo (cycle which servo is selected with a
# third button), and SW2 captures the current pose as a new frame,
# appending it to the sequence rather than requiring the sequence to
# be hand-written in code ahead of time. You will need mutable lists
# built up one frame at a time (starting empty and growing with each
# capture) rather than the fixed-length lists used here - similar to
# how Simon Game's sequence list grows one step at a time, but built
# from live servo positions instead of random button choices.
#
# --------------------------------------------------------------------------------
# EA 5 - Random idle behaviour
# --------------------------------------------------------------------------------
#
# Instead of holding perfectly still in STATE_IDLE, add small random
# movements (a slight head tilt, an occasional blink) every few
# seconds while waiting for SW2, so the puppet appears "alive" even
# before playback starts. How would you keep these idle movements
# from interfering with a press of SW2 to begin the real sequence?