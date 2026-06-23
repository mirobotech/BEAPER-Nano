"""
Wifi_Nano.py
May 2026

WiFi IoT demo for the mirobo.tech BEAPER Nano circuit.

Hosts a WiFi access point and web page demonstrating:

  - Momentary button  : Beeper/horn (hold on desktop, tap on mobile)
  - Momentary buttons : SW2-SW5 diamond arrangement - each tap toggles
                        the matching LED, mirroring the physical buttons
  - Toggle sliders    : LED2-LED5 independent on/off controls
  - Sensor readouts   : Ambient light, analog temperature (U4), 
                        potentiometers RV1 and RV2, and VDIV battery
                        voltage (set JP4 to Enviro. or Robot as needed)

Set analog jumpers JP1-JP3 to the Enviro. position for this program.
JP4 can be set to Enviro. for RV2, or Robot for battery voltage.

To connect: join the 'BEAPER_Nano' WiFi network (password: 1234567890)
then open http://192.168.4.1 in a browser.
"""

import sys
import socket
import network
import json
import time

# Detach from the REPL serial streams so USB cable removal does not
# kill the running program. Note: print() becomes a no-op after this.
# sys.stdin  = None
# sys.stdout = None

import BEAPER_Nano as board
import LCDconfig_Nano as lcd_config
import NotoSansDisplay_24 as notosans24

# ---------------------------------------------------------------------
# LCD setup
# ---------------------------------------------------------------------

lcd = lcd_config.config(rotation=3)

def lcd_show_status(ip):
    # Draw the mirobo logo and show the host IP address on the LCD.
    logo_color = lcd.WHITE75
    logo_bg = 0x0008
    lcd.fill(logo_bg)
    lcd.round_rect(24,  48,  40, 114, 20, logo_color, True)
    lcd.round_rect(74,  24,  40, 138, 20, logo_color, True)
    lcd.round_rect(124, 48,  40, 114, 20, logo_color, True)
    lcd.round_rect(174, 74,  40,  88, 20, logo_color, True)
    lcd.ellipse(194, 44, 20, 20, logo_color, True)
    msg = "Host: " + ip
    msg_x = (240 - lcd.write_width(msg, notosans24)) // 2
    lcd.write(msg, msg_x, 200, notosans24, lcd.WHITE75)
    lcd.update()

# ---------------------------------------------------------------------
# Shared state dictionary
# ---------------------------------------------------------------------
# All hardware reads and writes go through this dict.
# HTTP handler reads/writes state; main loop applies it to hardware.
#
# leds[0-3]    : LED2-LED5 toggle states (0=off, 1=on)
# beep_freq    : >0 = beeping at this Hz, 0 = silent
# sw[0-3]      : physical SW2-SW5 states (0=released, 1=pressed)
#                updated by main loop; read-only from web side
# sensors      : Enviro. sensor readings updated each loop
#   light      : ambient light level (0=dark, 65535=bright, inverted)
#   temp_c     : MCP9700A temperature in degrees C (float)
#   rv1        : potentiometer RV1 raw value (0-65535)
#   rv2        : potentiometer RV2 raw value (0-65535, JP4=Enviro.)
#   vdiv       : battery voltage divider raw value (0-65535, JP4=Robot)

state = {
    "leds":      [0, 0, 0, 0],
    "beep_freq": 0,
    "sw":        [0, 0, 0, 0],
    "sensors": {
        "light":  0,
        "temp_c": 0.0,
        "rv1":    0,
        "rv2":    0,
        "vdiv":   0,
    },
}

# ---------------------------------------------------------------------
# Button edge detection
# ---------------------------------------------------------------------
# Physical SW2-SW5 use internal pull-ups (active LOW).
# A falling edge (1->0) toggles the matching LED state.

_prev_sw = [1, 1, 1, 1]
DEBOUNCE_MS = 20
_last_press_ms = [0, 0, 0, 0]

def poll_buttons():
    now = time.ticks_ms()
    for i, sw in enumerate(board.SWITCHES):
        val = sw.value()
        if _prev_sw[i] == 1 and val == 0:
            if time.ticks_diff(now, _last_press_ms[i]) >= DEBOUNCE_MS:
                state["leds"][i] ^= 1
                _last_press_ms[i] = now
        _prev_sw[i] = val
        state["sw"][i] = 1 - val   # Invert: 1 = pressed for web display

# ---------------------------------------------------------------------
# Hardware output
# ---------------------------------------------------------------------

def apply_hardware():
    for i, led in enumerate(board.LEDS):
        led.value(state["leds"][i])
    freq = state["beep_freq"]
    if freq > 0:
        board.tone(freq)
    else:
        board.noTone()

# ---------------------------------------------------------------------
# Sensor polling (JP1-JP3 set to Enviro. position)
# ---------------------------------------------------------------------
# ADC0 = ambient light sensor Q4 (inverted: higher = brighter)
# ADC1 = MCP9700A temperature sensor U4
# ADC2 = potentiometer RV1
# ADC3 = potentiometer RV2 (JP4=Enviro.) or battery VDIV (JP4=Robot)
#
# MCP9700A conversion: Vout = 0.5V + 0.01V/degC
# With ATTN_11DB full-scale ~3.3V: voltage = raw * 3.3 / 65535
# Temperature (C) = (voltage - 0.5) / 0.01

def poll_sensors():
    state["sensors"]["light"]  = 65535 - board.ADC0.read_u16()
    raw_temp = board.ADC1.read_u16()
    voltage   = raw_temp * 3.3 / 65535
    state["sensors"]["temp_c"] = round((voltage - 0.5) / 0.01, 1)
    state["sensors"]["rv1"]    = board.ADC2.read_u16()
    adc3 = board.ADC3.read_u16()   # JP4 selects: Enviro.=RV2, Robot=VDIV
    state["sensors"]["rv2"]    = adc3
    state["sensors"]["vdiv"]   = adc3

# ---------------------------------------------------------------------
# HTTP handler
# ---------------------------------------------------------------------
# A single makefile() stream handles both reading the request and
# writing the response. This is critical on MicroPython/lwIP: mixing
# a makefile() read stream with raw socket.send() writes causes TCP
# ACK timing problems that silently truncate large responses.

def handle_request(client):
    stream = client.makefile('rwb', 0)
    path = "/"
    query = {}

    try:
        while True:
            line = stream.readline()
            if not line or line == b'\r\n':
                break
            line = line.decode('utf-8')
            if line.startswith('GET'):
                parts = line.split(' ')[1].split('?', 1)
                path = parts[0]
                if len(parts) > 1:
                    for p in parts[1].split('&'):
                        pair = p.split('=')
                        if len(pair) == 2:
                            query[pair[0]] = pair[1]

        if path == "/":
            body   = HTML
            status = "200 OK"
            ctype  = "text/html"

        elif path == "/update":
            t = query.get("type", "")
            try:
                if t == "led":
                    i = int(query["index"])
                    state["leds"][i] = int(query["val"])
                elif t == "sw":
                    # Virtual SW press: val=1 toggles LED, val=0 is release (no-op)
                    i = int(query["index"])
                    if int(query["val"]) == 1:
                        state["leds"][i] ^= 1
                elif t == "beep":
                    state["beep_freq"] = int(query["val"])
            except (KeyError, ValueError, IndexError):
                pass
            body   = "OK"
            status = "200 OK"
            ctype  = "text/plain"

        elif path == "/status":
            body   = json.dumps(state)
            status = "200 OK"
            ctype  = "application/json"

        else:
            body   = "Not Found"
            status = "404 Not Found"
            ctype  = "text/plain"

        if isinstance(body, str):
            body = body.encode('utf-8')
        header = "HTTP/1.0 {}\r\nContent-Type: {}\r\nContent-Length: {}\r\n\r\n".format(
            status, ctype, len(body))
        stream.write(header.encode('utf-8'))
        stream.write(body)

    except Exception as e:
        print("Request error:", e)
    finally:
        stream.close()
        client.close()

# ---------------------------------------------------------------------
# HTML page
# ---------------------------------------------------------------------

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>BEAPER Nano</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,">
  <style>
    * { box-sizing: border-box; }
    body {
      font-family: Verdana, Helvetica, sans-serif;
      max-width: 480px;
      margin: 0 auto;
      padding: 16px;
      background: #f0f4f8;
      color: #0f2d55;
    }
    h1 { font-size: 1.4rem; text-align: center; margin-bottom: 4px; }
    h2 { font-size: 1.1rem; margin: 20px 0 8px; border-bottom: 2px solid #124881; padding-bottom: 4px; }
    .note { font-size: 0.78rem; color: #555; margin: -4px 0 10px; }

    /* ---- Momentary beeper button ---- */
    #beep-btn {
      display: block;
      width: 100%;
      padding: 18px;
      font-size: 1.1rem;
      font-weight: bold;
      background: #124881;
      color: white;
      border: none;
      border-radius: 12px;
      cursor: pointer;
      user-select: none;
      -webkit-user-select: none;
      touch-action: none;
    }
    #beep-btn.active { background: #2496F2; }

    /* ---- SW diamond momentary buttons ----
       3x3 grid: SW2 top-centre, SW3 mid-left, SW4 mid-right,
       SW5 bottom-centre. Corner cells are empty placeholders. */
    .sw-grid {
      display: grid;
      grid-template-columns: repeat(3, 72px);
      grid-template-rows: repeat(3, 72px);
      gap: 8px;
      justify-content: center;
      margin: 8px 0;
    }
    .sw-btn {
      width: 72px;
      height: 72px;
      font-size: 0.95rem;
      font-weight: bold;
      border: 2px solid #124881;
      border-radius: 12px;
      background: white;
      color: #124881;
      cursor: pointer;
      user-select: none;
      -webkit-user-select: none;
      touch-action: none;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      line-height: 1.2;
    }
    .sw-btn .led-dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: #dde3ea;
      margin-top: 5px;
      transition: background 0.15s;
    }
    .sw-btn.pressed { background: #2496F2; color: white; border-color: #2496F2; }
    .sw-btn.led-on .led-dot { background: #f5c400; }
    .sw-btn.pressed.led-on .led-dot { background: white; }
    .sw-placeholder { width: 72px; height: 72px; }

    /* ---- Toggle sliders (LEDs) ---- */
    .led-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 6px 0;
      border-bottom: 1px solid #dde3ea;
    }
    .led-row:last-child { border-bottom: none; }
    .led-label { font-size: 1rem; }
    .switch {
      position: relative;
      display: inline-block;
      width: 64px;
      height: 34px;
      flex-shrink: 0;
    }
    .switch input { opacity: 0; width: 0; height: 0; }
    .slider {
      position: absolute;
      cursor: pointer;
      inset: 0;
      background: #124881;
      border-radius: 34px;
      transition: background 0.2s;
    }
    .slider::before {
      content: "";
      position: absolute;
      width: 26px; height: 26px;
      left: 4px; bottom: 4px;
      background: white;
      border-radius: 50%;
      transition: transform 0.2s;
    }
    input:checked + .slider { background: #2496F2; }
    input:checked + .slider::before { transform: translateX(30px); }

    /* ---- Sensor readouts ---- */
    .sensor-row {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 6px 0;
      border-bottom: 1px solid #dde3ea;
    }
    .sensor-row:last-child { border-bottom: none; }
    .sensor-label { font-size: 0.9rem; width: 76px; flex-shrink: 0; }
    .sensor-bar-bg {
      flex: 1; height: 14px;
      background: #dde3ea;
      border-radius: 7px;
      overflow: hidden;
    }
    .sensor-bar {
      height: 100%;
      background: #2496F2;
      border-radius: 7px;
      width: 0%;
      transition: width 0.15s;
    }
    .sensor-val { font-size: 0.82rem; width: 52px; text-align: right; flex-shrink: 0; }
  </style>
</head>
<body>
  <h1>BEAPER Nano</h1>

  <!-- SECTION 1: Momentary button - Beeper -->
  <h2>Beeper &mdash; Momentary Button</h2>
  <p class="note">Hold to beep on desktop &bull; Tap to beep on mobile</p>
  <button id="beep-btn">&#128264; Hold to Beep</button>

  <!-- SECTION 2: SW diamond - momentary buttons toggling LEDs -->
  <h2>Switches &mdash; Momentary Buttons</h2>
  <p class="note">Each button toggles its LED, mirroring the physical SW2-SW5 buttons. The dot shows the current LED state.</p>
  <div class="sw-grid">
    <div class="sw-placeholder"></div>
    <button class="sw-btn" id="sw-btn-0" data-i="0">SW2<div class="led-dot"></div></button>
    <div class="sw-placeholder"></div>
    <button class="sw-btn" id="sw-btn-1" data-i="1">SW3<div class="led-dot"></div></button>
    <div class="sw-placeholder"></div>
    <button class="sw-btn" id="sw-btn-2" data-i="2">SW4<div class="led-dot"></div></button>
    <div class="sw-placeholder"></div>
    <button class="sw-btn" id="sw-btn-3" data-i="3">SW5<div class="led-dot"></div></button>
    <div class="sw-placeholder"></div>
  </div>

  <!-- SECTION 3: Toggle sliders - LEDs -->
  <h2>LEDs &mdash; Toggle Sliders</h2>
  <div id="led-section">
    <div class="led-row">
      <span class="led-label">LED2</span>
      <label class="switch">
        <input type="checkbox" id="led2" onchange="ledToggle(0,this.checked)">
        <span class="slider"></span>
      </label>
    </div>
    <div class="led-row">
      <span class="led-label">LED3</span>
      <label class="switch">
        <input type="checkbox" id="led3" onchange="ledToggle(1,this.checked)">
        <span class="slider"></span>
      </label>
    </div>
    <div class="led-row">
      <span class="led-label">LED4</span>
      <label class="switch">
        <input type="checkbox" id="led4" onchange="ledToggle(2,this.checked)">
        <span class="slider"></span>
      </label>
    </div>
    <div class="led-row">
      <span class="led-label">LED5</span>
      <label class="switch">
        <input type="checkbox" id="led5" onchange="ledToggle(3,this.checked)">
        <span class="slider"></span>
      </label>
    </div>
  </div>

  <!-- SECTION 4: Enviro. sensor readouts -->
  <h2>Sensors</h2>
  <p class="note">Set JP1-JP3 to Enviro. JP4 selects RV2 (Enviro.) or battery voltage (Robot).</p>
  <div class="sensor-row">
    <span class="sensor-label">Light</span>
    <div class="sensor-bar-bg"><div class="sensor-bar" id="bar-light"></div></div>
    <span class="sensor-val" id="val-light">-</span>
  </div>
  <div class="sensor-row">
    <span class="sensor-label">Temp (U4)</span>
    <div class="sensor-bar-bg"><div class="sensor-bar" id="bar-temp"></div></div>
    <span class="sensor-val" id="val-temp">-</span>
  </div>
  <div class="sensor-row">
    <span class="sensor-label">RV1</span>
    <div class="sensor-bar-bg"><div class="sensor-bar" id="bar-rv1"></div></div>
    <span class="sensor-val" id="val-rv1">-</span>
  </div>
  <div class="sensor-row">
    <span class="sensor-label">RV2 / VDIV</span>
    <div class="sensor-bar-bg"><div class="sensor-bar" id="bar-rv2"></div></div>
    <span class="sensor-val" id="val-rv2">-</span>
  </div>

  <script>
  // ------------------------------------------------------------------
  // SECTION 1: Momentary beeper
  // ------------------------------------------------------------------
  const BEEP_FREQ = 1000;
  const beepBtn = document.getElementById('beep-btn');
  let beeping = false;

  function beepStart() {
    if (beeping) return;
    beeping = true;
    beepBtn.classList.add('active');
    sendUpdate('beep', null, BEEP_FREQ);
  }
  function beepStop() {
    if (!beeping) return;
    beeping = false;
    beepBtn.classList.remove('active');
    sendUpdate('beep', null, 0);
  }
  beepBtn.addEventListener('mousedown',  beepStart);
  beepBtn.addEventListener('mouseup',    beepStop);
  beepBtn.addEventListener('mouseleave', beepStop);
  beepBtn.addEventListener('touchstart', e => { e.preventDefault(); beepStart(); }, {passive: false});
  beepBtn.addEventListener('touchend',   e => { e.preventDefault(); beepStop();  }, {passive: false});

  // ------------------------------------------------------------------
  // SECTION 2: SW diamond momentary buttons
  // ------------------------------------------------------------------
  document.querySelectorAll('.sw-btn').forEach(btn => {
    const i = parseInt(btn.dataset.i);
    function onPress()   { btn.classList.add('pressed');    sendUpdate('sw', i, 1); }
    function onRelease() { btn.classList.remove('pressed'); sendUpdate('sw', i, 0); }
    btn.addEventListener('mousedown',  onPress);
    btn.addEventListener('mouseup',    onRelease);
    btn.addEventListener('mouseleave', onRelease);
    btn.addEventListener('touchstart', e => { e.preventDefault(); onPress();   }, {passive: false});
    btn.addEventListener('touchend',   e => { e.preventDefault(); onRelease(); }, {passive: false});
  });

  // ------------------------------------------------------------------
  // SECTION 3: LED toggle sliders
  // ------------------------------------------------------------------
  function ledToggle(index, checked) {
    sendUpdate('led', index, checked ? 1 : 0);
  }

  // ------------------------------------------------------------------
  // /status polling - syncs LED sliders, SW button dots, sensor bars
  // ------------------------------------------------------------------
  const LED_CBS = ['led2', 'led3', 'led4', 'led5'];

  // MCP9700A temperature sensor range for bar display: 0C to 60C
  const TEMP_MIN = 0, TEMP_MAX = 60;

  setInterval(() => {
    fetch('/status')
      .then(r => r.json())
      .then(s => {
        // LED sliders and SW button LED state dots
        for (let i = 0; i < 4; i++) {
          const on = s.leds[i] === 1;
          document.getElementById(LED_CBS[i]).checked = on;
          document.getElementById('sw-btn-' + i).classList.toggle('led-on', on);
        }
        // Sensor bars
        setBar('light', s.sensors.light, 0, 65535, s.sensors.light);
        setBar('temp',  s.sensors.temp_c, TEMP_MIN, TEMP_MAX,
               s.sensors.temp_c.toFixed(1) + '\u00b0C');
        setBar('rv1',   s.sensors.rv1,  0, 65535, s.sensors.rv1);
        setBar('rv2',   s.sensors.rv2,  0, 65535, s.sensors.rv2);
      })
      .catch(() => {});
  }, 300);

  function setBar(id, val, min, max, label) {
    const pct = Math.max(0, Math.min(100,
                  (val - min) / (max - min) * 100)).toFixed(1);
    document.getElementById('bar-' + id).style.width = pct + '%';
    document.getElementById('val-' + id).textContent = label;
  }

  // ------------------------------------------------------------------
  // Helper: send a control update to /update
  // ------------------------------------------------------------------
  function sendUpdate(type, index, val) {
    let url = '/update?type=' + type + '&val=' + val;
    if (index !== null) url += '&index=' + index;
    fetch(url).catch(() => {});
  }
  </script>
</body>
</html>
"""

# ---------------------------------------------------------------------
# WiFi Access Point setup
# ---------------------------------------------------------------------

SSID = 'BEAPER_Nano'
KEY  = '1234567890'

board.nano_led_on()
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=SSID, key=KEY)

while not ap.active():
    time.sleep_ms(100)

ip = ap.ifconfig()[0]
print("Hosting on", ip)

lcd_show_status(ip)
board.nano_led_off()
board.beep(100)

# ---------------------------------------------------------------------
# Non-blocking socket server
# ---------------------------------------------------------------------

server = socket.socket()
server.bind(socket.getaddrinfo('0.0.0.0', 80)[0][-1])
server.listen(5)
server.setblocking(False)

print("Listening on port 80")

# ---------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------

SENSOR_INTERVAL_MS = 100
_last_sensor_ms = 0

while True:
    now = time.ticks_ms()

    poll_buttons()

    if time.ticks_diff(now, _last_sensor_ms) >= SENSOR_INTERVAL_MS:
        poll_sensors()
        _last_sensor_ms = now

    apply_hardware()

    try:
        client, addr = server.accept()
        client.setblocking(True)
        print("Client:", addr)
        handle_request(client)
    except OSError:
        pass

    time.sleep_ms(10)