"""
BEAPER Nano Layered Graphics Demo
Updated: June 2, 2026

Displays an Intersex-Inclusive Progress Pride Flag created using layered
graphics primitives. (Learn more about the different Pride flags here:
https://www.hrc.org/resources/lgbtq-pride-flags)

The colours are stored in MicroPython tuples allowing the stripes to be
animated when pushbutton SW4 is held.

Requires:
    BEAPER_Nano.py    - BEAPER Nano board configuration file
    LCDconfig_Nano.py - LCD configuration file for BEAPER Nano
    LCD.py            - LCD driver module for ST7789 displays

"""

from machine import SPI, Pin
import BEAPER_Nano as beaper         # BEAPER Nano board module
import LCDconfig_Nano as lcd_config  # LCD configuration file (calls LCD.py driver)
import time

# Rainbow stripe colours
STRIPES = (
  (0xB800, 0xBBC0, 0xBDC0, 0x05E0, 0x0016, 0xB816)
)

# Triangle colours
TRIANGLES = (
  (0x0000, 0x78E0, 0xBBFF, 0xFBEF, 0xFFFF, 0xBDE0)
)

# Deinit(ialize) SPI on Arduino Nano ESP32 after software restart
spi = SPI(2, baudrate=40000000, sck=Pin(48), mosi=Pin(38), miso=None)
spi.deinit()

# Create LCD object
lcd = lcd_config.config()

# Layout constants

# Calculate stripe sizes
STRIPE_WIDTH = lcd.width
STRIPE_HEIGHT = lcd.height // 6  # Height of each stripe

# Calculate triangle paramaters
TRIANGLE_OFFSET = lcd.width // 16 # Triangle X spacing
TRIANGLE_START = TRIANGLE_OFFSET * 4
TRIANGLE_WIDTH = lcd.width // 3
TRIANGLE_HEIGHT = lcd.height
TRIANGLE_MIDDLE = TRIANGLE_HEIGHT // 2

# Caluclate circle parameters
CIRCLE_X = int(TRIANGLE_OFFSET * 1.4)
CIRCLE_Y = lcd.height // 2
CIRCLE_RADIUS = CIRCLE_X
CIRCLE_WIDTH = 4

# Draw stripes
def draw_stripes(index = 0):
  y = 0
  for s in range(6):
    lcd.rect(0, s * STRIPE_HEIGHT, STRIPE_WIDTH, STRIPE_HEIGHT, STRIPES[index], True)
    index += 1
    if index >= 6:
      index = 0

# Draw triangles
def draw_triangles(index = 0):
  x = TRIANGLE_START
  for t in range(6):
    lcd.triangle(x, 0, x + TRIANGLE_WIDTH, TRIANGLE_MIDDLE, x, TRIANGLE_HEIGHT, TRIANGLES[index], True)
    if x > 0:
      lcd.rect(0, 0, x, TRIANGLE_HEIGHT, TRIANGLES[index], True)
    index += 1
    x -= TRIANGLE_OFFSET

# Draw circle
def draw_circle():
  lcd.ellipse(CIRCLE_X, CIRCLE_Y, CIRCLE_RADIUS, CIRCLE_RADIUS, 0xB816, True)
  lcd.ellipse(CIRCLE_X, CIRCLE_Y, CIRCLE_RADIUS - CIRCLE_WIDTH, CIRCLE_RADIUS - CIRCLE_WIDTH, 0xBDE0, True)
  
color_index = 0

while True:
  SW4_pressed = beaper.SW4.value() == 0

  # Animate the colour stripes when SW4 is pressed
  if SW4_pressed:
    color_index -= 1
    if color_index < 0:
      color_index = 5
  else:
    color_index = 0
    
  draw_stripes(color_index)
  draw_triangles()
  draw_circle()
  lcd.update()

  time.sleep_ms(120)
