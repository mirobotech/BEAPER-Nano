"""
bar_graph.py
April 3, 2026

Bar graph functions for creating continuous and segmented bar graphs
using the LCD.py driver module on BEAPER Pico and BEAPER Nano.

Requires:
    LCD.py - LCD driver module that extends the MicroPython framebuffer

Functions:
    vertical        - Continuous vertical bar graph
    horizontal      - Continuous horizontal bar graph
    seg_vertical    - Segmented vertical bar graph
    seg_horizontal  - Segmented horizontal bar graph

Continuous bar graphs (vertical, horizontal) - draw a value on a
    continuous vertical or horizontal bar graph, with:
        - a specified bar color
        - minimum and maximum bar graph values (default 0-100)
        - an optional background color (to prevent persistence and/or
          enable partial LCD updates) or over a transparent background
          (requires background to be re-drawn each bar graph update)
        - an optional border color and width, incuding optional
          padding to inset the bar from the border

Segmented bar graphs (seg_vertical, seg_horizontal) - draw a value on
    a segmented vertical or horizontal bar graph (like simulated LEDs,
    segments are fully lit at the mid-point of their sub-range), with:
        - a specified color
        - minimum and maximum bar graph values (default 0-100)
        - optional background color (to prevent persistence and
          enable partial LCD updates) or a transparent background
          (requires background to be re-drawn each bar graph update)
        - an optional border using specified color and width
        - optional padding to inset the segments from the border and
          space segments from each other 
        - the selectable numbers of segments (default 10)

Border behaviour:
    If border > 0, a border is drawn. If not supplied, border_color
    defaults to lcd.BLACK. 

Padding behaviour:
    The padding parameter controls the inset of the bar from the inner
    edges of the border on all sides. A padding of 0 fills the bar flush
    to the border, and padding > 0 floats the bar within the border. In
    segmented graphs, padding also controls the spacing between segments.

Usage examples:
    import bar_graph

    # Continuous bar displaying values from 0-100, background provided by caller
    lcd.fill(lcd.BLACK)
    bar_graph.vertical(lcd, x, y, width, length, value, color=lcd.GREEN)
    lcd.update()

    # Continuous bar from 0-65535 with bg_color and border for in-place updates
    bar_graph.vertical(lcd, x, y, width, length,
                       value, 0, 65535,
                       color=lcd.GREEN, bg_color=lcd.BLACK,
                       border=2, border_color=lcd.GREY,
                       padding=2)
    lcd.update()

    # Segmented bar, default 10 segments, values from 10-30, with navy background
    bar_graph.seg_vertical(lcd, x, y, width, length,
                           value, 10, 30,
                           color=lcd.CYAN, bg_color-lcd.BLUE50,
                           2, 10)
    lcd.update()
"""

# Default bar graph dimensions
BAR_SHORT   = const(40)     # Default short dimension (width of vertical, height of horizontal)
BAR_LONG    = const(120)    # Default long dimension (length of vertical, length of horizontal)
BAR_PADDING = const(2)      # Default padding between segments and edges in pixels


# ---------------------------------------------------------------------
# Internal helper: draw border and return inner drawing area
# ---------------------------------------------------------------------

def _border_and_inner(lcd, x, y, width, height, border, border_color):
    """Draw border if requested and return (inner_x, inner_y, inner_w, inner_h)."""
    if border > 0:
        if border_color is None:
            border_color = lcd.BLACK
        for i in range(border):
            lcd.rect(x + i, y + i, width - 2 * i, height - 2 * i, border_color, False)
    bw = border if border > 0 else 0
    return x + bw, y + bw, width - 2 * bw, height - 2 * bw


# ---------------------------------------------------------------------
# Continuous vertical bar graph
# ---------------------------------------------------------------------

def vertical(lcd, x, y, width=BAR_SHORT, length=BAR_LONG,
             value=0, min_val=0, max_val=100,
             color=None, bg_color=None,
             border=0, border_color=None,
             padding=0):
    """
    Draw a continuous vertical bar graph, growing upward from the bottom.
    Bar is drawn over the background (or bg_color fill).

    Parameters:
        lcd          - LCD canvas object (from LCD.py)
        x, y         - Top-left corner of the bar graph
        width        - Width of the bar graph in pixels
        length       - Length (height) of the bar graph in pixels
        value        - Current value to display
        min_val      - Value corresponding to an empty bar
        max_val      - Value corresponding to a full bar
        color        - Colour of the filled bar (defaults to lcd.WHITE)
        bg_color     - Colour of the bar interior; if None (default), only
                       the filled portion is drawn and the caller manages
                       the background
        border       - Width of border in pixels; 0 = no border (default)
        border_color - Colour of border; defaults to lcd.BLACK if
                       border > 0 and border_color is not supplied
        padding      - Inset of bar from border edges on all sides; 0 = flush
    """
    if color is None:
        color = lcd.WHITE

    inner_x, inner_y, inner_w, inner_h = _border_and_inner(
        lcd, x, y, width, length, border, border_color)

    # Apply padding inset on all sides for the bar rect only
    rect_x = inner_x + padding
    rect_y = inner_y + padding
    rect_w = inner_w - 2 * padding
    rect_h = inner_h - 2 * padding

    # Fill full inner area with bg_color if supplied
    if bg_color is not None:
        lcd.rect(inner_x, inner_y, inner_w, inner_h, bg_color, True)

    # Clamp value and compute filled pixel height within padded area
    value = max(min_val, min(max_val, value))
    fill_h = int((value - min_val) / (max_val - min_val) * rect_h)

    # Draw filled portion (bottom)
    if fill_h > 0:
        lcd.rect(rect_x, rect_y + rect_h - fill_h, rect_w, fill_h, color, True)


# ---------------------------------------------------------------------
# Continuous horizontal bar graph
# ---------------------------------------------------------------------

def horizontal(lcd, x, y, width=BAR_LONG, length=BAR_SHORT,
               value=0, min_val=0, max_val=100,
               color=None, bg_color=None,
               border=0, border_color=None,
               padding=0):
    """
    Draw a continuous horizontal bar graph, growing rightward from the left.
    Bar is drawn over the background (or bg_color fill).

    Parameters:
        lcd          - LCD canvas object (from LCD.py)
        x, y         - Top-left corner of the bar graph
        width        - Width (vertical height) of the bar graph in pixels
        length       - Length (horizonta width) of the bar graph in pixels
        value        - Current value to display
        min_val      - Value corresponding to an empty bar
        max_val      - Value corresponding to a full bar
        color        - Colour of the filled bar (defaults to lcd.WHITE)
        bg_color     - Colour of the bar interior; if None (default), only
                       the filled portion is drawn and the caller manages
                       the background
        border       - Width of border in pixels; 0 = no border (default)
        border_color - Colour of border; defaults to lcd.BLACK if
                       border > 0 and border_color is not supplied
        padding      - Inset of bar from border edges on all sides; 0 = flush
    """
    if color is None:
        color = lcd.WHITE

    inner_x, inner_y, inner_w, inner_h = _border_and_inner(
        lcd, x, y, width, length, border, border_color)

    # Apply padding inset on all sides for the bar rect only
    rect_x = inner_x + padding
    rect_y = inner_y + padding
    rect_w = inner_w - 2 * padding
    rect_h = inner_h - 2 * padding

    # Fill full inner area with bg_color if supplied
    if bg_color is not None:
        lcd.rect(inner_x, inner_y, inner_w, inner_h, bg_color, True)

    # Clamp value and compute filled pixel width within padded area
    value = max(min_val, min(max_val, value))
    fill_w = int((value - min_val) / (max_val - min_val) * rect_w)

    # Draw filled portion (left)
    if fill_w > 0:
        lcd.rect(rect_x, rect_y, fill_w, rect_h, color, True)


# ---------------------------------------------------------------------
# Segmented vertical bar graph
# ---------------------------------------------------------------------

def seg_vertical(lcd, x, y, width=BAR_SHORT, length=BAR_LONG,
                 value=0, min_val=0, max_val=100,
                 color=None, bg_color=None,
                 border=0, border_color=None,
                 padding=BAR_PADDING, segments=10):
    """
    Draw a vertical bar graph with LED-style segments, growing upward.
    'Lit' segments are drawn over the background (or bg_color fill).

    Parameters:
        lcd          - LCD canvas object (from LCD.py)
        x, y         - Top-left corner of the bar graph
        width        - Width of the bar graph in pixels
        length       - Height of the bar graph in pixels
        value        - Current value to display
        min_val      - Value corresponding to no segments lit
        max_val      - Value corresponding to all segments lit
        color        - Colour of lit segments (defaults to lcd.WHITE)
        bg_color     - Colour of the bar interior; if None (default), only
                       lit segments are drawn and the caller manages the
                       background
        border       - Width of border in pixels; 0 = no border (default)
        border_color - Colour of border; defaults to lcd.BLACK if
                       border > 0 and border_color is not supplied
        padding      - Gap between segments and inset from side edges
        segments     - Number of LED-style segments (1 = single on/off block)
    """
    if color is None:
        color = lcd.WHITE

    inner_x, inner_y, inner_w, inner_h = _border_and_inner(
        lcd, x, y, width, length, border, border_color)

    # Segment rects are inset from the side edges by padding
    rect_x = inner_x + padding
    rect_w = inner_w - 2 * padding

    # Segment height: fit all segments and inter-segment gaps within inner_h,
    # distributing any slack evenly above and below the segment stack
    seg_count = max(1, segments)
    seg_h = (inner_h - (seg_count - 1) * padding) // seg_count
    used_h = seg_count * seg_h + (seg_count - 1) * padding
    top_pad = (inner_h - used_h) // 2

    # Fill full inner area with bg_color if supplied
    if bg_color is not None:
        lcd.rect(inner_x, inner_y, inner_w, inner_h, bg_color, True)

    # Each segment lights when value reaches the midpoint of its sub-range
    sub_range = (max_val - min_val) / seg_count

    # Draw lit segments from bottom (i=0) upward
    for i in range(seg_count):
        threshold = min_val + sub_range * (i + 0.5)
        if value < threshold:
            break                           # All remaining segments unlit
        rect_y = inner_y + top_pad + (seg_count - 1 - i) * (seg_h + padding)
        lcd.rect(rect_x, rect_y, rect_w, seg_h, color, True)


# ---------------------------------------------------------------------
# Segmented horizontal bar graph
# ---------------------------------------------------------------------

def seg_horizontal(lcd, x, y, width=BAR_LONG, length=BAR_SHORT,
                   value=0, min_val=0, max_val=100,
                   color=None, bg_color=None,
                   border=0, border_color=None,
                   padding=BAR_PADDING, segments=10):
    """
    Draw a horizontal bar graph with LED-style segments, growing rightward.
    'Lit' segments are drawn over the background (or bg_color fill).

    Parameters:
        lcd          - LCD canvas object (from LCD.py)
        x, y         - Top-left corner of the bar graph
        width        - Width of the bar graph in pixels
        length       - Height of the bar graph in pixels
        value        - Current value to display
        min_val      - Value corresponding to no segments lit
        max_val      - Value corresponding to all segments lit
        color        - Colour of lit segments (defaults to lcd.WHITE)
        bg_color     - Colour of the bar interior; if None (default), only
                       lit segments are drawn and the caller manages the
                       background
        border       - Width of border in pixels; 0 = no border (default)
        border_color - Colour of border; defaults to lcd.BLACK if
                       border > 0 and border_color is not supplied
        padding      - Gap between segments and inset from top/bottom edges
        segments     - Number of LED-style segments (1 = single on/off block)
    """
    if color is None:
        color = lcd.WHITE

    inner_x, inner_y, inner_w, inner_h = _border_and_inner(
        lcd, x, y, width, length, border, border_color)

    # Segment rects are inset from the top/bottom edges by padding
    rect_y = inner_y + padding
    rect_h = inner_h - 2 * padding

    # Segment width: fit all segments and inter-segment gaps within inner_w,
    # distributing any slack evenly left and right of the segment stack
    seg_count = max(1, segments)
    seg_w = (inner_w - (seg_count - 1) * padding) // seg_count
    used_w = seg_count * seg_w + (seg_count - 1) * padding
    left_pad = (inner_w - used_w) // 2

    # Fill full inner area with bg_color if supplied
    if bg_color is not None:
        lcd.rect(inner_x, inner_y, inner_w, inner_h, bg_color, True)

    # Each segment lights when value reaches the midpoint of its sub-range
    sub_range = (max_val - min_val) / seg_count

    # Draw lit segments from left (i=0) rightward
    for i in range(seg_count):
        threshold = min_val + sub_range * (i + 0.5)
        if value < threshold:
            break                           # All remaining segments unlit
        rect_x = inner_x + left_pad + i * (seg_w + padding)
        lcd.rect(rect_x, rect_y, seg_w, rect_h, color, True)
