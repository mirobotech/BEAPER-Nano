"""
LCD.py
Updated: March 1, 2025

Adapted from Russ Hughes' st7789mpy.py MicroPython ST7789 driver library.
(https://github.com/russhughes/st7789py_mpy)

This module implements an ST7789 LCD driver for the 240x240 pixel TFT LCD
display panel used on mirobo.tech BEAPER Nano and BEAPER Pico circuits. The
MicroPython FrameBuffer class and parts of Russ Hughes driver are merged
to implement a comprehensive set of stylistically common functions:

LCD control functions:

    init() - initialize the LCD panel
    
    hard_reset() - hardware reset the LCD panel (not used on BEAPER Nano or
        BEAPER Pico since the microcontroller does not control the LCD panel
        RESET pin (LCD RESET pin is connected to the Reset button circuit)
    
    soft_reset() - software reset the LCD panel
    
    invert_mode(m) - invert image if m=True
    
    sleep_mode(m) - sleep LCD controller and turn off backlight if m=True
    
    rotation(r) - rotate image to one of 4 orientations (r=0-3, 3 is upright)
    
    blit_buffer(b, x, y, w, h) - copy memory buffer b to LCD display memory at
        location x, y, using width w, and height h
    
    update() - update the LCD display memory with the contents of the frame buffer

LCD graphics functions:

    fill(c) - fill the frame buffer with color c (in RGB565 format)
    
    color565(r, g, b) - convert r, g, b color values to RGB565 format
    
    pixel(x, y [, c]) - draw pixel at x, y in the color c. If c is not
        supplied, return the color of the pixel at the x, y coordinate.
    
    hline(x, y, w, c) - draw a horizontal line starting at x, y, width w,
        using color c
    
    vline(x, y, h, c) - draw a vertical line starting at x, y, height h,
        using color c
    
    line(x1, y1, x2, y2, c) - draw a line starting at x1, y1, and ending
        at x2, y2, using color c
    
    rect(x, y, w, h, c, [, f]) - draw a rectange at x, y, width w, height
        h, using color c, and optionally fill the rectangle if f=True
    
    round_rect(x, y, w, h, r, c [, f]) - draw a rounded rectange at x, y,
        width w, height h, having corner radius r, using color c, and
        optionally fill the rectangle if f=True
    
    ellipse(x, y, xr, yr, c, [, f, m]) - draw an ellipse centred at x, y,
        with x radius xr, y radius yr, using color c, and optionally fill
        the ellipse if f=True. Optional m parameter enables drawing only
        one quadrant of the ellipse: 1=top right, 2=top left, 3=bottom
        left, 4=bottom right
    
    poly(x, y, coords, c [, f]) - draw a polygon at x, y, from an array of
        integer coords (e.g. array('h', [x0, y0, x1, y1, ... xn, yn]),
        using color c, and optionally fill the polygon if f=True
    
    polygon(x, y, points, color [, angle, center_x, center_y]) - draw a
        rotatable polygon at x, y, from a list of coordinates points,
        using color c, at an optional rotation angle (radians) and at
        optional offset center_x and center_y
    
    scroll(xstep, ystep) - scroll the contents of the frame buffer by
        xstep and ystep
    
    bitmap(bitmap, x, y [, index]) - draw a converted bitmap file at x, y,
        from an optional index (currently only draws bitmaps with size equal
        to the display size)

Text functions:

    text(s, x, y, [, c]) - write text string s (in a fixed 8x8 pixel font)
        at location x, y, using color c
    
    write(s, x, y, font, fg [, bg]) - write text string s at location x, y,
        in font font (a font object converted from a TTF font file), using
        color fg, on a transparent background or using optional background
        color bg
    
    write_width(s, font) - return the width of string s, written in font font

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
    GRAY - 25% white
    BLACK - 0% white

Example use:

    import LCDconfig_Pico as lcd_config     # Custom config for BEAPER Pico I/O
    # import LCDconfig_Nano as lcd_config     # Use this config for BEAPER Nano
    import NotoSansDisplay_24 as notosans24 # Load converted display font

    # Create an lcd object. Rotation=3 is the normal BEAPER Pico LCD orientation.
    lcd = lcd_config.config(rotation=3)

    lcd.fill(lcd.BLACK)     # Fill framebuffer with black
    lcd.round_rect(0, 0, 200, 40, 10, lcd.BLUE75, True)  # filled blue round rect
    lcd.write("Hello, world!", 10, 10, notosans24, lcd.YELLOW)  # write text
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

RGB = 0x00
BGR = 0x08

# Color modes - non needed
# _COLOR_MODE_65K = const(0x50)
# _COLOR_MODE_262K = const(0x60)
# _COLOR_MODE_12BIT = const(0x03)
# _COLOR_MODE_16BIT = const(0x05)
# _COLOR_MODE_18BIT = const(0x06)
# _COLOR_MODE_16M = const(0x07)

_ENCODE_PIXEL = const(">H")
_ENCODE_PIXEL_SWAPPED = const("<H")
_ENCODE_POS = const(">HH")
_ENCODE_POS_16 = const("<HH")

# must be at least 128 for 8 bit wide fonts
# must be at least 256 for 16 bit wide fonts
# _BUFFER_SIZE = const(256)

# _BIT7 = const(0x80)
# _BIT6 = const(0x40)
# _BIT5 = const(0x20)
# _BIT4 = const(0x10)
# _BIT3 = const(0x08)
# _BIT2 = const(0x04)
# _BIT1 = const(0x02)
# _BIT0 = const(0x01)

# fmt: off

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

# index values into rotation table
_WIDTH = const(0)
_HEIGHT = const(1)
_XSTART = const(2)
_YSTART = const(3)
_NEEDS_SWAP = const(4)

# Supported displays (physical width, physical height, rotation table)
_SUPPORTED_DISPLAYS = (
    (240, 320, _DISPLAY_240x320),
    (240, 240, _DISPLAY_240x240),
    (135, 240, _DISPLAY_135x240),
    (128, 128, _DISPLAY_128x128))

# Default init from st7789mpy.py library - overridden by LCDconfig_Pico.py
# init tuple format (b'command', b'data', delay_ms)
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

class Canvas(framebuf.FrameBuffer):
    """
    Canvas class inherits and extends MicroPython Framebuffer primitives with:
        round_rect - draw rounded rectangle
        write - write string using converted TrueType font
        write_width - find width of string using converted TrueType font
        prbitmap - draw progressive bitmap
        polygon - draw polygon with rotation
        
    """
    
    def __init__(self, buffer, width, height, format):
        self.display_buffer = buffer
        super().__init__(self.display_buffer, width, height, format)
        
    def color565(self, red, green, blue):
        """
        Convert red, green and blue values (0-255) into a 16-bit 565 encoding.
        """
        return (red & 0xF8) << 8 | (green & 0xFC) << 3 | blue >> 3

    def round_rect(self, x, y, w, h, r, color, fill=False):
        """
        Draw a rounded rectange at the given location, size, and color.
 
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
        
        if fill == False:
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

    def write(self, string, x, y, font, fg=0xFFFF, bg=None):
        """
        Writes a string to the MicroPython FrameBuffer using a converted True-Type
        font. Each character in the string is created in a one character width *
        height sized memory buffer and blitted to the display FrameBuffer starting
        at the x and y coordinates marking the top left of the string bounding box.
        The string is written in white (default) or in an optional foreground (fg)
        color, onto either a transparent background (None) or an optional
        background (bg) color.

        Use https://github.com/russhughes/st7789py_mpy/utils/text_font_converter.py
        to convert the TTF font files into python-formattedd font data files. Upload
        the converted fonts into the on-board memory of your device and import the
        font file(s) into your program. e.g.:
        
        import NotoSansDisplay_24 as notosans24
        lcd.write("Hello, world!", 10, 10, notosans24)

        Parameters:
            string (string): The string to write
            x (int): column to write startoing letter of string
            y (int): row to write starting letter of string
            font (font): The module containing the converted true-type font
            fg (int): foreground color (RGB565, optional), defaults to WHITE
            bg (int): background color (RGB565, optional), defaults to transparent
                      (None) which is internally represented as 0x0020
        """
        char_size = font.MAX_WIDTH * font.HEIGHT * 2
        char_buffer = bytearray(char_size)
        char_canvas = framebuf.FrameBuffer(
            char_buffer, font.MAX_WIDTH, font.HEIGHT, framebuf.RGB565
        )

        fg_hi = fg >> 8
        fg_lo = fg & 0xFF

        if bg is not None:
            bg_hi = bg >> 8
            bg_lo = bg & 0xFF

        for character in string:
            try:
                char_index = font.MAP.index(character)
                offset = char_index * font.OFFSET_WIDTH
                bs_bit = font.OFFSETS[offset]
                if font.OFFSET_WIDTH > 1:
                    bs_bit = (bs_bit << 8) + font.OFFSETS[offset + 1]

                if font.OFFSET_WIDTH > 2:
                    bs_bit = (bs_bit << 8) + font.OFFSETS[offset + 2]

                char_width = font.WIDTHS[char_index]

                if bg is not None:
                    char_canvas.fill(bg)
                else:
                    char_canvas.fill(0x0020)  # fill buffer with transparency value

                char_col = 0
                for i in range(0, char_size, 2):
                    if char_col < char_width:
                        if font.BITMAPS[bs_bit // 8] & 1 << (7 - (bs_bit % 8)) > 0:
                            char_buffer[i] = fg_lo
                            char_buffer[i + 1] = fg_hi
                        else:
                            if bg is not None:
                                char_buffer[i] = bg_lo
                                char_buffer[i + 1] = bg_hi

                        bs_bit += 1
  
                    char_col += 1
                    if char_col == font.MAX_WIDTH:
                        char_col = 0

                if bg is not None:
                    self.blit(char_canvas, x, y)
                else:
                    self.blit(char_canvas, x, y, 0x0020)

                x += char_width

            except ValueError:
                pass

    def write_width(self, string, font):
        """
        Returns the width of the string written in the specified font in pixels.

        Parameters:
            string (string): The string to measure
            font (font): The module containing the converted true-type font

        Returns:
            int: The width of the string in pixels

        """
        width = 0
        for character in string:
            try:
                char_index = font.MAP.index(character)
                width += font.WIDTHS[char_index]
            except ValueError:
                pass

        return width

    def bitmap(self, bitmap, x, y, index=0):
        """
        Draws a converted bitmap image into the MicroPython FrameBuffer. (Currently,
        bitmap size must equal display size.)
        
        Use https://github.com/russhughes/st7789py_mpy/tree/master/utils to convert
        the image file into a Python-formatted data file and upload it into the
        memory of your device.
 
        Parameters:
            bitmap (bitmap_module): The module containing the bitmap to draw
            x (int): column to start drawing at
            y (int): row to start drawing at
            index (int): Optional index of bitmap to draw from multiple bitmap
                module

        """
 
        width = bitmap.WIDTH
        height = bitmap.HEIGHT
        bitmap_size = height * width * 2
        bpp = bitmap.BPP
        bs_bit = bpp * bitmap_size * index  # if index > 0 else 0
        palette = bitmap.PALETTE
        for px in range(0, bitmap_size, 2):
            color_index = 0
            for _ in range(bpp):
                color_index <<= 1
                color_index |= (
                    bitmap.BITMAP[bs_bit // 8] & 1 << (7 - (bs_bit % 8))
                ) > 0
                bs_bit += 1
            color = palette[color_index]
            self.display_buffer[px] = color & 0xFF
            self.display_buffer[px + 1] = color >> 8 & 0xFF
        
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

          - RGB: Red, Green Blue, default
          - BGR: Blue, Green, Red

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
        inversion mode(bool) - invert display when True
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
    GRAY = const(0x2102)

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
        color_order=RGB,
        custom_init=None,
        custom_rotations=None,
        format=framebuf.RGB565,
        display_buffer=None,
    ):
        """
        Initialize LCD.
        """
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
        # yes, twice, once is not always enough
        self.init(self.init_cmds)
        self.init(self.init_cmds)
        self.rotation(self._rotation)
        self.fill(0x0)

        if backlight is not None:
            backlight.value(1)

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
        Hard reset display.
        """
        if self.cs:
            self.cs.off()
        if self.reset:
            self.reset.on()
        sleep_ms(10)
        if self.reset:
            self.reset.off()
        sleep_ms(10)
        if self.reset:
            self.reset.on()
        sleep_ms(120)
        if self.cs:
            self.cs.on()

    def soft_reset(self):
        """
        Soft reset display.
        """
        self._write(_ST7789_SWRESET)
        sleep_ms(5)

    def invert_mode(self, value):
        """
        Enable or disable display inverted color mode.

        Parameters:
            value (bool): if True enable inverted color mode. if False disable
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
            value (bool): if True enable sleep mode. if False disable sleep
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

        if self.color_order == BGR:
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
            Y (int): Top left corner y coordinate
            width (int): Width
            height (int): Height
        """
        self._set_window(x, y, x + width - 1, y + height - 1)
        self._write(None, buffer)

    def update(self):
        """
        Blit entire framebuffer to LCD display memory.
        """
        self.blit_buffer(self.display_buffer, 0, 0, self.width, self.height)

    def _write(self, command=None, data=None):
        """
        SPI write to the device: commands and data.
        """
        if self.cs:
            self.cs.off()
        if command is not None:
            self.dc.off()
            self.spi.write(command)
        if data is not None:
            self.dc.on()
            self.spi.write(data)
            if self.cs:
                self.cs.on()

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


