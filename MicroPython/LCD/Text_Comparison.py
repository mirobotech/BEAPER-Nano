# ==============================================================================
# BEAPER Nano Text Comparison
# Version 1.1
# Updated: September 4, 2026
# 
# Compares the time taken to write text using text16() with the built-in
# display font and write() using converted TrueType fonts while allowing
# users to compare the appearance of all font characters from 0x20-0x7e.
# 
# Uses the LCD.py driver module adapted from Russ Hughes' st7789py.py MicroPython
# ST7789 driver library. (https://github.com/russhughes/st7789py_mpy)
# 
# Requires TrueType fonts to be converted using write_font_converter.py
# 
# Required files:
#     LCDconfig_Nano.py - LCD configuration file for BEAPER Nano, or
#     LCDconfig_Pico.py - LCD configuration file for BEAPER Pico
#     LCD.py - LCD driver module that extends the MicroPython framebuffer
#
#     A converted TrueType font (use Russ Hughes' write_font_converter.py
#     program to convert the font for use with write()):
#          NotoSansDisplay_16.py - converted Noto Sans Display font
# ==============================================================================

from machine import Pin, PWM, SPI
import time

import LCDconfig_Nano as lcd_config     # Customized for BEAPER Nano I/O pins
# import LCDconfig_Pico as lcd_config     # Customized for BEAPER Pico I/O pins

# Import converted TrueType font as font16 for comparison
import NotoSansDisplay_16 as font16
# import NotoSansMono_16 as font16

lcd = lcd_config.config()    # Configure LCD as lcd

# All printable ASCII characters (0x20-0x7e) are displayed in both
# fonts using the same row layout. The time taken to draw each
# font set is measured and displayed below each font's output.

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
    lcd.write(row, 0, 121 + i * font16_h, font16)
font16_time = time.ticks_diff(time.ticks_us(), start_time)

# Display timing results below the font samples.
t16_str  = "mirobo16: " + str(text16_time) + "us"
t16_x    = (240 - lcd.text16_width(t16_str)) // 2
f16_str  = "font16: " + str(font16_time) + "us"
f16_x    = (240 - lcd.write_width(f16_str, font16)) // 2
lcd.text16(t16_str, t16_x, 100)
lcd.write(f16_str, f16_x, 220, font16)
lcd.update()


