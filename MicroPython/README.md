## What is BEAPER Nano?

**BEAPER** (Beginner Electronics and Programming Educational Robot) **Nano** is a fully-integrated beginner circuit designed for learning programming and robotics using the Arduino Nano ESP32. BEAPER Nano can be programmed using **MicroPython** (in Arduino Lab for MicroPython or other MicroPython IDEs) or using **Arduino C/C++** (in the Arduino IDE or compatible tools). See the [BEAPER Nano](https://mirobo.tech/beaper) web page for more details.

## Compatible Hardware

BEAPER_Nano.py is designed for the **Arduino Nano ESP32** module.

## On-Board Hardware

| Hardware | Details |
|---|---|
| Pushbutton switches | 4 user buttons (SW2–SW5) with internal pull-ups |
| LEDs | 4 user LEDs (LED2–LED5), shared with motor driver |
| Piezo buzzer | PWM tone generation (LS1) |
| Motor driver | SH754410NE — two DC motors forward/reverse, or one bipolar stepper |
| Analog potentiometers | Two pots (RV1, RV2) — jumper-selectable |
| Ambient light sensor | TEPT4400 (Q4) — jumper-selectable |
| Temperature sensor | MCP9700A analog sensor (U4) — jumper-selectable |
| Floor/line sensors | IR LED + phototransistor modules (Q1, Q2, Q3) — jumper-selectable |
| Battery voltage divider | VDIV — jumper-selectable |
| SONAR header | 3.3V I/O headers H1–H4 for HC-SR04P ultrasonic distance sensor |
| Servo headers | Four 5V servo/output headers (H5–H8), shared with H1–H4 and I2C |
| I2C/QWIIC connector | JST-SH connector for 3.3V I2C devices |
| LCD/SPI header | Optional 1.54" 240×240 ST7789 TFT LCD display |
| Nano LED | On-board Arduino Nano ESP32 LED |
| RGB LED | On-board Arduino Nano ESP32 RGB LED (active-low, PWM controlled) |

# BEAPER_Nano.py

`BEAPER_Nano.py` is a MicroPython board support module for BEAPER Nano. It defines and configures the Arduino Nano ESP32s GPIO pins for all of BEAPER Nano's on-board hardware, and provides simple helper functions so beginners can focus on learning programming concepts first — no other special libraries are required.

`BEAPER_Nano.py` is used by all of the BEAPER Nano **Beginner Activities** and most of the other example programs for BEAPER Nano.

> An Arduino C/C++ header file is also available for BEAPER Nano. See the Arduino IDE readme for details.

## Getting Started

1. Copy `BEAPER_Nano.py` to your Arduino Nano ESP32 (e.g. using Arduino Lab for MicroPython or Thonny).
2. Import the module at the top of your program:

```python
from BEAPER_Nano import *
```

3. Start using the helper functions — no additional setup needed.

## Analog Jumper Settings

BEAPER Nano has on-board jumpers that select which analog devices are connected to the ADC pins. **Set jumpers before running programs that use analog inputs.**

| Jumper | Enviro. position | Robot position |
|---|---|---|
| JP1 (ADC0 / GP1) | Light sensor Q4 | Floor sensor Q1 |
| JP2 (ADC1 / GP2) | Temperature sensor U4 | Line sensor Q2 |
| JP3 (ADC2 / GP3) | Potentiometer RV1 | Floor/line sensor Q3 |
| JP4 (ADC3 / GP4) | Potentiometer RV2 | Battery voltage divider VDIV |

## Function Reference

### Arduino Nano ESP32 On-Board LED

```python
nano_led_on()       # Turn Nano LED on
nano_led_off()      # Turn Nano LED off
nano_led_toggle()   # Toggle Nano LED
```

### Arduino Nano ESP32 RGB LED

The RGB LED is active-low and PWM-controlled. Brightness ranges from 0 (off) to 65535 (full brightness).

```python
nano_rgb_red(brightness)    # Set red element brightness (0–65535)
nano_rgb_green(brightness)  # Set green element brightness (0–65535)
nano_rgb_blue(brightness)   # Set blue element brightness (0–65535)
```

Example — full red:

```python
nano_rgb_red(65535)
nano_rgb_green(0)
nano_rgb_blue(0)
```

### User LEDs

> **Note:** LED pins are shared with the motor driver. Do not use LEDs and motors at the same time.

```python
leds_on()           # Turn all four LEDs on
leds_off()          # Turn all four LEDs off

LED2.value(1)       # Control individual LEDs directly
LED3.toggle()
```

Individual LED objects: `LED2`, `LED3`, `LED4`, `LED5`

A tuple of all LEDs is available for iteration: `LEDS`

### Pushbutton Switches

Buttons use internal pull-up resistors — **pressed = 0, released = 1**.

```python
if SW2.value() == 0:    # Check if SW2 is pressed
    print("SW2 pressed")
```

Individual switch objects: `SW2`, `SW3`, `SW4`, `SW5`

A tuple of all switches is available for iteration: `SWITCHES`

### Motors

> **Note:** Motor pins are shared with LED pins. Do not use LEDs and motors at the same time.

```python
motors_stop()           # Stop both motors

left_motor_forward()    # Left motor forward
left_motor_reverse()    # Left motor reverse
left_motor_stop()       # Stop left motor

right_motor_forward()   # Right motor forward
right_motor_reverse()   # Right motor reverse
right_motor_stop()      # Stop right motor
```

> The actual forward/reverse direction of each motor depends on its physical wiring to CON1.

### Piezo Buzzer

```python
tone(frequency)             # Start a continuous tone (Hz)
tone(frequency, duration)   # Play a tone for duration (ms), then stop
noTone()                    # Stop the tone
noTone(duration)            # Stop the tone, then pause (ms)
beep()                      # Play a 1000 Hz beep for 100 ms
beep(duration)              # Play a 1000 Hz beep for duration (ms)
```

### Analog Inputs

```python
light_level()   # Ambient light sensor Q4 (JP1 = Enviro.) — brighter → higher
temp_level()    # Temperature sensor U4 (JP2 = Enviro.) — warmer → higher
RV1_level()     # Potentiometer RV1 (JP3 = Enviro.) — clockwise → higher
RV2_level()     # Potentiometer RV2 (JP4 = Enviro.) — clockwise → higher

Q1_level()      # Floor sensor Q1 (JP1 = Robot) — higher reflectivity → higher
Q2_level()      # Line sensor Q2 (JP2 = Robot) — higher reflectivity → higher
Q3_level()      # Floor/line sensor Q3 (JP3 = Robot) — higher reflectivity → higher
VDIV_level()    # Battery voltage divider (JP4 = Robot)
```

All analog functions return a 16-bit value (0–65535).

### SONAR Distance Sensor (HC-SR04P)

Connect a 3.3V HC-SR04P module to headers H2 (TRIG) and H3 (ECHO).

> **Note:** SONAR uses pins shared with servo headers H7 and H8 and I2C. Do not use SONAR, servos, and I2C simultaneously on the same pins.

```python
distance = sonar_range()        # Measure distance, default max 100 cm
distance = sonar_range(200)     # Measure distance, max 200 cm
```

Return values:

| Value | Meaning |
|---|---|
| > 0 | Distance to nearest target in cm |
| 0 | No target detected within max range |
| -1 | Timeout waiting for ECHO to start |
| -2 | Previous ECHO pulse still in progress |

### Servos

> **Important:** Servo headers H5–H8 share GPIO pins with 3.3V I/O headers H1–H4 and the I2C/QWIIC connector. Disable I2C or SONAR pin configuration before enabling servo outputs.

Servo lines in `BEAPER_Nano.py` are commented out by default. Uncomment and configure them before use:

```python
SERVO1 = PWM(Pin(H5_PIN), freq=50, duty_u16=4915)
SERVO2 = PWM(Pin(H6_PIN), freq=50, duty_u16=4915)
SERVO3 = PWM(Pin(H7_PIN), freq=50, duty_u16=4915)
SERVO4 = PWM(Pin(H8_PIN), freq=50, duty_u16=4915)

SERVOS = (SERVO1, SERVO2, SERVO3, SERVO4)
```

Then set servo positions using:

```python
set_servo(SERVO1, 45)   # Set SERVO1 to 45 degrees (0–90)
set_servo(SERVO2, 0)    # Set SERVO2 to 0 degrees
set_servo(SERVO3, 90)   # Set SERVO3 to 90 degrees
```

Default pulse range is 1000–2000 µs over 90°. Adjust `SERVO_MIN_US`, `SERVO_MAX_US`, and `SERVO_RANGE` constants for your servo if needed. Servos initialize to the centre position (≈1.5 ms pulse) — verify this is safe for your application before connecting servos.

### I2C / QWIIC

```python
devices = QWIIC.scan()      # Scan for I2C devices on connector J4
```

The `QWIIC` object is a standard MicroPython `I2C` instance on GP11 (SDA) and GP12 (SCL) and is compatible with any 3.3V I2C or QWIIC device.

> **Note:** I2C pins are shared with headers H1, H4, H5, and H6. Plan pin usage carefully when combining I2C with servos or digital I/O headers.

### Digital I/O Headers

Headers H1–H4 provide 3.3V digital I/O and can be used as general-purpose inputs or outputs. They share pins with H5–H8, I2C, and SONAR — plan usage carefully.

```python
H1 = Pin(H1_PIN, Pin.OUT)   # Example: configure H1 as output
H3 = Pin(H3_PIN, Pin.IN)    # Example: configure H3 as input
```

Pin constants: `H1_PIN` (GP11), `H2_PIN` (GP13), `H3_PIN` (GP14), `H4_PIN` (GP12)

## Shared Pin Summary

Many BEAPER Nano pins serve multiple roles. Plan your project around these overlaps:

| GPIO | Shared functions |
|---|---|
| GP11 | I2C SDA, H1 digital I/O, H5 servo |
| GP12 | I2C SCL, H4 digital I/O, H6 servo |
| GP13 | H2 digital I/O, SONAR TRIG, H7 servo |
| GP14 | H3 digital I/O, SONAR ECHO, H8 servo |
| GP7–GP10 | User LEDs, motor driver inputs |

## GPIO Pin Map

| GPIO | Arduino Pin | Function |
|---|---|---|
| GP48 | D13 / LED_BUILTIN | Nano LED (also SPI SCK / LCD SCK) |
| GP46 | LED_RED | RGB LED red (active-low, PWM) |
| GP0 | LED_GREEN | RGB LED green (active-low, PWM) |
| GP45 | LED_BLUE | RGB LED blue (active-low, PWM) |
| GP44 | D0 | SW2 pushbutton (pull-up) |
| GP43 | D1 | SW3 pushbutton (pull-up) |
| GP5 | D2 | SW4 pushbutton (pull-up) |
| GP6 | D3 | SW5 pushbutton (pull-up) |
| GP7 | D4 | LED2 / Motor M1A (left motor A) |
| GP8 | D5 | LED3 / Motor M1B (left motor B) |
| GP9 | D6 | LED4 / Motor M2A (right motor A) |
| GP10 | D7 | LED5 / Motor M2B (right motor B) |
| GP17 | D8 | Piezo buzzer LS1 |
| GP18 | D9 | LCD DC |
| GP47 | D12 | LCD CIPO / backlight |
| GP21 | D10 | LCD CS |
| GP48 | D13 | LCD SCK (shared with Nano LED) |
| GP38 | D11 | LCD COPI |
| GP11 | A4 / SDA | I2C SDA / H1 / H5 servo |
| GP12 | A5 / SCL | I2C SCL / H4 / H6 servo |
| GP13 | A6 | H2 / SONAR TRIG / H7 servo |
| GP14 | A7 | H3 / SONAR ECHO / H8 servo |
| GP1 | A0 | Light sensor Q4 or floor sensor Q1 (jumper) |
| GP2 | A1 | Temperature sensor U4 or line sensor Q2 (jumper) |
| GP3 | A2 | Potentiometer RV1 or floor/line sensor Q3 (jumper) |
| GP4 | A3 | Potentiometer RV2 or battery voltage divider (jumper) |

## License

See [LICENSE](LICENSE) for details.
