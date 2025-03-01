# MicroPython LCD Driver for BEAPER Nano and BEAPER Pico

This module implements an ST7789 LCD driver for the 1.54", 240x240 pixel TFT LCD display panel that can be added to mirobo.tech BEAPER Nano and BEAPER Pico circuit boards. The LCD display panel is controlled over the SPI bus.

The primary goals of this driver are: 1) to implement a simplified set of LCD control functions and graphics primitives in a style common to MicroPython's built-in frame buffer, and 2) to leverage MicroPython's frame buffer for consistent and fast operation.

This LCD.py driver is extended from Russ Hughes' extensive and excellent [st7789py_mpy] (https://github.com/russhughes/st7789py_mpy) driver, and the utilities on the linked GitHub page can be used to convert TrueType fonts and bitmap images for use with this driver. The LCD.py driver implements the LCD control functions, graphics functions, and text functions listed below, and also pre-defines a set of RGB565 color values.


## LCD control functions

* init() - initialize the LCD panel
    
* hard_reset() - hardware reset the LCD panel (This is not used on BEAPER Nano or BEAPER Pico since their microcontrollers are not connected to the RESET pin of the LCD panel. Instead, the LCD RESET pin is connected to the Reset button circuit on these boards.)
    
* soft_reset() - software reset the LCD panel
    
* invert_mode(m) - invert image if m=True
    
* sleep_mode(m) - sleep LCD controller and turn off backlight if m=True
    
* rotation(r) - rotate LCD image to one of 4 orientations (r=0-3, 3 is upright on BEAPER Nano and BEAPER Pico)
    
* blit_buffer(b, x, y, w, h) - copy memory buffer b to LCD display memory at location x, y, using buffer width w, and height h
    
* update() - update the LCD display memory with the contents of the frame buffer


## LCD graphics functions

* fill(c) - fill the frame buffer with color c (in RGB565 format)
    
* color565(r, g, b) - convert r, g, b color values to RGB565 format
    
* pixel(x, y [, c]) - draw pixel at location x, y in color c, or if c is not supplied, return the color of the pixel at location x, y
    
* hline(x, y, w, c) - draw a horizontal line starting at x, y, width w, using color c
    
* vline(x, y, h, c) - draw a vertical line starting at x, y, height h, using color c
    
* line(x1, y1, x2, y2, c) - draw a line starting at location x1, y1, and ending at location x2, y2, using color c
    
* rect(x, y, w, h, c, [, f]) - draw a rectange at x, y, width w, height h, using color c, and optionally fill the rectangle with color c if f=True
    
* round_rect(x, y, w, h, r, c [, f]) - draw a rounded-rectange at x, y, width w, height h, having corner radius r, using color c, and optionally fill the rectangle with color c if f=True
    
* ellipse(x, y, xr, yr, c, [, f, m]) - draw an ellipse centred at x, y, with x radius xr, y radius yr, using color c, and optionally fill the ellipse with color c if f=True. Optional m parameter enables the drawing of only one quadrant of the ellipse: 1=top right, 2=top left, 3=bottom left, 4=bottom right
    
* poly(x, y, coords, c [, f]) - draw a polygon at location x, y, from an array of integer coords (e.g. array('h', [x0, y0, x1, y1, ... xn, yn]), using color c, and optionally fill the polygon with color c if f=True
    
* scroll(xstep, ystep) - scroll the contents of the frame buffer by xstep and ystep
    
* bitmap(bitmap, x, y [, index]) - draw a converted bitmap file at x, y, from an optional index (currently only draws bitmaps with size equal to the display size). The bitmap image must be converted to a python module using Russ Hughes' [image_converter.py] (https://github.com/russhughes/st7789py_mpy/tree/master/utils) program.


## LCD Text functions

* text(s, x, y, [, c]) - write text string s (in a fixed 8x8 pixel font) at location x, y, using color c
    
* write(s, x, y, font, fg [, bg]) - write text string s at location x, y, in font font (a font module converted from a TTF font file using Russ Hughes' [write_font_converter.py] (https://github.com/russhughes/st7789py_mpy/tree/master/utils) program), using color fg, on a transparent background or on top of optional background color bg
    
* write_width(s, font) - return the width of string s, written in font font


## Pre-defined colors:

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


## Example use:

    import LCDconfig_Pico as lcd_config     # Custom config for BEAPER Pico I/O
    # import LCDconfig_Nano as lcd_config     # Use this custom config for BEAPER Nano I/O
    import NotoSansDisplay_24 as notosans24 # Load converted TrueType font
    
    # Create an lcd object. Rotation=3 is the normal BEAPER Pico LCD orientation.
    lcd = lcd_config.config(rotation=3)
    
    lcd.fill(lcd.BLACK)     # Fill LCD framebuffer with black
    lcd.round_rect(0, 0, 200, 40, 10, lcd.BLUE75, True)  # Draw filled blue round rect
    lcd.write("Hello, world!", 10, 10, notosans24, lcd.YELLOW)  # Write yellow text
    lcd.update()            # update the LCD to display the framebuffer contents

