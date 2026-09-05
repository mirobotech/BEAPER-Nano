# ==============================================================================
# ToF and SONAR Comparison [ToF_SONAR_Comparison.py]
# Version: 1.2
# Updated: September 4, 2026
#
# Platform: mirobo.tech BEAPER Nano
# Requires: BEAPER_Nano.py board support module file
#           VL53L4CD.py driver module
#           LCDconfig_Nano.py LCD configuration module for BEAPER Nano
#           LCD.py LCD driver module
# 
# Compares distance results and ranging acquisition time between
# HC-SR04P SONAR and VL53L4CD ToF (Time of Flight) modules using
# LCD text output and a stylized visual bar graph display.
# ==============================================================================

# MicroPython Modules
from machine import I2C, SPI
import framebuf
import array
import time

# LCD driver module
import LCDconfig_Nano as lcd_config

# BEAPER Nano support module
import BEAPER_Nano as beaper

# Configure VL53L4CD module and begin ranging
from VL53L4CD import VL53L4CD
tof = VL53L4CD(beaper.QWIIC)
# tof.set_offset(n)  # Calibrate sensor and set offset n = measured mm - actual mm
# tof.set_range_timing(10) # 10ms (less accurate) - 200ms, default is 50ms.
tof.start_ranging()

# Colour Constants 
sonar_colour = const(0xA314)
laser_colour = const(0xF580)

# Display Constants
sonar_x = const(40)
laser_x = const(56)

# Program Variables
sonar_range_mm = 0
sonar_time_us = 0
tof_range_mm = 0
tof_time_us = 0
buffer_time_ms = 0
lcd_time_ms = 0

# Start SONAR ranging and time both the TRIG -> ECHO delay and the
# ECHO pulse width
def sonar_range_timing(_timeout_us=35000):
    # Returns (trig_time_us, echo_time_us), or (-1, 0) if ECHO never
    # starts, or (trig_time_us, -1) if ECHO never ends
    beaper.SONAR_TRIG.value(1)
    time.sleep_us(10)
    beaper.SONAR_TRIG.value(0)

    trig_start = time.ticks_us()
    while beaper.SONAR_ECHO.value() == 0:
        if time.ticks_diff(time.ticks_us(), trig_start) > _timeout_us:
            return -1, 0
    echo_start = time.ticks_us()
    trig_time_us = time.ticks_diff(echo_start, trig_start)

    while beaper.SONAR_ECHO.value() == 1:
        if time.ticks_diff(time.ticks_us(), echo_start) > _timeout_us:
            return trig_time_us, -1
    echo_end = time.ticks_us()
    echo_time_us = time.ticks_diff(echo_end, echo_start)

    return trig_time_us, echo_time_us
    
# Status LED on
beaper.nano_led_on()

# Configure LCD
lcd = lcd_config.config()

while True:
    loop_start = time.ticks_ms()
    # Measure time to acquire SONAR range and convert range
    trig_time_us, echo_time_us = sonar_range_timing()
    if trig_time_us < 0 or echo_time_us < 0:
        # ECHO never started, or never ended - skip this update
        time.sleep_ms(50)
        continue
    sonar_range_mm = int(echo_time_us / 5.82)
    sonar_time_us = trig_time_us + echo_time_us
    
    # Measure time to read ToF range if it's ready
    tof_start = time.ticks_us()
    if tof.data_ready():
        result = tof.get_result()
        tof.clear_interrupt()
        if result['range_status'] is 0:
            tof_range_mm = result['distance_mm']
            tof_time_us = time.ticks_diff(time.ticks_us(), tof_start)
        else:
            tof_range_mm = 0

    # Measure time to draw results into the frambuffer
    buffer_start = time.ticks_ms()
  
    # Clear screen
    lcd.fill(lcd.BLACK)

    # Draw info boxes
    lcd.round_rect(110, 0, 130, 70, 10, sonar_colour)
    lcd.round_rect(110, 90, 130, 70, 10, laser_colour)
    lcd.round_rect(110, 180, 130, 50, 10, lcd.CYAN75)

    # Write titles
    lcd.text16("HC-SR04P", 120, 10, lcd.WHITE75)
    lcd.text16("VL53L4CD", 120, 100, lcd.WHITE75)

    # Write SONAR range and ranging time
    lcd.text16(f"Dist:{sonar_range_mm}mm", 120, 30, lcd.WHITE75)
    lcd.text16(f"Time:{sonar_time_us}us", 120, 50, lcd.WHITE75)

    # Write ToF range and ranging time
    lcd.text16(f"Dist:{tof_range_mm}mm", 120, 120, lcd.WHITE75)
    lcd.text16(f"Time:{tof_time_us}us", 120, 140, lcd.WHITE75)

    # Write LCD update times
    lcd.text16(f"Buf: {buffer_time_ms}ms", 120, 190, lcd.WHITE75)
    lcd.text16(f"LCD: {lcd_time_ms}ms", 120, 210, lcd.WHITE75)

    # Draw distance grid
    lcd.vline(0, 0, 240, lcd.GREY)
    lcd.hline(0, 0, 96, lcd.GREY)
    for x in range(24, 100, 24):
        lcd.vline(x-1, 0, 240, lcd.GREY)
    for y in range(0, 241, 24):
        lcd.hline(0, y-1, 96, lcd.GREY)

    # Adjust distance bars to fit < 240mm or < 480 mm
    if sonar_range_mm > 239 or tof_range_mm > 239:
      sonar_range_mm = sonar_range_mm // 2
      tof_range_mm = tof_range_mm // 2
    
    # Draw distance bars
    # lcd.rect(12, 239-sonar_range_mm, 24, sonar_range_mm, sonar_colour, True)
    lcd.triangle(sonar_x-(sonar_range_mm//4), 239-sonar_range_mm,
                 sonar_x+(sonar_range_mm//4), 239-sonar_range_mm,
                 sonar_x, 239, sonar_colour, True)
    lcd.rect(laser_x, 239-tof_range_mm+4, 2, tof_range_mm, laser_colour, True)
  
    # Draw laser spot for fun!
    lcd.ellipse(laser_x, 239-tof_range_mm, 4, 4, laser_colour, True)
    lcd.vline(laser_x, 239-tof_range_mm-16, 6, laser_colour)
    lcd.line(laser_x+6, 239-tof_range_mm-8, laser_x+10, 239-tof_range_mm-12, laser_colour)
    lcd.hline(laser_x+10, 239-tof_range_mm, 6, laser_colour)
    lcd.line(laser_x+6, 239-tof_range_mm+8, laser_x+10, 239-tof_range_mm+12, laser_colour)
    lcd.line(laser_x-6, 239-tof_range_mm-8, laser_x-10, 239-tof_range_mm-12, laser_colour)
    lcd.hline(laser_x-16, 239-tof_range_mm, 6, laser_colour)
    lcd.line(laser_x-6, 239-tof_range_mm+8, laser_x-10, 239-tof_range_mm+12, laser_colour)

    # Caluclate buffer update time
    buffer_time_ms = time.ticks_diff(time.ticks_ms(), buffer_start)

    # Update LCD from framebuffer
    lcd_start = time.ticks_ms()
    lcd.update()

    # Calculate lcd display time
    lcd_time_ms = time.ticks_diff(time.ticks_ms(), lcd_start)
  
    # Wait at least 50ms
    while time.ticks_diff(time.ticks_ms(), loop_start) < 50:
      time.delay_ms(1)
    loop_time_ms = time.ticks_diff(time.ticks_ms(), loop_start)

