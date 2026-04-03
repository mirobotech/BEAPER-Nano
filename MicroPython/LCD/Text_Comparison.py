"""
BEAPER Nano Text Comparison
Updated: April 2, 2026

Compares the time taken to write text using text16() with the built-in
display font and write() using converted TrueType fonts while allowing
users to compare the appearance of all font characters from 0x20-0x7e.

Uses the LCD.py driver module adapted from Russ Hughes' st7789py.py MicroPython
ST7789 driver library. (https://github.com/russhughes/st7789py_mpy)

Requires TrueType fonts to be converted using write_font_converter.py

Required files:
    LCDconfig_Nano.py - LCD configuration file for BEAPER Nano, or
    LCDconfig_Pico.py - LCD configuration file for BEAPER Pico

    LCD.py - LCD driver module that extends the MicroPython framebuffer

    A converted TrueType font (use Russ Hughes' write_font_converter.py
        program to convert the font for use with write())
"""

from machine import Pin, PWM, SPI
import time

import LCDconfig_Nano as lcd_config     # Customized for BEAPER Nano I/O pins
# import LCDconfig_Pico as lcd_config     # Customized for BEAPER Pico I/O pins

# Import converted TrueType font as font16 for comparison
import NotoSansDisplay_16 as font16

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

# Deinit(ialize) SPI on Arduino Nano ESP32 after software restart
spi = SPI(2, baudrate=40000000, sck=Pin(48), mosi=Pin(38), miso=None)
spi.deinit()

lcd = lcd_config.config()    # Configure LCD as lcd

# ---------------------------------------------------------------------
# Text comparison screen: text16() vs write() at the same font height
#
# All printable ASCII characters (0x20-0x7e) are displayed in both
# fonts using the same row layout, so letterforms can be compared
# directly. The time taken to draw each complete set is measured and
# displayed below each font's output.
# ---------------------------------------------------------------------

# Character rows in display order — each string is drawn as one text16()
# or write() call, so the measured time covers all character glyphs.

_CHAR_ROWS = (
    "ABCDEFGHIJKLMNOPQRST",
    "abcdefghijklmnopqrst",
    "UVWXYZ~!@#$%^&*()_+?",
    "uvwxyz`1234567890-=/",
    "\"':;< >,.{|}[\]",
)

lcd.fill(0x0008)

# Time text16() to draw all 95 characters
start_time = time.ticks_us()
for i, row in enumerate(_CHAR_ROWS):
    lcd.text16(row, 0, 1 + i * 16)
text16_time = time.ticks_diff(time.ticks_us(), start_time)

# Dividing line
lcd.hline(0, 119, 240, lcd.WHITE75)

# Time write() with font16 drawing the same 95 characters
font16_h = lcd.write_height(font16)
start_time = time.ticks_us()
for i, row in enumerate(_CHAR_ROWS):
    lcd.write(row, 0, 121 + i * font16_h, font16, lcd.WHITE75)
font16_time = time.ticks_diff(time.ticks_us(), start_time)

# Display timing results and prompt below the font samples.
# Use text16() for the compact result lines and notosans24 for the prompt.
t16_str  = "mirobo16: " + str(text16_time) + "us"
t16_x    = (240 - lcd.text16_width(t16_str)) // 2
f16_str  = "font16: " + str(font16_time) + "us"
f16_x    = (240 - lcd.write_width(f16_str, font16)) // 2
lcd.text16(t16_str, t16_x, 100, lcd.WHITE75)
lcd.write(f16_str, f16_x, 220, font16, lcd.WHITE75)
lcd.update()


