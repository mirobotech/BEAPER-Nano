"""
MicroPython LCD Driver [LCD.py]
Updated: April 2, 2026

Adapted from Russ Hughes' st7789mpy.py MicroPython ST7789 driver
library. (https://github.com/russhughes/st7789py_mpy)

This module implements a MicroPython driver for the optional 240x240
pixel 1.54" LCD display module used with BEAPER Nano and BEAPER Pico
circuits. It merges Russ Hughes' MicroPyton ST7789 LCD driver with
MicroPython's FrameBuffer while adding additional functionality in
a stylistically common way. 

LCD control functions:

    init() - initialize the LCD panel
    
    hard_reset() - hardware reset the LCD by using the LCD RESET pin.
        (Not used for BEAPER Nano or BEAPER Pico since their LCD
        Reset pins are hard-wired to their RESET button circuits.)
    
    soft_reset() - software reset the LCD panel
    
    invert_mode(m) - invert image if m=True
    
    sleep_mode(m) - sleep the LCD controller and turn off backlight
        if m=True
    
    rotation(r) - rotate image to one of 4 orientations (r=0-3, 3 is
        upright for the way the LCD is mounted on BEAPER Nano and
        BEAPER Pico)
    
    blit_buffer(b, x, y, w, h) - copy memory buffer b to the LCD
        display memory at location x, y, using width w, and height h
    
    update([x, y, w, h]) - updates the entire LCD display memory with
        the contents of the memory buffer when used without arguments.
        With x, y, w, h arguments, updates only the specified (dirty
        rectangle) region of the LCD display memory for faster updates.

LCD graphics functions:

    color565(r, g, b) - convert r, g, b color values to RGB565 format
    
    fill(c) - fill the frame buffer with color c (in RGB565 format)
    
    pixel(x, y [, c]) - draw pixel at x,y in the color c. If c is not
        supplied, return the color of the pixel at coordinate x,y
    
    hline(x, y, w, c) - draw a horizontal line starting at x,y, 
        width w, using color c
    
    vline(x, y, h, c) - draw a vertical line starting at x,y, 
        height h, using color c
    
    line(x1, y1, x2, y2, c) - draw a line starting at x1,y1, and
        ending at x2,y2, using color c
    
    rect(x, y, w, h, c, [, f]) - draw a rectangle at x,y, width w,
        height h, using color c, and optionally fill the rectangle
        if f=True
    
    round_rect(x, y, w, h, r, c [, f]) - draw a rounded rectangle at
        x,y, width w, height h, having corner radius r, using color
        c, and optionally fill the rounded rectangle if f=True
    
    triangle(x1, y1, x2, y2, x3, y3, c [, f]) - draw a triangle with
        vertices at x1,y1, x2,y2, and x3,y3, using color c, and
        optionally fill the triangle if f=True
    
    ellipse(x, y, xr, yr, c, [, f, m]) - draw an ellipse centred at
        x,y, with x radius xr, y radius yr, using color c, and
        optionally fill the ellipse if f=True. Optional m parameter
        enables drawing only one quadrant of the ellipse: 1=top right,
        2=top left, 3=bottom left, 4=bottom right
    
    poly(x, y, coords, c [, f]) - draw a polygon at x,y, from array
        of integer coords (e.g. array('h', [x0, y0, x1, y1, ... xn, yn]),
        using color c, and optionally fill the polygon if f=True
    
    polygon(x, y, points, color [, angle, center_x, center_y) - draw
        a rotatable polygon at x, y, from a list of coordinates points,
        using color c, at an optional rotation angle (radians) and at
        optional offset center_x and center_y
    
    scroll(xstep, ystep) - scroll the contents of the frame buffer by
        xstep and ystep
    
    bitmap(bitmap, x, y [, index, transparent]) - draw a palette-
        compressed bitmap at x,y, clipped to the display bounds.
        Optional index selects from a multi-bitmap module. Optional
        transparent palette index skips drawing transparent pixels.

    bitmap_to_buffer(bitmap [, index]) - convert a palette-compressed
        bitmap module to a raw RGB565 bytearray for fast repeated
        drawing using blit_buffer(). Optional index selects from
        a multi-bitmap module.

Text functions:

    text(s, x, y [, c]) - write text string s using MicroPython's built-in
        8x8 pixel font at location x,y, using optional color c (if color
        is not provided, text is written using 75% white). Each character
        is 8 pixels wide and 8 pixels tall, giving up to 30 characters
        per row on a 240-pixel wide display.

    text16(s, x, y [, c]) - write text string s using this module's
        built-in 10x16 pixel font at location x,y, using optional
        color c (if color is not proviced, text is written using 75%
        white). Each character is 10 pixels wide and 16 pixels tall,
        giving up to 24 characters per row on a 240-pixel wide display.

    text16_width(s) - return the pixel width of string s in the built-in
        10x16 pixel font (always len(s) * 10)

    text16_height() - return the pixel height of the built-in 10x16 pixel
        font (always 16)

    write(s, x, y, font, fg [, bg]) - write text string s at location
        x,y, in font 'font' (a font object converted from a TTF font
        file), using color fg, on a transparent background or using
        optional background color bg

    write_width(s, font) - return the pixel width of string s written in
        the specified converted TrueType font

    write_height(font) - return the pixel height of characters in the
        specified converted TrueType font

Pre-defined colors:

    WHITE - 100% white
    WHITE75 - 75% white
    WHITE50 - 50% white
    YELLOW - 100% yellow
    YELLOW75 - 75% yellow
    YELLOW50 - 50% yellow
    CYAN - 100% cyan
    CYAN75 - 75% cyan
    CYAN50 - 50% cyan
    GREEN - 100% green
    GREEN75 - 75% green
    GREEN50 - 50% green
    MAGENTA - 100% magenta
    MAGENTA75 - 75% magenta
    MAGENTA50 - 50% magenta
    RED - 100% red
    RED75 - 75% red
    RED50 - 50% red
    BLUE - 100% blue
    BLUE75 - 75% blue
    BLUE50 - 50% blue
    GREY (or GRAY) - 25% white
    BLACK - 0% white

Example use:

    import LCDconfig_Pico as lcd_config     # Custom config for BEAPER Pico I/O
    # import LCDconfig_Nano as lcd_config     # Use this config for BEAPER Nano
    import NotoSansDisplay_24 as font24     # Load converted display font

    # Rotation=3 is the normal BEAPER Pico and Nano LCD orientation.
    lcd = lcd_config.config(rotation=3)     # Create an lcd object

    lcd.fill(lcd.BLACK)     # Fill framebuffer with black
    lcd.round_rect(0, 0, 200, 40, 10, lcd.BLUE75, True)  # Draw filled blue round rect
    lcd.write("Hello, world!", 10, 10, font24, lcd.YELLOW)  # Write text string
    lcd.update()            # update the LCD display

---- Original license below: ----

MIT License

Copyright (c) 2020-2023 Russ Hughes

Copyright (c) 2019 Ivan Belokobylskiy

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

The driver is based on devbis' st7789py_mpy module from
https://github.com/devbis/st7789py_mpy.

"""

import framebuf
from array import array
from time import sleep_ms
from math import sin, cos
import struct

# ST7789 commands
_ST7789_SWRESET = b'\x01'
_ST7789_SLPIN = b'\x10'
_ST7789_SLPOUT = b'\x11'
_ST7789_NORON = b'\x13'
_ST7789_INVOFF = b'\x20'
_ST7789_INVON = b'\x21'
_ST7789_DISPOFF = b'\x28'
_ST7789_DISPON = b'\x29'
_ST7789_CASET = b'\x2a'
_ST7789_RASET = b'\x2b'
_ST7789_RAMWR = b'\x2c'
_ST7789_VSCRDEF = b'\x33'
_ST7789_COLMOD = b'\x3a'
_ST7789_MADCTL = b'\x36'
_ST7789_VSCSAD = b'\x37'
_ST7789_RAMCTL = b'\xb0'

# MADCTL bits
_ST7789_MADCTL_MY = const(0x80)
_ST7789_MADCTL_MX = const(0x40)
_ST7789_MADCTL_MV = const(0x20)
_ST7789_MADCTL_ML = const(0x10)
_ST7789_MADCTL_BGR = const(0x08)
_ST7789_MADCTL_MH = const(0x04)

_ENCODE_POS = const(">HH")

# fmt: off

# ---------------------------------------------------------------------
# Display panel support
#
# The ST7789 controller supports multiple panel sizes. The rotation
# tables below cover the most common variants. Each entry defines:
#   (MADCTL, width, height, xstart, ystart, needs_swap)
#   for each of the four rotation settings (0-3).
#
# BEAPER Nano and BEAPER Pico both use 240x240 panels with
# custom_rotations supplied by their LCDconfig files, so
# _find_rotations() and _SUPPORTED_DISPLAYS are only used if you are
# adapting this driver for a different panel without supplying your
# own rotation table.
# ---------------------------------------------------------------------

# Rotation tables
#   (madctl, width, height, xstart, ystart, needs_swap)[rotation % 4]
_DISPLAY_240x320 = (
    (0x00, 240, 320, 0, 0, False),
    (0x60, 320, 240, 0, 0, False),
    (0xc0, 240, 320, 0, 0, False),
    (0xa0, 320, 240, 0, 0, False))

_DISPLAY_240x240 = (
    (0x00, 240, 240,  0,  0, False),
    (0x60, 240, 240,  0,  0, False),
    (0xc0, 240, 240,  0, 80, False),
    (0xa0, 240, 240, 80,  0, False))

_DISPLAY_135x240 = (
    (0x00, 135, 240, 52, 40, False),
    (0x60, 240, 135, 40, 53, False),
    (0xc0, 135, 240, 53, 40, False),
    (0xa0, 240, 135, 40, 52, False))

_DISPLAY_128x128 = (
    (0x00, 128, 128, 2, 1, False),
    (0x60, 128, 128, 1, 2, False),
    (0xc0, 128, 128, 2, 1, False),
    (0xa0, 128, 128, 1, 2, False))

# Supported displays (physical width, physical height, rotation table)
_SUPPORTED_DISPLAYS = (
    (240, 320, _DISPLAY_240x320),
    (240, 240, _DISPLAY_240x240),
    (135, 240, _DISPLAY_135x240),
    (128, 128, _DISPLAY_128x128))

# Default initialization commands from the st7789mpy.py library.
# BEAPER programs always supply custom_init via their LCDconfig file,
# so this fallback is only used if LCD() is called without custom_init
# (e.g. when adapting the driver for use outside of BEAPER circuits).
# init tuple format: (b'command', b'data', delay_ms)
_ST7789_INIT_CMDS = (
    ( b'\x11', b'\x00', 120),               # Exit sleep mode
    ( b'\x13', b'\x00', 0),                 # Turn on the display
    ( b'\xb6', b'\x0a\x82', 0),             # Set display function control
    ( b'\x3a', b'\x55', 10),                # Set pixel format to 16 bits per pixel (RGB565)
    ( b'\xb2', b'\x0c\x0c\x00\x33\x33', 0), # Set porch control
    ( b'\xb7', b'\x35', 0),                 # Set gate control
    ( b'\xbb', b'\x28', 0),                 # Set VCOMS setting
    ( b'\xc0', b'\x0c', 0),                 # Set power control 1
    ( b'\xc2', b'\x01\xff', 0),             # Set power control 2
    ( b'\xc3', b'\x10', 0),                 # Set power control 3
    ( b'\xc4', b'\x20', 0),                 # Set power control 4
    ( b'\xc6', b'\x0f', 0),                 # Set VCOM control 1
    ( b'\xd0', b'\xa4\xa1', 0),             # Set power control A
                                            # Set gamma curve positive polarity
    ( b'\xe0', b'\xd0\x00\x02\x07\x0a\x28\x32\x44\x42\x06\x0e\x12\x14\x17', 0),
                                            # Set gamma curve negative polarity
    ( b'\xe1', b'\xd0\x00\x02\x07\x0a\x28\x31\x54\x47\x0e\x1c\x17\x1b\x1e', 0),
    ( b'\x21', b'\x00', 0),                 # Enable display inversion
    ( b'\x29', b'\x00', 120)                # Turn on the display
)


# Default colour for text() and text16() when no colour is specified
_TEXT_COLOR = const(0xBDF7)     # 75% white

# ---------------------------------------------------------------------
# Built-in 10x16 pixel font for text16()
#
# Each character is encoded in 16 bytes (16 rows × 1 byte per row), as
# a full 8 x 16 pixel glyph without inter-character spaces. The text16()
# function displays characters 10 pixels apart, giving a 2-pixel space
# between characters and resulting in 24 characters/line on a 240-pixel
# wide display.
#
# Characters cover printable ASCII 0x20 (space) through 0x7e (~).
# Character index = ord(char) - 0x20
# ---------------------------------------------------------------------

_MIROBO16 = bytes((
    # 0x20 space
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    # 0x21 !
    0x18, 0x18, 0x18 ,0x18, 0x18, 0x18, 0x18, 0x18,
    0x00, 0x00, 0x18, 0x18, 0x00, 0x00, 0x00, 0x00,
    # 0x22 "
    0x33, 0x33, 0x33, 0x33, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    # 0x23 #
    0x00, 0x36, 0x36, 0xff, 0xff, 0x36, 0x6c, 0xff,
    0xff, 0x6c, 0x6c, 0x00, 0x00, 0x00, 0x00, 0x00,
    # 0x24 $
    0x18, 0x3e, 0x7f, 0xdb, 0xd8, 0x78, 0x1e, 0x1b,
    0xdb, 0xfe, 0x7c, 0x18, 0x00, 0x00, 0x00, 0x00,
    # 0x25 %
    0x20, 0x70, 0xdb, 0x77, 0x2e, 0x1c, 0x38, 0x74,
    0xee, 0xdb, 0x0e, 0x04, 0x00, 0x00, 0x00, 0x00,
    # 0x26 &
    0x00, 0x70, 0xf8, 0xd8, 0xf8, 0x78, 0x7b, 0xff,
    0xce, 0xce, 0xff, 0x7b, 0x00, 0x00, 0x00, 0x00,
    # 0x27 '
    0x18, 0x18, 0x18, 0x18, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    # 0x28 (
    0x04, 0x0c, 0x18, 0x18, 0x18, 0x30, 0x30, 0x30,
    0x30, 0x18, 0x18, 0x18, 0x0c, 0x04, 0x00, 0x00,
    # 0x29 )
    0x20, 0x30, 0x18, 0x18, 0x18, 0x0c, 0x0c, 0x0c,
    0x0c, 0x18, 0x18, 0x18, 0x30, 0x20, 0x00, 0x00,
    # 0x2a *
    0x00, 0x18, 0x18, 0xdb, 0xff, 0x7e, 0x3c, 0x7e,
    0xe7, 0xc3, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    # 0x2b +
    0x00, 0x18, 0x18, 0x18, 0x18, 0xff, 0xff, 0x18,
    0x18, 0x18, 0x18, 0x00, 0x00, 0x00, 0x00, 0x00,
    # 0x2c ,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x1c, 0x1c, 0x1c, 0x38, 0x30, 0x00, 0x00,
    # 0x2d -
    0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0xff, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    # 0x2e .
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x1c, 0x1c, 0x1c, 0x00, 0x00, 0x00, 0x00,
    # 0x2f /
    0x03, 0x03, 0x06, 0x06, 0x0c, 0x0c, 0x18, 0x18,
    0x30, 0x30, 0x60, 0x60, 0xc0, 0xc0, 0x00, 0x00,
    # 0x30 0
    0x3c, 0x7e, 0x66, 0xcf, 0xcb, 0xdb, 0xd3, 0xf3,
    0xe3, 0x66, 0x7e, 0x3c, 0x00, 0x00, 0x00, 0x00,
    # 0x31 1
    0x0c, 0x1c, 0x3c, 0x7c, 0x6c, 0x0c, 0x0c, 0x0c,
    0x0c, 0x0c, 0x0c, 0x0c, 0x00, 0x00, 0x00, 0x00,
    # 0x32 2
    0x3c, 0x7e, 0xe7, 0xc3, 0x03, 0x07, 0x1e, 0x38,
    0x70, 0xe0, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00,
    # 0x33 3
    0x3c, 0x7e, 0xe7, 0xc3, 0x03, 0x0e, 0x0e, 0x03,
    0xc3, 0xe7, 0x7e, 0x3c, 0x00, 0x00, 0x00, 0x00,
    # 0x34 4
    0x06, 0x0e, 0x1e, 0x3e, 0x76, 0xe6, 0xc6, 0xff,
    0xff, 0x06, 0x06, 0x06, 0x00, 0x00, 0x00, 0x00,
    # 0x35 5
    0xff, 0xff, 0xc0, 0xc0, 0xfc, 0xfe, 0x07, 0x03,
    0xc3, 0xe7, 0x7e, 0x3c, 0x00, 0x00, 0x00, 0x00,
    # 0x36 6
    0x3e, 0x7f, 0xe3, 0xc0, 0xdc, 0xfe, 0xe7, 0xc3,
    0xc3, 0xe7, 0x7e, 0x3c, 0x00, 0x00, 0x00, 0x00,
    # 0x37 7
    0xff, 0xff, 0x03, 0x07, 0x06, 0x0e, 0x0c, 0x1c,
    0x18, 0x38, 0x30, 0x30, 0x00, 0x00, 0x00, 0x00,
    # 0x38 8
    0x3c, 0x7e, 0xe7, 0xc3, 0xe7, 0x7e, 0x7e, 0xe7,
    0xc3, 0xe7, 0x7e, 0x3c, 0x00, 0x00, 0x00, 0x00,
    # 0x39 9
    0x3c, 0x7e, 0xe7, 0xc3, 0xc3, 0xe7, 0x7f, 0x3e,
    0x06, 0x06, 0x0c, 0x0c, 0x00, 0x00, 0x00, 0x00,
    # 0x3a :
    0x00, 0x00, 0x00, 0x00, 0x1c, 0x1c, 0x1c, 0x00,
    0x00, 0x1c, 0x1c, 0x1c, 0x00, 0x00, 0x00, 0x00,
    # 0x3b ;
    0x00, 0x00, 0x00, 0x00, 0x1c, 0x1c, 0x1c, 0x00,
    0x00, 0x1c, 0x1c, 0x1c, 0x38, 0x30, 0x00, 0x00,
    # 0x3c <
    0x00, 0x00, 0x03, 0x0e, 0x38, 0xe0, 0xe0, 0x38,
    0x0e, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    # 0x3d =
    0x00, 0x00, 0x00, 0xff, 0xff, 0x00, 0x00, 0xff,
    0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    # 0x3e >
    0x00, 0x00, 0xc0, 0x70, 0x1c, 0x07, 0x07, 0x1c,
    0x70, 0xc0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    # 0x3f ?
    0x3c, 0x7e, 0xe7, 0xc3, 0x07, 0x0e, 0x1c, 0x18,
    0x18, 0x00, 0x18, 0x18, 0x00, 0x00, 0x00, 0x00,
    # 0x40 @
    0x00, 0x00, 0x3c, 0x66, 0xda, 0xba, 0xaa, 0xaa,
    0xbe, 0x9c, 0xc3, 0x7e, 0x00, 0x00, 0x00, 0x00,
    # 0x41 A
    0x3c, 0x7e, 0xe7, 0xc3, 0xc3, 0xff, 0xff, 0xc3,
    0xc3, 0xc3, 0xc3, 0xc3, 0x00, 0x00, 0x00, 0x00,
    # 0x42 B
    0xfc, 0xfe, 0xc7, 0xc3, 0xc7, 0xfe, 0xfe, 0xc7,
    0xc3, 0xc7, 0xfe, 0xfc, 0x00, 0x00, 0x00, 0x00,
    # 0x43 C
    0x3c, 0x7e, 0xe7, 0xc3, 0xc0, 0xc0, 0xc0, 0xc0,
    0xc3, 0xe7, 0x7e, 0x3c, 0x00, 0x00, 0x00, 0x00,
    # 0x44 D
    0xfc, 0xfe, 0xc7, 0xc3, 0xc3, 0xc3, 0xc3, 0xc3,
    0xc3, 0xc7, 0xfe, 0xfc, 0x00, 0x00, 0x00, 0x00,
    # 0x45 E
    0xff, 0xff, 0xc0, 0xc0, 0xc0, 0xfc, 0xfc, 0xc0,
    0xc0, 0xc0, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00,
    # 0x46 F
    0xff, 0xff, 0xc0, 0xc0, 0xc0, 0xfc, 0xfc, 0xc0,
    0xc0, 0xc0, 0xc0, 0xc0, 0x00, 0x00, 0x00, 0x00,
    # 0x47 G
    0x3c, 0x7e, 0xe7, 0xc0, 0xc0, 0xcf, 0xcf, 0xc3,
    0xc3, 0xe7, 0x7e, 0x3c, 0x00, 0x00, 0x00, 0x00,
    # 0x48 H
    0xc3, 0xc3, 0xc3, 0xc3, 0xc3, 0xff, 0xff, 0xc3,
    0xc3, 0xc3, 0xc3, 0xc3, 0x00, 0x00, 0x00, 0x00,
    # 0x49 I
    0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18,
    0x18, 0x18, 0x18, 0x18, 0x00, 0x00, 0x00, 0x00,
    # 0x4a J
    0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0xc3,
    0xc3, 0xe7, 0x7e, 0x3c, 0x00, 0x00, 0x00, 0x00,
    # 0x4b K
    0xc3, 0xc7, 0xce, 0xdc, 0xf8, 0xf0, 0xf0, 0xf8,
    0xdc, 0xce, 0xc7, 0xc3, 0x00, 0x00, 0x00, 0x00,
    # 0x4c L
    0xc0, 0xc0, 0xc0, 0xc0, 0xc0, 0xc0, 0xc0, 0xc0,
    0xc0, 0xc0, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00,
    # 0x4d M
    0x66, 0xff, 0xff, 0xdb, 0xdb, 0xdb, 0xdb, 0xdb,
    0xdb, 0xdb, 0xdb, 0xdb, 0x00, 0x00, 0x00, 0x00,
    # 0x4e N
    0xc3, 0xe3, 0xe3, 0xf3, 0xd3, 0xdb, 0xcb, 0xcf,
    0xc7, 0xc7, 0xc3, 0xc3, 0x00, 0x00, 0x00, 0x00,
    # 0x4f O
    0x3c, 0x7e, 0xe7, 0xc3, 0xc3, 0xc3, 0xc3, 0xc3,
    0xc3, 0xe7, 0x7e, 0x3c, 0x00, 0x00, 0x00, 0x00,
    # 0x50 P
    0xfc, 0xfe, 0xc7, 0xc3, 0xc7, 0xfe, 0xfc, 0xc0,
    0xc0, 0xc0, 0xc0, 0xc0, 0x00, 0x00, 0x00, 0x00,
    # 0x51 Q
    0x3c, 0x7e, 0xe7, 0xc3, 0xc3, 0xc3, 0xc3, 0xc3,
    0xcf, 0xee, 0x7f, 0x3b, 0x00, 0x00, 0x00, 0x00,
    # 0x52 R
    0xfc, 0xfe, 0xc7, 0xc3, 0xc7, 0xfe, 0xfc, 0xcc,
    0xc6, 0xc6, 0xc3, 0xc3, 0x00, 0x00, 0x00, 0x00,
    # 0x53 S
    0x3c, 0x7e, 0xe7, 0xc3, 0xe0, 0x7c, 0x3e, 0x07,
    0xc3, 0xe7, 0x7e, 0x3c, 0x00, 0x00, 0x00, 0x00,
    # 0x54 T
    0xff, 0xff, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18,
    0x18, 0x18, 0x18, 0x18, 0x00, 0x00, 0x00, 0x00,
    # 0x55 U
    0xc3, 0xc3, 0xc3, 0xc3, 0xc3, 0xc3, 0xc3, 0xc3,
    0xc3, 0xe7, 0x7e, 0x3c, 0x00, 0x00, 0x00, 0x00,
    # 0x56 V
    0xc3, 0xc3, 0xc3, 0x66, 0x66, 0x66, 0x3c, 0x3c,
    0x3c, 0x18, 0x18, 0x18, 0x00, 0x00, 0x00, 0x00,
    # 0x57 W
    0xc3, 0xc3, 0xc3, 0xc3, 0xc3, 0xdb, 0xdb, 0xdb,
    0xdb, 0xff, 0x7e, 0x66, 0x00, 0x00, 0x00, 0x00,
    # 0x58 X
    0xc3, 0xc3, 0x66, 0x66, 0x3c, 0x18, 0x18, 0x3c,
    0x66, 0x66, 0xc3, 0xc3, 0x00, 0x00, 0x00, 0x00,
    # 0x59 Y
    0xc3, 0xc3, 0x66, 0x66, 0x3c, 0x3c, 0x18, 0x18,
    0x18, 0x18, 0x18, 0x18, 0x00, 0x00, 0x00, 0x00,
    # 0x5a Z
    0xff, 0xff, 0x03, 0x07, 0x0e, 0x1c, 0x38, 0x70,
    0xe0, 0xc0, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00,
    # 0x5b [
    0x3c, 0x3c, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30,
    0x30, 0x30, 0x30, 0x30, 0x3c, 0x3c, 0x00, 0x00,
    # 0x5c \
    0xc0, 0xc0, 0x60, 0x60, 0x30, 0x30, 0x18, 0x18,
    0x0c, 0x0c, 0x06, 0x06, 0x03, 0x03, 0x00, 0x00,
    # 0x5d ]
    0x3c, 0x3c, 0x0c, 0x0c, 0x0c, 0x0c, 0x0c, 0x0c,
    0x0c, 0x0c, 0x0c, 0x0c, 0x3c, 0x3c, 0x00, 0x00,
    # 0x5e ^
    0x00, 0x00, 0x18, 0x3c, 0x7e, 0xe7, 0xc3, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    # 0x5f _
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0xff, 0x00,
    # 0x60 `
    0x18, 0x18, 0x0c, 0x04, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    # 0x61 a
    0x00, 0x00, 0x00, 0x3e, 0x7f, 0xe7, 0xc3, 0xc3,
    0xc3, 0xe7, 0x7f, 0x3f, 0x00, 0x00, 0x00, 0x00,
    # 0x62 b
    0xc0, 0xc0, 0xc0, 0xfc, 0xfe, 0xe7, 0xc3, 0xc3,
    0xc3, 0xe7, 0xfe, 0xfc, 0x00, 0x00, 0x00, 0x00,
    # 0x63 c
    0x00, 0x00, 0x00, 0x3e, 0x7f, 0xe3, 0xc0, 0xc0,
    0xc0, 0xe3, 0x7f, 0x3e, 0x00, 0x00, 0x00, 0x00,
    # 0x64 d
    0x03, 0x03, 0x03, 0x3f, 0x7f, 0xe7, 0xc3, 0xc3,
    0xc3, 0xe7, 0x7f, 0x3f, 0x00, 0x00, 0x00, 0x00,
    # 0x65 e
    0x00, 0x00, 0x00, 0x3c, 0x7e, 0xc3, 0xff, 0xff,
    0xc0, 0xe3, 0x7f, 0x3e, 0x00, 0x00, 0x00, 0x00,
    # 0x66 f
    0x1e, 0x3e, 0x30, 0x30, 0xfe, 0xfe, 0x30, 0x30,
    0x30, 0x30, 0x30, 0x30, 0x00, 0x00, 0x00, 0x00,
    # 0x67 g
    0x00, 0x00, 0x00, 0x3f, 0x7f, 0xe7, 0xc3, 0xc3,
    0xc3, 0xe7, 0x7f, 0x3f, 0x03, 0x7f, 0x3e, 0x00,
    # 0x68 h
    0xc0, 0xc0, 0xc0, 0xdc, 0xfe, 0xe7, 0xc3, 0xc3,
    0xc3, 0xc3, 0xc3, 0xc3, 0x00, 0x00, 0x00, 0x00,
    # 0x69 i
    0x18, 0x18, 0x00, 0x00, 0x18, 0x18, 0x18, 0x18,
    0x18, 0x18, 0x18, 0x18, 0x00, 0x00, 0x00, 0x00,
    # 0x6a j
    0x06, 0x06, 0x00, 0x00, 0x06, 0x06, 0x06, 0x06,
    0x06, 0x06, 0x06, 0x06, 0x66, 0x7e, 0x3c, 0x00,
    # 0x6b k
    0xc0, 0xc0, 0xc0, 0xc0, 0xc6, 0xce, 0xdc, 0xf8,
    0xfc, 0xee, 0xc7, 0xc3, 0x00, 0x00, 0x00, 0x00,
    # 0x6c l
    0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18,
    0x18, 0x18, 0x18, 0x18, 0x00, 0x00, 0x00, 0x00,
    # 0x6d m
    0x00, 0x00, 0x00, 0x66, 0xff, 0xff, 0xdb, 0xdb,
    0xdb, 0xdb, 0xdb, 0xdb, 0x00, 0x00, 0x00, 0x00,
    # 0x6e n
    0x00, 0x00, 0x00, 0xde, 0xff, 0xe7, 0xc3, 0xc3,
    0xc3, 0xc3, 0xc3, 0xc3, 0x00, 0x00, 0x00, 0x00,
    # 0x6f o
    0x00, 0x00, 0x00, 0x3c, 0x7e, 0xe7, 0xc3, 0xc3,
    0xc3, 0xe7, 0x7e, 0x3c, 0x00, 0x00, 0x00, 0x00,
    # 0x70 p
    0x00, 0x00, 0x00, 0xfc, 0xfe, 0xe7, 0xc3, 0xc3,
    0xc3, 0xe7, 0xfe, 0xfc, 0xc0, 0xc0, 0xc0, 0x00,
    # 0x71 q
    0x00, 0x00, 0x00, 0x3f, 0x7f, 0xe7, 0xc3, 0xc3,
    0xc3, 0xe7, 0x7f, 0x3f, 0x03, 0x03, 0x03, 0x00,
    # 0x72 r
    0x00, 0x00, 0x00, 0xde, 0xfe, 0xe0, 0xc0, 0xc0,
    0xc0, 0xc0, 0xc0, 0xc0, 0x00, 0x00, 0x00, 0x00,
    # 0x73 s
    0x00, 0x00, 0x00, 0x3c, 0x7e, 0xc3, 0xe0, 0x7e,
    0x07, 0xc3, 0x7e, 0x3c, 0x00, 0x00, 0x00, 0x00,
    # 0x74 t
    0x18, 0x18, 0x18, 0xff, 0xff, 0x18, 0x18, 0x18,
    0x18, 0x18, 0x1e, 0x0e, 0x00, 0x00, 0x00, 0x00,
    # 0x75 u
    0x00, 0x00, 0x00, 0xc3, 0xc3, 0xc3, 0xc3, 0xc3,
    0xc3, 0xe7, 0x7f, 0x3b, 0x00, 0x00, 0x00, 0x00,
    # 0x76 v
    0x00, 0x00, 0x00, 0xc3, 0xc3, 0x63, 0x66, 0x66,
    0x3c, 0x3c, 0x18, 0x18, 0x00, 0x00, 0x00, 0x00,
    # 0x77 w
    0x00, 0x00, 0x00, 0xc3, 0xc3, 0xc3, 0xdb, 0xdb,
    0xdb, 0xff, 0x7e, 0x66, 0x00, 0x00, 0x00, 0x00,
    # 0x78 x
    0x00, 0x00, 0x00, 0xc3, 0xe7, 0x66, 0x3c, 0x18,
    0x3c, 0x66, 0xe7, 0xc3, 0x00, 0x00, 0x00, 0x00,
    # 0x79 y
    0x00, 0x00, 0x00, 0xc3, 0xc3, 0xc3, 0xc3, 0xc3,
    0xc3, 0xe7, 0x7f, 0x3f, 0x07, 0x7e, 0x7c, 0x00,
    # 0x7a z
    0x00, 0x00, 0x00, 0xff, 0xff, 0x06, 0x0c, 0x18,
    0x30, 0x60, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00,
    # 0x7b {
    0x0e, 0x1c, 0x18, 0x18, 0x18, 0x18, 0x30, 0x70,
    0x30, 0x18, 0x18, 0x18, 0x18, 0x1c, 0x0e, 0x00,
    # 0x7c |
    0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18,
    0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x00,
    # 0x7d }
    0x70, 0x38, 0x18, 0x18, 0x18, 0x18, 0x0c, 0x0e,
    0x0c, 0x18, 0x18, 0x18, 0x18, 0x38, 0x70, 0x00,
    # 0x7e ~
    0x00, 0x00, 0x00, 0x00, 0x70, 0xfb, 0xdf, 0x0e,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
))


class Canvas(framebuf.FrameBuffer):
    """
    Canvas class inherits and extends MicroPython's Framebuffer
    primitives with:
        color565      - convert 8-bit RGB values to 16-bit RGB565 format
        round_rect    - draw rounded rectangle
        text          - write string using MicroPython's built-in 8x8 pixel font
        text16        - write string using the built-in 10x16 pixel font
        text16_width  - return the pixel width of a string in the 10x16 font
        text16_height - return the pixel height of the 10x16 font (always 16)
        triangle      - draw a triangle using three vertices
        write         - write string using a converted TrueType font
        write_width   - return the pixel width of a string in a TrueType font
        write_height  - return the pixel height of a converted TrueType font
        bitmap        - draw a palette-compressed bitmap image
        bitmap_to_buffer - convert a palette-compressed bitmap to a raw RGB565
                        bytearray for fast repeated drawing with blit_buffer()
        polygon       - draw a polygon with optional rotation
        
    """
    
    def __init__(self, buffer, width, height, format):
        self.display_buffer = buffer
        super().__init__(self.display_buffer, width, height, format)
        # Character buffer and canvas for write() - allocated once and reused.
        # Reallocated only when the font changes (fonts differ in MAX_WIDTH/HEIGHT).
        self._char_font = None      # Font module currently sized for
        self._char_buffer = None    # bytearray backing _char_canvas
        self._char_canvas = None    # FrameBuffer wrapping _char_buffer
        
    def color565(self, red, green, blue):
        """
        Convert red, green and blue values (0-255) into 16-bit RGB565 encoding.
        """
        return (red & 0xF8) << 8 | (green & 0xFC) << 3 | blue >> 3

    def round_rect(self, x, y, w, h, r, color, fill=False):
        """
        Draw a rounded rectangle at the given location, size, and color.
 
        Parameters:
            x (int): top left bounding box x pixel position
            y (int): top left bounding box y pixel position
            w (int): width of bounding box in pixels           
            h (int): height of bounding box in pixels
            r (int): corner radius in pixels
            color (int): rectangle color (RGB565)
            fill (bool): outline (default), or optional fill (True) with color

        """
        
        r2 = 2 * r      # Bounds check r
        if r2 > w:
            r = w // 2
        if r2 > h:
            r = h // 2
        r2 = 2 * r      # Update r2 in case it has changed

        x1 = x + r
        x2 = x + w - 1 - r
        y1 = y + r
        y2 = y + h - 1 - r
        
        if not fill:
            vseg = h-r2     # Draw vertical line segments if longer than 0
            if vseg > 0:
                self.vline(x, y1, vseg, color)
                self.vline(x2+r, y1, vseg, color)
            hseg = w-r2     # Draw horizontal line segments if longer than 0
            if hseg > 0:
                self.hline(x1, y, hseg, color)
                self.hline(x1, y2+r, hseg, color)
        else:
            self.rect(x, y1, w, h-r2, color, fill)
            self.rect(x+r, y, w-r2, r, color, fill)
            self.rect(x+r, y2+1, w-r2, r, color, fill)
                
        self.ellipse(x2, y1, r, r, color, fill, 1)  # Quadrant 1 - top right
        self.ellipse(x1, y1, r, r, color, fill, 2)  # Quadrant 2 - top left
        self.ellipse(x1, y2, r, r, color, fill, 4)  # Quadrant 3 - bottom left
        self.ellipse(x2, y2, r, r, color, fill, 8)  # Quadrant 4 - bottom right

    def text(self, string, x, y, color=None):
        """
        Write a text string using MicroPython's built-in 8x8 pixel font.
        No font file is required. If color is not given, text is drawn
        in 75% white. Each character is 8 pixels wide and 8 pixels tall,
        giving up to 30 characters per row on a 240-pixel wide display.

        Parameters:
            string (str): The string to write
            x (int): Left edge of the first character
            y (int): Top edge of the characters
            color (int): Text color (RGB565, optional, defaults to 75% white)
        """
        if color is None:
            color = _TEXT_COLOR
        super().text(string, x, y, color)

    def text16(self, string, x, y, color=None):
        """
        Write a text string using the built-in 10x16 pixel font. No
        font file is required. If color is not given, text is drawn in
        75% white. Each character is 10 pixels wide and 16 pixels tall,
        giving up to 24 characters per row on a 240-pixel wide display.

        Parameters:
            string (str): The string to write
            x (int): Left edge of the first character
            y (int): Top edge of the characters
            color (int): Text color (RGB565, optional, defaults to 75% white)
        """
        if color is None:
            color = _TEXT_COLOR

        # Bind frequently accessed values local variable for faster access
        buf    = self.display_buffer
        width  = self.width
        height = self.height
        c_lo   = color & 0xFF
        c_hi   = color >> 8
        stride = width * 2          # Bytes per display row in the framebuffer

        for char in string:
            code = ord(char) - 0x20
            if 0 <= code < 95:
                offset = code * 16  # 16 bytes per character (1 byte per row)
                for row in range(16):
                    py = y + row
                    if 0 <= py < height:    # Skip rows outside display bounds
                        byte = _MIROBO16[offset + row]
                        if byte:            # Skip empty rows with no set pixels
                            row_base = py * stride
                            for col in range(8):
                                if byte & (0x80 >> col):
                                    px = x + col
                                    if 0 <= px < width:
                                        buf_idx = row_base + px * 2
                                        buf[buf_idx]     = c_lo
                                        buf[buf_idx + 1] = c_hi
            x += 10  # Character spacing

    def text16_width(self, string):
        """
        Returns the pixel width of a string written in the built-in
        10x16 font. Character glyphs are 8 pixels wide, and are
        displayed spaced 10 pixels apart.

        Parameters:
            string (str): The string to measure

        Returns:
            int: The width of the string in pixels
        """
        return len(string) * 10

    def text16_height(self):
        """
        Returns the pixel height of the built-in 10x16 font (always 16).

        Returns:
            int: The height of the builtin 10x16 font in pixels (16)
        """
        return 16

    def triangle(self, x0, y0, x1, y1, x2, y2, color, fill=False):
        """
        Draw a triangle defined by three vertices, in the given color.

        Parameters:
            x0, y0 (int): first vertex
            x1, y1 (int): second vertex
            x2, y2 (int): third vertex
            color (int): triangle color (RGB565)
            fill (bool): outline (default), or optional fill (True) with color
        """
        if not fill:
            self.line(x0, y0, x1, y1, color)
            self.line(x1, y1, x2, y2, color)
            self.line(x2, y2, x0, y0, color)
        else:
            self.poly(0, 0, array('h', [x0, y0, x1, y1, x2, y2]), color, True)

    def write(self, string, x, y, font, fg=0xFFFF, bg=None):
        """
        Writes a string to the MicroPython FrameBuffer using a converted
        True-Type font. Each character in the string is created in a
        one character width * height sized memory buffer and blitted
        to the display FrameBuffer starting at the x and y coordinates
        marking the top left of the string bounding box. The string is
        written in white (default) or in an optional foreground (fg)
        color, onto either a transparent background (None) or onto an
        optional background (bg) color.

        Use https://github.com/russhughes/st7789py_mpy/utils/text_font_converter.py
        to convert the TTF font files into python-formatted font data
        files. Upload the converted fonts into the on-board memory of
        your device and import the font file(s) into your program as
        shown:
        
        import NotoSansDisplay_24 as font24
        lcd.write("Hello, world!", 10, 10, font24)

        Parameters:
            string (string): The string to write
            x (int): column to write starting letter of string
            y (int): row to write starting letter of string
            font (font): The module containing the converted true-type font
            fg (int): foreground color (RGB565, optional), defaults to WHITE
            bg (int): background color (RGB565, optional), defaults to transparent
        """
        # Reallocate the character buffer and canvas only when the font changes.
        # The same bytearray is used for both direct byte writes and char_canvas
        # blitting, so both references must stay in sync.
        if font is not self._char_font:
            char_size = font.MAX_WIDTH * font.HEIGHT * 2
            self._char_buffer = bytearray(char_size)
            self._char_canvas = framebuf.FrameBuffer(
                self._char_buffer, font.MAX_WIDTH, font.HEIGHT, framebuf.RGB565
            )
            self._char_font = font
        char_buffer = self._char_buffer
        char_canvas = self._char_canvas

        # Build a character index cache on the font module the first time it
        # is used. This makes MAP lookups O(1) instead of O(n) per character.
        # The cache is stored on the font module object itself so it persists
        # across calls and is shared between write() and write_width().
        if not hasattr(font, '_map_cache'):
            font._map_cache = {c: i for i, c in enumerate(font.MAP)}
        map_cache = font._map_cache

        # Bind frequently accessed font attributes to locals. Local variable
        # access is faster than repeated module attribute lookups in MicroPython,
        # particularly for values used inside the inner pixel loop.
        bitmaps     = font.BITMAPS
        offsets     = font.OFFSETS
        widths      = font.WIDTHS
        max_width   = font.MAX_WIDTH
        height      = font.HEIGHT
        offset_width = font.OFFSET_WIDTH

        fg_hi = fg >> 8
        fg_lo = fg & 0xFF

        if bg is None:
            # Choose a transparency key value that is guaranteed not to
            # equal fg colour, so blit() never treats a foreground pixel
            # as transparent. Flipping all bits ensures the key value always
            # differs from fg; the one edge case (fg == 0xFFFF) falls back
            # to 0x0000.
            transparent = (fg ^ 0xFFFF) if fg != 0xFFFF else 0x0000
            fill_colour = transparent
        else:
            fill_colour = bg

        for character in string:
            char_index = map_cache.get(character)
            if char_index is None:
                continue                    # Character not in font, skip it

            offset = char_index * offset_width
            bs_bit = offsets[offset]
            if offset_width > 1:
                bs_bit = (bs_bit << 8) + offsets[offset + 1]
            if offset_width > 2:
                bs_bit = (bs_bit << 8) + offsets[offset + 2]

            char_width = widths[char_index]

            # Pre-fill the buffer with the background or transparency key.
            # The pixel loop writes only foreground pixels.
            char_canvas.fill(fill_colour)

            # Iterate only over the char_width active columns per row.
            # The font bitmap stores exactly char_width bits per row with no
            # padding, so bs_bit advances char_width times per row naturally.
            # Uses bitwise ops (>> 3, & 7) instead of // and % for speed.
            for row in range(height):
                for col in range(char_width):
                    if bitmaps[bs_bit >> 3] & 1 << (7 - (bs_bit & 7)):
                        idx = (row * max_width + col) * 2
                        char_buffer[idx]     = fg_lo
                        char_buffer[idx + 1] = fg_hi
                    bs_bit += 1

            if bg is None:
                self.blit(char_canvas, x, y, transparent)
            else:
                self.blit(char_canvas, x, y)

            x += char_width

    def write_width(self, string, font):
        """
        Returns the width of the string written in the specified font
        in pixels.

        Parameters:
            string (string): The string to measure
            font (font): The module containing the converted true-type font

        Returns:
            int: The width of the string in pixels

        """
        if not hasattr(font, '_map_cache'):
            font._map_cache = {c: i for i, c in enumerate(font.MAP)}
        map_cache = font._map_cache

        width = 0
        for character in string:
            char_index = map_cache.get(character)
            if char_index is not None:
                width += font.WIDTHS[char_index]

        return width

    def write_height(self, font):
        """
        Returns the height of characters written in the specified font
        in pixels. All characters in a converted TrueType font share the
        same height.

        Parameters:
            font (font): The module containing the converted true-type font

        Returns:
            int: The height of the font in pixels

        """
        return font.HEIGHT

    def bitmap(self, bitmap, x=0, y=0, index=0, transparent=None):
        """
        Draw a palette-compressed bitmap at position x, y. The bitmap can be
        any size and is clipped to the display bounds. Supports an optional
        transparent palette index to skip drawing those pixels, allowing the
        existing framebuffer background to show through.

        Use image_converter.py to convert image files into bitmap modules:
            python image_converter.py image.png bits_per_pixel > bitmap.py

        Parameters:
            bitmap (module): The module containing the bitmap to draw
            x (int): Left edge of the bitmap on the display (default 0)
            y (int): Top edge of the bitmap on the display (default 0)
            index (int): Index of bitmap to draw from a multi-bitmap module
                         (default 0)
            transparent (int): Palette index to treat as transparent; pixels
                         with this index are not drawn (default None)
        """
        bm_w    = bitmap.WIDTH
        bm_h    = bitmap.HEIGHT
        bpp     = bitmap.BPP
        palette = bitmap.PALETTE
        bm_data = bitmap.BITMAP

        # Starting bit offset for the requested index — WIDTH * HEIGHT * BPP
        # bits per image (not bytes, fixing the original byte-based calculation)
        bs_bit  = bm_w * bm_h * bpp * index

        # Clip bitmap bounds to display area
        x0 = max(x, 0)
        y0 = max(y, 0)
        x1 = min(x + bm_w, self.width)
        y1 = min(y + bm_h, self.height)

        stride = self.width * 2     # Bytes per display row in the framebuffer

        for row in range(bm_h):
            for col in range(bm_w):
                # Extract BPP bits MSB-first to form the palette index
                color_index = 0
                for _ in range(bpp):
                    color_index = (color_index << 1) | (
                        (bm_data[bs_bit >> 3] >> (7 - (bs_bit & 7))) & 1
                    )
                    bs_bit += 1

                # Write pixel only if within clipped bounds and not transparent
                px = x + col
                py = y + row
                if x0 <= px < x1 and y0 <= py < y1:
                    if color_index != transparent:
                        color = palette[color_index]
                        buf_idx = (py * stride) + px * 2
                        self.display_buffer[buf_idx]     = color & 0xFF
                        self.display_buffer[buf_idx + 1] = color >> 8

    def bitmap_to_buffer(self, bitmap, index=0):
        """
        Convert a palette-compressed bitmap module to a raw RGB565 bytearray.
        Decode once at startup, then use the returned buffer with
        blit_buffer(buf, x, y, width, height) during every update loop.
        
        Typical usage:
            import sprite
            sprite_buf = lcd.bitmap_to_buffer(sprite)
            del sys.modules['sprite']; del sprite   # free module RAM
            import gc; gc.collect()

            # In game loop:
            lcd.blit_buffer(sprite_buf, x, y, sprite.WIDTH, sprite.HEIGHT)

        Parameters:
            bitmap (module): The module containing the bitmap to convert
            index (int): Index of bitmap to convert from a multi-bitmap module
                         (default 0)

        Returns:
            bytearray: Raw RGB565 pixel data, WIDTH * HEIGHT * 2 bytes,
                       ready to pass to blit_buffer()
        """
        bm_w    = bitmap.WIDTH
        bm_h    = bitmap.HEIGHT
        bpp     = bitmap.BPP
        palette = bitmap.PALETTE
        bm_data = bitmap.BITMAP
        bs_bit  = bm_w * bm_h * bpp * index

        buf = bytearray(bm_w * bm_h * 2)
        buf_idx = 0

        for _ in range(bm_w * bm_h):
            color_index = 0
            for _ in range(bpp):
                color_index = (color_index << 1) | (
                    (bm_data[bs_bit >> 3] >> (7 - (bs_bit & 7))) & 1
                )
                bs_bit += 1
            color = palette[color_index]
            buf[buf_idx]     = color & 0xFF
            buf[buf_idx + 1] = color >> 8
            buf_idx += 2

        return buf
        
    def polygon(self, x, y, points, color, angle=0, center_x=0, center_y=0):
        """
        Draw a polygon on the display.

        Parameters:
            x (int): X-coordinate of the polygon's position.
            y (int): Y-coordinate of the polygon's position.
            points (list): List of points to draw.
            color (int): 565 encoded color.
            angle (float): Rotation angle in radians (default: 0).
            center_x (int): X-coordinate of the rotation center (default: 0).
            center_y (int): Y-coordinate of the rotation center (default: 0).

        Raises:
            ValueError: If the polygon has less than 3 points.
        """
        if len(points) < 3:
            raise ValueError("Polygon must have at least 3 points.")

        if angle:
            cos_a = cos(angle)
            sin_a = sin(angle)
            rotated = [
                (
                    x
                    + center_x
                    + int(
                        (point[0] - center_x) * cos_a - (point[1] - center_y) * sin_a
                    ),
                    y
                    + center_y
                    + int(
                        (point[0] - center_x) * sin_a + (point[1] - center_y) * cos_a
                    ),
                )
                for point in points
            ]
        else:
            rotated = [(x + int((point[0])), y + int((point[1]))) for point in points]

        for i in range(1, len(rotated)):
            self.line(
                rotated[i - 1][0],
                rotated[i - 1][1],
                rotated[i][0],
                rotated[i][1],
                color,
            )
        self.line(rotated[-1][0], rotated[-1][1], rotated[0][0], rotated[0][1], color)

class LCD(Canvas):
    """
    ST7789-based LCD driver class

    Parameters:
        spi (spi): spi object **Required**
        width (int): display width **Required**
        height (int): display height **Required**
        reset (pin): reset pin
        dc (pin): dc pin **Required**
        cs (pin): cs pin
        backlight(pin): backlight pin
        rotation (int):

          - 0-Portrait
          - 1-Landscape
          - 2-Inverted Portrait
          - 3-Inverted Landscape

        color_order (int):

          - LCD.RGB: Red, Green, Blue (default)
          - LCD.BGR: Blue, Green, Red

        custom_init (tuple): custom initialization commands

          - ((b'command', b'data', delay_ms), ...)

        custom_rotations (tuple): custom rotation definitions

          - ((MADCTL, WIDTH, HEIGHT, xstart, ystart, needs_swap), ...)
          
        format (constant): framebuf.RGB565 is pre-selected
        
        buffer (byte array): frame buffer in memory
          
    Functions:
        init() - send initialization commands
        hard_reset() - hardware reset using reset pin
        soft_reset() - software reset
        invert_mode(bool) - invert display when True
        sleep_mode(bool) - display sleep (True), display on (False)
        rotation(int) - set display rotation (0-3)
        update() - blit framebuffer to LCD
        blit_buffer(
            buffer - buffer object
            x (int) - display x position
            y (int) - display y position
            width (int) - buffer width
            height (int) - buffer height
            )   

    """

    # Color order constants for color_order parameter in __init__()
    RGB = 0x00  # Red, Green, Blue (default)
    BGR = 0x08  # Blue, Green, Red

    # Color definitions - includes color, 75% color brightness, 50% color brightness
    WHITE = const(0xFFFF)
    WHITE75 = const(0xBDF7)
    WHITE50 = const(0x4208)
    YELLOW = const(0xFFE0)
    YELLOW75 = const(0xBDE0)
    YELLOW50 = const(0x4200)
    CYAN = const(0x07FF)
    CYAN75 = const(0x05FB)
    CYAN50 = const(0x0208)
    GREEN = const(0x07E0)
    GREEN75 = const(0x05E0)
    GREEN50 = const(0x0400)
    MAGENTA = const(0xF81F)
    MAGENTA75 = const(0xB817)
    MAGENTA50 = const(0x4008)
    RED = const(0xF800)
    RED75 = const(0xB800)
    RED50 = const(0x4000)
    BLUE = const(0x001F)
    BLUE75 = const(0x0017)
    BLUE50 = const(0x0004)
    BLACK = const(0x0000)
    GREY = const(0x2104)
    GRAY = const(0x2104)

    def __init__(
        self,
        spi,
        width,
        height,
        reset=None,
        dc=None,
        cs=None,
        backlight=None,
        rotation=0,
        color_order=None,
        custom_init=None,
        custom_rotations=None,
        format=framebuf.RGB565,
        display_buffer=None,
    ):
        """
        Initialize LCD.
        """
        if color_order is None:
            color_order = LCD.RGB
        if display_buffer is None:
            display_buffer = bytearray(width * height * 2)
        super().__init__(display_buffer, width, height, format)

        self.rotations = custom_rotations or self._find_rotations(width, height)
        if not self.rotations:
            supported_displays = ", ".join(
                [f"{display[0]}x{display[1]}" for display in _SUPPORTED_DISPLAYS]
            )
            raise ValueError(
                f"Unsupported {width}x{height} display. Supported displays: {supported_displays}"
            )

        if dc is None:
            raise ValueError("DC pin is required.")

        self.width = width
        self.height = height
        self.xstart = 0
        self.ystart = 0
        self.spi = spi
        self.reset = reset
        self.dc = dc
        self.cs = cs
        self.backlight = backlight
        self._rotation = rotation % 4
        self.color_order = color_order
        self.init_cmds = custom_init or _ST7789_INIT_CMDS
        self.soft_reset()
        # Initialize twice: some ST7789 panels don't reliably complete
        # all settings in a single pass after a soft reset.
        self.init(self.init_cmds)
        self.init(self.init_cmds)
        self.rotation(self._rotation)
        self.fill(0x0)

        if backlight is not None:
            backlight.value(1)

    @staticmethod
    def _find_rotations(width, height):
        for display in _SUPPORTED_DISPLAYS:
            if display[0] == width and display[1] == height:
                return display[2]
        return None

    def init(self, commands):
        """
        Send initialization commands.
        """
        for command, data, delay in commands:
            self._write(command, data)
            sleep_ms(delay)

    def hard_reset(self):
        """
        Hardware reset display (Usable only if LCD reset line is controllable).
        """
        if self.cs:
            self.cs.value(0)
        if self.reset:
            self.reset.value(1)
        sleep_ms(10)
        if self.reset:
            self.reset.value(0)
        sleep_ms(10)
        if self.reset:
            self.reset.value(1)
        sleep_ms(120)
        if self.cs:
            self.cs.value(1)

    def soft_reset(self):
        """
        Software reset display controller.
        """
        self._write(_ST7789_SWRESET)
        sleep_ms(5)

    def invert_mode(self, value):
        """
        Enable or disable display inverted color mode.

        Parameters:
            value (bool): if True enable inverted color mode, if False disable
            inversion mode
        """
        if value:
            self._write(_ST7789_INVON)
        else:
            self._write(_ST7789_INVOFF)

    def sleep_mode(self, value):
        """
        Enable or disable display sleep mode.

        Parameters:
            value (bool): if True enable sleep mode, if False disable sleep
            mode
        """
        if value:
            if self.backlight is not None:
                self.backlight.value(0)
            self._write(_ST7789_SLPIN)
        else:
            self._write(_ST7789_SLPOUT)
            if self.backlight is not None:
                self.backlight.value(1)
            sleep_ms(5)

    def rotation(self, rotation):
        """
        Set display rotation.

        Parameters:
            rotation (int):
                - 0-Portrait
                - 1-Landscape
                - 2-Inverted Portrait
                - 3-Inverted Landscape

            custom_rotations can have any number of rotations
        """
        rotation %= len(self.rotations)
        self._rotation = rotation
        (
            madctl,
            self.width,
            self.height,
            self.xstart,
            self.ystart,
            self.needs_swap,
        ) = self.rotations[rotation]

        if self.color_order == LCD.BGR:
            madctl |= _ST7789_MADCTL_BGR
        else:
            madctl &= ~_ST7789_MADCTL_BGR

        self._write(_ST7789_MADCTL, bytes([madctl]))

    def blit_buffer(self, buffer, x, y, width, height):
        """
        Copy the buffer to the LCD display memory at the given location.

        Parameters:
            buffer (bytes): Data to copy to display
            x (int): Top left corner x coordinate
            y (int): Top left corner y coordinate
            width (int): Width
            height (int): Height
        """
        self._set_window(x, y, x + width - 1, y + height - 1)
        self._write(None, buffer)

    def update(self, x=0, y=0, w=None, h=None):
        """
        Blit framebuffer to LCD display memory.

        Without arguments, updates the entire display. With x, y, w, h
        arguments, updates only the specified rectangular region. This
        dirty-rectangle update is faster when only a small area of the
        framebuffer has changed, since fewer bytes are sent over SPI.

        The region is clamped to the display bounds automatically.

        Parameters:
            x (int): Left edge of update region (default 0)
            y (int): Top edge of update region (default 0)
            w (int): Width of update region (default: full display width)
            h (int): Height of update region (default: full display height)
        """
        if w is None:
            w = self.width
        if h is None:
            h = self.height

        # Clamp region to display bounds
        x = max(0, min(x, self.width))
        y = max(0, min(y, self.height))
        w = max(0, min(w, self.width - x))
        h = max(0, min(h, self.height - y))

        if w == 0 or h == 0:
            return

        if x == 0 and y == 0 and w == self.width and h == self.height:
            # Full update: send the entire framebuffer in one operation
            self.blit_buffer(self.display_buffer, 0, 0, self.width, self.height)
        else:
            # Partial update: assemble the sub-region row by row into a
            # temporary buffer, then send it in a single blit_buffer() call.
            row_bytes = w * 2                           # Bytes per row in the region
            stride = self.width * 2                     # Bytes per row in the framebuffer
            region = bytearray(row_bytes * h)
            for row in range(h):
                src = (y + row) * stride + x * 2
                dst = row * row_bytes
                region[dst:dst + row_bytes] = self.display_buffer[src:src + row_bytes]
            self.blit_buffer(region, x, y, w, h)

    def _write(self, command=None, data=None):
        """
        SPI write to the device: commands and data.
        """
        if self.cs:
            self.cs.value(0)
        if command is not None:
            self.dc.value(0)
            self.spi.write(command)
        if data is not None:
            self.dc.value(1)
            self.spi.write(data)
        if self.cs:
            self.cs.value(1)

    def _set_window(self, x0, y0, x1, y1):
        """
        Set window to column and row address.

        Parameters:
            x0 (int): column start address
            y0 (int): row start address
            x1 (int): column end address
            y1 (int): row end address
        """
        if x0 <= x1 <= self.width and y0 <= y1 <= self.height:
            self._write(
                _ST7789_CASET,
                struct.pack(_ENCODE_POS, x0 + self.xstart, x1 + self.xstart),
            )
            self._write(
                _ST7789_RASET,
                struct.pack(_ENCODE_POS, y0 + self.ystart, y1 + self.ystart),
            )
            self._write(_ST7789_RAMWR)

