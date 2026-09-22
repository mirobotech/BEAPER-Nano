/* ==============================================================================
Colour Conversion Header [colour.h]
Version: 1.1
Updated: July 25, 2026

Colour conversion functions for Arduino C.

This header converts between colour representations commonly used
with RGB LEDs, NeoPixel strips, and colour LCD displays.

Colour ranges used in this header:
  HSV    - H: 0-360 degrees, S: 0-100 percent, V: 0-100 percent
  RGB    - R, G, B: 0-255 (8-bit per channel)
  RGBW   - R, G, B, W: 0-255 (8-bit per channel)
  RGB565 - single 16-bit value, for colour LCD displays

NOTE: This header's RGB output uses the 8-bit (0-255) range common
to NeoPixel strips and colour displays. BEAPER Nano's on-board RGB
LED uses 'analogWrite()' at the same 8-bit range, so no scaling is
needed to use these functions with 'set_rgb()' in the RGB Controller
project.

NOTE: The intermediate brightness calculations in hsvToRGB() use
'long' rather than 'int' for their products. On boards with a 16-bit
int (such as Arduino UNO Rev 3, used with ARPS-2), a product like
v * (255 - s) can reach 65,025 - larger than a 16-bit int's maximum
of 32,767. Using 'long' for these products keeps the calculation
correct on every board this curriculum supports, not just the ones
with a 32-bit int. See the Numeric Types sidebar for more on how
int size varies by board.

Before getting started with it you should know:
- nothing here is hidden, or **magic**, or requires special libraries
- the functions are just normal Arduino C code to help you start learning
- you're encouraged to modify the code to make it work better for you!
============================================================================== */

#ifndef COLOUR_H
#define COLOUR_H

// ------------------------------------------------------------------------------
// Colour structures
// ------------------------------------------------------------------------------

// A simple structure for an RGB colour
struct RGB {
  uint8_t r;
  uint8_t g;
  uint8_t b;
};

// A simple structure for an RGBW colour
struct RGBW {
  uint8_t r;
  uint8_t g;
  uint8_t b;
  uint8_t w;
};


// ------------------------------------------------------------------------------
// HSV to RGB
// ------------------------------------------------------------------------------

inline RGB hsvToRGB(int h, int s, int v)
{
    // Convert HSV (hue, saturation, value) to 8-bit RGB.
    // h: hue in degrees (0-360, wraps automatically)
    // s: saturation as a percentage (0-100)
    // v: brightness as a percentage (0-100)

    // Keep hue within 0-359 degrees
    h = h % 360;

    // Limit saturation and value
    s = constrain(s, 0, 100);
    v = constrain(v, 0, 100);

    // Convert S and V to the 0-255 range
    s = s * 255 / 100;
    v = v * 255 / 100;

    // Find the hue sector and position within it
    int sector = h / 60;
    int position = h % 60;

    // Calculate the three intermediate brightness values.
    // The products below use 'long' to avoid overflow on boards
    // with a 16-bit int - see the note above.
    int p = (long)v * (255 - s) / 255;
    int q = (long)v * (255 - s * position / 60) / 255;
    int t = (long)v * (255 - s * (60 - position) / 60) / 255;

    RGB colour;

    // Select the RGB values for this hue sector
    if (sector == 0) {
        colour.r = v;
        colour.g = t;
        colour.b = p;
    }
    else if (sector == 1) {
        colour.r = q;
        colour.g = v;
        colour.b = p;
    }
    else if (sector == 2) {
        colour.r = p;
        colour.g = v;
        colour.b = t;
    }
    else if (sector == 3) {
        colour.r = p;
        colour.g = q;
        colour.b = v;
    }
    else if (sector == 4) {
        colour.r = t;
        colour.g = p;
        colour.b = v;
    }
    else {
        colour.r = v;
        colour.g = p;
        colour.b = q;
    }

    return colour;
}


// ------------------------------------------------------------------------------
// HSV to RGBW
// ------------------------------------------------------------------------------

inline RGBW hsvToRGBW(int h, int s, int v)
{
    // Convert HSV to 8-bit RGBW, extracting a white channel from the
    // brightness shared by all three RGB channels. Useful for RGBW
    // NeoPixel strips, which have a dedicated white LED per pixel.

    // Convert HSV to RGB first
    RGB rgb = hsvToRGB(h, s, v);

    // Extract the common brightness as white
    uint8_t w = min(rgb.r, min(rgb.g, rgb.b));

    RGBW colour;

    // Remove the white component from RGB
    colour.r = rgb.r - w;
    colour.g = rgb.g - w;
    colour.b = rgb.b - w;
    colour.w = w;

    return colour;
}


// ------------------------------------------------------------------------------
// RGB to RGB565
// ------------------------------------------------------------------------------

inline uint16_t rgbToRGB565(uint8_t r, uint8_t g, uint8_t b)
{
    // Convert 8-bit RGB to the 16-bit RGB565 format used by many
    // colour LCD displays (5 bits red, 6 bits green, 5 bits blue).
    return ((r >> 3) << 11) |
           ((g >> 2) << 5) |
           (b >> 3);
}

#endif
