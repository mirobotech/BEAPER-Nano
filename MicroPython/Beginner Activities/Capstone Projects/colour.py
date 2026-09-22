# ==============================================================================
# Colour Conversion Module [colour.py]
# Version: 1.2
# Updated: August 15, 2026
#
# 8-bit colour conversion functions for MicroPython.
#
# This module converts colours from HSV (hue, saturation, and value)
# to 8-bit (0-255) RGB and RGBW colour representations commonly used
# by NeoPixel addressable LEDs, and also to 16-bit RGB565 values
# used by colour LCD displays. Integer arithmetic provides fast
# conversion and produces 8-bit (or 16-bit RGB565) values that can
# be passed directly to their hardware functions. 
#
# Colour ranges used by this module:
#   HSV    - Hue: 0-360 degrees, Saturation: 0-100 percent, Value: 0-100 percent
#   RGB    - Red, Green, Blue: 0-255 (8-bit per channel)
#   RGBW   - Red, Green, Blue, White: 0-255 (8-bit per channel)
#   RGB565 - Red (5-bits), Green (6-bits), Blue (5-bits) in a single 16-bit
#            value for colour LCD displays
# ==============================================================================


# ------------------------------------------------------------------------------
# HSV to RGB
# ------------------------------------------------------------------------------

def hsv_to_rgb(h, s=100, v=100):
    # Convert HSV (hue, saturation, value) to 8-bit RGB.
    # h: hue in degrees (0-360, wraps automatically)
    # s: saturation as a percentage (0-100, default 100)
    # v: value (brightness) as a percentage (0-100, default 100)
    # Pass h, s, and v as integers - dividing an int by another int with
    # '//' only reliably stays an int if both operands are already int

    # Keep hue within 0-359 degrees
    h = h % 360

    # Limit saturation and value to 0-100 range
    s = max(0, min(100, s))
    v = max(0, min(100, v))

    # Convert S and V to the 0-255 range
    s = s * 255 // 100
    v = v * 255 // 100

    # Find the hue sector and position within it
    sector = h // 60
    position = h % 60

    # Calculate the three intermediate brightness values
    p = v * (255 - s) // 255
    q = v * (255 - s * position // 60) // 255
    t = v * (255 - s * (60 - position) // 60) // 255

    # Select the RGB values for this hue sector
    if sector == 0:
        r, g, b = v, t, p
    elif sector == 1:
        r, g, b = q, v, p
    elif sector == 2:
        r, g, b = p, v, t
    elif sector == 3:
        r, g, b = p, q, v
    elif sector == 4:
        r, g, b = t, p, v
    else:
        r, g, b = v, p, q

    return (r, g, b)


# ------------------------------------------------------------------------------
# HSV to RGBW
# ------------------------------------------------------------------------------

def hsv_to_rgbw(h, s=100, v=100):
    # Convert HSV to 8-bit RGBW, extracting a white channel from the
    # brightness shared by all three RGB channels. Useful for RGBW
    # NeoPixel strips which use a dedicated white LED per pixel.

    # Convert HSV to RGB first
    r, g, b = hsv_to_rgb(h, s, v)

    # Extract the common brightness as white
    w = min(r, g, b)

    # Remove the white component from RGB
    r -= w
    g -= w
    b -= w

    return (r, g, b, w)


# ------------------------------------------------------------------------------
# RGB to RGB565
# ------------------------------------------------------------------------------

def rgb_to_rgb565(r, g, b):
    # Convert 8-bit RGB to the 16-bit RGB565 format used by colour
    # LCD displays (5 red bits, 6 green bits, and 5 blue bits).

    # Reduce encoding from 8 bits
    r = r >> 3
    g = g >> 2
    b = b >> 3

    # Assemble into RGB565 format
    return (r << 11) | (g << 5) | b
  