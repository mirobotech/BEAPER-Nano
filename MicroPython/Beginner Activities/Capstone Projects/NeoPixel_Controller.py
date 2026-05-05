"""
================================================================================
Capstone Project: NeoPixel Display Controller [BEAPER_Nano-Capstone_NeoPixel.py]
May 4, 2026

Platform: mirobo.tech BEAPER Nano circuit (robot configuration with
  voltage regulator U1 and 74HCT541 buffer/level shifter U2 is needed
  to run short 5V NeoPixel sticks or rings)
Requires: BEAPER_Nano.py board module file.

Hardware used:
    SW2        - Cycle parameter up within the current mode (hold to repeat)
    SW3        - Previous animation mode (cycles backward)
    SW4        - Next animation mode (cycles forward)
    SW5        - Toggle strip on/off (remembers the last active mode)
    LS1        - Piezo speaker (mode-change confirmation beep)
    On-board LED - On while a mode is active

    NeoPixel strip (data input connects to PIXEL_PIN - see strip setup, below)

--------------------------------------------------------------------------------
* Connecting a large NeoPixel strip *

WARNING: A 60 LED strip at full brightness draws up to 3.6A (60ma
  per pixel at white). Connect the strip's power and GND directly
  to an external 5V power supply rated for at least 10% more than
  the highest expected current. Connect the BEAPER Nano GND to
  the external power supply GND (shared ground), and run the data
  wire from the BEAPER Nano to the Din pin on the strip.

* Connecting short NeoPixel sticks, rings, or strips *

5V WS2812B or SK6812 LEDs:
  Power BEAPER Nano with an external power supply (6-12V) connected
  to screw terminal CON1. Up to 30 WS2812B LEDs can be connected
  to 5V output header H5 (GPIO 11) and used at low brightness
  (MAX_BRIGHTNESS = 32 or less).

3.3V SK6812 LEDs only:
  Up to 10 SK6812 LEDs can be connected using the 3.3V side of
  header H1 (also GPIO 11). H1 and H5 share the same GPIO pin on
  the BEAPER Nano, so the data connection is identical for both
  strip types - only the strip's supply voltage differs.
    
--------------------------------------------------------------------------------
Animation modes (selected with SW3 / SW4):
    OFF      - Strip dark. SW5 toggles between OFF and the last active mode.
    SOLID    - All pixels set to a single colour.
               SW2: step hue by 10 degrees.
    CHASE    - One lit pixel travels along the strip.
               SW2: cycle speed (pixels per frame).
    THEATRE  - Every third pixel lit, pattern advances each frame.
               SW2: cycle advance rate.
    RAINBOW  - Full spectrum gradient slowly rotates along the strip.
               SW2: cycle rotation speed.
    PULSE    - All pixels fade in and out; hue advances each cycle.
               SW2: step hue by 10 degrees.
--------------------------------------------------------------------------------
Before you begin - complete your capstone plan:
    1. Write a plain-English description from the viewer's perspective.
    2. List all modes, what each displays, and what SW2 adjusts.
    3. Draw the state diagram showing mode transitions and the OFF state.
    4. List all constants and variables you will need.
    5. Write your testing plan - verify each step before moving to the next.
================================================================================
"""
# IMPORTANT: Copy BEAPER_Nano.py into your Arduino Nano ESP32
import BEAPER_Nano as beaper

import time
import neopixel
from machine import Pin

# =============================================================================
# Strip configuration - set these to match your hardware
# =============================================================================

NUM_LEDS       = 30           # Number of pixels in your strip.

MAX_BRIGHTNESS = 32           # Global brightness cap (0-255).
                              # 32 is safe for USB power with a short strip.
                              # Raise toward 255 only with an external supply.

# Strip type: "RGB" for WS2812B (3-byte), "RGBW" for SK6812 (4-byte).
STRIP_TYPE = "RGB"            # Change to "RGBW" for SK6812 strips.

# Data pin: H5 (GPIO 11) for WS2812B (5V header).
#           H1 (GPIO 11) for SK6812  (3.3V header).
# H1 and H5 share GPIO 11 on the BEAPER Nano, so PIXEL_PIN is the same
# for both strip types. Only the strip supply voltage differs.
# NOTE: GPIO 11 is also used by the QWIIC I2C bus (SDA). Creating the
# NeoPixel object on this pin reclaims it from I2C - QWIIC will be
# unavailable while the NeoPixel strip is in use.
PIXEL_PIN = Pin(beaper.H5_PIN, Pin.OUT)

# NeoPixel strip object.
# bpp=3 for RGB (WS2812B), bpp=4 for RGBW (SK6812).
# Change bpp=3 to bpp=4 when switching to SK6812.
strip = neopixel.NeoPixel(PIXEL_PIN, NUM_LEDS, bpp=3)

# How the strip object works - read this before writing any animation code!
#
# Writing strip[i] = (r, g, b) stores the red, green, and blue colour
# data for pixel i in memory, but does not change the LED immediately.
# (For RGBW strips, use strip[i] = (r, g, b, w) to store the red, green,
# blue, and white colour data for each pixel.)
# Calling strip.write() sends the stored pixel data to all of the LEDs
# in the strip at once. This is known as a buffered output model.
#
# This means your pogram should:
#
# 1. Call strip.write() to update the LEDs after setting pixel values.
#    (Forgetting strip.write() is the most common mistake when working
#    with NeoPixels.)
#
# 2. Call strip.write() once at the end of a loop, instead of during
#    every loop, when setting multiple pixels in a loop. (Calling
#    strip.write() inside the loop works but will be much slower, since
#    the full strip data would be sent to the LEDs after every step.)
#
# Reading strip[i] returns the colour tuple that is currently stored for
# pixel i. This is useful when you need to know the current colour of a
# pixel, for example when dimming a tail in the COMET extension.


# =============================================================================
# Mode constants
# =============================================================================

MODE_OFF     = const(0)  # Strip dark - starting state
MODE_SOLID   = const(1)  # All pixels one colour
MODE_CHASE   = const(2)  # Single pixel travelling along the strip
MODE_THEATRE = const(3)  # Every third pixel lit, pattern advances
MODE_RAINBOW = const(4)  # Full spectrum gradient rotating along the strip
MODE_PULSE   = const(5)  # All pixels fading in and out

NUM_MODES = const(6)

MODE_NAMES = {
  MODE_OFF:     "OFF",
  MODE_SOLID:   "SOLID",
  MODE_CHASE:   "CHASE",
  MODE_THEATRE: "THEATRE",
  MODE_RAINBOW: "RAINBOW",
  MODE_PULSE:   "PULSE",
}

# =============================================================================
# Timing constants
# =============================================================================

LOOP_DELAY      = const(1)    # Main loop delay (ms) - keeps loop responsive
FRAME_INTERVAL  = const(20)   # Animation frame update interval (ms) - 50 fps
ADJUST_FIRST    = const(500)  # Delay before SW2 auto-repeat begins (ms)
ADJUST_REPEAT   = const(80)   # Auto-repeat interval while SW2 is held (ms)

# =============================================================================
# Animation parameter defaults
# (Each mode has one SW2-adjustable parameter - see the main loop.)
# =============================================================================

DEFAULT_HUE          = 0    # Starting hue for SOLID, CHASE, PULSE (0-359 deg)
DEFAULT_CHASE_SPEED  = 1    # Pixels advanced per frame in CHASE (1-20)
DEFAULT_THEATRE_RATE = 3    # Frames between THEATRE advances (1-20)
DEFAULT_RAINBOW_SPEED= 2    # Hue degrees advanced per frame in RAINBOW (1-20)

# =============================================================================
# Program variables
# =============================================================================

mode         = MODE_OFF
mode_changed = True          # Forces a display update on the first frame

# --- SOLID / PULSE hue ---
hue = DEFAULT_HUE            # Current hue (0-359 degrees)

# --- CHASE ---
chase_pos   = 0              # Current lit pixel position (0 to NUM_LEDS-1)
chase_speed = DEFAULT_CHASE_SPEED

# --- THEATRE ---
theatre_offset = 0           # Which pixel in the group-of-3 is currently lit
theatre_rate   = DEFAULT_THEATRE_RATE
theatre_frames = 0           # Counts frames since the last advance

# --- RAINBOW ---
rainbow_offset = 0           # Hue offset that rotates the gradient along the strip
rainbow_speed  = DEFAULT_RAINBOW_SPEED

# --- PULSE ---
pulse_bright = 0             # Current brightness (0 to MAX_BRIGHTNESS)
pulse_up     = True          # True while brightness is increasing

# --- Timing ---
last_frame_time = 0

# --- SW2 hold-and-repeat (Activity 11 pattern) ---
sw2_held        = False
sw2_held_start  = 0
sw2_last_repeat = 0

# --- SW3/SW4/SW5 edge detection ---
sw3_last = 1
sw4_last = 1
sw5_last = 1

# --- SW5 toggle state ---
last_active_mode = MODE_SOLID    # Mode to return to when SW5 turns the strip on


# =============================================================================
# Helper functions
# =============================================================================

def hsv_to_rgb(h, s, v):
  # Convert a colour from HSV to an (R, G, B) tuple.
  # h: hue 0-359 degrees
  # s: saturation 0-100 (0 = grey, 100 = fully saturated)
  # v: value (brightness) 0-100 (0 = black, 100 = full brightness)
  # Returns (r, g, b) with each component in the range 0-255.
  #
  # Why HSV instead of RGB?
  # In RGB, colours are described as amounts of red, green, and blue
  # light. To smoothly cycle through the spectrum in RGB you would need
  # to change all three components simultaneously in a complex pattern.
  # HSV describes colours as a position on a colour wheel using:
  #  - Hue - the colour, where each colour is represented by its
  #    angle in degrees around a circle. (red is hue=0, green is hue=120,
  #    and blue is hue=240)
  #  - Saturation - how vivid the colour is from 0 (no colour) to 100
  #    (full colour).
  #  - Value - how bright the colour is from 0 (black) to 100 (bright)
  # Using HSV, cycling hue from 0 to 359 displays every colour in the
  # spectrum - red, orange, yellow, green, cyan, blue, violet, and back
  # to red - without touching saturation or brightness. This makes smooth
  # colour animations easier than triying to simultaneously adjust
  # individual RGB values up and down to mix colours.
  if s == 0:
    c = int(v * 255 / 100)
    return (c, c, c)
  s /= 100.0
  v /= 100.0
  i = int(h / 60) % 6
  f = (h / 60) - int(h / 60)
  p = int(v * (1 - s) * 255)
  q = int(v * (1 - f * s) * 255)
  t = int(v * (1 - (1 - f) * s) * 255)
  v = int(v * 255)
  if i == 0: return (v, t, p)
  if i == 1: return (q, v, p)
  if i == 2: return (p, v, t)
  if i == 3: return (p, q, v)
  if i == 4: return (t, p, v)
  return (v, p, q)


def scale_colour(r, g, b, brightness):
  # Scale an RGB colour by a brightness factor (0-255).
  # brightness=255 returns the colour unchanged.
  # brightness=128 returns half-brightness.
  # brightness=0   returns black.
  #
  # This is used to apply MAX_BRIGHTNESS globally - all colour math
  # uses full 0-255 values, and scale_colour() dims them at the end.
  factor = brightness / 255
  return (int(r * factor), int(g * factor), int(b * factor))


def make_pixel(r, g, b):
  # Build a pixel value tuple for the current strip type.
  # For RGB strips  (STRIP_TYPE = "RGB"):  returns (r, g, b)
  # For RGBW strips (STRIP_TYPE = "RGBW"): returns (r, g, b, 0)
  #
  # Using make_pixel() throughout means all animation code works with
  # both strip types without any other changes.
  if STRIP_TYPE == "RGBW":
    return (r, g, b, 0)
  return (r, g, b)


def fill_strip(r, g, b):
  # Set every pixel on the strip to (r, g, b) and push to hardware.
  for i in range(NUM_LEDS):
    strip[i] = make_pixel(r, g, b)
  strip.write()


def clear_strip():
  # Turn off all pixels.
  fill_strip(0, 0, 0)


def enter_mode(new_mode):
  # Transition to a new mode.
  # Clears the strip, resets all animation counters, plays a
  # mode-specific confirmation tone, and prints the mode name.
  # This is the same enter_state() pattern from Activity 12.
  global mode, mode_changed
  global chase_pos, theatre_offset, theatre_frames
  global rainbow_offset, pulse_bright, pulse_up

  mode           = new_mode
  mode_changed   = True
  chase_pos      = 0
  theatre_offset = 0
  theatre_frames = 0
  rainbow_offset = 0
  pulse_bright   = 0
  pulse_up       = True

  clear_strip()

  if new_mode == MODE_OFF:
    beaper.nano_led_off()
    beaper.noTone()
  else:
    beaper.nano_led_on()
    beaper.tone(660 + new_mode * 80, 60)

  print("-->", MODE_NAMES[new_mode])


def check_sw2(current_time):
  # Read SW2 with the Activity 11 hold-and-repeat pattern.
  # Returns True if a parameter increment step is due this iteration,
  # False otherwise. Fires once on first press, then repeatedly after
  # ADJUST_FIRST ms with ADJUST_REPEAT ms between repeats.
  global sw2_held, sw2_held_start, sw2_last_repeat

  sw2_current = beaper.SW2.value()
  if sw2_current == 0:
    if not sw2_held:
      sw2_held        = True
      sw2_held_start  = current_time
      sw2_last_repeat = current_time
      return True
    elif (time.ticks_diff(current_time, sw2_held_start) >= ADJUST_FIRST and
              time.ticks_diff(current_time, sw2_last_repeat) >= ADJUST_REPEAT):
      sw2_last_repeat = current_time
      return True
  else:
    sw2_held = False
  return False


# =============================================================================
# Startup
# =============================================================================

clear_strip()
beaper.nano_led_off()
print("NeoPixel Display Controller")
print("Strip type:", STRIP_TYPE, " Pixels:", NUM_LEDS,
      " Max brightness:", MAX_BRIGHTNESS)
print("SW3/SW4: previous/next mode   SW2: adjust parameter   SW5: on/off")
print()

last_frame_time = time.ticks_ms()
enter_mode(MODE_OFF)


# =============================================================================
# Main loop
# =============================================================================

while True:
  current_time = time.ticks_ms()

  # ---- Button: SW3 - previous mode ------------------------------------
  sw3_current = beaper.SW3.value()
  if sw3_current == 0 and sw3_last == 1:
    if mode != MODE_OFF:
      enter_mode((mode - 1 - 1) % (NUM_MODES - 1) + 1)
  sw3_last = sw3_current

  # ---- Button: SW4 - next mode ----------------------------------------
  sw4_current = beaper.SW4.value()
  if sw4_current == 0 and sw4_last == 1:
    if mode != MODE_OFF:
      enter_mode(mode % (NUM_MODES - 1) + 1)
  sw4_last = sw4_current

  # ---- Button: SW5 - toggle strip on/off ------------------------------
  sw5_current = beaper.SW5.value()
  if sw5_current == 0 and sw5_last == 1:
    if mode == MODE_OFF:
      enter_mode(last_active_mode)   # Return to the last active mode
    else:
      last_active_mode = mode        # Remember current mode before turning off
      enter_mode(MODE_OFF)
  sw5_last = sw5_current

  # ---- SW2: cycle mode parameter (hold to repeat) ---------------------
  if check_sw2(current_time):
    if mode == MODE_SOLID or mode == MODE_PULSE:
      hue = (hue + 10) % 360
      print("    hue:", hue)
    elif mode == MODE_CHASE:
      chase_speed = chase_speed % 20 + 1   # Cycles 1->20->1
      print("    chase speed:", chase_speed, "pixels/frame")
    elif mode == MODE_THEATRE:
      theatre_rate = theatre_rate % 20 + 1  # Cycles 1->20->1
      print("    theatre rate:", theatre_rate, "frames/step")
    elif mode == MODE_RAINBOW:
      rainbow_speed = rainbow_speed % 20 + 1  # Cycles 1->20->1
      print("    rainbow speed:", rainbow_speed, "deg/frame")

  # ---- Animation frame (non-blocking, rate-limited by FRAME_INTERVAL) -
  if time.ticks_diff(current_time, last_frame_time) >= FRAME_INTERVAL:
    last_frame_time = current_time

    # ------------------------------------------------------------------
    # MODE_SOLID: all pixels set to a single colour.
    #
    # This mode is already complete and working - it shows how
    # hsv_to_rgb(), scale_colour(), and make_pixel() work together.
    # Read and understand this before implementing the other modes.
    # ------------------------------------------------------------------
    if mode == MODE_SOLID:
      r, g, b = scale_colour(*hsv_to_rgb(hue, 100, 100), MAX_BRIGHTNESS)
      fill_strip(r, g, b)

    # ------------------------------------------------------------------
    # MODE_CHASE: one lit pixel travels along the strip.
    #
    # Concept: strip[i] addresses a single pixel by index.
    # The lit pixel index is stored in chase_pos. Each frame:
    #   1. Clear the entire strip (all pixels off).
    #   2. Set strip[chase_pos] to the current colour.
    #   3. Call strip.write() to push the change to the hardware.
    #   4. Advance chase_pos by chase_speed.
    #      Use % NUM_LEDS to wrap back to 0 after the last pixel.
    #
    # TODO: implement MODE_CHASE using the steps above.
    # ------------------------------------------------------------------
    elif mode == MODE_CHASE:
      pass

    # ------------------------------------------------------------------
    # MODE_THEATRE: every third pixel is lit and the pattern advances.
    #
    # Concept: the modulo operator % tests whether a number is a
    # multiple of another. (i % 3 == 0) is True for i = 0, 3, 6, 9...
    # Adding theatre_offset shifts which pixels are lit:
    #   offset=0: pixels 0, 3, 6, 9...  are lit
    #   offset=1: pixels 1, 4, 7, 10... are lit
    #   offset=2: pixels 2, 5, 8, 11... are lit
    #
    # Each frame, count up theatre_frames. When theatre_frames reaches
    # theatre_rate, reset it to 0 and advance theatre_offset by 1
    # (wrapping at 3 with % 3). This controls how fast the pattern moves.
    #
    # TODO: use a for loop over range(NUM_LEDS). For each pixel i,
    #       set strip[i] to the colour if (i % 3 == theatre_offset),
    #       or to make_pixel(0, 0, 0) (off) otherwise. After the loop,
    #       call strip.write(). Then update theatre_frames and advance
    #       theatre_offset when theatre_frames reaches theatre_rate.
    # ------------------------------------------------------------------
    elif mode == MODE_THEATRE:
      pass

    # ------------------------------------------------------------------
    # MODE_RAINBOW: a full colour spectrum is spread across the strip
    # and the gradient slowly rotates.
    #
    # Concept: each pixel is assigned a hue based on its position.
    # Pixel i gets the hue: (rainbow_offset + i * 360 // NUM_LEDS) % 360
    # This spreads 360 degrees of hue evenly across NUM_LEDS pixels.
    # Adding rainbow_offset (which increases each frame) rotates the
    # gradient along the strip.
    #
    # Why // instead of /? The expression i * 360 // NUM_LEDS uses
    # integer division to produce a whole-number hue value. Regular
    # division would give a float, which hsv_to_rgb() also handles
    # but integer arithmetic is faster on a microcontroller.
    #
    # TODO: use a for loop over range(NUM_LEDS). For each pixel i,
    #       calculate pixel_hue using the formula above, convert it
    #       to a scaled colour using hsv_to_rgb() and scale_colour(),
    #       and assign it to strip[i] via make_pixel(). After the loop,
    #       call strip.write(). Then advance rainbow_offset by
    #       rainbow_speed, wrapping at 360 with % 360.
    # ------------------------------------------------------------------
    elif mode == MODE_RAINBOW:
      pass

    # ------------------------------------------------------------------
    # MODE_PULSE: all pixels fade in and out together, and the hue
    # advances at the start of each new cycle.
    #
    # Concept: pulse_bright ramps from 0 up to MAX_BRIGHTNESS then
    # back down to 0. pulse_up tracks the direction (True = going up).
    # Each frame, fill the strip with hue at the current pulse_bright.
    # Note: use pulse_bright directly as the brightness argument to
    # scale_colour() - not MAX_BRIGHTNESS - because pulse_bright IS
    # the brightness for this mode.
    #
    # When pulse_bright reaches MAX_BRIGHTNESS, set pulse_up to False.
    # When pulse_bright reaches 0 going down, set pulse_up to True and
    # advance the hue by 30 degrees so each pulse is a different colour.
    #
    # TODO: implement MODE_PULSE using the description above.
    # Hint: the update logic looks like this:
    #   if pulse_up:
    #       pulse_bright = min(pulse_bright + PULSE_STEP, MAX_BRIGHTNESS)
    #       if pulse_bright == MAX_BRIGHTNESS: pulse_up = False
    #   else:
    #       pulse_bright = max(pulse_bright - PULSE_STEP, 0)
    #       if pulse_bright == 0:
    #           pulse_up = True
    #           hue = (hue + 30) % 360
    #
    # Add PULSE_STEP = 2 to the constants section above.
    # ------------------------------------------------------------------
    elif mode == MODE_PULSE:
      pass

  time.sleep_ms(LOOP_DELAY)


"""
Capstone Development Guide

Work through these steps in order. Complete and test each step before
moving to the next. Start with a short strip (8-10 LEDs) at low
brightness while the circuit is USB-powered.

Step 1 - Hardware setup and first pixel
    Wire the strip: data input to PIXEL_PIN, strip GND to BEAPER Nano
    GND, strip power to an external supply (or USB for a short test strip).
    Before any animation code, verify the connection by temporarily adding
    these lines before the main loop:

        strip[0] = make_pixel(32, 0, 0)   # Red at low brightness
        strip.write()
        # Stop here to verify

    If the first pixel does not light, check the data line connection,
    power, and shared ground. If the pixel shows the wrong colour, the
    strip may have a different colour order (GRB vs RGB). WS2812B and
    SK6812 strips both typically use GRB ordering but MicroPython's
    neopixel driver handles this internally with the standard RGB tuple.

    For SK6812 strips, make sure STRIP_TYPE = "RGBW" and bpp=4 in the
    NeoPixel() constructor before testing. Connect data to H1, not H5.

Step 2 - Verify hsv_to_rgb()
    The hsv_to_rgb() function converts a colour described in HSV (hue,
    saturation, value) into the (R, G, B) tuple that the strip expects.
    Read the explanation in the function's comment block above to
    understand why HSV is used here before testing it.

    To test the function in the MicroPython REPL, you need to paste the
    function definition in first, since the REPL doesn't have access to
    functions defined in a file that isn't running. Copy the entire
    hsv_to_rgb() function (from 'def hsv_to_rgb' down to and including
    the last 'return' line) and paste it into the REPL, then press
    Enter to confirm the definition. Then test with known values:

        print(hsv_to_rgb(0,   100, 100))  # (255, 0, 0)   red
        print(hsv_to_rgb(120, 100, 100))  # (0, 255, 0)   green
        print(hsv_to_rgb(240, 100, 100))  # (0, 0, 255)   blue
        print(hsv_to_rgb(60,  100, 100))  # (255, 255, 0) yellow
        print(hsv_to_rgb(0,   0,   100))  # (255, 255, 255) white (s=0)

    Notice that the last test uses s=0 (no saturation), which produces
    white regardless of the hue value. This is because when saturation
    is 0, there is no colour - only brightness.

    If any result is wrong, check the function logic before continuing.
    Correct colour output here is essential for every mode that follows.

Step 3 - Verify scale_colour() and make_pixel()
    Paste the scale_colour() and make_pixel() function definitions into
    the REPL the same way you pasted hsv_to_rgb() in Step 2. Then test:

        print(scale_colour(255, 0, 0, 255))   # (255, 0, 0) unchanged
        print(scale_colour(255, 0, 0, 128))   # (127, 0, 0) half brightness
        print(scale_colour(255, 0, 0, 32))    # (32, 0, 0)  low brightness
        print(scale_colour(255, 0, 0, 0))     # (0, 0, 0)   black

    scale_colour() works by multiplying each component by brightness/255.
    At brightness=255 the factor is 1.0 (unchanged). At brightness=128
    the factor is 0.5 (half). At brightness=0 the factor is 0 (black).
    This is why all colour calculations in this program use full 0-255
    values - scale_colour() applies the global MAX_BRIGHTNESS cap at the
    end, just before the colour is sent to the strip.

    You will also need STRIP_TYPE to be defined before make_pixel() will
    work in the REPL. Type this first, then paste make_pixel():

        STRIP_TYPE = "RGB"

    Then test make_pixel():

        print(make_pixel(255, 0, 0))          # (255, 0, 0) for RGB strips

    Change STRIP_TYPE = "RGBW" and repeat - make_pixel() should now
    return (255, 0, 0, 0), adding the white channel byte automatically.
    Change STRIP_TYPE back to "RGB" when done.

    Understanding these three functions is the key to all modes. Every
    animation follows the same pattern:
        1. Choose a hue (or calculate one from pixel position)
        2. Convert to RGB:  r, g, b = hsv_to_rgb(hue, 100, 100)
        3. Apply brightness: r, g, b = scale_colour(r, g, b, MAX_BRIGHTNESS)
        4. Format for strip: strip[i] = make_pixel(r, g, b)
        5. Send to hardware: strip.write()

Step 4 - SOLID mode (reference implementation)
    SOLID is already complete and working. Run the program, press SW5
    to turn the strip on, then press SW4 to enter SOLID mode. Confirm
    the strip lights at a single colour. Press SW2 to step through hue
    changes in 10-degree increments. Hold SW2 and confirm auto-repeat
    kicks in after 500 ms.

    Read the SOLID code carefully before continuing:

        r, g, b = scale_colour(*hsv_to_rgb(hue, 100, 100), MAX_BRIGHTNESS)
        fill_strip(r, g, b)

    This single line does steps 1-3 from the pattern in Step 3 above.
    Breaking it apart to understand it:

        (r_full, g_full, b_full) = hsv_to_rgb(hue, 100, 100)

    hsv_to_rgb() returns a tuple of three values. Normally you would
    pass those three values individually to scale_colour(). The * operator
    (called 'splat' or 'unpack') expands a tuple into separate arguments
    automatically, so:

        scale_colour(*hsv_to_rgb(hue, 100, 100), MAX_BRIGHTNESS)

    is exactly the same as:

        r_full, g_full, b_full = hsv_to_rgb(hue, 100, 100)
        scale_colour(r_full, g_full, b_full, MAX_BRIGHTNESS)

    The result - the dimmed (r, g, b) tuple - is then unpacked into the
    three variables r, g, b on the left side of the assignment, ready to
    pass to fill_strip(). This is a compact but common Python pattern.
    Look for it in the modes you implement - you will use it in every one.

Step 5 - CHASE mode
    Implement MODE_CHASE following the TODO comment.

    Key ideas:
    - strip[i] = make_pixel(r, g, b) writes to a single pixel at index i.
    - clear_strip() sets every pixel to make_pixel(0, 0, 0) and writes.
    - chase_pos % NUM_LEDS wraps the position back to 0 after the last
      pixel, producing smooth continuous motion.

    Test by pressing SW4 twice from SOLID to reach CHASE (SOLID -> CHASE).
    The single lit pixel should travel smoothly from pixel 0 to the last
    pixel and wrap back to 0. Press SW2 and confirm the speed changes.

    Question: what happens if you remove the clear_strip() call? Try it.
    Why does the strip need to be cleared on every frame for CHASE?

Step 6 - THEATRE mode
    Implement MODE_THEATRE following the TODO comment.

    Key ideas:
    - (i % 3 == theatre_offset) is True for every third pixel starting
      at theatre_offset. This is the same modulo operator (%) from the
      counted loop activities.
    - theatre_frames counts how many animation frames have elapsed since
      the last pattern advance. When it reaches theatre_rate, reset it to
      0 and advance theatre_offset by 1 (% 3).
    - Setting theatre_rate = 1 makes the pattern advance every frame.
      Setting it higher slows the advance.

    Test by pressing SW4 once from CHASE to reach THEATRE. You should see
    three evenly-spaced lit pixels. Press SW2 to change the advance
    rate. At rate=1 the pattern moves quickly; at rate=20 it moves slowly.

    Question: change (i % 3 == theatre_offset) to (i % 4 == theatre_offset)
    and update the theatre_offset wrap from % 3 to % 4. What changes in
    the appearance? Restore to % 3 when done.

Step 7 - RAINBOW mode
    Implement MODE_RAINBOW following the TODO comment.

    Key ideas:
    - i * 360 // NUM_LEDS spreads the full colour spectrum (0-360 degrees)
      evenly across the strip. Pixel 0 gets hue 0, the middle pixel gets
      hue ~180, the last pixel gets hue close to 360.
    - Adding rainbow_offset to every pixel's hue shifts the gradient along
      the strip. Incrementing rainbow_offset each frame makes it rotate.
    - % 360 keeps the hue in the valid range as the offset grows.

    Test: the strip should show a smooth continuous spectrum from red
    through green, blue, and back to red. Pressing SW2 should increase
    the rotation speed. Pressing SW3 should cycle back to THEATRE.

    Question: what would happen if you multiplied rainbow_offset by -1
    before applying it? Try it. What does a negative speed feel like?

Step 8 - PULSE mode
    Implement MODE_PULSE following the TODO comment.

    Key ideas:
    - pulse_bright is used directly as the brightness argument, not
      MAX_BRIGHTNESS. This is the key difference from SOLID, where the
      brightness is fixed at MAX_BRIGHTNESS.
    - The ramp uses min() and max() to clamp pulse_bright within
      [0, MAX_BRIGHTNESS] rather than checking with if/elif. Both
      approaches work - min/max is more concise.
    - The hue advances by 30 degrees at the bottom of each cycle so each
      pulse is a slightly different colour.

    Test: the strip should fade smoothly from black to full brightness and
    back to black. Confirm true black is reached at the bottom (not just
    very dim). Confirm the hue shifts slightly with each new cycle.

Step 9 - Full integration
    Cycle through all modes with SW3 and SW4. Check:
    - Each mode produces the expected animation
    - SW2 adjusts the correct parameter in each mode (with hold-and-repeat)
    - SW3 cycles backward (CHASE -> SOLID -> PULSE -> RAINBOW -> ...)
    - SW5 turns the strip off and back on, returning to the last mode
    - The strip clears cleanly when entering each new mode
    - The confirmation beep fires once per mode press (not while holding)

    Open the serial monitor and confirm state transition messages print
    correctly and that parameter adjustments print with the right values.

Step 10 - RGBW strips (SK6812)
    To use an SK6812 RGBW strip instead of a WS2812B:

    1. Change STRIP_TYPE = "RGB" to STRIP_TYPE = "RGBW"
    2. Change bpp=3 to bpp=4 in the NeoPixel() constructor
    3. The data pin does not change: H1 and H5 share GPIO 11 on the
       BEAPER Nano. Connect the SK6812 data input to the H1 header
       (3.3V side) instead of H5 (5V side) - same pin, different voltage
    4. Connect the strip data input to H1 instead of H5

    The make_pixel() function handles the rest: it automatically adds
    a fourth white channel byte (set to 0) when STRIP_TYPE = "RGBW".
    All four modes will work without any other changes.

    To use the white channel deliberately, modify make_pixel() or
    add a separate white_level variable:

        def make_pixel(r, g, b, w=0):
            if STRIP_TYPE == "RGBW":
                return (r, g, b, w)
            return (r, g, b)

    Experiment: in SOLID mode, set the white channel to a low value
    (e.g. w=32) while keeping the colour channels non-zero. Compare the
    appearance to pure-colour output. White channel light tends to look
    "warmer" and more neutral than mixing white from RGB.

Extensions

    a) PULSE_STEP control: right now PULSE_STEP is a constant you define.
       Add it as a SW2 parameter in MODE_PULSE so students can adjust
       how fast the pulse ramps. What range of values produces smooth fades
       vs. harsh flashing?

    b) COMET effect: modify CHASE to draw a short fading tail behind the
       lit pixel. Each frame, instead of clearing the whole strip, dim every
       pixel by multiplying its current colour components by a factor < 1
       (e.g. 0.7). Then set the head pixel to full brightness. You will need
       to read back strip[i] to dim it - strip[i] returns the current tuple.
       How does the tail length change with the fade factor?

    c) THEATRE colour gradient: instead of all lit pixels being the same
       hue, assign each lit pixel a hue based on its position (similar to
       RAINBOW). The pattern should still advance each frame. How does this
       change the appearance of the animation?

    d) Beat-reactive brightness: read an analog input (e.g. beaper.RV1_level()
       with JP2=Enviro., or an external microphone on H1) and map the reading
       to MAX_BRIGHTNESS using map_range(). This makes the strip brightness
       respond to the potentiometer or to sound. Which mode looks best with
       a changing brightness?

    e) White channel mood lamp: for SK6812 strips only. Create a new mode
       that ignores the colour channels and uses only the white channel,
       slowly pulsing between warm-white and off. Compare the light quality
       to the PULSE mode running in white (hue=0, saturation=0).

    f) Star Wars light saber: press a button to grow the 'blade' from the
       hilt, and then shimmer the brightness. Pressing the button again
       shrinks the blade back down into the hilt. Use another button to
       change or cycle the colour of the light saber blade.


"""