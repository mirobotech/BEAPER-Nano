# ================================================================================
# Reach-Ahead: WiFi NeoPixel Controller [NeoPixel_Controller_WiFi.py]
# Version: 1.1
# Updated: July 25, 2026
#
# Platform: mirobo.tech BEAPER Nano circuit (robot configuration with
#   voltage regulator U1 and 74HCT541 buffer/level shifter U2 is needed
#   to run short 5V NeoPixel sticks or rings)
# Requires: BEAPER_Nano.py, colour.py
#
# A preview of what WiFi can add to a program you already know well -
# this is a complete, working version of the NeoPixel Controller
# capstone (with all of its modes filled in as a reference), plus a
# second way to control it: a web page served directly from the
# BEAPER Nano itself. Connect a phone or laptop to the BEAPER Nano's
# own WiFi network, open a web browser, and control the strip from
# there - at the same time as the physical buttons, which keep
# working exactly as before.
#
# This program creates its own WiFi network (an "access point") -
# there is no need for an existing WiFi router, a network password
# you don't know, or an internet connection. The BEAPER Nano's
# built-in ESP32-S3 WiFi radio does all of this without any extra
# hardware. A future intermediate-course activity covers networking
# in depth (addresses, HTTP, sockets); this program does not attempt
# to teach that - it uses a handful of new functions (network.WLAN,
# socket) as tools, the same way you already use tone() or
# time.sleep_ms(), to show what becomes possible once your board can
# talk to other devices wirelessly.
#
# Hardware used:
#   SW2        - Cycle parameter up within the current mode (hold to repeat)
#   SW3        - Previous animation mode (cycles backward)
#   SW4        - Next animation mode (cycles forward)
#   SW5        - Toggle strip on/off (remembers the last active mode)
#   LS1        - Piezo speaker (mode-change confirmation beep)
#   On-board LED - On while a mode is active
#
#   NeoPixel strip (data input connects to PIXEL_PIN - see strip setup, below)
#
# --------------------------------------------------------------------------------
# Connecting to the web interface:
#
#   1. Run this program. Watch the Serial Monitor for a line like:
#        Connect to WiFi network: BEAPER-NeoPixel  (password: beaper123)
#        Then browse to: http://192.168.4.1/
#   2. On your phone or laptop, open WiFi settings and connect to the
#      "BEAPER-NeoPixel" network using the password shown.
#   3. Open a web browser and go to the address shown. You do not
#      need an internet connection - you are connecting directly to
#      the BEAPER Nano.
#   4. Tap a mode link to switch modes. Once a mode is active, drag
#      the slider to adjust that mode's parameter (hue for SOLID and
#      PULSE, speed or rate for the others) - this offers smoother,
#      direct control than SW2's one-step-at-a-time button press, and
#      either control method can be used at any time, even switching
#      back and forth.
#
# --------------------------------------------------------------------------------
# * Connecting a large NeoPixel strip *
#
# WARNING: A 60 LED strip at full brightness draws up to 3.6A (60ma
#   per pixel at white). Connect the strip's power and GND directly
#   to an external 5V power supply rated for at least 10% more than
#   the highest expected current. Connect the BEAPER Nano GND to
#   the external power supply GND (shared ground), and run the data
#   wire from the BEAPER Nano to the Din pin on the strip.
#
# * Connecting short NeoPixel sticks, rings, or strips *
#
# 5V WS2812B or SK6812 LEDs:
#   Power BEAPER Nano with an external power supply (6-12V) connected
#   to screw terminal CON1. Up to 30 WS2812B LEDs can be connected
#   to 5V output header H5 (GPIO 11) and used at low brightness
#   (MAX_BRIGHTNESS = 32 or less).
#
# 3.3V SK6812 LEDs only:
#   Up to 10 SK6812 LEDs can be connected using the 3.3V side of
#   header H1 (also GPIO 11). H1 and H5 share the same GPIO pin on
#   the BEAPER Nano, so the data connection is identical for both
#   strip types - only the strip's supply voltage differs.
#
# --------------------------------------------------------------------------------
# Animation modes (selected with SW3/SW4 or the web page):
#   OFF      - Strip dark. SW5 toggles between OFF and the last active mode.
#   SOLID    - All pixels set to a single colour.
#   CHASE    - One lit pixel travels along the strip.
#   THEATRE  - Every third pixel lit, pattern advances each frame.
#   RAINBOW  - Full spectrum gradient slowly rotates along the strip.
#   PULSE    - All pixels fade in and out; hue advances each cycle.
# ================================================================================

# IMPORTANT: Copy BEAPER_Nano.py and colour.py into your Arduino Nano ESP32.
import BEAPER_Nano as beaper  # Set up BEAPER Nano I/O
import colour                 # HSV-to-RGB colour conversion - see colour.py

import time
import neopixel
from machine import Pin
import network
import socket

# =============================================================================
# Strip configuration - set these to match your hardware
# =============================================================================

NUM_LEDS       = 30           # Number of pixels in your strip.
MAX_BRIGHTNESS = 32           # Global brightness cap (0-255).
STRIP_TYPE     = "RGB"        # "RGB" for WS2812B, "RGBW" for SK6812.
PIXEL_PIN      = Pin(beaper.H5_PIN, Pin.OUT)
strip = neopixel.NeoPixel(PIXEL_PIN, NUM_LEDS, bpp=3)

# =============================================================================
# WiFi Access Point configuration
# =============================================================================

AP_SSID     = "BEAPER-NeoPixel"
AP_PASSWORD = "beaper123"            # Must be at least 8 characters for WPA2
AP_IP       = "192.168.4.1"          # Fixed address, so it's always the same
                                      # regardless of what the board would
                                      # otherwise pick on its own.

# =============================================================================
# Mode constants
# =============================================================================

MODE_OFF     = const(0)
MODE_SOLID   = const(1)
MODE_CHASE   = const(2)
MODE_THEATRE = const(3)
MODE_RAINBOW = const(4)
MODE_PULSE   = const(5)

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

LOOP_DELAY      = const(1)
FRAME_INTERVAL  = const(20)
ADJUST_FIRST    = const(500)
ADJUST_REPEAT   = const(80)

# =============================================================================
# Animation parameter defaults
# =============================================================================

DEFAULT_HUE           = 0
DEFAULT_CHASE_SPEED   = 1
DEFAULT_THEATRE_RATE  = 3
DEFAULT_RAINBOW_SPEED = 2
PULSE_STEP            = 2

# =============================================================================
# Program variables
# =============================================================================

mode = MODE_OFF

hue = DEFAULT_HUE

chase_pos   = 0
chase_speed = DEFAULT_CHASE_SPEED

theatre_offset = 0
theatre_rate   = DEFAULT_THEATRE_RATE
theatre_frames = 0

rainbow_offset = 0
rainbow_speed  = DEFAULT_RAINBOW_SPEED

pulse_bright = 0
pulse_up     = True

last_frame_time = 0

sw2_held        = False
sw2_held_start  = 0
sw2_last_repeat = 0

sw3_last = 1
sw4_last = 1
sw5_last = 1

last_active_mode = MODE_SOLID


# =============================================================================
# Web page template
# =============================================================================
# {{ }} in a .format() template means a literal { or } in the output -
# needed here for the CSS and JavaScript blocks, which use real curly
# braces of their own. {mode_name} and {slider_section} are the actual
# placeholders, filled in fresh on every request.

PAGE = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>NeoPixel Controller</title>
<style>
  body {{ font-family: sans-serif; text-align: center; margin-top: 30px;
          background: #222; color: #eee; }}
  input[type=range] {{ width: 80%; }}
  a {{ color: #6cf; margin: 0 6px; text-decoration: none; }}
</style>
</head>
<body>
  <h2>BEAPER NeoPixel Controller</h2>
  <p style="font-size:1.2em;">Mode: {mode_name}</p>
  <p>
    <a href="/mode/off">Off</a> |
    <a href="/mode/solid">Solid</a> |
    <a href="/mode/chase">Chase</a> |
    <a href="/mode/theatre">Theatre</a> |
    <a href="/mode/rainbow">Rainbow</a> |
    <a href="/mode/pulse">Pulse</a>
  </p>
  {slider_section}
<script>
let updatePending = false;
function sendUpdate() {{
  // The slider fires "oninput" continuously while dragging. Waiting a
  // short moment between requests keeps the board's single-connection
  // web server from being overwhelmed by a flood of rapid updates.
  if (updatePending) return;
  updatePending = true;
  setTimeout(function() {{
    let value = document.getElementById('param').value;
    fetch(`/update?value=${{value}}`)
      .finally(function() {{ updatePending = false; }});
  }}, 100);
}}
</script>
</body>
</html>
"""

SLIDER = """<p>{label}</p>
  <input type="range" id="param" min="{min}" max="{max}" value="{value}" oninput="sendUpdate()">
"""


# =============================================================================
# Helper functions
# =============================================================================

def scale_colour(r, g, b, brightness):
  factor = brightness / 255
  return (int(r * factor), int(g * factor), int(b * factor))

def make_pixel(r, g, b):
  if STRIP_TYPE == "RGBW":
    return (r, g, b, 0)
  return (r, g, b)

def fill_strip(r, g, b):
  for i in range(NUM_LEDS):
    strip[i] = make_pixel(r, g, b)
  strip.write()

def clear_strip():
  fill_strip(0, 0, 0)

def enter_mode(new_mode):
  # Transition to a new mode. Both the physical buttons and the web
  # interface call this same function, so the two control methods
  # always stay in sync with each other.
  global mode, chase_pos, theatre_offset, theatre_frames
  global rainbow_offset, pulse_bright, pulse_up

  mode           = new_mode
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

def adjust_parameter():
  # Advance the current mode's adjustable parameter by one step - SW2's
  # (physical) behaviour. See set_parameter() for the web slider's
  # direct-set equivalent - both act on the same underlying variables.
  global hue, chase_speed, theatre_rate, rainbow_speed
  if mode == MODE_SOLID or mode == MODE_PULSE:
    hue = (hue + 10) % 360
    print("    hue:", hue)
  elif mode == MODE_CHASE:
    chase_speed = chase_speed % 20 + 1
    print("    chase speed:", chase_speed, "pixels/frame")
  elif mode == MODE_THEATRE:
    theatre_rate = theatre_rate % 20 + 1
    print("    theatre rate:", theatre_rate, "frames/step")
  elif mode == MODE_RAINBOW:
    rainbow_speed = rainbow_speed % 20 + 1
    print("    rainbow speed:", rainbow_speed, "deg/frame")

def set_parameter(value):
  # Directly set the current mode's adjustable parameter to a specific
  # value - the web slider's behaviour. Clamped to each parameter's
  # valid range, since the value arrives as text from the network and
  # should not be trusted to already be in range.
  global hue, chase_speed, theatre_rate, rainbow_speed
  if mode == MODE_SOLID or mode == MODE_PULSE:
    hue = value % 360
  elif mode == MODE_CHASE:
    chase_speed = max(1, min(20, value))
  elif mode == MODE_THEATRE:
    theatre_rate = max(1, min(20, value))
  elif mode == MODE_RAINBOW:
    rainbow_speed = max(1, min(20, value))

def check_sw2(current_time):
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
# WiFi and web server
# =============================================================================

def build_slider_section():
  # Build the slider block for the current mode, or an empty string
  # when the strip is off and there is nothing to adjust.
  if mode == MODE_OFF:
    return ""
  elif mode == MODE_SOLID or mode == MODE_PULSE:
    return SLIDER.format(label="Hue", min=0, max=359, value=hue)
  elif mode == MODE_CHASE:
    return SLIDER.format(label="Chase Speed", min=1, max=20, value=chase_speed)
  elif mode == MODE_THEATRE:
    return SLIDER.format(label="Theatre Rate", min=1, max=20, value=theatre_rate)
  elif mode == MODE_RAINBOW:
    return SLIDER.format(label="Rainbow Speed", min=1, max=20, value=rainbow_speed)
  return ""

def build_html():
  # Build the status page, reflecting whatever mode and parameter
  # value are currently active. Built fresh on every request, so it
  # always shows the current state - including changes made from the
  # physical buttons, not just from the web page itself.
  return PAGE.format(mode_name=MODE_NAMES[mode], slider_section=build_slider_section())

def parse_query(path):
  # Pull "key=value" pairs out of a request path like /update?value=180
  params = {}
  if "?" not in path:
    return params
  query = path.split("?", 1)[1]
  for pair in query.split("&"):
    if "=" in pair:
      key, value = pair.split("=", 1)
      params[key] = value
  return params

def handle_client(client):
  # A single request/response exchange with one connected browser.
  client.settimeout(2.0)
  try:
    stream = client.makefile('rwb', 0)
    request_line = stream.readline().decode()

    # Read and discard the remaining request headers, up to the blank
    # line that marks the end of the header block - properly draining
    # the request rather than assuming it all arrived in one recv().
    while True:
      header = stream.readline()
      if header in (b"\r\n", b""):
        break

    path = request_line.split(" ")[1]

    if path.startswith("/mode/"):
      requested = path.split("/mode/")[1]
      if requested == "off":
        enter_mode(MODE_OFF)
      elif requested == "solid":
        enter_mode(MODE_SOLID)
      elif requested == "chase":
        enter_mode(MODE_CHASE)
      elif requested == "theatre":
        enter_mode(MODE_THEATRE)
      elif requested == "rainbow":
        enter_mode(MODE_RAINBOW)
      elif requested == "pulse":
        enter_mode(MODE_PULSE)
      response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + build_html()

    elif path.startswith("/update"):
      params = parse_query(path)
      if "value" in params:
        set_parameter(int(params["value"]))
      response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nOK"

    else:
      response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + build_html()

    stream.write(response.encode())

  except (OSError, IndexError):
    pass  # Client disconnected, sent a malformed request, or timed out -
          # nothing more to do for this connection.

  finally:
    client.close()


# =============================================================================
# Startup
# =============================================================================

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=AP_SSID, password=AP_PASSWORD, authmode=network.AUTH_WPA2_PSK)
ap.ifconfig((AP_IP, "255.255.255.0", AP_IP, AP_IP))
while not ap.active():
  time.sleep_ms(100)

addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# SO_REUSEADDR lets the port be reused immediately after this program
# stops - without it, restarting after anything other than a full
# soft reset raises OSError: [Errno 112] EADDRINUSE, since the OS
# still considers the old socket's port briefly reserved.
server.bind(addr)
server.listen(1)
server.setblocking(False)

beaper.nano_led_off()
print("WiFi NeoPixel Controller")
print("Strip type:", STRIP_TYPE, " Pixels:", NUM_LEDS,
      " Max brightness:", MAX_BRIGHTNESS)
print()
print("Connect to WiFi network:", AP_SSID, " (password:", AP_PASSWORD, ")")
print("Then browse to: http://" + ap.ifconfig()[0] + "/")
print()
print("SW3/SW4: previous/next mode   SW2: adjust parameter   SW5: on/off")
print()

last_frame_time = time.ticks_ms()
enter_mode(MODE_OFF)


# =============================================================================
# Main loop
# =============================================================================

try:
  while True:
    current_time = time.ticks_ms()

    try:
      client, client_addr = server.accept()
      handle_client(client)
    except OSError:
      pass  # No pending connection - normal for a non-blocking socket

    # ---- Button: SW3 - previous mode ------------------------------------
    sw3_current = beaper.SW3.value()
    if sw3_current == 0 and sw3_last == 1:
      if mode != MODE_OFF:
        enter_mode((mode - 2) % (NUM_MODES - 1) + 1)
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
        enter_mode(last_active_mode)
      else:
        last_active_mode = mode
        enter_mode(MODE_OFF)
    sw5_last = sw5_current

    # ---- SW2: cycle mode parameter (hold to repeat) ---------------------
    if check_sw2(current_time):
      adjust_parameter()

    # ---- Animation frame (non-blocking, rate-limited by FRAME_INTERVAL) -
    if time.ticks_diff(current_time, last_frame_time) >= FRAME_INTERVAL:
      last_frame_time = current_time

      if mode == MODE_SOLID:
        r, g, b = scale_colour(*colour.hsv_to_rgb(hue, 100, 100), MAX_BRIGHTNESS)
        fill_strip(r, g, b)

      elif mode == MODE_CHASE:
        r, g, b = scale_colour(*colour.hsv_to_rgb(hue, 100, 100), MAX_BRIGHTNESS)
        clear_strip()
        strip[chase_pos] = make_pixel(r, g, b)
        strip.write()
        chase_pos = (chase_pos + chase_speed) % NUM_LEDS

      elif mode == MODE_THEATRE:
        r, g, b = scale_colour(*colour.hsv_to_rgb(hue, 100, 100), MAX_BRIGHTNESS)
        for i in range(NUM_LEDS):
          if i % 3 == theatre_offset:
            strip[i] = make_pixel(r, g, b)
          else:
            strip[i] = make_pixel(0, 0, 0)
        strip.write()
        theatre_frames += 1
        if theatre_frames >= theatre_rate:
          theatre_frames = 0
          theatre_offset = (theatre_offset + 1) % 3

      elif mode == MODE_RAINBOW:
        for i in range(NUM_LEDS):
          pixel_hue = (rainbow_offset + i * 360 // NUM_LEDS) % 360
          r, g, b = scale_colour(*colour.hsv_to_rgb(pixel_hue, 100, 100), MAX_BRIGHTNESS)
          strip[i] = make_pixel(r, g, b)
        strip.write()
        rainbow_offset = (rainbow_offset + rainbow_speed) % 360

      elif mode == MODE_PULSE:
        r, g, b = scale_colour(*colour.hsv_to_rgb(hue, 100, 100), pulse_bright)
        fill_strip(r, g, b)
        if pulse_up:
          pulse_bright = min(pulse_bright + PULSE_STEP, MAX_BRIGHTNESS)
          if pulse_bright == MAX_BRIGHTNESS:
            pulse_up = False
        else:
          pulse_bright = max(pulse_bright - PULSE_STEP, 0)
          if pulse_bright == 0:
            pulse_up = True
            hue = (hue + 30) % 360

    time.sleep_ms(LOOP_DELAY)

finally:
  # Stopping the script (rather than a soft reset) doesn't automatically
  # release the listening socket on this port, so without this cleanup
  # a restart raises OSError: [Errno 112] EADDRINUSE.
  server.close()
  print("Server stopped - socket closed.")