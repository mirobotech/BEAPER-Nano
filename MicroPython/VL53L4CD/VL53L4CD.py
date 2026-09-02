# ==============================================================================
# VL53L4CD MicroPython Driver [VL53L4CD.py]
# Version: 1.1
# Updated: August 31, 2026
#
# MicroPython driver for the ST VL53L4CD time-of-flight distance sensor.
#
# Ported from ST's VL53L4CD_ULD_DRIVER v2.2.3 (VL53L4CD_api.c / VL53L4CD_api.h)
# Copyright (c) 2023 STMicroelectronics. All rights reserved. See licence below.
#
# Usage from a Raspberry Pi Pico or any MicroPython board with hardware I2C:
#
#   from machine import I2C, Pin
#   from VL53L4CD import VL53L4CD
#
#   i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400_000)  # substitute your pin numbers
#   tof = VL53L4CD(i2c)
#   tof.start_ranging()
#
#   # Simple use - get_range() blocks until a reading is ready (~50 ms)
#   while True:
#       dist = tof.get_range()
#       if dist >= 0:
#           print(dist, "mm")
#       elif dist == VL53L4CD.ERR_NO_TARGET:
#           print("Nothing detected")
#       elif dist == VL53L4CD.ERR_SIGMA_HIGH:
#           print("Noisy measurement - try a longer timing budget")
#       elif dist == VL53L4CD.ERR_WRAP_AROUND:
#           print("Target may be beyond sensor range")
#       else:   # ERR_HARDWARE
#           print("VL53L4CD sensor fault")
#
#   # Advanced use - non-blocking poll with full result detail
#   while True:
#       if tof.data_ready():
#           result = tof.get_result()
#           tof.clear_interrupt()
#           print(result['distance_mm'], "mm  status:", result['range_status'])
#
# ==============================================================================
#
# ST BSD Clear Licence (SLA0103)
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# - Redistributions of source code must retain the above copyright notice,
#   this list of conditions, and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions, and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# - Neither the name of STMicroelectronics nor the names of its contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# ==============================================================================

from micropython import const
import time

# ------------------------------------------------------------------------------
# Register addresses (from ST ULD v2.2.3)
# ------------------------------------------------------------------------------

_SOFT_RESET                            = const(0x0000)
_I2C_SLAVE__DEVICE_ADDRESS             = const(0x0001)
_VHV_CONFIG__TIMEOUT_MACROP_LOOP_BOUND = const(0x0008)
_XTALK_PLANE_OFFSET_KCPS               = const(0x0016)
_XTALK_X_PLANE_GRADIENT_KCPS           = const(0x0018)
_XTALK_Y_PLANE_GRADIENT_KCPS           = const(0x001A)
_RANGE_OFFSET_MM                       = const(0x001E)
_INNER_OFFSET_MM                       = const(0x0020)
_OUTER_OFFSET_MM                       = const(0x0022)
_GPIO_HV_MUX__CTRL                     = const(0x0030)
_GPIO__TIO_HV_STATUS                   = const(0x0031)
_SYSTEM__INTERRUPT                     = const(0x0046)
_RANGE_CONFIG_A                        = const(0x005E)
_RANGE_CONFIG_B                        = const(0x0061)
_RANGE_CONFIG__SIGMA_THRESH            = const(0x0064)
_MIN_COUNT_RATE_RTN_LIMIT_MCPS         = const(0x0066)
_INTERMEASUREMENT_MS                   = const(0x006C)
_THRESH_HIGH                           = const(0x0072)
_THRESH_LOW                            = const(0x0074)
_SYSTEM__INTERRUPT_CLEAR               = const(0x0086)
_SYSTEM_START                          = const(0x0087)
_RESULT__RANGE_STATUS                  = const(0x0089)
_RESULT__SPAD_NB                       = const(0x008C)
_RESULT__SIGNAL_RATE                   = const(0x008E)
_RESULT__AMBIENT_RATE                  = const(0x0090)
_RESULT__SIGMA                         = const(0x0092)
_RESULT__DISTANCE                      = const(0x0096)
_RESULT__OSC_CALIBRATE_VAL             = const(0x00DE)
_FIRMWARE__SYSTEM_STATUS               = const(0x00E5)
_IDENTIFICATION__MODEL_ID              = const(0x010F)

# ------------------------------------------------------------------------------
# Default configuration blob - written to registers 0x2D-0x87 during init.
# Byte at index N is written to register (0x2D + N).
# ------------------------------------------------------------------------------

_DEFAULT_CONFIGURATION = bytes([
    0x00,  # 0x2D  set bits 2 and 5 to 1 for fast plus mode (1 MHz I2C),
           #       otherwise leave unchanged
    0x00,  # 0x2F  set bit 0 to 0 if I2C is pulled up to 1.8V,
           #       or set bit 0 to 1 to pull up to AVDD
    0x00,  # 0x2F  set bit 0 to 0 if GPIO is pulled up to 1.8V,
           #       or set bit 0 to 1 to pull up to AVDD
    0x11,  # 0x30  set bit 4 to 0 for active-high interrupt, or 1 for active-low
           #       (bits 3:0 must remain 0x1); use set_interrupt_polarity()
    0x02,  # 0x31  bit 1 sets interrupt behaviour based on polarity;
           #       use data_ready()
    0x00,  # 0x32
    0x02,  # 0x33
    0x08,  # 0x34
    0x00,  # 0x35
    0x08,  # 0x36
    0x10,  # 0x37
    0x01,  # 0x38
    0x01,  # 0x39
    0x00,  # 0x3A
    0x00,  # 0x3B
    0x00,  # 0x3C
    0x00,  # 0x3D
    0xFF,  # 0x3E
    0x00,  # 0x3F
    0x0F,  # 0x40
    0x00,  # 0x41
    0x00,  # 0x42
    0x00,  # 0x43
    0x00,  # 0x44
    0x00,  # 0x45
    0x20,  # 0x46  interrupt mode: 0=level low, 1=level high, 2=out of window,
           #       3=in window, 0x20=new sample ready
    0x0B,  # 0x47
    0x00,  # 0x48
    0x00,  # 0x49
    0x02,  # 0x4A
    0x14,  # 0x4B
    0x21,  # 0x4C
    0x00,  # 0x4D
    0x00,  # 0x4E
    0x05,  # 0x4F
    0x00,  # 0x50
    0x00,  # 0x51
    0x00,  # 0x52
    0x00,  # 0x53
    0xC8,  # 0x54
    0x00,  # 0x55
    0x00,  # 0x56
    0x38,  # 0x57
    0xFF,  # 0x58
    0x01,  # 0x59
    0x00,  # 0x5A
    0x08,  # 0x5B
    0x00,  # 0x5C
    0x00,  # 0x5D
    0x01,  # 0x5E
    0xCC,  # 0x5F
    0x07,  # 0x60
    0x01,  # 0x61
    0xF1,  # 0x62
    0x05,  # 0x63
    0x00,  # 0x64  sigma threshold MSB (14.2 fixed-point mm, MSB+LSB combined);
           #       use set_sigma_threshold(); default value 15 mm
    0xA0,  # 0x65  sigma threshold LSB
    0x00,  # 0x66  minimum signal rate threshold MSB (9.7 fixed-point MCPS, MSB+LSB);
           #       use set_signal_threshold()
    0x80,  # 0x67  minimum signal rate threshold LSB
    0x08,  # 0x68
    0x38,  # 0x69
    0x00,  # 0x6A
    0x00,  # 0x6B
    0x00,  # 0x6C  inter-measurement period MSB (32-bit register);
           #       use set_range_timing()
    0x00,  # 0x6D  inter-measurement period
    0x0F,  # 0x6E  inter-measurement period
    0x89,  # 0x6F  inter-measurement period LSB
    0x00,  # 0x70
    0x00,  # 0x71
    0x00,  # 0x72  distance threshold high MSB (mm, MSB+LSB combined);
           #       use set_detection_thresholds()
    0x00,  # 0x73  distance threshold high LSB
    0x00,  # 0x74  distance threshold low MSB (mm, MSB+LSB combined);
           #       use set_detection_thresholds()
    0x00,  # 0x75  distance threshold low LSB
    0x00,  # 0x76
    0x01,  # 0x77
    0x07,  # 0x78
    0x05,  # 0x79
    0x06,  # 0x7A
    0x06,  # 0x7B
    0x00,  # 0x7C
    0x00,  # 0x7D
    0x02,  # 0x7E
    0xC7,  # 0x7F
    0xFF,  # 0x80
    0x9B,  # 0x81
    0x00,  # 0x82
    0x00,  # 0x83
    0x00,  # 0x84
    0x01,  # 0x85
    0x00,  # 0x86  clear interrupt; use clear_interrupt()
    0x00,  # 0x87  start/stop ranging; use start_ranging() and stop_ranging()
])

# Range status translation table. Index = raw hardware status, value = reported status.
_STATUS_RTN = (255, 255, 255, 5, 2, 4, 1, 7, 3,
               0, 255, 255, 9, 13, 255, 255, 255, 255, 10, 6,
               255, 255, 11, 12)


# ------------------------------------------------------------------------------
# VL53L4CDError exception class
# ------------------------------------------------------------------------------

class VL53L4CDError(Exception):
    pass


# ------------------------------------------------------------------------------
# VL53L4CD driver class
# ------------------------------------------------------------------------------

class VL53L4CD:

    # Default 7-bit I2C address
    DEFAULT_ADDRESS = const(0x29)

    # Return codes for get_range() when a measurement is not valid.
    # Codes are negative so they cannot be confused with a real distance in mm.

    # Signal too low - nothing detected within range, or target absorbs too much light.
    ERR_NO_TARGET   = const(-1)

    # Measurement noise (sigma) above threshold - result unreliable; try a longer
    # timing budget or clean the external lens if one is fitted to the sensor.
    ERR_SIGMA_HIGH  = const(-2)

    # Target may be beyond the sensor's ~1300 mm unambiguous range; the reflected
    # pulse has wrapped around.
    ERR_WRAP_AROUND = const(-3)

    # Sensor reported a hardware or algorithm fault.
    ERR_HARDWARE    = const(-4)

    def __init__(self, i2c, address=DEFAULT_ADDRESS):
        # Initialise the driver and run sensor startup and VHV calibration.
        # i2c must be an already-initialised machine.I2C instance.
        self._i2c = i2c
        self._addr = address
        self._init()

    # --------------------------------------------------------------------------
    # Public API
    # --------------------------------------------------------------------------

    def get_sensor_id(self):
        # Return the 16-bit model ID. Expected value is 0xEBAA.
        return self._rd_word(_IDENTIFICATION__MODEL_ID)

    def set_i2c_address(self, new_address):
        # Change the sensor's I2C address to new_address (7-bit value).
        self._wr_byte(_I2C_SLAVE__DEVICE_ADDRESS, new_address >> 1)
        self._addr = new_address

    def start_ranging(self):
        # Start ranging. Uses continuous mode when the inter-measurement period
        # register is 0 (the default after init), or autonomous mode otherwise.
        # Set the inter-measurement period with set_range_timing() before calling
        # this function to select autonomous mode.
        tmp = self._rd_dword(_INTERMEASUREMENT_MS)
        if tmp == 0:
            self._wr_byte(_SYSTEM_START, 0x21)  # continuous mode
        else:
            self._wr_byte(_SYSTEM_START, 0x40)  # autonomous mode

    def stop_ranging(self):
        # Stop an ongoing ranging session.
        self._wr_byte(_SYSTEM_START, 0x80)

    def clear_interrupt(self):
        # Clear the data-ready interrupt flag to re-arm the sensor for the next
        # measurement. Must be called after every get_result() call.
        # Note: get_range() calls this automatically.
        self._wr_byte(_SYSTEM__INTERRUPT_CLEAR, 0x01)

    def data_ready(self):
        # Return True if a new ranging result is available. Used for
        # non-blocking polling; call get_result() when True.
        temp = self._rd_byte(_GPIO_HV_MUX__CTRL)
        int_pol = 0 if (temp & 0x10) >> 4 == 1 else 1
        status = self._rd_byte(_GPIO__TIO_HV_STATUS)
        return (status & 0x01) == int_pol

    def get_result(self):
        # Read and return the latest ranging result as a dictionary.
        # Call get_result() after data_ready() is True, then call
        # clear_interrupt() to initiate next range measurement.
        # Note: get_range() handles all three steps automatically.
        #
        # Dictionary keys:
        #   range_status          - 0 = valid measurement
        #   distance_mm           - distance in millimetres
        #   ambient_rate_kcps     - ambient light noise rate (kcps)
        #   ambient_per_spad_kcps - ambient noise per SPAD (kcps)
        #   signal_rate_kcps      - returned signal rate (kcps)
        #   signal_per_spad_kcps  - signal rate per SPAD (kcps)
        #   number_of_spad        - number of enabled SPADs
        #   sigma_mm              - standard deviation of the measurement (mm)

        # Read and translate the raw range status byte
        temp_8 = self._rd_byte(_RESULT__RANGE_STATUS) & 0x1F
        if temp_8 < 24:
            temp_8 = _STATUS_RTN[temp_8]

        # Read SPAD count
        raw_spads = self._rd_word(_RESULT__SPAD_NB)
        number_of_spad = raw_spads // 256

        # Read signal and ambient rates (scaled to kcps)
        signal_rate_kcps  = self._rd_word(_RESULT__SIGNAL_RATE)  * 8
        ambient_rate_kcps = self._rd_word(_RESULT__AMBIENT_RATE) * 8

        # Read sigma and distance
        sigma_mm    = self._rd_word(_RESULT__SIGMA) // 4
        distance_mm = self._rd_word(_RESULT__DISTANCE)

        # Calculate per-SPAD rates (guard against division by zero)
        if raw_spads:
            signal_per_spad_kcps  = signal_rate_kcps  * 256 // raw_spads
            ambient_per_spad_kcps = ambient_rate_kcps * 256 // raw_spads
        else:
            signal_per_spad_kcps  = 0
            ambient_per_spad_kcps = 0

        return {
            'range_status':          temp_8,
            'distance_mm':           distance_mm,
            'ambient_rate_kcps':     ambient_rate_kcps,
            'ambient_per_spad_kcps': ambient_per_spad_kcps,
            'signal_rate_kcps':      signal_rate_kcps,
            'signal_per_spad_kcps':  signal_per_spad_kcps,
            'number_of_spad':        number_of_spad,
            'sigma_mm':              sigma_mm,
        }

    def get_range(self):
        # Blocking distance read for simple projects.
        # Waits until range measurement is finished, then returns one of:
        #   distance in mm (int >= 0)  - valid measurement
        #   ERR_NO_TARGET  (-1)        - signal too low; nothing detected
        #   ERR_SIGMA_HIGH (-2)        - measurement too noisy; result unreliable
        #   ERR_WRAP_AROUND (-3)       - target may be beyond the ~1300 mm range
        #   ERR_HARDWARE   (-4)        - sensor hardware or algorithm fault
        #
        # clear_interrupt() is called automatically so the sensor is immediately
        # ready for the next measurement.
        #
        # Example:
        #   tof.start_ranging()
        #   while True:
        #       dist = tof.get_range()
        #       if dist >= 0:
        #           print(dist, "mm")
        #       elif dist == VL53L4CD.ERR_NO_TARGET:
        #           print("Nothing detected")

        while not self.data_ready():
            time.sleep_ms(1)

        result = self.get_result()
        self.clear_interrupt()

        status = result['range_status']
        if status == 0:
            return result['distance_mm']
        elif status == 2:
            return self.ERR_NO_TARGET
        elif status == 1:
            return self.ERR_SIGMA_HIGH
        elif status in (4, 7):
            return self.ERR_WRAP_AROUND
        else:
            return self.ERR_HARDWARE

    def set_range_timing(self, timing_budget_ms, inter_measurement_ms=0):
        # Set the timing budget and inter-measurement period.
        #
        # timing_budget_ms     - VCSEL on-time per measurement, 10-200 ms (default 50).
        #                        Longer budgets improve accuracy and range but reduce
        #                        the measurement update rate.
        # inter_measurement_ms - 0 = continuous mode (back-to-back measurements).
        #                        Any value greater than timing_budget_ms enables
        #                        autonomous (low-power) mode, with the sensor sleeping
        #                        between measurements for the specified period.

        osc_frequency = self._rd_word(0x0006)
        if osc_frequency == 0:
            raise VL53L4CDError("invalid osc_frequency (0)")

        if not (10 <= timing_budget_ms <= 200):
            raise VL53L4CDError("timing_budget_ms must be 10-200")

        timing_budget_us = timing_budget_ms * 1000
        macro_period_us  = (2304 * (0x40000000 // osc_frequency)) >> 6

        if inter_measurement_ms == 0:
            # Continuous mode - sensor measures back-to-back
            self._wr_dword(_INTERMEASUREMENT_MS, 0)
            timing_budget_us -= 2500

        elif inter_measurement_ms > timing_budget_ms:
            # Autonomous mode - sensor sleeps between measurements
            clock_pll = self._rd_word(_RESULT__OSC_CALIBRATE_VAL) & 0x3FF
            inter_meas_reg = int(1.055 * inter_measurement_ms * clock_pll)
            self._wr_dword(_INTERMEASUREMENT_MS, inter_meas_reg)
            timing_budget_us -= 4300
            timing_budget_us //= 2

        else:
            raise VL53L4CDError(
                "inter_measurement_ms must be 0 (continuous) "
                "or greater than timing_budget_ms (autonomous)"
            )

        # Encode and write RANGE_CONFIG_A (macro period * 16)
        self._wr_word(_RANGE_CONFIG_A,
                      self._encode_timeout(timing_budget_us, macro_period_us * 16))
        # Encode and write RANGE_CONFIG_B (macro period * 12)
        self._wr_word(_RANGE_CONFIG_B,
                      self._encode_timeout(timing_budget_us, macro_period_us * 12))

    def get_range_timing(self):
        # Return the current timing budget and inter-measurement period as a
        # (timing_budget_ms, inter_measurement_ms) tuple.
        tmp       = self._rd_dword(_INTERMEASUREMENT_MS)
        clock_pll = self._rd_word(_RESULT__OSC_CALIBRATE_VAL) & 0x3FF
        inter_ms  = tmp // int(1.065 * clock_pll) if clock_pll else 0

        osc_frequency         = self._rd_word(0x0006)
        range_config_macrop_h = self._rd_word(_RANGE_CONFIG_A)

        macro_period_us = (2304 * (0x40000000 // osc_frequency)) >> 6
        ls_byte = (range_config_macrop_h & 0x00FF) << 4
        ms_byte = (range_config_macrop_h & 0xFF00) >> 8
        ms_byte = 0x04 - (ms_byte - 1) - 1

        macro_period_us *= 16
        budget_ms = (((ls_byte + 1) * (macro_period_us >> 6))
                     - ((macro_period_us >> 6) >> 1)) >> 12

        if ms_byte < 12:
            budget_ms >>= ms_byte

        if tmp == 0:
            budget_ms += 2500       # continuous mode offset
        else:
            budget_ms = budget_ms * 2 + 4300  # autonomous mode offset

        budget_ms //= 1000
        return int(budget_ms), int(inter_ms)

    def set_offset(self, offset_mm):
        # Set the range offset correction in mm (-1024 to +1023).
        # Compensates for a fixed distance error caused by the optical stack or
        # a coverglass. Measure against a target at a known distance and pass the
        # difference (true distance minus measured distance) to this function.
        temp = (offset_mm * 4) & 0xFFFF
        self._wr_word(_RANGE_OFFSET_MM, temp)
        self._wr_word(_INNER_OFFSET_MM, 0)
        self._wr_word(_OUTER_OFFSET_MM, 0)

    def get_offset(self):
        # Return the current range offset correction in mm.
        temp = self._rd_word(_RANGE_OFFSET_MM)
        temp = (temp << 3) >> 5  # sign-extend the 11-bit value
        if temp > 1024:
            temp -= 2048
        return temp

    def set_xtalk(self, xtalk_kcps):
        # Set cross-talk correction in kcps (0-128; use 0 for no coverglass).
        # Compensates for light reflected from a coverglass back into the sensor.
        self._wr_word(_XTALK_X_PLANE_GRADIENT_KCPS, 0)
        self._wr_word(_XTALK_Y_PLANE_GRADIENT_KCPS, 0)
        self._wr_word(_XTALK_PLANE_OFFSET_KCPS, (xtalk_kcps << 9) & 0xFFFF)

    def get_xtalk(self):
        # Return the current cross-talk correction value in kcps.
        raw = self._rd_word(_XTALK_PLANE_OFFSET_KCPS)
        return round(raw / 512.0)

    def set_detection_thresholds(self, distance_low_mm, distance_high_mm, window):
        # Configure the distance-threshold interrupt.
        # window values:
        #   0 - trigger when distance is below distance_low_mm
        #   1 - trigger when distance is above distance_high_mm
        #   2 - trigger when distance is outside [distance_low_mm, distance_high_mm]
        #   3 - trigger when distance is inside  [distance_low_mm, distance_high_mm]
        self._wr_byte(_SYSTEM__INTERRUPT, window)
        self._wr_word(_THRESH_HIGH, distance_high_mm)
        self._wr_word(_THRESH_LOW,  distance_low_mm)

    def get_detection_thresholds(self):
        # Return the current detection threshold settings as a
        # (distance_low_mm, distance_high_mm, window) tuple.
        high   = self._rd_word(_THRESH_HIGH)
        low    = self._rd_word(_THRESH_LOW)
        window = self._rd_byte(_SYSTEM__INTERRUPT) & 0x07
        return low, high, window

    def set_signal_threshold(self, signal_kcps):
        # Set the minimum signal threshold in kcps (0-16384; default 1024).
        # Measurements below this threshold report range_status 2 (no target).
        self._wr_word(_MIN_COUNT_RATE_RTN_LIMIT_MCPS, signal_kcps >> 3)

    def get_signal_threshold(self):
        # Return the current minimum signal threshold in kcps.
        return self._rd_word(_MIN_COUNT_RATE_RTN_LIMIT_MCPS) << 3

    def set_sigma_threshold(self, sigma_mm):
        # Set the sigma (standard deviation) threshold in mm (0-16383; default 15).
        # Measurements above this threshold report range_status 1 (noisy).
        if sigma_mm > (0xFFFF >> 2):
            raise VL53L4CDError("sigma_mm too large (max 16383)")
        self._wr_word(_RANGE_CONFIG__SIGMA_THRESH, sigma_mm << 2)

    def get_sigma_threshold(self):
        # Return the current sigma threshold in mm.
        return self._rd_word(_RANGE_CONFIG__SIGMA_THRESH) >> 2

    def start_temperature_update(self):
        # Recalibrate the VHV circuit when ambient temperature has changed by
        # more than 8 degrees C since the last calibration.
        # The sensor must not be ranging when this function is called.
        self._wr_byte(_VHV_CONFIG__TIMEOUT_MACROP_LOOP_BOUND, 0x81)
        self._wr_byte(0x0B, 0x92)
        self.start_ranging()

        deadline = time.ticks_add(time.ticks_ms(), 1000)
        while not self.data_ready():
            if time.ticks_diff(deadline, time.ticks_ms()) <= 0:
                raise VL53L4CDError("temperature update timed out")
            time.sleep_ms(1)

        self.clear_interrupt()
        self.stop_ranging()
        self._wr_byte(_VHV_CONFIG__TIMEOUT_MACROP_LOOP_BOUND, 0x09)
        self._wr_byte(0x0B, 0x00)

    # --------------------------------------------------------------------------
    # Initialisation (mirrors VL53L4CD_SensorInit from ST ULD v2.2.3)
    # --------------------------------------------------------------------------

    def _init(self):
        # Wait for the sensor firmware to finish booting (register 0xE5 == 0x03),
        # with a 1000 ms timeout.
        deadline = time.ticks_add(time.ticks_ms(), 1000)
        while True:
            if self._rd_byte(_FIRMWARE__SYSTEM_STATUS) == 0x03:
                break
            if time.ticks_diff(deadline, time.ticks_ms()) <= 0:
                raise VL53L4CDError("sensor boot timed out")
            time.sleep_ms(1)

        # Write the default configuration to registers 0x2D-0x87
        for i, val in enumerate(_DEFAULT_CONFIGURATION):
            self._wr_byte(0x2D + i, val)

        # Run VHV (voltage high voltage) calibration
        self._wr_byte(_SYSTEM_START, 0x40)
        deadline = time.ticks_add(time.ticks_ms(), 1000)
        while not self.data_ready():
            if time.ticks_diff(deadline, time.ticks_ms()) <= 0:
                raise VL53L4CDError("VHV calibration timed out")
            time.sleep_ms(1)

        self.clear_interrupt()
        self.stop_ranging()
        self._wr_byte(_VHV_CONFIG__TIMEOUT_MACROP_LOOP_BOUND, 0x09)
        self._wr_byte(0x0B, 0x00)
        self._wr_word(0x0024, 0x0500)

        # Set default timing: 50 ms budget, continuous mode
        self.set_range_timing(50, 0)

    # --------------------------------------------------------------------------
    # I2C register helpers
    # The VL53L4CD uses 16-bit big-endian register addresses followed by data.
    # --------------------------------------------------------------------------

    def _wr_byte(self, reg, val):
        # Write one byte to a 16-bit register address.
        self._i2c.writeto(self._addr,
                          bytes([(reg >> 8) & 0xFF, reg & 0xFF, val & 0xFF]))

    def _wr_word(self, reg, val):
        # Write a 16-bit value (big-endian) to a 16-bit register address.
        self._i2c.writeto(self._addr,
                          bytes([(reg >> 8) & 0xFF, reg & 0xFF,
                                 (val >> 8) & 0xFF, val & 0xFF]))

    def _wr_dword(self, reg, val):
        # Write a 32-bit value (big-endian) to a 16-bit register address.
        self._i2c.writeto(self._addr,
                          bytes([(reg >> 8) & 0xFF, reg & 0xFF,
                                 (val >> 24) & 0xFF, (val >> 16) & 0xFF,
                                 (val >> 8)  & 0xFF,  val & 0xFF]))

    def _rd_byte(self, reg):
        # Read and return one byte from a 16-bit register address.
        self._i2c.writeto(self._addr,
                          bytes([(reg >> 8) & 0xFF, reg & 0xFF]))
        return self._i2c.readfrom(self._addr, 1)[0]

    def _rd_word(self, reg):
        # Read and return a 16-bit big-endian value from a 16-bit register address.
        self._i2c.writeto(self._addr,
                          bytes([(reg >> 8) & 0xFF, reg & 0xFF]))
        d = self._i2c.readfrom(self._addr, 2)
        return (d[0] << 8) | d[1]

    def _rd_dword(self, reg):
        # Read and return a 32-bit big-endian value from a 16-bit register address.
        self._i2c.writeto(self._addr,
                          bytes([(reg >> 8) & 0xFF, reg & 0xFF]))
        d = self._i2c.readfrom(self._addr, 4)
        return (d[0] << 24) | (d[1] << 16) | (d[2] << 8) | d[3]

    # --------------------------------------------------------------------------
    # Internal timing helper
    # --------------------------------------------------------------------------

    @staticmethod
    def _encode_timeout(timing_budget_us, macro_period_x):
        # Encode a timing budget into the 16-bit RANGE_CONFIG register format
        # used by RANGE_CONFIG_A and RANGE_CONFIG_B.
        # timing_budget_us - budget value (already shifted left by 12 by the caller)
        # macro_period_x   - macro_period_us * 16 for RANGE_CONFIG_A,
        #                    or macro_period_us * 12 for RANGE_CONFIG_B
        tb = timing_budget_us << 12
        denom = macro_period_x >> 6
        ls_byte = ((tb + (denom >> 1)) // denom) - 1

        ms_byte = 0
        while ls_byte & 0xFFFFFF00:
            ls_byte >>= 1
            ms_byte  += 1

        return ((ms_byte << 8) | (ls_byte & 0xFF)) & 0xFFFF