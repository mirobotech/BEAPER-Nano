"""
BEAPER Nano Bar Graph Demo
Updated: April 29, 2026

Demonstrates the bar_graph module using BEAPER Nano's two potentiometers
(RV1, RV2), ambient light sensor (Q4), and temperature sensor (U4).

RV1 and temperature drive continuous vertical bar graphs, while
RV2 and Q4 drive segmented vertical bar graphs.

Requires:
    BEAPER_Nano.py    - BEAPER Nano board configuration file
    LCDconfig_Nano.py - LCD configuration file for BEAPER Nano
    LCD.py            - LCD driver module
    bar_graph.py      - Bar graph module

Hardware:
    Set JP1, JP2, JP3, and JP4 jumpers to Enviro. to connect Q4, U4, RV1, and RV2.
"""

from machine import SPI, Pin
import BEAPER_Nano as beaper         # BEAPER Nano board module
import LCDconfig_Nano as lcd_config  # LCD configuration file (calls LCD.py driver)
import bar_graph                     # Bar graph module
import time

# Deinit(ialize) SPI on Arduino Nano ESP32 after software restart
spi = SPI(2, baudrate=40000000, sck=Pin(48), mosi=Pin(38), miso=None)
spi.deinit()

# Create LCD object
lcd = lcd_config.config()

# ---------------------------------------------------------------------
# Layout constants
# ---------------------------------------------------------------------

MARGIN      = 10        # Left and right screen margin in pixels
BAR_GAP_X   = 10        # Horizontal gap between bars
BAR_W       = 48        # Width of each bar graph
BAR_L       = 186       # Length (height) of each bar graph
BAR_TOP     = 5         # Y position of bar top
FONT_H      = 20        # Font height + leading in pixels (adjust to match font)
LABEL_Y     = BAR_TOP + BAR_L + 6      # Y position of label text
VALUE_Y     = LABEL_Y + FONT_H         # Y position of value text

SEGMENTS    = 16        # Number of segments for segmented bar graphs
PADDING     = 2         # Edge/segment padding for all bars
BORDER      = 4         # Border width for all bars

# X positions of the three bars
BAR1_X = MARGIN
BAR2_X = MARGIN + BAR_W + BAR_GAP_X
BAR3_X = MARGIN + 2 * (BAR_W + BAR_GAP_X)
BAR4_X = MARGIN + 3 * (BAR_W + BAR_GAP_X)

# Colours
RV1_COLOR   = lcd.RED75
RV2_COLOR   = lcd.YELLOW75
Q4_COLOR    = lcd.CYAN75
TMP_COLOR   = lcd.GREEN75
BG_COLOR    = lcd.BLACK
BORDER_COL  = lcd.WHITE50

# Labels
LABEL_RV1   = "RV1"
LABEL_RV2   = "RV2"
LABEL_Q4    = "Light"
LABEL_TMP   = "Temp"
LABEL_COLOR = lcd.WHITE75

# Map a value from one range to another, returning a float result.
def map_range(value, in_min, in_max, out_min, out_max):
  # Use int(map_range(...)) when an integer result is required.
  return out_min + (value - in_min) * (out_max - out_min) / (in_max - in_min)

# Write a centred text string under a bar
def write_centred(text, bar_x, bar_w, y, color):
    tx = bar_x + (bar_w - lcd.text16_width(text)) // 2
    lcd.text16(text, tx, y, color)

while True:
    # Read sensor values
    rv1_val = int(map_range(beaper.RV1_level(), 0, 65535, 0, 100))
    rv2_val = beaper.RV2_level()
    q4_val  = beaper.light_level()
    amb_temp = (beaper.temp_level() / 19.859 - 500) / 10

    # Background fill
    lcd.fill(lcd.BLUE50)
    
    # RV1 0-100 continuous bar with border and background color
    bar_graph.vertical(lcd, BAR1_X, BAR_TOP, BAR_W, BAR_L,
                       rv1_val, 0, 100,
                       RV1_COLOR, lcd.color565(16,0,0),
                       BORDER, BORDER_COL,
                       PADDING)

    # RV2 10 segment bar with no border over transparent background
    bar_graph.seg_vertical(lcd, BAR2_X, BAR_TOP, BAR_W, BAR_L,
                           rv2_val, 0, 65535,
                           RV2_COLOR, None,
                           0, BORDER_COL,
                           4)

    # Q4 (light level) 16 segment bar with border and background
    bar_graph.seg_vertical(lcd, BAR3_X, BAR_TOP, BAR_W, BAR_L,
                           q4_val, 0, 65535,
                           Q4_COLOR, BG_COLOR,
                           2, lcd.WHITE75,
                           PADDING, SEGMENTS)
    
    # U4 (temperature) continuous bar over transparent background
    bar_graph.vertical(lcd, BAR4_X, BAR_TOP, BAR_W, BAR_L,
                       amb_temp, 0, 50,
                       TMP_COLOR)

    # Write labels and current values centred under each bar
    write_centred(LABEL_RV1,     BAR1_X, BAR_W, LABEL_Y, LABEL_COLOR)
    write_centred(LABEL_RV2,     BAR2_X, BAR_W, LABEL_Y, LABEL_COLOR)
    write_centred(LABEL_Q4,      BAR3_X, BAR_W, LABEL_Y, LABEL_COLOR)
    write_centred(LABEL_TMP,     BAR4_X, BAR_W, LABEL_Y, LABEL_COLOR)
    write_centred(str(rv1_val),  BAR1_X, BAR_W, VALUE_Y, RV1_COLOR)
    write_centred(str(rv2_val),  BAR2_X, BAR_W, VALUE_Y, RV2_COLOR)
    write_centred(str(q4_val),   BAR3_X, BAR_W, VALUE_Y, Q4_COLOR)
    temp = f"{amb_temp:.1f}C"
    write_centred(str(temp),  BAR4_X, BAR_W, VALUE_Y, TMP_COLOR)

    time.sleep_ms(50)
    lcd.update()
