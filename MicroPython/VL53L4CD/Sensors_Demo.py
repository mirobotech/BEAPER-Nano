"""
================================================================================
Sensors_Demo.py
Updated: May 29, 2026

A radar read-out style graphical display for BEAPER Nano showing Q1 and Q3
floor sensor reflectivity, battery voltage, temperature, and distance
to the closest target.

Platform: mirobo.tech BEAPER Nano circuit
Requires: BEAPER_Nano.py board support module file
          LCD.py LCD driver library module
          LCDconfig_Nano.py LCD configuration module for BEAPER Nano
          Orbitron_medium_28.py font
          DotoRounded_semibold_30.py font
          DotoRounded_20.py font
          A distance sensor. Choose either:
          HC-SR04P (3.3V) SONAR distance sensor module, or,
          VL43L0X I2C ToF distance sensor module and vl53l0x_nb.py driver, or
          VL53L4CD I2C ToF distance sensor module and VL53L4CD.py driver

Jumper Settings:  JP1 - Robot (Q1/Left floor sensor)
                  JP2 - Eniro.(U4 temperature sensor)
                  JP3 - Robot (Q3/Right floor sensor)
                  JP4 - Robot (VDIV battery voltage divider)
================================================================================
"""

# --- MicroPython Modules --------------
from machine import Pin, PWM, I2C, ADC
import framebuf
import time

# BEAPER Nano board support module
import BEAPER_Nano as beaper

# LCD driver and font modules
import LCDconfig_Nano as lcd_config
import Orbitron_medium_28 as orbitron28
import DotoRounded_semibold_30 as doto30
import DotoRounded_20 as doto20

# QWIIC/I2C bus is pre-configured in BEAPER_Nano module.
# QWIIC = I2C(id=beaper.I2C_ID, sda=beaper.SDA, scl=beaper.SCL)

# Configure ToF sensor. Un-comment either VL53L0X or VL53L4CD configuration

"""
# Configure VL53L0X sensor -----------------------------------------
# Import VL53L0X driver module
from vl53l0x_nb import VL53L0X

# Testing: VL53L0X device should answer I2C scan at address 41
# print("I2C scan:", beaper.QWIIC.scan())

# Create tof sensor object
tof = VL53L0X(beaper.QWIIC)
# Start first range request (non-blocking)
tof.start_range_request()
# ------------------------------------------------------------------
"""

# Configure VL53L4CD sensor ----------------------------------------
# Import VL53L4CD driver module
from VL53L4CD import VL53L4CD
# Create tof sensor object
tof = VL53L4CD(beaper.QWIIC)
# Start first range request
tof.start_ranging()
# ------------------------------------------------------------------


# --- Program Constants ----------------
MAX_TARGET_RANGE = const(500)   # Follow targets within max range (mm)
DARK_THRESHOLD = const(60)      # Floor sensor dark threshold (%, lower -> darker)
TOF_OFFSET = const(0)           # ToF sensor module range offset (mm)
TEMP_OFFSET = const(1)          # Temperature sensor offset (degrees C)
TV_PERIOD = const(1000)         # Tempeature and voltage update period (ms)

left_floor = 0                  # Left floor sensor reflectivity
right_floor = 0                 # Right floor sensor reflectivity
range_mm = 0                    # Sensor target range (0 = no target)
range_last = time.ticks_ms()    # Last update time
tv_last = time.ticks_ms()

def map_range(value, in_min, in_max, out_min, out_max):
  # Map value from input range to output range.
  return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def draw_range_scale():
  # Draw LCD 'radar' display scale
  lcd.rect(0, 0, 240, 152, lcd.BLACK, True)
  lcd.vline(120, 0, 155, lcd.GREEN50)
  lcd.ellipse(120, 152, 150, 150, lcd.GREEN50, False, 3)  # 3 = 2+1 (top half)        
  lcd.hline(113, 27, 14, lcd.GREEN50)
  lcd.ellipse(120, 152, 100, 100, lcd.GREEN50, False, 3)
  lcd.hline(113, 77, 14, lcd.GREEN50)
  lcd.ellipse(120, 152, 50, 50, lcd.GREEN50, False, 3)
  lcd.hline(113, 127, 14, lcd.GREEN50)
  lcd.hline(110, 152, 20, lcd.GREEN50)
  lcd.triangle(119, 152, 0, 32, 0, 152, lcd.BLACK, True)
  lcd.triangle(119, 152, 239, 32, 239, 152, lcd.BLACK, True)

def update_floor_leds():
  # Set virtual LED colour based on floor reflectivity
  if Q1_value < DARK_THRESHOLD:
    lcd.ellipse(25, 170, 6, 6, lcd.RED50, True)
    lcd.ellipse(25, 170, 4, 4, lcd.RED75, True)
    lcd.ellipse(25, 170, 2, 2, lcd.RED, True)
    lcd.pixel(24, 169, lcd.WHITE75)
  else:
    lcd.ellipse(25, 170, 6, 6, lcd.GREEN50, True)
    lcd.ellipse(25, 170, 4, 4, lcd.GREEN75, True)
    lcd.ellipse(25, 170, 2, 2, lcd.GREEN, True)
    lcd.pixel(24, 169, lcd.WHITE75)

  if Q3_value < DARK_THRESHOLD:
    lcd.ellipse(215, 170, 6, 6, lcd.RED50, True)
    lcd.ellipse(215, 170, 4, 4, lcd.RED75, True)
    lcd.ellipse(215, 170, 2, 2, lcd.RED, True)
    lcd.pixel(214, 169, lcd.WHITE75)
  else:
    lcd.ellipse(215, 170, 6, 6, lcd.GREEN50, True)
    lcd.ellipse(215, 170, 4, 4, lcd.GREEN75, True)
    lcd.ellipse(215, 170, 2, 2, lcd.GREEN, True)
    lcd.pixel(214, 169, lcd.WHITE75)


# Read temperature and system voltage
temp_C = (beaper.temp_level() * 3.3 / 65535 -0.5) / 0.01
sys_V = beaper.VDIV_level() * 3.3 / 65535 * 6.225

# Deinit(ialize) SPI on Arduino Nano ESP32 (needed after software restart)
spi = SPI(2, baudrate=60000000, sck=Pin(48), mosi=Pin(38), miso=None)
spi.deinit()

# Configure TFT
lcd = lcd_config.config()
lcd.fill(0)
lcd.update()

# Draw BEAPER Bot robot outline on LCD
chassis = lcd.YELLOW75  # Set chassis colour
pcb = 0x0008            # Set PCB colour to navy blue

# Draw floor sensors
lcd.round_rect(5, 153, 40, 50, 10, chassis, True)
lcd.round_rect(9, 157, 32, 42, 10, pcb, True)
lcd.round_rect(195, 153, 40, 50, 10, chassis, True)
lcd.round_rect(199, 157, 32, 42, 10, pcb, True)

# Draw BEAPER PCB
lcd.round_rect(0, 200, 240, 50, 10, chassis, True)
lcd.round_rect(50, 160, 140, 50, 10, chassis, True)
lcd.round_rect(4, 204, 232, 50, 6, pcb, True)
lcd.round_rect(54, 164, 132, 50, 10, pcb, True)
text_x = (240 - lcd.write_width("BEAPER Nano", orbitron28)) // 2
lcd.write("BEAPER Nano", text_x, 206, orbitron28, lcd.WHITE75, None)
lcd.update()

while True:
  # Update floor sensors on LCD
  Q1_value = int(map_range(beaper.Q1_level(), 0, 65535, 0, 100))
  Q3_value = int(map_range(beaper.Q3_level(), 0, 65535, 0, 100))
  update_floor_leds()

  if time.ticks_diff(time.ticks_ms(), tv_last) > TV_PERIOD:
    tv_last = time.ticks_ms()
    # Update temperature
    temp_C = (beaper.temp_level() * 3.3 / 65535 -0.5) / 0.01 + TEMP_OFFSET
    # Update system voltage
    sys_V = beaper.VDIV_level() * 3.3 / 65535 * 6.225

  # Un-comment one of the three distance sensor sections

  """
  # Read VL53L0X distance sensor ------------------------------------
  if tof.reading_available():
    # Single measurement has larger distance variation
    # tof_range_mm = tof.get_range_value()
    
    # Average of two measurements produces slightly smoother results
    range_mm = (range_mm + tof.get_range_value()) // 2 + TOF_OFFSET
    # Start new measurement
    tof.start_range_request()
    # ---------------------------------------------------------------
  """
  
  # Read VL53L4CD distance sensor -----------------------------------
  if tof.data_ready():
    result = tof.get_result()
    tof.clear_interrupt()
    range_mm = result['distance_mm']
  # -----------------------------------------------------------------
  
  
  """
  # Read SONAR distance sensor --------------------------------------
  range_mm = int(beaper.sonar_range(MAX_TARGET_RANGE) * 10)
  # -----------------------------------------------------------------
  """

  # Ignore far away targets
  if range_mm > MAX_TARGET_RANGE:
    range_mm = 0

  # Update range dot
  draw_range_scale()
  if 5 < range_mm < 300:
    lcd.ellipse(120, (300-range_mm)//2+3, 6, 6, lcd.YELLOW50, True)
    lcd.ellipse(120, (300-range_mm)//2+3, 4, 4, lcd.YELLOW75, True)
    lcd.ellipse(120, (300-range_mm)//2+3, 2, 2, lcd.YELLOW, True)

  # Update range display
  if range_mm == 0:
    lcd.write("---mm", 140, 20, doto30, lcd.GREEN75)
  else:
    range = f"{range_mm:3d}mm"
    if range_mm <= 100:
      lcd.write(range, 140, 20, doto30, lcd.GREEN)
    else:
      lcd.write(range, 140, 20, doto30, lcd.GREEN75)

  # Write sensor values to LCD
  text = f"Q1: {Q1_value:2d}%"
  lcd.write(text, 0, 0, doto20, lcd.GREEN75)
  text = f"Q3: {Q3_value:2d}%"
  lcd.write(text, 0, 20, doto20, lcd.GREEN75)
  text = f"T: {temp_C:4.1f}C"
  lcd.write(text, 0, 100, doto20, lcd.GREEN75)
  text = f"V: {sys_V:4.1f}V"
  lcd.write(text, 0, 120, doto20, lcd.GREEN75)

  # Update LCD
  lcd.update()
