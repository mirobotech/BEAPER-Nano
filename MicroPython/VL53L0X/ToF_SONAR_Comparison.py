"""
================================================================================
SONAR_ToF_Comparison.py
April 22, 2026

Platform: mirobo.tech BEAPER Nano circuit
Requires: BEAPER_Nano.py board support module file
          vl53l0x_nb.py non-blocking VL53L0X driver module
          LCDconfig_Nano.py LCD driver module

Compares distance results and ranging acquisition time between
HC-SR04(P) SONAR and VL53L0X ToF (Time of Flight) modules using
LCD text output and a simulated oscilloscope display.
================================================================================
"""

# --- MicroPython Modules --------------
from machine import I2C
import framebuf
import array
import time

# LCD driver module
import LCDconfig_Nano as lcd_config

# VL53L0X module
from vl53l0x_nb import VL53L0X

# BEAPER Pico support module
import BEAPER_Nano as beaper

# --- Program Constants ----------------
TIME_DIV = 500  # Scope grid horizontal time/div in us
VOLT_DIV = 2    # Scope grid vertical Volts/div in V

# --- Program Variables ----------------
sonar_range_mm = 0
sonar_time_us = 0
tof_range_mm = 0
tof_time_us = 0
trig_time_us = 0

time_mult = 24 / TIME_DIV
volt_mult = 24 / VOLT_DIV

# --- Start SONAR ranging, time SONAR TRIG -> ECHO delay
def sonar_range_trig():
    # Make a 10us TRIG pulse to start a range measurement
    beaper.SONAR_TRIG.value(1)
    time.sleep_us(10)
    beaper.SONAR_TRIG.value(0)

    trig_start = time.ticks_us()
    while beaper.SONAR_ECHO.value() == 0:
        time.sleep_us(1)
    return time.ticks_diff(time.ticks_us(), trig_start)
    
# ---- Get SONAR range by timing ECHO pulse ---------------
def sonar_range_echo():
    # Measure ECHO pulse duration. Time-out value is set to round-trip
    # time for max_range plus 1cm, in microseconds. (~29us/cm one way)
    echo_start = time.ticks_us()
    while beaper.SONAR_ECHO.value() == 1:
        time.sleep_us(1)
    return time.ticks_diff(time.ticks_us(), echo_start)
    
# --- Main program starts here
beaper.nano_led_on()

# Configure ToF. I2C bus is configured in BEAPER_Nano module:
# QWIIC = I2C(id=beaper.I2C_ID, sda=beaper.SDA, scl=beaper.SCL)
# VL53L0X device should answer I2C scan at address 41
# print("I2C scan:", beaper.QWIIC.scan())
tof = VL53L0X(beaper.QWIIC)

# Configure LCD
lcd = lcd_config.config()

# Write LCD headings into framebuffer
lcd.fill(0x0)
lcd.text16("SONAR", 0, 0, lcd.WHITE)
lcd.text16("VL53L0X", 120, 0, lcd.WHITE)

while True:
    # Measure times to acquire SONAR range and convert range
    trig_time_us = sonar_range_trig()  # Time delay from TRIG -> ECHO
    echo_time_us = sonar_range_echo()  # Time ECHO pulse
    sonar_range_mm = int(echo_time_us / 5.82)
    sonar_time_us = trig_time_us + echo_time_us
    
    # Measure time to acquire ToF range
    tof_start = time.ticks_us()
    tof.start_range_request()
    while not tof.reading_available():
        pass
    tof_range_mm = tof.get_range_value()
    tof_time_us = time.ticks_diff(time.ticks_us(), tof_start)
    
    # Clear lower screen area
    lcd.rect(0, 20, 240, 220, lcd.BLACK, True)

    # Write ranges and ranging times into LCD framebuffer
    text = f"Dist:{sonar_range_mm}mm"
    lcd.text16(text, 0, 20, lcd.WHITE75)
    text = f"Time:{sonar_time_us}us"
    lcd.text16(text, 0, 40, lcd.WHITE75)
    
    text = f"TRIG>ECHO:{trig_time_us}us"
    lcd.text16(text, 0, 80, lcd.WHITE75)
    
    text = f"Dist:{tof_range_mm}mm"
    lcd.text16(text, 120, 20, lcd.WHITE75)
    text = f"Time:{tof_time_us}us"
    lcd.text16(text, 120, 40, lcd.WHITE75)
    
    lcd.vline(0, 96, 144, lcd.GREY)
    for x in range(24, 241, 24):
        lcd.vline(x-1, 96, 144, lcd.GREY)
    for y in range(96, 241, 24):
        lcd.hline(0, y-1, 240, lcd.GREY)
    
    # Set up virtual scope
    trace = 0  # trace time 0
    ch1 = 144  # Channel 1 GND reference pixel row
    ch2 = 216  # Channel 2 GND reference pixel row

    # TRIG pulse
    sig = int(3.3 * volt_mult) 
    lcd.vline(trace, ch1 - sig, sig, lcd.CYAN)
    lcd.hline(trace, ch1, 240, lcd.CYAN)
    
    # TRIG delay
    h = int(trig_time_us * time_mult)
    lcd.hline(trace, ch2, h, lcd.YELLOW)
    trace += h
    
    # ECHO pulse
    lcd.vline(trace, ch2-sig, sig, lcd.YELLOW)
    h = int((sonar_time_us - trig_time_us) * time_mult)
    lcd.hline(trace, ch2 - sig, h, lcd.YELLOW)
    trace += h
    lcd.vline(trace, ch2 - sig, sig, lcd.YELLOW)
    lcd.hline(trace, ch2, 240 - trace, lcd.YELLOW)

    # Unit display
    text = f"T:{TIME_DIV}us/div"
    lcd.text(text, 16, 230, lcd.WHITE75)
    text = f"V:{VOLT_DIV}V/div"
    lcd.text(text, 150, 230, lcd.WHITE75)

    # Update LCD from framebuffer
    lcd.update()
