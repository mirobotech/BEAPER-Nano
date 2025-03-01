"""
BEAPER Nano Breakout
Updated: March 1, 2025

A nano-sized Breakout game made for BEAPER Nano: https://mirobo.tech/beaper

This game requires the following modules be copied to your device:

    LCDconfig_Nano.py - low-level hardware configuration file for BEAPER nano
    
    LCD.py - LCD driver module that extends the MicroPython framebuffer
    
    DotoRounded_20.py - converted font file
    
    All files are available from:
    https://github.com/mirobotech/BEAPER-Nano/tree/main/MicroPython/LCD

"""

# Import ADC, random, and time functions
from machine import ADC, Pin, PWM, SPI
import random
import time

# Import LCD configuration and display font
import LCDconfig_Nano as lcd_config
import DotoRounded_20 as doto20

# Arduino Nano ESP32 on-board LED I/O definitions
LED_BUILTIN = Pin(48, Pin.OUT, value = 0)   # Active High
LED_BLUE = Pin(45, Pin.OUT, value = 1)      # Active Low
LED_GREEN = Pin(0, Pin.OUT, value = 1)      # Active Low
LED_RED = Pin(46, Pin.OUT, value = 1)       # Active Low

# BEAPER Nano user I/O pin definitions and starting values
SW2 = Pin(44, Pin.IN, Pin.PULL_UP)
SW3 = Pin(43, Pin.IN, Pin.PULL_UP)
SW4 = Pin(5, Pin.IN, Pin.PULL_UP)
SW5 = Pin(6, Pin.IN, Pin.PULL_UP)
LED2 = M1A = Pin(7, Pin.OUT, value = 0)
LED3 = M1B = Pin(8, Pin.OUT, value = 0)
LED4 = M2A = Pin(9, Pin.OUT, value = 0)
LED5 = M2B = Pin(10, Pin.OUT, value = 0)
BEEPER = PWM(Pin(17), freq=1000, duty_u16=0)
RV1 = ADC(3, atten=ADC.ATTN_11DB)

# Deinit(ialize) SPI on Arduino Nano ESP32 after software restart
spi = SPI(2, baudrate=60000000, sck=Pin(48), mosi=Pin(38), miso=None)
spi.deinit()

# Create lcd object. Rotation=3 is the normal BEAPER Nano LCD orientation.
lcd = lcd_config.config(rotation=3)

# Brick constants
BRICK_HEIGHT = 8
ROWS = 8
COLUMNS = 8
MARGIN = 2
GAP = 24
RAINBOW = [
    (255, 0, 0),
    (255, 127, 0),
    (255, 255, 0),
    (127, 255, 0),
    (0, 255, 127),
    (0, 191, 255),
    (0, 0, 255),
    (191, 0, 191),
]

# Paddle variables
paddle_width = 32
paddle_height = 8
half_paddle_w = paddle_width // 2
paddle_x = lcd.width // 2
paddle_y = lcd.height - 1 - paddle_height
paddle_color = lcd.RED

# Ball variables
ball_x = paddle_x
ball_y = paddle_y - 2
ball_x_velocity = 0
ball_y_velocity = 0
ball_color = lcd.WHITE

# Game variables
bricks_remaining = ROWS * COLUMNS
lives = 3
score = 0
speed = 1
lives_message = "Lives: "
message_row = lcd.height // 2
lcd_middle = lcd.width // 2

def rainbow_rgb(color1, color2, t):
    return (
        int(color1[0] * (1 - t) + color2[0] * t),
        int(color1[1] * (1 - t) + color2[1] * t),
        int(color1[2] * (1 - t) + color2[2] * t),
    )

def get_rainbow(t):
    i = t * len(RAINBOW)
    low = RAINBOW[int(i)]
    high = RAINBOW[min(int(i) + 1, len(RAINBOW) - 1)]
    # print(i, low, high, rainbow_rgb(low, high, i % 1))
    return rainbow_rgb(low, high, i % 1)

class Brick:
    def __init__(self, x, y, width, height, color):
        self.x1 = x
        self.y1 = y
        self.width = width
        self.height = height
        self.x2 = x + width - 1
        self.y2 = y + height - 1
        self.color = color
        self.hit = False

    def draw(self, buffer):
        buffer.rect(self.x1, self.y1, self.width, self.height, bg_color if self.hit else self.color, True)

# Map value in input range to output range.
def map(value, in_min, in_max, out_min, out_max):
    return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

# Create array of bricks
brick_width = lcd.width // COLUMNS - MARGIN
bricks = []
for row in range(ROWS):
    color = get_rainbow(row / ROWS)
    for column in range(COLUMNS):
        bricks.append(Brick(
            column * (brick_width + MARGIN) + MARGIN // 2,
            row * (BRICK_HEIGHT + MARGIN) + MARGIN // 2 + GAP,
            brick_width,
            BRICK_HEIGHT,
            lcd.color565(color[0], color[1], color[2]),
        ))

# Set background color
bg_color = lcd.BLACK

# Draw start screen...
lcd.fill(bg_color)

# Draw bricks
for brick in bricks:
    brick.draw(lcd)

# Display score
lcd.write(str(score), 0, 0, doto20, lcd.RED)

# Display lives
message = lives_message + str(lives)
msg_x = lcd_middle - lcd.write_width(message, doto20) // 2
lcd.write(message, msg_x, message_row, doto20, lcd.YELLOW)

# Display start message
lcd.ellipse(msg_x + 10, message_row + 34, 8, 8, ball_color, True)
lcd.write("Start", msg_x + 30, message_row + 24, doto20, lcd.YELLOW)

skip = 2

while(True):
    # Erase ball and paddle from last position
    lcd.rect(paddle_x - half_paddle_w, paddle_y, paddle_width, paddle_height, bg_color, True)
    lcd.rect(ball_x - 2, ball_y - 2, 4, 4, bg_color, True)

    # Calculate analog pot controlled paddle position
    half_paddle_w = paddle_width // 2
    paddle_x = map(RV1.read_u16(), 0, 65535, 0 + half_paddle_w, lcd.width - half_paddle_w)
    
    # Calculate button controlled paddle position
    # if buttons.left and buttons.left.value() == 0:
    #     if paddle_x - half_paddle_w >= 2:
    #         paddle_x -= 2
    # if buttons.right and buttons.right.value() == 0:
    #     if paddle_x + half_paddle_w < tft.width - 2:
    #         paddle_x += 2
    
    # Draw paddle in current position
    lcd.rect(paddle_x - half_paddle_w, paddle_y, paddle_width, paddle_height, paddle_color, True)

    # Check if ball is on paddle (ball velocities are both 0 before ball launches)
    if ball_x_velocity == 0 and ball_y_velocity == 0:
        ball_x = paddle_x
        ball_y = paddle_y - 2
        #Draw ball on paddle
        lcd.rect(ball_x - 2, ball_y - 2, 4, 4, ball_color, True)
        
        # When launch? Now? Ok, set starting velocity.
        if SW2.value() == 0:
            ball_x_velocity = -2
            ball_y_velocity = -4
            # Clear messages
            lcd.rect(0, message_row, lcd.width, 50, bg_color, True)
    else:
        # Ball is in flight. Bounce off left or right edges.
        if ball_x + ball_x_velocity <= 2 or ball_x + ball_x_velocity >= lcd.width - 2:
            ball_x_velocity = -ball_x_velocity
        # Update ball position
        ball_x = ball_x + ball_x_velocity * speed
        ball_y = ball_y + ball_y_velocity * speed
    
        # Check for brick hit
        for brick in bricks:
            if brick.x1 < ball_x + 2 and ball_x - 2 < brick.x2:
                if brick.y1 < ball_y + 2 and ball_y - 2 < brick.y2:
                    if brick.hit == False:
                        brick.hit = True
                        brick.draw(lcd)
                        ball_y_velocity = -ball_y_velocity
                        bricks_remaining -= 1
                        score += 10 * speed
        
        # Check for paddle hit
        if paddle_x - half_paddle_w < ball_x + 2 and ball_x - 2 < paddle_x + half_paddle_w:
            if paddle_y + 2 > ball_y > paddle_y - 4:
                ball_y_velocity = -ball_y_velocity
                ball_y = ball_y + ball_y_velocity
                
        # Check for ball drain
        if ball_y >= lcd.height:
            ball_x_velocity = 0
            ball_y_velocity = 0
            lives -= 1
            if lives == 0:
                msg_x = lcd_middle - lcd.write_width(message, doto20) // 2
                lcd.write("Game Over", msg_x, message_row, doto20, lcd.RED)
                lcd.update()
                time.sleep(2)
                lcd.rect(msg_x+2, message_row + 26, 16, 16, lcd.WHITE, True)
                lcd.write("Restart", msg_x + 30, message_row + 24, doto20, lcd.YELLOW)
                lcd.update()
                while SW5.value() == 1:
                    time.sleep_ms(20)
                # Reset game variables
                lives = 3
                score = 0
                ball_x_velocity = 0
                ball_y_velocity = 0
                bricks_remaining = ROWS * COLUMNS
                lcd.fill(bg_color)
                # Re-draw bricks
                for brick in bricks:
                    brick.hit = False
                    brick.draw(lcd)
                # Display start message
                lcd.ellipse(msg_x + 10, message_row + 34, 8, 8, ball_color, True)
                lcd.write("Start", msg_x + 30, message_row + 24, doto20, lcd.YELLOW)        
                
            else:
                message = lives_message + str(lives)
                msg_x = lcd_middle - lcd.write_width(message, doto20) // 2
                lcd.write(message, msg_x, message_row, doto20, lcd.RED)
                lcd.update()
                time.sleep(2)
                lcd.write(message, msg_x, message_row, doto20, bg_color)
                lcd.update()
            
        # Check for top hit
        if ball_y <= 4:
            ball_y_velocity = -ball_y_velocity

        # Update score
        lcd.write(str(score), 0, 0, doto20, lcd.RED, bg_color)

        # Draw ball at current position
        lcd.rect(ball_x - 2, ball_y - 2, 4, 4, ball_color, True)            

        # Breakout?
        if bricks_remaining == 0:
            msg_x = lcd_middle - lcd.write_width(message, doto20) // 2
            lcd.write("BREAKOUT!!", msg_x, message_row, doto20, lcd.YELLOW)
            lcd.update()
            time.sleep(2)
            ball_x_velocity = 0
            ball_y_velocity = 0
            ball_y = paddle_y - 2
            bricks_remaining = ROWS * COLUMNS
            # Re-draw bricks
            lcd.fill(bg_color)
            for brick in bricks:
                brick.hit = False
                brick.draw(lcd)
            # Display start message
            lcd.ellipse(msg_x + 10, message_row + 34, 8, 8, ball_color, True)
            lcd.write("Start", msg_x + 30, message_row + 24, doto20, lcd.YELLOW)        

    # Update LCD every 2 frames on BEAPER Pico
    # skip -= 1
    # if skip == 0:
    #     lcd.update()
    #     skip = 2

    # Update LCD every frame on BEAPER Nano
    lcd.update()