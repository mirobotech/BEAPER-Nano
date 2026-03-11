"""
BEAPER Pico LCD demo program
Updated: March 11, 2026

Displays the time taken by various LCD operations and draws multiple screens
of graphics primitives using MicroPython's framebuffer. Records and displays
the number of each type of graphical object drawn per second.

Uses the LCD.py driver module adapted from Russ Hughes' st7789py.py MicroPython
ST7789 driver library. (https://github.com/russhughes/st7789py_mpy)

Navigation:
    SW3 ( < ) - previous screen       SW4 ( > ) - next screen

Required files:
    LCDconfig_Nano.py - LCD configuration file for BEAPER Nano, or
    LCDconfig_Pico.py - LCD configuration file for BEAPER Pico

    LCD.py - LCD driver module that extends the MicroPython framebuffer

    NotoSansDisplay_24.py - Noto Sans Display font converted from TrueType
        using Russ Hughes' write_font_converter.py program
"""

frames_per_sec = 20                         # Target frames per second
frame_period = 1000000 // frames_per_sec    # Frame period in microseconds

from machine import Pin, PWM, ADC
import array
import random
import time

import LCDconfig_Nano as lcd_config        # Customized for BEAPER Nano I/O pins
# import LCDconfig_Nano as lcd_config        # Customized for BEAPER Pico I/O pins

import NotoSansDisplay_24 as notosans24

# Built-in Raspberry Pi Pico LED
LED = Pin("LED", Pin.OUT, value=1)

# BEAPER Pico pushbutton switches (active LOW with internal pull-ups)
SW2 = Pin(0, Pin.IN, Pin.PULL_UP)          # Circle button
SW3 = Pin(1, Pin.IN, Pin.PULL_UP)          # Left arrow  ( < ) - previous screen
SW4 = Pin(2, Pin.IN, Pin.PULL_UP)          # Right arrow ( > ) - next screen
SW5 = Pin(3, Pin.IN, Pin.PULL_UP)          # Square button

# BEAPER Pico output devices
LED2 = Pin(10, Pin.OUT)
LED3 = Pin(11, Pin.OUT)
LED4 = Pin(12, Pin.OUT)
LED5 = Pin(13, Pin.OUT)
BEEPER = H8OUT = PWM(Pin(14), freq=1000, duty_u16=0)

# BEAPER Pico analog input devices
Q1 = Q4 = ADC(Pin(26))
Q2 = RV1 = ADC(Pin(27))
Q3 = RV2 = ADC(Pin(28))
temp_sensor = ADC(4)

triangle = array.array('b', [0, -20, -20, 10, 20, 10])

rainbow240 = (
    b"\x00\x00\x01\x01\x02\x03\x04\x05"
    b"\x06\x08\x0a\x0c\x0e\x10\x13\x15"
    b"\x18\x1b\x1f\x22\x26\x29\x2d\x31"
    b"\x35\x39\x3d\x41\x46\x4a\x4f\x53"
    b"\x58\x5d\x62\x67\x6c\x71\x76\x7b"
    b"\x80\x85\x8a\x8e\x93\x98\x9d\xa2"
    b"\xa7\xac\xb0\xb5\xb9\xbe\xc2\xc6"
    b"\xca\xce\xd2\xd6\xda\xdd\xe0\xe4"
    b"\xe7\xea\xec\xef\xf1\xf3\xf5\xf7"
    b"\xf9\xfa\xfb\xfc\xfd\xfe\xff\xff"
    b"\xff\xff\xfe\xfe\xfd\xfc\xfb\xfa"
    b"\xf9\xf7\xf5\xf3\xf1\xef\xec\xea"
    b"\xe7\xe4\xe0\xdd\xda\xd6\xd2\xce"
    b"\xca\xc6\xc2\xbe\xb9\xb5\xb0\xac"
    b"\xa7\xa2\x9d\x98\x93\x8e\x8a\x85"
    b"\x80\x7b\x76\x71\x6c\x67\x62\x5d"
    b"\x58\x53\x4f\x4a\x46\x41\x3d\x39"
    b"\x35\x31\x2d\x29\x25\x22\x1f\x1b"
    b"\x18\x15\x13\x10\x0e\x0c\x0a\x08"
    b"\x06\x05\x04\x03\x02\x01\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x00"
)

# ---------------------------------------------------------------------
# Navigation helper
# ---------------------------------------------------------------------

def wait_for_nav():
    """
    Block until SW3 ( < ) or SW4 ( > ) is pressed.
    Waits for the button to be released before returning, to avoid
    the press registering on the next screen.

    Returns:
        -1 if SW3 ( < ) was pressed (go to previous screen)
        +1 if SW4 ( > ) was pressed (go to next screen)
    """
    while SW3.value() == 1 and SW4.value() == 1:
        time.sleep_ms(20)
    direction = -1 if SW3.value() == 0 else 1
    while SW3.value() == 0 or SW4.value() == 0:   # Wait for release
        time.sleep_ms(20)
    return direction

# ---------------------------------------------------------------------
# Benchmark helper
# ---------------------------------------------------------------------

def run_benchmark(label, draw_fn):
    """
    Run a one-second benchmark, then display the result and a navigation
    prompt. Runs draw_fn() as many times as possible within frames_per_sec
    frames, updating the LCD once per frame.

    Parameters:
        label (str): Short description shown on the result screen,
                     e.g. "pixels/s" or "fld-rects/s"
        draw_fn (callable): Function called repeatedly within each frame
                            to draw one primitive. Takes no arguments.

    Returns:
        int: Total number of primitives drawn (count per second)
    """
    count = 0
    frames = frames_per_sec
    lcd.fill(lcd.BLACK)
    while frames > 0:
        start_time = time.ticks_us()
        lcd.update()
        while time.ticks_diff(time.ticks_us(), start_time) < frame_period:
            draw_fn()
            count += 1
        frames -= 1
    lcd.update()

    # Overlay the result and navigation prompt on top of the drawn graphics
    # using transparent text (no background colour).
    result_str = str(count) + " " + label
    msg_x = (240 - lcd.write_width(result_str, notosans24)) // 2
    lcd.write(result_str, msg_x, 108, notosans24, lcd.WHITE)
    prompt = "< back    next >"
    prompt_x = (240 - lcd.write_width(prompt, notosans24)) // 2
    lcd.write(prompt, prompt_x, 210, notosans24, lcd.WHITE)
    lcd.update()

    return count

# ---------------------------------------------------------------------
# Startup: time config(), fill(), update(), colour bars, and write()
# ---------------------------------------------------------------------

# Time how long it takes to create the lcd object and initialize the LCD
start_time = time.ticks_us()
lcd = lcd_config.config()
config_time = time.ticks_diff(time.ticks_us(), start_time)

# Time how long it takes to fill the framebuffer
start_time = time.ticks_us()
logo_bg = 0x0004
lcd.fill(logo_bg)
fill_time = time.ticks_diff(time.ticks_us(), start_time)

# Time how long it takes to update the LCD
start_time = time.ticks_us()
lcd.update()
update_time = time.ticks_diff(time.ticks_us(), start_time)

# Draw the mirobo logo with a fade-in from white to black
for i in range(200, 0, -8):
    logo_color = lcd.color565(i, i, i)
    lcd.round_rect(24, 48, 40, 114, 20, logo_color, fill=True)
    lcd.round_rect(74, 24, 40, 138, 20, logo_color, fill=True)
    lcd.round_rect(124, 48, 40, 114, 20, logo_color, fill=True)
    lcd.round_rect(174, 74, 40, 88, 20, logo_color, fill=True)
    lcd.ellipse(194, 44, 20, 20, logo_color, True)
    # letter m
    lcd.ellipse(27, 200, 16, 16, logo_color, True, 1)
    lcd.ellipse(27, 200, 16, 16, logo_color, True, 2)
    lcd.ellipse(27, 200, 8, 8, logo_bg, True, 1)
    lcd.ellipse(27, 200, 8, 8, logo_bg, True, 2)
    lcd.ellipse(51, 200, 16, 16, logo_color, True, 1)
    lcd.ellipse(51, 200, 16, 16, logo_color, True, 2)
    lcd.ellipse(51, 200, 8, 8, logo_bg, True, 1)
    lcd.ellipse(51, 200, 8, 8, logo_bg, True, 2)
    lcd.round_rect(11, 196, 8, 24, 4, logo_color, True)
    lcd.round_rect(35, 196, 8, 24, 4, logo_color, True)
    lcd.round_rect(60, 196, 8, 24, 4, logo_color, True)
    # letter i
    lcd.round_rect(74, 184, 8, 36, 4, logo_color, True)
    lcd.ellipse(78, 174, 4, 4, logo_color, True)
    # letter r
    lcd.round_rect(88, 184, 8, 36, 4, logo_color, True)
    lcd.ellipse(106, 202, 18, 18, logo_color, True, 2)
    lcd.ellipse(106, 202, 10, 10, logo_bg, True, 2)
    lcd.ellipse(106, 187, 4, 4, logo_color, True)
    # letter o
    lcd.ellipse(130, 202, 18, 18, logo_color, True)
    lcd.ellipse(130, 202, 10, 10, logo_bg, True)
    # letter b
    lcd.round_rect(153, 168, 8, 34, 4, logo_color, True)
    lcd.ellipse(171, 202, 18, 18, logo_color, True)
    lcd.ellipse(171, 202, 10, 10, logo_bg, True)
    # letter o
    lcd.ellipse(212, 202, 18, 18, logo_color, True)
    lcd.ellipse(212, 202, 10, 10, logo_bg, True)

    lcd.update()
    if i == 200:
        time.sleep(2)

# Time how long it takes to generate the colour bar test image, excluding
# the initial fill (which is already timed separately as fill_time above).
lcd.fill(lcd.BLACK)
start_time = time.ticks_us()
lcd.rect(0, 0, 36, 160, lcd.WHITE75, True)
lcd.rect(35, 0, 34, 160, lcd.YELLOW75, True)
lcd.rect(69, 0, 34, 160, lcd.CYAN75, True)
lcd.rect(103, 0, 34, 160, lcd.GREEN75, True)
lcd.rect(137, 0, 34, 160, lcd.MAGENTA75, True)
lcd.rect(171, 0, 34, 160, lcd.RED75, True)
lcd.rect(204, 0, 34, 160, lcd.BLUE75, True)
for x in range(0, 256, 2):
    lcd.vline(x>>1, 160, 20, lcd.color565(x, 0, 0))
    lcd.vline(x>>1, 180, 20, lcd.color565(0, x, 0))
    lcd.vline(x>>1, 200, 20, lcd.color565(0, 0, x))
    lcd.vline(239-(x>>2), 160, 60, lcd.color565(x, x, x))
r_idx = 80
g_idx = 0
b_idx = 160
for x in range(240):
    r = 255 - rainbow240[(x + r_idx) % 240]
    g = 255 - rainbow240[(x + g_idx) % 240]
    b = 255 - rainbow240[(x + b_idx) % 240]
    lcd.vline(x, 220, 20, lcd.color565(r, g, b))
lcd.update()
cbars_time = time.ticks_diff(time.ticks_us(), start_time)

# Display all timings. show_timings() draws the first four results and the
# prompt, and is itself timed to measure write().
def show_timings():
    """Draw the LCD timing results screen (shown once at startup)."""
    msg_x = 120 - lcd.write_width("config( ): ", notosans24)
    lcd.write("config( ): " + str(config_time) + "us", msg_x, 10, notosans24, lcd.WHITE)
    msg_x = 120 - lcd.write_width("fill( ): ", notosans24)
    lcd.write("fill( ): " + str(fill_time) + "us", msg_x, 34, notosans24, lcd.WHITE)
    msg_x = 120 - lcd.write_width("update( ): ", notosans24)
    lcd.write("update( ): " + str(update_time) + "us", msg_x, 58, notosans24, lcd.WHITE)
    msg_x = 120 - lcd.write_width("colorbars: ", notosans24)
    lcd.write("colorbars: " + str(cbars_time) + "us", msg_x, 82, notosans24, lcd.WHITE)
    prompt = "Press > to begin"
    prompt_x = (240 - lcd.write_width(prompt, notosans24)) // 2
    lcd.write(prompt, prompt_x, 200, notosans24, lcd.WHITE)
    lcd.update()

# Time how long it takes to write the first four timing lines and the prompt,
# then write the write() result once with the measured value. The time taken
# to write that final line is necessarily excluded, but all other text is included.
start_time = time.ticks_us()
show_timings()
write_time = time.ticks_diff(time.ticks_us(), start_time)
msg_x = 120 - lcd.write_width("write( ): ", notosans24)
lcd.write("write( ): " + str(write_time) + "us", msg_x, 106, notosans24, lcd.WHITE)
lcd.update()

# Wait for SW4 ( > ) before entering the benchmark loop. SW3 is ignored
# since there is no previous screen to go back to.
while SW4.value() == 1:
    time.sleep_ms(20)
while SW4.value() == 0:  # Wait for release
    time.sleep_ms(20)

# ---------------------------------------------------------------------
# Benchmark screen definitions
# Each entry is (label, draw_fn) passed to run_benchmark().
# Benchmarks that need local state (round rects) use a nested function.
# ---------------------------------------------------------------------

def draw_pixel():
    lcd.pixel(
        random.randint(0, lcd.width),
        random.randint(0, lcd.height),
        lcd.color565(random.getrandbits(8), random.getrandbits(8), random.getrandbits(8)),
    )

def draw_line():
    lcd.line(
        random.randint(0, lcd.width), random.randint(0, lcd.height),
        random.randint(0, lcd.width), random.randint(0, lcd.height),
        lcd.color565(random.getrandbits(8), random.getrandbits(8), random.getrandbits(8)),
    )

def draw_rect():
    lcd.rect(
        random.randint(0, lcd.width - 120), random.randint(0, lcd.height - 120),
        random.randint(0, lcd.width - 120), random.randint(0, lcd.height - 120),
        lcd.color565(random.getrandbits(8), random.getrandbits(8), random.getrandbits(8)),
        False,
    )

def draw_filled_rect():
    lcd.rect(
        random.randint(0, lcd.width - 120), random.randint(0, lcd.height - 120),
        random.randint(0, lcd.width - 120), random.randint(0, lcd.height - 120),
        lcd.color565(random.getrandbits(8), random.getrandbits(8), random.getrandbits(8)),
        True,
    )

def draw_ellipse():
    lcd.ellipse(
        random.randint(0, lcd.width - 80) + 40, random.randint(0, lcd.height - 80) + 40,
        random.randint(0, 39), random.randint(0, 39),
        lcd.color565(random.getrandbits(8), random.getrandbits(8), random.getrandbits(8)),
        False,
    )

def draw_filled_ellipse():
    lcd.ellipse(
        random.randint(0, lcd.width - 80) + 40, random.randint(0, lcd.height - 80) + 40,
        random.randint(0, 39), random.randint(0, 39),
        lcd.color565(random.getrandbits(8), random.getrandbits(8), random.getrandbits(8)),
        True,
    )

def draw_round_rect():
    r = random.randint(4, 20)
    lcd.round_rect(
        random.randint(r, lcd.width - 120), random.randint(r, lcd.height - 120),
        random.randint(r, lcd.width - 120), random.randint(r, lcd.height - 120),
        r,
        lcd.color565(random.getrandbits(8), random.getrandbits(8), random.getrandbits(8)),
        False,
    )

def draw_filled_round_rect():
    r = random.randint(4, 20)
    lcd.round_rect(
        random.randint(r, lcd.width - 120), random.randint(r, lcd.height - 120),
        random.randint(r, lcd.width - 120), random.randint(r, lcd.height - 120),
        r,
        lcd.color565(random.getrandbits(8), random.getrandbits(8), random.getrandbits(8)),
        True,
    )

def draw_triangle():
    lcd.poly(
        random.randint(0, lcd.width - 40) + 20, random.randint(0, lcd.height - 30) + 20,
        triangle,
        lcd.color565(random.getrandbits(8), random.getrandbits(8), random.getrandbits(8)),
        False,
    )

def draw_filled_triangle():
    lcd.poly(
        random.randint(0, lcd.width - 40) + 20, random.randint(0, lcd.height - 30) + 20,
        triangle,
        lcd.color565(random.getrandbits(8), random.getrandbits(8), random.getrandbits(8)),
        True,
    )

# Benchmark screens as (label, draw_fn) pairs. Order here controls navigation order.
BENCHMARKS = (
    ("pixels/s",        draw_pixel),
    ("lines/s",         draw_line),
    ("rects/s",         draw_rect),
    ("fld-rects/s",     draw_filled_rect),
    ("ellipses/s",      draw_ellipse),
    ("fld-ellipses/s",  draw_filled_ellipse),
    ("rnd-rects/s",     draw_round_rect),
    ("fld-rnd-rects/s", draw_filled_round_rect),
    ("polys/s",         draw_triangle),
    ("fld-polys/s",     draw_filled_triangle),
)

# ---------------------------------------------------------------------
# Main navigation loop
#
# Runs the current benchmark, then waits for navigation. 
# Wraps through all benchmark screens in both directions.
# ---------------------------------------------------------------------

NUM_SCREENS = len(BENCHMARKS)    # One screen per benchmark
screen = 0                       # Start at first benchmark

while True:
    label, draw_fn = BENCHMARKS[screen]
    run_benchmark(label, draw_fn)
    direction = wait_for_nav()
    screen = (screen + direction) % NUM_SCREENS
