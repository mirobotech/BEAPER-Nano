"""
BEAPER Nano LCD demo program
Updated: April 2, 2026

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

"""

frames_per_sec = 30                         # Target frames per second
frame_period = 1000000 // frames_per_sec    # Frame period in microseconds

from machine import Pin, PWM, ADC, SPI
import random
import time

import LCDconfig_Nano as lcd_config        # Customized for BEAPER Nano I/O pins
# import LCDconfig_Pico as lcd_config        # Customized for BEAPER Pico I/O pins

# BEAPER Nano pushbutton switches (active LOW)
SW2 = Pin(44, Pin.IN, Pin.PULL_UP)  # Circle button
SW3 = Pin(43, Pin.IN, Pin.PULL_UP)  # Left arrow  ( < ) - previous screen
SW4 = Pin(5, Pin.IN, Pin.PULL_UP)   # Right arrow ( > ) - next screen
SW5 = Pin(6, Pin.IN, Pin.PULL_UP)   # Square button

# BEAPER Nano output devices
LED2 = Pin(7, Pin.OUT)
LED3 = Pin(8, Pin.OUT)
LED4 = Pin(9, Pin.OUT)
LED5 = Pin(10, Pin.OUT)
BEEPER = PWM(Pin(17), freq=1000, duty_u16=0)

# Arduino Nano ESP32 LEDs
LED_BUILTIN = Pin(48, Pin.OUT, value=0)    # Active High
LED_BLUE = Pin(45, Pin.OUT, value=1)       # Active Low
LED_GREEN = Pin(0, Pin.OUT, value=1)       # Active Low
LED_RED = Pin(46, Pin.OUT, value=0)        # Active Low

RAINBOW240 = bytes((
    0x00, 0x00, 0x01, 0x01, 0x02, 0x03, 0x04, 0x05,
    0x06, 0x08, 0x0a, 0x0c, 0x0e, 0x10, 0x13, 0x15,
    0x18, 0x1b, 0x1f, 0x22, 0x26, 0x29, 0x2d, 0x31,
    0x35, 0x39, 0x3d, 0x41, 0x46, 0x4a, 0x4f, 0x53,
    0x58, 0x5d, 0x62, 0x67, 0x6c, 0x71, 0x76, 0x7b,
    0x80, 0x85, 0x8a, 0x8e, 0x93, 0x98, 0x9d, 0xa2,
    0xa7, 0xac, 0xb0, 0xb5, 0xb9, 0xbe, 0xc2, 0xc6,
    0xca, 0xce, 0xd2, 0xd6, 0xda, 0xdd, 0xe0, 0xe4,
    0xe7, 0xea, 0xec, 0xef, 0xf1, 0xf3, 0xf5, 0xf7,
    0xf9, 0xfa, 0xfb, 0xfc, 0xfd, 0xfe, 0xff, 0xff,
    0xff, 0xff, 0xfe, 0xfe, 0xfd, 0xfc, 0xfb, 0xfa,
    0xf9, 0xf7, 0xf5, 0xf3, 0xf1, 0xef, 0xec, 0xea,
    0xe7, 0xe4, 0xe0, 0xdd, 0xda, 0xd6, 0xd2, 0xce,
    0xca, 0xc6, 0xc2, 0xbe, 0xb9, 0xb5, 0xb0, 0xac,
    0xa7, 0xa2, 0x9d, 0x98, 0x93, 0x8e, 0x8a, 0x85,
    0x80, 0x7b, 0x76, 0x71, 0x6c, 0x67, 0x62, 0x5d,
    0x58, 0x53, 0x4f, 0x4a, 0x46, 0x41, 0x3d, 0x39,
    0x35, 0x31, 0x2d, 0x29, 0x25, 0x22, 0x1f, 0x1b,
    0x18, 0x15, 0x13, 0x10, 0x0e, 0x0c, 0x0a, 0x08,
    0x06, 0x05, 0x04, 0x03, 0x02, 0x01, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
))

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
    result_y = 112
    result_str = str(count) + " " + label
    result_x = (240 - lcd.text16_width(result_str)) // 2
    lcd.text16(result_str, result_x, 112, lcd.WHITE)
    prompt_y = 210
    prompt = "back    next"
    prompt_x = (240 - lcd.text16_width(prompt)) // 2
    lcd.text16(prompt, prompt_x, prompt_y, lcd.WHITE)
    tri_x = prompt_x - 10
    lcd.triangle(tri_x - 12, prompt_y + 6,
                 tri_x, prompt_y,
                 tri_x, prompt_y + 12,
                 lcd.WHITE, True)
    tri_x = 240 - prompt_x + 10
    lcd.triangle(tri_x + 12, prompt_y + 6,
                 tri_x, prompt_y,
                 tri_x, prompt_y + 12,
                 lcd.WHITE, True)    
    font_h = lcd.text16_height()
    lcd.update(0, result_y, lcd.width, font_h)   # result line
    lcd.update(0, prompt_y, lcd.width, font_h)   # prompt line

    return count

# ---------------------------------------------------------------------
# Startup: time config(), fill(), update(), colour bars, and text16()
# ---------------------------------------------------------------------

# Deinit(ialize) SPI on Arduino Nano ESP32 after software restart
spi = SPI(2, baudrate=60000000, sck=Pin(48), mosi=Pin(38), miso=None)
spi.deinit()

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

# Draw the mirobo logo with a fade-out from white to black
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
    r = 255 - RAINBOW240[(x + r_idx) % 240]
    g = 255 - RAINBOW240[(x + g_idx) % 240]
    b = 255 - RAINBOW240[(x + b_idx) % 240]
    lcd.vline(x, 220, 20, lcd.color565(r, g, b))
lcd.update()
cbars_time = time.ticks_diff(time.ticks_us(), start_time)

# Display all timings. show_timings() draws the first four results and the
# prompt, and is itself timed to measure write(). A partial update of a
# single row is then timed and displayed as 'part.up:' for comparison.
def show_timings():
    """Draw the LCD timing results screen (shown once at startup)."""
    msg_y = 10
    msg_x = 150 - lcd.text16_width("lcd.config():")
    lcd.text16("lcd.config():", msg_x, msg_y, lcd.WHITE)
    msg = str(config_time) + "us"
    msg_x = 230 - lcd.text16_width(msg)
    lcd.text16(msg, msg_x, msg_y, lcd.WHITE)
    msg_y += 20
    msg_x = 150 - lcd.text16_width("lcd.fill():")
    lcd.text16("lcd.fill():", msg_x, msg_y, lcd.WHITE)
    msg = str(fill_time) + "us"
    msg_x = 230 - lcd.text16_width(msg)
    lcd.text16(msg, msg_x, msg_y, lcd.WHITE)
    msg_y += 20
    msg_x = 150 - lcd.text16_width("lcd.update():")
    lcd.text16("lcd.update():", msg_x, msg_y, lcd.WHITE)
    msg = str(update_time) + "us"
    msg_x = 230 - lcd.text16_width(msg)
    lcd.text16(msg, msg_x, msg_y, lcd.WHITE)
    msg_y += 20
    msg_x = 150 - lcd.text16_width("colorbars:")
    lcd.text16("colorbars:", msg_x, msg_y, lcd.WHITE)
    msg = str(cbars_time) + "us"
    msg_x = 230 - lcd.text16_width(msg)
    lcd.text16(msg, msg_x, msg_y, lcd.WHITE)
    prompt = "next >"
    prompt_x = (240 - lcd.text16_width(prompt)) // 2
    lcd.text16(prompt, prompt_x, 204, lcd.WHITE)

# Time how long it takes to write the first four timing lines and the prompt,
# then write the text16() result once with the measured value. The time taken
# to write that final line is excluded, but all other text is included.
msg_y = 90
start_time = time.ticks_us()
show_timings()
write_time = time.ticks_diff(time.ticks_us(), start_time)
msg_x = 150 - lcd.text16_width("lcd.text16():")
lcd.text16("lcd.text16():", msg_x, msg_y, lcd.WHITE)
msg = str(write_time) + "us"
msg_x = 230 - lcd.text16_width(msg)
lcd.text16(msg, msg_x, msg_y, lcd.WHITE)
lcd.update()

# Time a single-row partial update and display the result on the next line.
# Write the label first so the partial update has real content to push.
part_up_y = 110
msg_x = 150 - lcd.text16_width("partial upd.:")
lcd.text16("partial upd.:", msg_x, part_up_y, lcd.WHITE)
start_time = time.ticks_us()
lcd.update(0, part_up_y, lcd.width, lcd.text16_height())
part_up_time = time.ticks_diff(time.ticks_us(), start_time)
msg = str(part_up_time) + "us"
msg_x = 230 - lcd.text16_width(msg)
lcd.text16(msg, msg_x, part_up_y, lcd.WHITE)
lcd.update(0, part_up_y, lcd.width, lcd.text16_height())

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
    v1x = random.randint(20, lcd.width - 20)
    v1y = random.randint(20, lcd.height - 20)
    v2x = random.randint(20, lcd.width - 20)
    v2y = random.randint(20, lcd.height - 20)
    v3x = random.randint(20, lcd.width - 20)
    v3y = random.randint(20, lcd.height - 20)
    lcd.triangle(
        v1x, v1y,
        v2x, v2y,
        v3x, v3y,
        lcd.color565(random.getrandbits(8), random.getrandbits(8), random.getrandbits(8)),
        False,
    )

def draw_filled_triangle():
    v1x = random.randint(20, lcd.width - 20)
    v1y = random.randint(20, lcd.height - 20)
    v2x = random.randint(20, lcd.width - 20)
    v2y = random.randint(20, lcd.height - 20)
    v3x = random.randint(20, lcd.width - 20)
    v3y = random.randint(20, lcd.height - 20)
    lcd.triangle(
        v1x, v1y,
        v2x, v2y,
        v3x, v3y,
        lcd.color565(random.getrandbits(8), random.getrandbits(8), random.getrandbits(8)),
        True,
    )

# Benchmark screens as (label, draw_fn) pairs. Order here controls navigation order.
BENCHMARKS = (
    ("pixels/s",           draw_pixel),
    ("lines/s",            draw_line),
    ("rectangles/s",       draw_rect),
    ("filled-rects/s",     draw_filled_rect),
    ("ellipses/s",         draw_ellipse),
    ("filled-ellipses/s",  draw_filled_ellipse),
    ("round-rects/s",      draw_round_rect),
    ("filled-rnd-rects/s", draw_filled_round_rect),
    ("triangles/s",        draw_triangle),
    ("filled-triangles/s", draw_filled_triangle),
)

# ---------------------------------------------------------------------
# Main navigation loop
#
# Runs the current benchmark, then waits for navigation. 
# Wraps through all benchmark screens in both directions.
# ---------------------------------------------------------------------

NUM_SCREENS = len(BENCHMARKS)   # One screen per benchmark
screen = 0                       # Start at first benchmark

while True:
    label, draw_fn = BENCHMARKS[screen]
    run_benchmark(label, draw_fn)
    direction = wait_for_nav()
    screen = (screen + direction) % NUM_SCREENS