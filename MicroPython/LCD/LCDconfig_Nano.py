"""
BEAPER Nano LCD Configuration for 1.54" 240x240 LCD

Adapted from st7789py_mpy by Russ Hughes:
https://github.com/russhughes/st7789py_mpy

Updated March 1, 2025
"""

from machine import Pin, SPI
import LCD as lcd

TFA = 0
BFA = 80
WIDE = 1
TALL = 0

def config(rotation=3):
    """
    Configures and returns an instance of the ST7789 display driver.

    Args:
        rotation (int): The rotation of the display. BEAPER orientation is 3.

    Returns:
        ST7789: An instance of the ST7789 display driver.
    """
    INIT_CMDS = (
        ( b'\x11', None, 5),    	# SLPOUT - Exit sleep mode
        ( b'\x13', None, 0),		# NORON - Normal display mode on
        ( b'\x20', None, 0),    	# INVOFF - Display inversion off
        ( b'\x26', b'\x01', 0),		# GAMSET - Gamma set curve 1 (g2.2)
        #( b'\x26', b'\x02', 0),		# GAMSET - Gamma set curve 2 (g1.8)
        ( b'\xb0', b'\x00\xf8', 0), # RAMCTRL - Swap endian order
        ( b'\x3a', b'\x55', 5), 	# COLMOD - 16 bit per pixel (RGB565) color mode
        ( b'\xc0', b'\x3c', 0), 	# LCMCTRL - Mirrorring control
        ( b'\x29', b'\x00', 0), 	# DISPON - Turn the display on
    )

    DISPLAY_240x240 = (
        (0x00, 240, 240,  0,  0, True),
        (0x60, 240, 240,  0,  0, True),
        (0xc0, 240, 240,  0, 80, True),
        (0xa0, 240, 240, 80,  0, True),
    )

    return lcd.LCD(
        SPI(2, baudrate=60000000, sck=Pin(48), mosi=Pin(38), miso=None),
        240,
        240,
        reset=None,
        dc=Pin(18, Pin.OUT),
        cs=Pin(21, Pin.OUT),
        backlight=Pin(47, Pin.OUT),
        rotation=rotation,
        custom_init=INIT_CMDS,
        custom_rotations=DISPLAY_240x240,
    )
