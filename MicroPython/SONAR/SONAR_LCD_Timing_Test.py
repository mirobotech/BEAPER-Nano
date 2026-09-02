# ================================================================================
# SONAR LCD Timing Test [SONAR_LCD_Timing_Test.py]
# Version: 1.1
# Updated: September 1, 2026
#
# Platform: mirobo.tech BEAPER Nano circuit
# Requires: BEAPER_Nano.py board support module file
#           LCDconfig_Nano.py LCD configuration module for BEAPER Nano
#           LCD.py LCD driver module
#
# Displays SONAR range, TRIG time, and ECHO time, and graphs TRIG and ECHO
# signals on an oscilloscope-like display.
# ================================================================================

# MicroPython Modules
from machine import I2C, SPI
import framebuf
import array
import time

# BEAPER Nano support module
import BEAPER_Nano as beaper

# Deinit(ialize) SPI on Arduino Nano ESP32 (needed after software restart)
spi = SPI(2, baudrate=60000000, sck=Pin(48), mosi=Pin(38), miso=None)
spi.deinit()

# LCD driver module
import LCDconfig_Nano as lcd_config

# Program variables
sonar_range_mm = 0
sonar_time_us = 0

# Oscilloscope display variables
time_div = 500   # Starting scope grid horizontal time/div in us
volt_div = 2     # Scope grid vertical Volts/div in V
time_mult = 24 / time_div  # Time display factor
volt_mult = 24 / volt_div  # Volts display factor

# Start SONAR ranging and time both the TRIG -> ECHO delay and the
# ECHO pulse width separately for display.
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
    

beaper.nano_led_on()  # Simple status indicator

# Configure LCD
lcd = lcd_config.config()

while True:
    # Measure time to acquire SONAR range and convert range
    trig_time_us, echo_time_us = sonar_range_timing()
    if trig_time_us < 0 or echo_time_us < 0:
        # ECHO never started, or never ended - skip this update
        time.sleep_ms(50)
        continue
    sonar_range_mm = int(echo_time_us / 5.82)    # Calculate distance
    sonar_time_us = trig_time_us + echo_time_us  # Total ranging time
    # print(f"Range: {sonar_range_mm:4d}mm")

    # Dynamically adjust time/div setting to fit total ranging time
    if sonar_time_us > 10000:
        time_div = 2000  # 2ms/div
    elif sonar_time_us > 5000:
        time_div = 1000  # 1ms/div
    else:
        time_div = 500  # 500us/div
    time_mult = 24 / time_div
  
    # Clear LCD and draw oscilloscope grid
    lcd.fill(0x0)
    lcd.vline(239, 0, 192, lcd.GREY)
    lcd.hline(0, 191, 240, lcd.GREY)
    for x in range(0, 240, 24):
        lcd.vline(x, 0, 192, lcd.GREY)
    for y in range(0, 192, 24):
        lcd.hline(0, y, 240, lcd.GREY)
  
    # Write range and timing into LCD framebuffer
    lcd.text16(f"SONAR Range: {sonar_range_mm}mm", 2, 6, lcd.WHITE75)
    
    lcd.text16(f"TRIG delay: {trig_time_us/1000:.3f}ms", 0, 192, lcd.GREEN75)
    lcd.text16(f"ECHO pulse: {echo_time_us/1000:.3f}ms", 0, 208, lcd.YELLOW75)
    lcd.text16(f"Total time: {sonar_time_us/1000:.3f}ms", 0, 224, lcd.WHITE75)
  
    # Virtual scope parameters
    trace = 0  # trace time 0 (LCD x-value)
    ch1 = 96   # Channel 1 GND reference (LCD y-value)
    ch2 = 168  # Channel 2 GND reference (LCD y-value)

    # Draw TRIG pulse
    sig = int(3.3 * volt_mult) 
    lcd.vline(trace, ch1 - sig, sig, lcd.GREEN)
    lcd.hline(trace, ch1, 240, lcd.GREEN)
    
    # Draw TRIG delay
    h = int(trig_time_us * time_mult)
    lcd.hline(trace, ch2, h, lcd.YELLOW)
    trace += h
    
    # Draw ECHO pulse
    lcd.vline(trace, ch2-sig, sig, lcd.YELLOW)
    h = int((sonar_time_us - trig_time_us) * time_mult)
    lcd.hline(trace, ch2 - sig, h, lcd.YELLOW)
    trace += h
    lcd.vline(trace, ch2 - sig, sig, lcd.YELLOW)
    lcd.hline(trace, ch2, 240 - trace, lcd.YELLOW)
    
    # Write oscilloscope settings to framebuffer
    lcd.text(f"T:{time_div/1000:.3f}ms/div", 16, 180, lcd.WHITE75)
    lcd.text(f"V:{volt_div}V/div", 150, 180, lcd.WHITE75)

    # Update LCD from framebuffer
    lcd.update()

    time.sleep_ms(50)