# ================================================================================
# Reach-Ahead: Reaction Time Game with LCD Display [Reaction_Game_LCD_Nano.py]
# Version: 1.2
# Updated: November 24, 2026
#
# Platform: mirobo.tech BEAPER Nano circuit with optional 1.54" LCD
# Requires: BEAPER_Nano_v1_2.py, LCD.py, LCDconfig_Nano.py
#
# A preview of what an LCD display can add to a program you already
# know well - this is a complete, working version of the Reaction
# Time Game capstone, with its result screen shown on an LCD instead
# of only printed to the Serial Monitor. It uses just two LCD
# functions you have not seen before, text16() and rect(), in the
# same way you already call functions like beaper.tone() or
# time.sleep_ms() - as tools to use, not something you need to
# understand the inner workings of yet. A full activity on how the
# LCD works internally (the framebuffer, SPI, colour encoding) comes
# later in the intermediate course as Activity I01 - this program
# does not attempt to teach that, only to show what becomes possible
# once you have a real display in your toolbox alongside LEDs and a
# speaker.
#
# Game modes and rules are unchanged from the original Reaction Time
# Game capstone - see that file for the full design discussion. This
# version fills in all of that capstone's TODOs so you have a
# complete, working reference to read alongside your own attempt.
#
# Hardware used:
#   SW1          - Start a round / react during a round
#   SW2 / SW3    - Cycle game mode (only while at the menu)
#   SW4          - Cancel the current round, return to the menu
#   LS1          - Piezo speaker (stimulus/target beep, result tones)
#   On-board LED - On during an active round
#   LCD          - Shows the result of each round
# ================================================================================

# IMPORTANT: Copy BEAPER_Nano_v1_2.py, LCD.py, and LCDconfig_Nano.py into
# your Arduino Nano ESP32.
import BEAPER_Nano_v1_2 as beaper       # Set up BEAPER Nano I/O
import LCDconfig_Nano as lcd_config  # LCD configuration for BEAPER Nano

import time
import random

# --- LCD Setup --------------------------------------------------------------
# lcd_config.config() sets up the LCD and returns a display object.
# After this line, lcd.fill(), lcd.text16(), lcd.update(), etc. are
# available the same way beaper.tone() or beaper.SW1.value() are.

lcd = lcd_config.config()

# --- State Constants -------------------
STATE_MENU    = const(0)             # Selecting a mode, waiting to start
STATE_WAITING = const(1)             # SIMPLE only: waiting out the random delay
STATE_REACT   = const(2)             # SIMPLE only: stimulus is showing, timing the press
STATE_CHASING = const(3)             # TIMING only: chase pattern running
STATE_RESULT  = const(4)             # Showing the result of the last round

STATE_NAMES = {
  STATE_MENU:    "MENU",
  STATE_WAITING: "WAITING",
  STATE_REACT:   "REACT",
  STATE_CHASING: "CHASING",
  STATE_RESULT:  "RESULT",
}

# --- Mode Constants ---------------------
MODE_SIMPLE = const(0)               # Simple reaction time
MODE_TIMING = const(1)               # Timing / anticipation
NUM_MODES   = const(2)

MODE_NAMES = {
  MODE_SIMPLE: "SIMPLE",
  MODE_TIMING: "TIMING",
}

# --- Simple Reaction Time Configuration -
REACT_LED     = beaper.LED1          # The single stimulus LED for SIMPLE mode
MIN_WAIT_MS   = const(1500)          # Shortest possible random delay before the stimulus
MAX_WAIT_MS   = const(4000)          # Longest possible random delay before the stimulus

# --- Timing/Anticipation Configuration --
CHASE_LEDS        = (beaper.LED1, beaper.LED2, beaper.LED3, beaper.LED4)
CHASE_INTERVAL_MS = const(300)       # Time the chase spends on each LED
TARGET_POSITION   = const(2)         # Index into CHASE_LEDS - 2 = LED3

# --- Timing Constants --------------------
RESULT_DISPLAY_MS = const(2500)      # Minimum time a result is shown before advancing
LOOP_DELAY        = const(1)         # Main loop delay (ms) - kept short for timing precision

# --- LCD Layout Constants ----------------
WIDTH      = const(240)
HEIGHT     = const(240)
HEADER_H   = const(40)
BAR_X      = const(20)
BAR_Y      = const(170)
BAR_WIDTH  = const(200)
BAR_HEIGHT = const(26)
MAX_BAR_MS = const(1000)             # Values at or above this fill the whole bar

# --- Program Variables -------------------
state        = STATE_MENU
state_start  = 0

current_mode = MODE_SIMPLE

# --- SIMPLE mode variables ---
wait_duration       = 0              # This round's random delay (ms)
stimulus_time       = 0              # When the stimulus actually lit
reaction_time       = 0              # Most recent trial's reaction time (ms)
best_reaction_time  = 999999         # Best (lowest) reaction time this session
false_start         = False          # True if the most recent trial was a false start

# --- TIMING mode variables ---
chase_position       = 0             # Which of the 4 CHASE_LEDS is currently lit
last_chase_step      = 0             # Time the chase last advanced
last_target_lit_time = 0             # Time the chase most recently lit the target LED
timing_error         = 0             # Most recent trial's timing error (ms)
best_timing_error    = 999999        # Best (lowest) timing error this session

# --- SW2/SW3 edge detection (menu mode cycling) ---
sw2_last = 1
sw3_last = 1

# --- Result tracking (for the LCD screen) ---
result_shown         = False         # True once this round's result has been drawn
result_was_new_best  = False
result_value         = 0
result_failed        = False         # True for "too soon"
result_fail_message  = ""


# --- Program Functions ------------------

def all_choice_leds_off():
  for led in CHASE_LEDS:   # CHASE_LEDS includes REACT_LED (LED1) as its first entry
    led.value(0)

def enter_state(new_state, current_time, reason=""):
  global state, state_start
  state       = new_state
  state_start = current_time
  print("-->", STATE_NAMES[new_state], end="")
  if reason:
    print(" (", reason, ")", sep="")
  else:
    print()

def start_round(current_time):
  # Begin a new round in the currently selected mode.
  global wait_duration, false_start, result_shown
  global chase_position, last_chase_step, last_target_lit_time
  beaper.nano_led_on()
  all_choice_leds_off()
  result_shown = False
  if current_mode == MODE_SIMPLE:
    wait_duration = random.randint(MIN_WAIT_MS, MAX_WAIT_MS)
    false_start   = False
    enter_state(STATE_WAITING, current_time, "round start")
  elif current_mode == MODE_TIMING:
    chase_position   = 0
    last_chase_step  = current_time
    CHASE_LEDS[0].value(1)
    if TARGET_POSITION == 0:
      last_target_lit_time = current_time
    enter_state(STATE_CHASING, current_time, "round start")

def draw_menu():
  # The menu screen - just the mode name, large and centred, so the
  # LCD is never left blank while a mode is being chosen.
  lcd.fill(lcd.BLACK)
  lcd.rect(0, 0, WIDTH, HEADER_H, lcd.BLUE50, True)
  title = "Reaction Game"
  lcd.text16(title, (WIDTH - lcd.text16_width(title)) // 2, 12, lcd.WHITE)

  mode_str = MODE_NAMES[current_mode]
  lcd.text16(mode_str, (WIDTH - lcd.text16_width(mode_str)) // 2, 100, lcd.CYAN75)

  hint = "SW1: play  SW2/3: mode"
  lcd.text16(hint, (WIDTH - lcd.text16_width(hint)) // 2, 210, lcd.WHITE50)
  lcd.update()

def draw_result():
  # The result screen - mode name in the header, the outcome as large
  # text, and (for a normal result, not a failure) a bar chart of this
  # round's time next to a marker showing the best time so far.
  lcd.fill(lcd.BLACK)
  lcd.rect(0, 0, WIDTH, HEADER_H, lcd.BLUE50, True)
  title = MODE_NAMES[current_mode]
  lcd.text16(title, (WIDTH - lcd.text16_width(title)) // 2, 12, lcd.WHITE)

  if result_failed:
    lcd.text16(result_fail_message,
               (WIDTH - lcd.text16_width(result_fail_message)) // 2, 100, lcd.RED75)
  else:
    color = lcd.GREEN75 if result_was_new_best else lcd.CYAN75
    value_str = str(result_value) + " ms"
    lcd.text16(value_str, (WIDTH - lcd.text16_width(value_str)) // 2, 70, color)

    if result_was_new_best:
      best_str = "NEW BEST!"
      lcd.text16(best_str, (WIDTH - lcd.text16_width(best_str)) // 2, 100, lcd.YELLOW75)

    # Bar chart: filled portion shows this round's time, scaled so a
    # time at or above MAX_BAR_MS fills the whole bar. This is the
    # same "multiply then divide" scaling used for PWM brightness in
    # Activity 10 and analog sensor thresholds throughout this
    # curriculum, applied here to a time value instead.
    capped_value = min(result_value, MAX_BAR_MS)
    bar_fill = capped_value * BAR_WIDTH // MAX_BAR_MS
    lcd.rect(BAR_X, BAR_Y, BAR_WIDTH, BAR_HEIGHT, lcd.GREY)
    lcd.rect(BAR_X, BAR_Y, bar_fill, BAR_HEIGHT, color, True)

    # Best-time marker - skipped on the very first successful round of
    # a session, when no best has been set yet (still at its 999999
    # sentinel value).
    best_value = best_reaction_time if current_mode == MODE_SIMPLE else best_timing_error
    if best_value != 999999:
      capped_best = min(best_value, MAX_BAR_MS)
      best_x = BAR_X + capped_best * BAR_WIDTH // MAX_BAR_MS
      lcd.vline(best_x, BAR_Y - 6, BAR_HEIGHT + 12, lcd.YELLOW)

  hint = "SW1: again  SW4: menu"
  lcd.text16(hint, (WIDTH - lcd.text16_width(hint)) // 2, 210, lcd.WHITE50)
  lcd.update()


# --- Main Program ---------------------

beaper.nano_led_off()
all_choice_leds_off()
print("Reaction Time Game with LCD Display")
print("SW2/SW3: change mode   SW1: start / react   SW4: cancel")
print()

state_start = time.ticks_ms()
enter_state(STATE_MENU, state_start, "startup")
draw_menu()

while True:
  current_time = time.ticks_ms()
  elapsed      = time.ticks_diff(current_time, state_start)

  # --- Cancel (SW4) - checked before all state logic, except at the menu ---
  if beaper.SW4.value() == 0 and state != STATE_MENU and state != STATE_RESULT:
    all_choice_leds_off()
    beaper.nano_led_off()
    enter_state(STATE_MENU, current_time, "cancelled")
    draw_menu()

  # --- State: Menu ---
  elif state == STATE_MENU:
    sw2_current = beaper.SW2.value()
    sw3_current = beaper.SW3.value()
    if (sw2_current == 0 and sw2_last == 1) or (sw3_current == 0 and sw3_last == 1):
      current_mode = (current_mode + 1) % NUM_MODES
      print("Mode:", MODE_NAMES[current_mode])
      draw_menu()
    sw2_last = sw2_current
    sw3_last = sw3_current

    if beaper.SW1.value() == 0:
      start_round(current_time)

  # --- State: Waiting (SIMPLE mode - random delay before stimulus) ---
  elif state == STATE_WAITING:
    if beaper.SW1.value() == 0:
      # False start - reacted before the stimulus appeared.
      false_start = True
      enter_state(STATE_RESULT, current_time, "false start")
    elif elapsed >= wait_duration:
      REACT_LED.value(1)
      beaper.tone(880, 100)
      stimulus_time = current_time
      enter_state(STATE_REACT, current_time)

  # --- State: React (SIMPLE mode - stimulus is showing) ---
  elif state == STATE_REACT:
    if beaper.SW1.value() == 0:
      reaction_time = time.ticks_diff(current_time, stimulus_time)
      if reaction_time < best_reaction_time:
        best_reaction_time = reaction_time
      REACT_LED.value(0)
      enter_state(STATE_RESULT, current_time)

  # --- State: Chasing (TIMING mode) ---
  elif state == STATE_CHASING:
    if time.ticks_diff(current_time, last_chase_step) >= CHASE_INTERVAL_MS:
      CHASE_LEDS[chase_position].value(0)
      chase_position = (chase_position + 1) % 4
      CHASE_LEDS[chase_position].value(1)
      last_chase_step = current_time
      if chase_position == TARGET_POSITION:
        last_target_lit_time = current_time
        beaper.tone(660, 80)

    if beaper.SW1.value() == 0:
      timing_error = abs(time.ticks_diff(current_time, last_target_lit_time))
      if timing_error < best_timing_error:
        best_timing_error = timing_error
      all_choice_leds_off()
      enter_state(STATE_RESULT, current_time)

  # --- State: Result ---
  elif state == STATE_RESULT:
    if not result_shown:
      result_shown = True
      beaper.nano_led_off()

      if current_mode == MODE_SIMPLE and false_start:
        result_failed = True
        result_fail_message = "Too soon!"
        print("Too soon!")
        beaper.tone(220, 300)
      else:
        result_failed = False
        if current_mode == MODE_SIMPLE:
          result_value = reaction_time
          result_was_new_best = (reaction_time == best_reaction_time)
        else:
          result_value = timing_error
          result_was_new_best = (timing_error == best_timing_error)

        print(MODE_NAMES[current_mode], "result:", result_value, "ms",
              "(new best!)" if result_was_new_best else "")

        if result_was_new_best:
          beaper.tone(660, 100)
          time.sleep_ms(120)
          beaper.tone(880, 150)
        else:
          beaper.tone(440, 150)

      draw_result()

    if elapsed >= RESULT_DISPLAY_MS:
      if beaper.SW1.value() == 0:
        start_round(current_time)
      elif beaper.SW4.value() == 0:
        enter_state(STATE_MENU, current_time, "SW4 pressed")
        draw_menu()

  time.sleep_ms(LOOP_DELAY)
