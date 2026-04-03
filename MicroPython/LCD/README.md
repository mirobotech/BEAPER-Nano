# MicroPython LCD Driver for BEAPER Nano and BEAPER Pico

This module implements a MicroPython driver for the optional 240x240 pixel 1.54" LCD display module used with BEAPER Nano and BEAPER Pico circuits. It merges Russ Hughes' MicroPyton ST7789 LCD driver with MicroPython's FrameBuffer while adding additional functionality in a stylistically common way. 

The primary goals of this driver are: 1) to implement a simplified set of LCD control functions and graphics primitives in a style common to MicroPython's built-in frame buffer, and 2) to leverage MicroPython's frame buffer for consistent and fast operation.

This LCD.py driver is extended from Russ Hughes' extensive and excellent [st7789py_mpy] (https://github.com/russhughes/st7789py_mpy) driver, and the utilities on the linked GitHub page can be used to convert TrueType fonts and bitmap images for use with this driver. The LCD.py driver implements the LCD control functions, graphics functions, and text functions listed below, and also pre-defines a set of RGB565 color values.


## LCD control functions

* init() - initialize the LCD panel
    
* hard_reset() - hardware reset the LCD by using the LCD RESET pin. (Not used for BEAPER Nano or BEAPER Pico since their LCD Reset pins are hard-wired to their RESET button circuits.)
    
* soft_reset() - software reset the LCD panel
    
* invert_mode(m) - invert image if m=True
    
* sleep_mode(m) - sleep LCD controller and turn off backlight if m=True
    
* rotation(r) - rotate image to one of 4 orientations (r=0-3, 3 is upright for the way the LCD is mounted on BEAPER Nano and BEAPER Pico)
    
* blit_buffer(b, x, y, w, h) - copy memory buffer b to the LCD display memory at location x, y, using width w, and height h
    
* update([x, y, w, h]) - updates the entire LCD display memory with the contents of the memory buffer when used without arguments. With x, y, w, h arguments, updates only the specified (dirty rectangle) region of the LCD display memory for faster updates.


## LCD graphics functions:

* color565(r, g, b) - convert r, g, b color values to RGB565 format
    
* fill(c) - fill the frame buffer with color c (in RGB565 format)
    
* pixel(x, y [, c]) - draw pixel at x,y in the color c. If c is not supplied, return the color of the pixel at coordinate x,y
    
* hline(x, y, w, c) - draw a horizontal line starting at x,y, width w, using color c
    
* vline(x, y, h, c) - draw a vertical line starting at x,y, height h, using color c
    
* line(x1, y1, x2, y2, c) - draw a line starting at x1,y1, and ending at x2,y2, using color c
    
* rect(x, y, w, h, c, [, f]) - draw a rectangle at x,y, width w, height h, using color c, and optionally fill the rectangle if f=True
    
* round_rect(x, y, w, h, r, c [, f]) - draw a rounded rectangle at x,y, width w, height h, having corner radius r, using color c, and optionally fill the rounded rectangle if f=True
    
* triangle(x1, y1, x2, y2, x3, y3, c [, f]) - draw a triangle with vertices at x1,y1, x2,y2, and x3,y3, using color c, and optionally fill the triangle if f=True
    
* ellipse(x, y, xr, yr, c, [, f, m]) - draw an ellipse centred at x,y, with x radius xr, y radius yr, using color c, and optionally fill the ellipse if f=True. Optional m parameter  enables drawing only one quadrant of the ellipse: 1=top right, 2=top left, 3=bottom left, 4=bottom right
    
* poly(x, y, coords, c [, f]) - draw a polygon at x,y, from array of integer coords (e.g. array('h', [x0, y0, x1, y1, ... xn, yn]), using color c, and optionally fill the polygon if f=True
    
* polygon(x, y, points, color [, angle, center_x, center_y) - draw a rotatable polygon at x, y, from a list of coordinates points, using color c, at an optional rotation angle (radians) and at optional offset center_x and center_y
    
* scroll(xstep, ystep) - scroll the contents of the frame buffer by xstep and ystep
    
* bitmap(bitmap, x, y [, index, transparent]) - draw a palette-compressed bitmap at x,y, clipped to the display bounds. Optional index selects from a multi-bitmap module. Optional  transparent palette index skips drawing transparent pixels.

* bitmap_to_buffer(bitmap [, index]) - convert a palette-compressed bitmap module to a raw RGB565 bytearray for fast repeated drawing using blit_buffer(). Optional index selects from a multi-bitmap module.


## Text functions:

* text(s, x, y [, c]) - write text string s using MicroPython's built-in 8x8 pixel font at location x,y, using optional color c (if color is not provided, text is written using 75% white). Each character is 8 pixels wide and 8 pixels tall, giving up to 30 characters per row on a 240-pixel wide display.

* text16(s, x, y [, c]) - write text string s using this module's built-in 10x16 pixel font at location x,y, using optional color c (if color is not proviced, text is written using 75% white). Each character is 10 pixels wide and 16 pixels tall, giving up to 24 characters per row on a 240-pixel wide display.

* text16_width(s) - return the pixel width of string s in the built-in 10x16 pixel font (always len(s) * 10)

* text16_height() - return the pixel height of the built-in 10x16 pixel font (always 16)

* write(s, x, y, font, fg [, bg]) - write text string s at location x,y, in font 'font' (a font object converted from a TTF font file), using color fg, on a transparent background or using optional background color bg

* write_width(s, font) - return the pixel width of string s written in the specified converted TrueType font

* write_height(font) - return the pixel height of characters in the specified converted TrueType font


** Pre-defined colors:

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


## Example use:

import LCDconfig_Pico as lcd_config     # Custom config for BEAPER Pico I/O
# import LCDconfig_Nano as lcd_config     # Use this config for BEAPER Nano
import NotoSansDisplay_24 as font24     # Load converted display font

lcd = lcd_config.config()               # Create an lcd object

lcd.fill(lcd.BLACK)     # Fill framebuffer with black
lcd.round_rect(0, 0, 200, 40, 10, lcd.BLUE75, True)  # Draw filled blue round rect
lcd.write("Hello, world!", 10, 10, font24, lcd.YELLOW)  # Write text string
lcd.update()            # update the LCD display


