"""
BEAPER Nano LCD demo program
February 8, 2025

Draws multiple screens of graphics primitives using MicroPython's frame buffer
and counts the number of graphical objects of each type drawn per second.

Uses the LCD.py driver module adapted from Russ Hughes' st7789mpy.py MicroPython
ST7789 driver library. (https://github.com/russhughes/st7789py_mpy)

Required files:
    LCDconfig_Nano.py, or
    LCDconfig_Pico.py - low-level hardware configuration file for each circuit
    
    LCD.py - LCD driver module that extends the MicroPython framebuffer
    
    NotoSansDisplay_24.py - Noto Sans Display font converted from TrueType
        using Russ Hughes' write_font_converter.py program
 
"""

from machine import Pin, PWM, ADC, SPI
import array
import random
import time

import LCDconfig_Nano as lcd_config     # Customized for BEAPER Nano I/O pins
# import LCDconfig_Pico as lcd_config     # Customized for BEAPER Pico I/O pins

import NotoSansDisplay_24 as notosans24

# Configure Educational Starter I/O devices
SW2 = Pin(44, Pin.IN, Pin.PULL_UP)
SW3 = Pin(43, Pin.IN, Pin.PULL_UP)
SW4 = Pin(5, Pin.IN, Pin.PULL_UP)
SW5 = Pin(6, Pin.IN, Pin.PULL_UP)
LED2 = Pin(7, Pin.OUT)
LED3 = Pin(8, Pin.OUT)
LED4 = Pin(9, Pin.OUT)
LED5 = Pin(10, Pin.OUT)
BEEPER = Pin(17, Pin.OUT)

# Configure built-in Arduino Nano ESP32 LEDs
LED_BUILTIN = Pin(48, Pin.OUT, value = 0)   # Active High
LED_BLUE = Pin(45, Pin.OUT, value = 1)      # Active Low
LED_GREEN = Pin(0, Pin.OUT, value = 1)      # Active Low
LED_RED = Pin(46, Pin.OUT, value = 0)       # Active Low

# Configure analog input devices
Q1 = Q4 = ADC(1, atten = ADC.ATTN_11DB)
Q2 = U4 = ADC(2, atten = ADC.ATTN_11DB)
Q3 = RV1 = ADC(3, atten = ADC.ATTN_11DB)
VDIV = RV2 = ADC(4, atten = ADC.ATTN_11DB)

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

# Deinit(ialize) SPI on Arduino Nano ESP32 after software restart
spi = SPI(2, baudrate=60000000, sck=Pin(48), mosi=Pin(38), miso=None)
spi.deinit()

start_time = time.ticks_us()

# Create lcd object. Rotation=3 is the normal BEAPER Pico LCD orientation.
lcd = lcd_config.config(rotation=3)
config_time = time.ticks_diff(time.ticks_us(), start_time)

start_time = time.ticks_us()
# mirobo logo
logo_bg = 0x0004
lcd.fill(logo_bg)
fill_time = time.ticks_diff(time.ticks_us(), start_time)

start_time = time.ticks_us()
lcd.update()
update_time = time.ticks_diff(time.ticks_us(), start_time)

for i in range(204, 0, -4):
    # Draw fading mirobo logo
    logo_color = lcd.color565(i, i, i)
    # logo_color = lcd.WHITE75
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
    if i == 204:
        time.sleep(2)
    
start_time = time.ticks_us()

# Color bars
start_time = time.ticks_us()
lcd.fill(lcd.BLACK)
lcd.rect(0, 0, 36, 160, lcd.WHITE75, True)
lcd.rect(35, 0, 34, 160, lcd.YELLOW75, True)
lcd.rect(69, 0, 34, 160, lcd.CYAN75, True)
lcd.rect(103, 0, 34, 160, lcd.GREEN75, True)
lcd.rect(137, 0, 34, 160, lcd.MAGENTA75, True)
lcd.rect(171, 0, 34, 160, lcd.RED75, True)
lcd.rect(204, 0, 34, 160, lcd.BLUE75, True)
for x in range(0, 256, 2):
    lcd.vline(x>>1, 160, 20, lcd.color565(x,0,0))
    lcd.vline(x>>1, 180, 20, lcd.color565(0,x,0))
    lcd.vline(x>>1, 200, 20, lcd.color565(0,0,x))
    lcd.vline(239-(x>>2), 160, 60, lcd.color565(x,x,x))
r_idx = 80
g_idx = 0
b_idx = 160
for x in range(240):
    r = 255-rainbow240[(x+r_idx)%240]
    g = 255-rainbow240[(x+g_idx)%240]
    b = 255-rainbow240[(x+b_idx)%240]
    color = lcd.color565(r, g, b)
    lcd.vline(x, 220, 20, color)
lcd.update()
finish_time = time.ticks_diff(time.ticks_us(), start_time)

msg_x = 120 - lcd.write_width("init( ): ", notosans24)
lcd.write("init( ): " + str(config_time) + "us", msg_x, 10, notosans24, lcd.WHITE)
msg_x = 120 - lcd.write_width("fill( ): ", notosans24)
lcd.write("fill( ): " + str(fill_time) + "us", msg_x, 34, notosans24, lcd.WHITE)
msg_x = 120 - lcd.write_width("update( ): ", notosans24)
lcd.write("update( ): " + str(update_time) + "us", msg_x, 58, notosans24, lcd.WHITE)
msg_x = 120 - lcd.write_width("Bars: ", notosans24)
lcd.write("Bars: " + str(finish_time) + "us", msg_x, 82, notosans24, lcd.WHITE)
msg_x = (240 - lcd.write_width("Press SW5", notosans24)) // 2
lcd.write("Press SW5", msg_x, 134, notosans24, lcd.WHITE)
lcd.update()

while SW5.value() == 1:
    time.sleep_ms(20)

frames_per_sec = 20  # target number of frames per second
frame_period = 1000000 // frames_per_sec  # frame period in microseconds

while True:
    # Pixels
    pixels = 0
    frames = frames_per_sec
    lcd.fill(lcd.BLACK)
    while frames > 0:
        start_time = time.ticks_us()
        lcd.update()
        while time.ticks_diff(time.ticks_us(), start_time) < frame_period:
            color = lcd.color565(
                random.getrandbits(8), random.getrandbits(8), random.getrandbits(8)
            )
            lcd.pixel(
                random.randint(0, lcd.width),
                random.randint(0, lcd.height),
                color,
            )
            pixels += 1
        frames -= 1
    lcd.update()
    time.sleep(1)

    # Lines
    lines = 0
    frames = frames_per_sec
    lcd.fill(lcd.BLACK)
    while frames > 0:
        start_time = time.ticks_us()
        lcd.update()
        while time.ticks_diff(time.ticks_us(), start_time) < frame_period:
            color = lcd.color565(
                random.getrandbits(8), random.getrandbits(8), random.getrandbits(8)
            )
            lcd.line(
                random.randint(0, lcd.width),
                random.randint(0, lcd.height),
                random.randint(0, lcd.width),
                random.randint(0, lcd.height),
                color,
            )
            lines += 1
        frames -= 1
    lcd.update()
    time.sleep(1)

    # Rectangles
    rects = 0
    frames = frames_per_sec
    lcd.fill(lcd.BLACK)
    while frames > 0:
        start_time = time.ticks_us()
        lcd.update()
        while time.ticks_diff(time.ticks_us(), start_time) < frame_period:
            color = lcd.color565(
                random.getrandbits(8), random.getrandbits(8), random.getrandbits(8)
            )
            lcd.rect(
                random.randint(0, lcd.width - 120),
                random.randint(0, lcd.height - 120),
                random.randint(0, lcd.width - 120),
                random.randint(0, lcd.height - 120),
                color,
                False,
            )
            rects += 1
        frames -= 1
    lcd.update()
    time.sleep(1)

    # Filled Rectangles
    frects = 0
    frames = frames_per_sec
    lcd.fill(lcd.BLACK)
    while frames > 0:
        start_time = time.ticks_us()
        lcd.update()
        while time.ticks_diff(time.ticks_us(), start_time) < frame_period:
            color = lcd.color565(
                random.getrandbits(8), random.getrandbits(8), random.getrandbits(8)
            )
            lcd.rect(
                random.randint(0, lcd.width - 120),
                random.randint(0, lcd.height - 120),
                random.randint(0, lcd.width - 120),
                random.randint(0, lcd.height - 120),
                color,
                True,
            )
            frects += 1
        frames -= 1
    lcd.update()
    time.sleep(1)

    # Ellipses
    ellipses = 0
    frames = frames_per_sec
    lcd.fill(lcd.BLACK)
    while frames > 0:
        start_time = time.ticks_us()
        lcd.update()
        while time.ticks_diff(time.ticks_us(), start_time) < frame_period:
            color = lcd.color565(
                random.getrandbits(8), random.getrandbits(8), random.getrandbits(8)
            )
            lcd.ellipse(
                random.randint(0, lcd.width - 80) + 40,
                random.randint(0, lcd.height - 80) + 40,
                random.randint(0, 39),
                random.randint(0, 39),
                color,
                False,
            )
            ellipses += 1
        frames -= 1
    lcd.update()
    time.sleep(1)

    # Filled Ellipses
    fellipses = 0
    frames = frames_per_sec
    lcd.fill(lcd.BLACK)
    while frames > 0:
        start_time = time.ticks_us()
        lcd.update()
        while time.ticks_diff(time.ticks_us(), start_time) < frame_period:
            color = lcd.color565(
                random.getrandbits(8), random.getrandbits(8), random.getrandbits(8)
            )
            lcd.ellipse(
                random.randint(0, lcd.width - 80) + 40,
                random.randint(0, lcd.height - 80) + 40,
                random.randint(0, 39),
                random.randint(0, 39),
                color,
                True,
            )
            fellipses += 1
        frames -= 1
    lcd.update()
    time.sleep(1)

    # Round Rects
    rrects = 0
    frames = frames_per_sec
    lcd.fill(lcd.BLACK)
    while frames > 0:
        start_time = time.ticks_us()
        lcd.update()
        while time.ticks_diff(time.ticks_us(), start_time) < frame_period:
            color = lcd.color565(
                random.getrandbits(8), random.getrandbits(8), random.getrandbits(8)
            )
            r = random.randint(4, 20)
            x = random.randint(r, lcd.width - 120)
            y = random.randint(r, lcd.height - 120)
            w = random.randint(r, lcd.width - 120)
            h = random.randint(r, lcd.height - 120)
            lcd.round_rect(x, y, w, h, r, color, False)
            rrects += 1
        frames -= 1
    lcd.update()
    time.sleep(1)

    # Filled Round Rects
    frrects = 0
    frames = frames_per_sec
    lcd.fill(lcd.BLACK)
    while frames > 0:
        start_time = time.ticks_us()
        lcd.update()
        while time.ticks_diff(time.ticks_us(), start_time) < frame_period:
            color = lcd.color565(
                random.getrandbits(8), random.getrandbits(8), random.getrandbits(8)
            )
            r = random.randint(4, 20)
            x = random.randint(r, lcd.width - 120)
            y = random.randint(r, lcd.height - 120)
            w = random.randint(r, lcd.width - 120)
            h = random.randint(r, lcd.height - 120)
            lcd.round_rect(x, y, w, h, r, color, True)
            frrects += 1
        frames -= 1
    lcd.update()
    time.sleep(1)

    # Triangles
    triangles = 0
    frames = frames_per_sec
    lcd.fill(lcd.BLACK)
    while frames > 0:
        start_time = time.ticks_us()
        lcd.update()
        while time.ticks_diff(time.ticks_us(), start_time) < frame_period:
            color = lcd.color565(
                random.getrandbits(8), random.getrandbits(8), random.getrandbits(8)
            )
            lcd.poly(
                random.randint(0, lcd.width - 40) + 20,
                random.randint(0, lcd.height - 30) + 20,
                triangle,
                color,
                False,
            )
            triangles += 1
        frames -= 1
    lcd.update()
    time.sleep(1)

    # Filled Triangles
    ftriangles = 0
    frames = frames_per_sec
    lcd.fill(lcd.BLACK)
    while frames > 0:
        start_time = time.ticks_us()
        lcd.update()
        while time.ticks_diff(time.ticks_us(), start_time) < frame_period:
            color = lcd.color565(
                random.getrandbits(8), random.getrandbits(8), random.getrandbits(8)
            )
            lcd.poly(
                random.randint(0, lcd.width - 40) + 20,
                random.randint(0, lcd.height - 30) + 20,
                triangle,
                color,
                True,
            )
            ftriangles += 1
        frames -= 1
    lcd.update()
    time.sleep(1)

    lcd.fill(lcd.BLUE75)
    lcd.write(str(pixels) + " pixels/s", 10, 0, notosans24, lcd.WHITE)
    lcd.write(str(lines) + " lines/s", 10, 24, notosans24, lcd.WHITE)
    lcd.write(str(rects) + " rects/s", 10, 48, notosans24, lcd.WHITE)
    lcd.write(str(frects) + " fld-rects/s", 10, 72, notosans24, lcd.WHITE)
    lcd.write(str(ellipses) + " ellipses/s", 10, 96, notosans24, lcd.WHITE)
    lcd.write(str(fellipses) + " fld-ellipses/s", 10, 120, notosans24, lcd.WHITE)
    lcd.write(str(rrects) + " rnd rects/s", 10, 144, notosans24, lcd.WHITE)
    lcd.write(str(frrects) + " fld-rnd rects/s", 10, 168, notosans24, lcd.WHITE)
    lcd.write(str(triangles) + " polys/s", 10, 192, notosans24, lcd.WHITE)
    lcd.write(str(ftriangles) + " fld-polys/s", 10, 216, notosans24, lcd.WHITE)
    lcd.update()

    while SW5.value() == 1:
        time.sleep_ms(20)

