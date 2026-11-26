# ==============================================================================
# BEAPER Nano I/O Test project [BEAPER_Nano_v1_2_IO_Test.py]
# Version: 1.2
# Updated: November 24, 2026
#
# BEAPER Nano v1.2 I/O functional test. This program tests:
#   - inputs (pushbuttons, ambient light sensor Q4, temperature sensor U4,
#     potentiometers RV1 and RV2)
#   - outputs (LEDs, RGB LED, piezo speaker)
#   - QWIIC/I2C connector (J4)
#   - SONAR module (connect a 3.3V HC-SR04P to H2/H3)
#
# Each pushbutton lights its own LED and plays its own note while held:
#   SW1 - LED1, note C5, and the Arduino Nano ESP32 on-board LED
#   SW2 - LED2, note E5, and the RGB LED red element
#   SW3 - LED3, note G5, and the RGB LED green element
#   SW4 - LED4, note C6, and the RGB LED blue element
#
# Jumper settings:
#   Set JP1-JP4 to Enviro. to select analog input devices Q4, U4, RV1,
#   and RV2. If floor sensors and voltage divider resistors are
#   installed, jumpers can be moved to Robot to test Q1, Q2, Q3, inputs.
#   Testing VDIV requires an external power supply to be attached to
#   VDC In inputs on CON1.
#
# See the https://mirobo.tech/beaper webpage for additional BEAPER Nano starter
# progams and beginner programming activities.
# ==============================================================================

# Import machine and time functions
import machine
from machine import Pin, PWM, ADC, I2C
import time

# Built-in Arduino Nano ESP32 LEDs
LED_BUILTIN = Pin(48, Pin.OUT, value = 0)   # Active High
LED_RGB_BLUE = Pin(45, Pin.OUT, value = 1)  # Active Low
LED_RGB_GREEN = Pin(0, Pin.OUT, value = 1)  # Active Low
LED_RGB_RED = Pin(46, Pin.OUT, value = 1)   # Active Low

# BEAPER Nano v1.2 Educational Starter I/O devices
SW1 = Pin(44, Pin.IN, Pin.PULL_UP)
SW2 = Pin(43, Pin.IN, Pin.PULL_UP)
SW3 = Pin(5, Pin.IN, Pin.PULL_UP)
SW4 = Pin(6, Pin.IN, Pin.PULL_UP)
LED1 = M1A = Pin(7, Pin.OUT)
LED2 = M1B = Pin(8, Pin.OUT)
LED3 = Pin(9, Pin.OUT)
LED4 = Pin(10, Pin.OUT)
LS1 = PWM(Pin(17), freq = 1000, duty_u16 = 0)

# BEAPER Nano optional analog input devices
Q1 = Q4 = ADC(1, atten = ADC.ATTN_11DB)
Q2 = U4 = ADC(2, atten = ADC.ATTN_11DB)
Q3 = RV1 = ADC(3, atten = ADC.ATTN_11DB)
VDIV = RV2 = ADC(4, atten = ADC.ATTN_11DB)

# QWIIC/I2C optional connector J4 (H1 = SDA, H4 = SCL)
QWIIC = I2C(0, scl=Pin(12), sda=Pin(11))

# SONAR module connections (H2 = TRIG, H3 = ECHO)
TRIG = Pin(13, Pin.OUT)
ECHO = Pin(14, Pin.IN, Pin.PULL_UP)

# Note frequencies for the C major chord played by SW1-SW4
NOTE_C5 = 523
NOTE_E5 = 659
NOTE_G5 = 784
NOTE_C6 = 1047

# Pushbutton switch variables
SW1_pressed = False
SW2_pressed = False
SW3_pressed = False
SW4_pressed = False

# Start a tone at specified frequency (Hz), and stop the tone after
# an optional duration (ms)
def tone(frequency, duration=None):
  LS1.freq(frequency)
  LS1.duty_u16(32768)
  if duration is not None:
    time.sleep_ms(duration)
    noTone()

# Stop the tone. Optionally pause for duration (ms)
def noTone(duration=None):
  LS1.duty_u16(0)
  if duration is not None:
    time.sleep(duration)

# SONAR range function with maximum range limit and ECHO pin error checking.
# Returns the range of the closest target in cm. The 'max' parameter limits
# the search range to objects no farther than 'max' cm. The function returns
# -1 if a previous ranging operation is still in progress, 0 if no target is
# found within the specified max range, or returns the range to the closest
# target in cm.
# Example application:
# range_cm = sonar_range(100)   # Find closest target within 100 cm
def sonar_range(max):
  # Check if previous ECHO has finished
  if ECHO.value() == 1:
    return -1   # ECHO in progress (wait 10ms after ECHO ends before re-triggering)

  # Create TRIG pulse
  TRIG.value(1)
  time.sleep_us(10)
  TRIG.value(0)

  # Wait for ECHO to go high. HC-SR04P (3.3V-capable modules, also labelled as
  # RCWL-9610A 2022) delay for approximately 2300us after TRIG pulse ends
  # before ECHO pulse starts.
  duration = machine.time_pulse_us(ECHO, 0, 2500)
  if duration < 0:
    return duration # ECHO didn't start. Return error code.

  # Time ECHO pulse. Set time-out value to max range.
  duration = machine.time_pulse_us(ECHO, 1, (max + 1) * 58)
  if duration < 0:
    return 0    # Return 0 if distance is > max range

  # Return range to target in cm
  return duration / 58

# Start-up sound and text
print("Starting BEAPER Nano")
tone(1000, 100)

# Scan the QWIIC connector once for any connected I2C device
i2c_devices = QWIIC.scan()
if i2c_devices:
  print("I2C devices found:", [hex(address) for address in i2c_devices])
else:
  print("No I2C devices found")

# Print brief instructions
print("SW1 - LED1, note C5, and the module LED")
print("SW2 - LED2, note E5, and the RGB LED red element")
print("SW3 - LED3, note G5, and the RGB LED green element")
print("SW4 - LED4, note C6, and the RGB LED blue element")
time.sleep(2)

# Set timer
sensor_timer = time.ticks_ms()

while True:
  # Update pushbutton states
  SW1_pressed = (SW1.value() == 0)
  SW2_pressed = (SW2.value() == 0)
  SW3_pressed = (SW3.value() == 0)
  SW4_pressed = (SW4.value() == 0)

  # Light BEAPER and Arduino Nano module LEDs while buttons are held
  LED1.value(1 if SW1_pressed else 0)
  LED_BUILTIN.value(1 if SW1_pressed else 0)
  LED2.value(1 if SW2_pressed else 0)
  LED_RGB_RED.value(0 if SW2_pressed else 1)    # Active-Low
  LED3.value(1 if SW3_pressed else 0)
  LED_RGB_GREEN.value(0 if SW3_pressed else 1)  # Active-Low
  LED4.value(1 if SW4_pressed else 0)
  LED_RGB_BLUE.value(0 if SW4_pressed else 1)   # Active-Low

  # Play the chord note for whichever button is held (checked in order)
  if SW1_pressed:
    tone(NOTE_C5)
  elif SW2_pressed:
    tone(NOTE_E5)
  elif SW3_pressed:
    tone(NOTE_G5)
  elif SW4_pressed:
    tone(NOTE_C6)
  else:
    noTone()

  # Update SONAR range and analog inputs every 500ms
  if time.ticks_diff(time.ticks_ms(), sensor_timer) > 500:
    # Reset sensor_timer
    sensor_timer = time.ticks_ms()
    # Get and print SONAR range
    range_cm = sonar_range(100)
    print("Range:", int(range_cm), "cm")
    # Read and print analog input levels (labelled for either jumper position)
    print("Q4/Q1 level: ", Q4.read_u16())
    print("U4/Q2 level: ", U4.read_u16())
    print("RV1/Q3 level: ", RV1.read_u16())
    print("RV2/VDIV level: ", RV2.read_u16())
    print("")

  # Add a short loop delay
  time.sleep_ms(20)