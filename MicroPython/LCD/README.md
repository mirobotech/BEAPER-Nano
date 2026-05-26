# LCD.py

MicroPython LCD driver for ST7789-based TFT displays, designed for use with [mirobo.tech](https://mirobo.tech) **BEAPER Nano** and **BEAPER Pico** circuits.

Adapted from Russ Hughes' [st7789py_mpy](https://github.com/russhughes/st7789py_mpy) MicroPython ST7789 driver. This module merges the ST7789 hardware driver with MicroPython's `FrameBuffer` class and adds additional graphics and text features.

## Files

| File | Purpose |
|---|---|
| `LCD.py` | ST7789 LCD driver module |
| `LCDconfig_Pico.py` | LCD configuration for BEAPER Pico |
| `LCDconfig_Nano.py` | LCD configuration for BEAPER Nano |

## Compatible Hardware

The included configuration files target the optional **1.54", 240×240 pixel ST7789 TFT LCD** that can be mounted on BEAPER Nano and BEAPER Pico circuits. The driver and config files can be adapted for other ST7789-based LCD sizes and resolutions.

## Getting Started

1. Copy `LCD.py` and the appropriate config file (`LCDconfig_Pico.py` or `LCDconfig_Nano.py`) to your microcontroller.
2. Import the config module and create an `lcd` object:

```python
import LCDconfig_Pico as lcd_config     # BEAPER Pico
# import LCDconfig_Nano as lcd_config   # BEAPER Nano
```

3. Call `config()` to initialize the display:

```python
lcd = lcd_config.config()
```

4. Draw into the framebuffer, then call `update()` to push it to the display:

```python
lcd.fill(lcd.BLACK)
lcd.text16("Hello, world!", 0, 0, lcd.CYAN)
lcd.update()
```

## Quick Example

```python
import LCDconfig_Pico as lcd_config     # Use LCDconfig_Nano for BEAPER Nano
import NotoSansDisplay_24 as font24     # Optional: converted TrueType font

lcd = lcd_config.config()

lcd.fill(lcd.BLACK)
lcd.round_rect(0, 0, 200, 40, 10, lcd.BLUE75, True)    # Filled rounded rectangle
lcd.write("Hello, world!", 10, 10, font24, lcd.YELLOW) # TrueType font text
lcd.update()
```

## Function Reference

### Display Control

```python
lcd.init(commands)          # Send initialization commands
lcd.soft_reset()            # Software reset the display controller
lcd.hard_reset()            # Hardware reset via RESET pin (not used on BEAPER circuits —
                            #   the LCD reset pin is wired to the board's reset button)
lcd.invert_mode(True)       # Invert display colors
lcd.invert_mode(False)      # Restore normal colors
lcd.sleep_mode(True)        # Sleep the controller and turn off backlight
lcd.sleep_mode(False)       # Wake the controller and turn on backlight
lcd.rotation(r)             # Set display rotation (0–3; 3 = upright on BEAPER circuits)
```

### Framebuffer Updates

Drawing functions write into an in-memory framebuffer. Call `update()` to push changes to the display.

```python
lcd.update()                # Push entire framebuffer to display
lcd.update(x, y, w, h)      # Push only the specified rectangular region (faster)
lcd.blit_buffer(buf, x, y, w, h)  # Copy a raw buffer directly to display memory
```

### Color

Colors are in **RGB565** format (16-bit). Use pre-defined color constants or convert from RGB:

```python
c = lcd.color565(r, g, b)  # Convert 8-bit r, g, b values to RGB565
```

#### Pre-defined Color Constants

| Constant | Description |
|---|---|
| `WHITE` | 100% white |
| `WHITE75` | 75% white |
| `WHITE50` | 50% white |
| `YELLOW` | 100% yellow |
| `YELLOW75` | 75% yellow |
| `YELLOW50` | 50% yellow |
| `CYAN` | 100% cyan |
| `CYAN75` | 75% cyan |
| `CYAN50` | 50% cyan |
| `GREEN` | 100% green |
| `GREEN75` | 75% green |
| `GREEN50` | 50% green |
| `MAGENTA` | 100% magenta |
| `MAGENTA75` | 75% magenta |
| `MAGENTA50` | 50% magenta |
| `RED` | 100% red |
| `RED75` | 75% red |
| `RED50` | 50% red |
| `BLUE` | 100% blue |
| `BLUE75` | 75% blue |
| `BLUE50` | 50% blue |
| `GREY` / `GRAY` | 25% white |
| `BLACK` | 0% white (off) |

### Graphics Functions

```python
lcd.fill(c)                             # Fill entire framebuffer with color c

lcd.pixel(x, y, c)                      # Draw pixel at x, y in color c
lcd.pixel(x, y)                         # Read and return the color of pixel at x, y

lcd.hline(x, y, w, c)                   # Horizontal line: start x,y, width w
lcd.vline(x, y, h, c)                   # Vertical line: start x,y, height h
lcd.line(x1, y1, x2, y2, c)            # Line from x1,y1 to x2,y2

lcd.rect(x, y, w, h, c)                # Rectangle outline
lcd.rect(x, y, w, h, c, True)          # Filled rectangle

lcd.round_rect(x, y, w, h, r, c)       # Rounded rectangle outline, corner radius r
lcd.round_rect(x, y, w, h, r, c, True) # Filled rounded rectangle

lcd.triangle(x1, y1, x2, y2, x3, y3, c)        # Triangle outline
lcd.triangle(x1, y1, x2, y2, x3, y3, c, True)  # Filled triangle

lcd.ellipse(x, y, xr, yr, c)           # Ellipse outline centred at x,y
lcd.ellipse(x, y, xr, yr, c, True)     # Filled ellipse
lcd.ellipse(x, y, xr, yr, c, True, m)  # Draw selected quadrants only (see below)

lcd.poly(x, y, coords, c)              # Polygon outline from coordinate array
lcd.poly(x, y, coords, c, True)        # Filled polygon

lcd.polygon(x, y, points, c)                       # Rotatable polygon outline
lcd.polygon(x, y, points, c, angle, cx, cy)        # With rotation (radians) and center offset

lcd.scroll(xstep, ystep)               # Scroll framebuffer contents
```

**Ellipse quadrant mask** (`m` parameter): bits select which quadrants to draw — bit 0 (1) = top right, bit 1 (2) = top left, bit 2 (4) = bottom left, bit 3 (8) = bottom right. Combine with `|` to draw multiple quadrants, e.g. `m=0b0011` draws the top half.

**Polygon coordinate array** (`coords`): an integer array in the form `array('h', [x0, y0, x1, y1, ..., xn, yn])`.

### Bitmap Functions

```python
lcd.bitmap(bitmap, x, y)                    # Draw a palette-compressed bitmap at x, y
lcd.bitmap(bitmap, x, y, index)             # Select from a multi-bitmap module
lcd.bitmap(bitmap, x, y, index, transparent)  # Skip pixels matching the transparent palette index

buf = lcd.bitmap_to_buffer(bitmap)          # Convert bitmap to raw RGB565 bytearray
buf = lcd.bitmap_to_buffer(bitmap, index)   # Select from a multi-bitmap module
lcd.blit_buffer(buf, x, y, w, h)            # Draw the converted buffer (fast repeated drawing)
```

`bitmap_to_buffer()` is useful when the same bitmap is drawn repeatedly — converting once and blitting the raw buffer each frame is faster than decoding the palette on every draw.

### Text Functions

Three text rendering options are available, each suited to different needs:

#### `text()` — Uses MicroPython's FrameBuffer 8×8 font to display **30 characters per row** on a 240-pixel wide display.

```python
lcd.text(s, x, y)           # Draw string s at x, y (75% white by default)
lcd.text(s, x, y, c)        # Draw string s at x, y in color c
```

#### `text16()` — Uses LCD.py's built-in 10×16 font to display **24 characters per row** on a 240-pixel wide display. Larger and more readable than `text()`, suitable for labels and data readouts.

```python
lcd.text16(s, x, y)         # Draw string s at x, y (75% white by default)
lcd.text16(s, x, y, c)      # Draw string s at x, y in color c

lcd.text16_width(s)         # Return pixel width of s (always len(s) * 10)
lcd.text16_height()         # Return font height (always 16)
```

#### `write()` — Write using converted TrueType fonts.

```python
lcd.write(s, x, y, font, fg)        # Draw string s using font, foreground color fg
lcd.write(s, x, y, font, fg, bg)    # Draw string s with background color bg

lcd.write_width(s, font)    # Return pixel width of s in the specified font
lcd.write_height(font)      # Return pixel height of characters in the specified font
```

`font` is a font module converted from a TTF file using the font conversion tool included with [st7789py_mpy](https://github.com/russhughes/st7789py_mpy). Allows custom typefaces and sizes.

## Display Rotation

Rotation `3` (inverted landscape) is the upright orientation for the LCD as mounted on BEAPER Nano and BEAPER Pico. The default `config()` call uses `rotation=3`.

| Value | Orientation |
|---|---|
| 0 | Portrait |
| 1 | Landscape |
| 2 | Inverted portrait |
| 3 | Inverted landscape *(default for BEAPER circuits)* |

## Notes on `update()`

All drawing functions write to an in-memory framebuffer — nothing appears on the display until `update()` is called. This allows an entire frame to be composed before displaying it, avoiding visible partial-frame artifacts.

For programs that update only a small area of the screen each frame, `update(x, y, w, h)` sends only the changed rectangular region over SPI and is significantly faster than a full update.

## Acknowledgements

This driver is adapted from [st7789py_mpy](https://github.com/russhughes/st7789py_mpy) by Russ Hughes, which is itself based on [st7789py_mpy](https://github.com/devbis/st7789py_mpy) by devbis.

## License

MIT License — Copyright (c) 2020–2023 Russ Hughes, Copyright (c) 2019 Ivan Belokobylskiy.

See [LICENSE](LICENSE) for the full license text.
