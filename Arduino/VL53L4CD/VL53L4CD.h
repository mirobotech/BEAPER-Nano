/**
 * VL53L4CD.h  –  Arduino library for the ST VL53L4CD time-of-flight sensor
 * Updated: June 15, 2026
 *
 * Ported from ST's VL53L4CD_ULD_DRIVER v2.2.3
 * Copyright (c) 2023 STMicroelectronics. All rights reserved. See licence below.
 *
 * ============================================================================
 * INSTALLATION
 * ============================================================================
 *
 * METHOD 1 – Install from ZIP (recommended for beginners)
 *   1. Download or copy the VL53L4CD library folder and compress it as a ZIP.
 *   2. In the Arduino IDE, open Sketch > Include Library > Add .ZIP Library…
 *   3. Select the ZIP file and click Open.
 *   4. The library is now available. Use Sketch > Include Library > VL53L4CD
 *      to add  #include <VL53L4CD.h>  to your sketch, or type it manually.
 *
 * METHOD 2 – Manual installation
 *   1. Copy the entire VL53L4CD folder (containing VL53L4CD.h and VL53L4CD.cpp)
 *      into your Arduino libraries folder:
 *        Windows : Documents\Arduino\libraries\
 *        macOS   : ~/Documents/Arduino/libraries/
 *        Linux   : ~/Arduino/libraries/
 *   2. Restart the Arduino IDE.
 *   3. Add  #include <VL53L4CD.h>  to the top of your sketch.
 *
 * ============================================================================
 * WIRING (for 3.3 V boards such as the Raspberry Pi Pico or Arduino Nano 33)
 * ============================================================================
 *
 *   VL53L4CD pin    Arduino / Pico pin
 *   ─────────────   ──────────────────
 *   VIN / VCC       3.3 V
 *   GND             GND
 *   SDA             SDA  (e.g. GP4 on Pico, A4 on Uno)
 *   SCL             SCL  (e.g. GP5 on Pico, A5 on Uno)
 *
 *   Call Wire.begin() in setup() before constructing the VL53L4CD object,
 *   or pass your Wire instance to the constructor (see below).
 *
 * ============================================================================
 * QUICK START
 * ============================================================================
 *
 *   #include <Wire.h>
 *   #include <VL53L4CD.h>
 *
 *   VL53L4CD tof;
 *
 *   void setup() {
 *     Serial.begin(115200);
 *     Wire.begin();
 *     if (!tof.begin()) {
 *       Serial.println("Sensor not found – check wiring!");
 *       while (1);
 *     }
 *     tof.startRanging();
 *   }
 *
 *   void loop() {
 *     int16_t dist = tof.getRange();
 *     if (dist >= 0) {
 *       Serial.print(dist);
 *       Serial.println(" mm");
 *     } else if (dist == VL53L4CD::ERR_NO_TARGET) {
 *       Serial.println("Nothing detected");
 *     }
 *   }
 */

/*
 * ST BSD Clear licence (SLA0103)
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * - Redistributions of source code must retain the above copyright notice,
 *   this list of conditions and the following disclaimer.
 * - Redistributions in binary form must reproduce the above copyright notice,
 *   this list of conditions and the following disclaimer in the documentation
 *   and/or other materials provided with the distribution.
 * - Neither the name of STMicroelectronics nor the names of its contributors
 *   may be used to endorse or promote products derived from this software
 *   without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

#ifndef VL53L4CD_H
#define VL53L4CD_H

#include <Arduino.h>
#include <Wire.h>

// ---------------------------------------------------------------------------
// Register addresses (from ST ULD v2.2.3)
// ---------------------------------------------------------------------------
#define VL53L4CD_SOFT_RESET                          ((uint16_t)0x0000)
#define VL53L4CD_I2C_SLAVE__DEVICE_ADDRESS           ((uint16_t)0x0001)
#define VL53L4CD_VHV_CONFIG__TIMEOUT_MACROP_LOOP_BOUND ((uint16_t)0x0008)
#define VL53L4CD_XTALK_PLANE_OFFSET_KCPS            ((uint16_t)0x0016)
#define VL53L4CD_XTALK_X_PLANE_GRADIENT_KCPS        ((uint16_t)0x0018)
#define VL53L4CD_XTALK_Y_PLANE_GRADIENT_KCPS        ((uint16_t)0x001A)
#define VL53L4CD_RANGE_OFFSET_MM                     ((uint16_t)0x001E)
#define VL53L4CD_INNER_OFFSET_MM                     ((uint16_t)0x0020)
#define VL53L4CD_OUTER_OFFSET_MM                     ((uint16_t)0x0022)
#define VL53L4CD_GPIO_HV_MUX__CTRL                   ((uint16_t)0x0030)
#define VL53L4CD_GPIO__TIO_HV_STATUS                 ((uint16_t)0x0031)
#define VL53L4CD_SYSTEM__INTERRUPT                   ((uint16_t)0x0046)
#define VL53L4CD_RANGE_CONFIG_A                      ((uint16_t)0x005E)
#define VL53L4CD_RANGE_CONFIG_B                      ((uint16_t)0x0061)
#define VL53L4CD_RANGE_CONFIG__SIGMA_THRESH          ((uint16_t)0x0064)
#define VL53L4CD_MIN_COUNT_RATE_RTN_LIMIT_MCPS       ((uint16_t)0x0066)
#define VL53L4CD_INTERMEASUREMENT_MS                 ((uint16_t)0x006C)
#define VL53L4CD_THRESH_HIGH                         ((uint16_t)0x0072)
#define VL53L4CD_THRESH_LOW                          ((uint16_t)0x0074)
#define VL53L4CD_SYSTEM__INTERRUPT_CLEAR             ((uint16_t)0x0086)
#define VL53L4CD_SYSTEM_START                        ((uint16_t)0x0087)
#define VL53L4CD_RESULT__RANGE_STATUS                ((uint16_t)0x0089)
#define VL53L4CD_RESULT__SPAD_NB                     ((uint16_t)0x008C)
#define VL53L4CD_RESULT__SIGNAL_RATE                 ((uint16_t)0x008E)
#define VL53L4CD_RESULT__AMBIENT_RATE                ((uint16_t)0x0090)
#define VL53L4CD_RESULT__SIGMA                       ((uint16_t)0x0092)
#define VL53L4CD_RESULT__DISTANCE                    ((uint16_t)0x0096)
#define VL53L4CD_RESULT__OSC_CALIBRATE_VAL           ((uint16_t)0x00DE)
#define VL53L4CD_FIRMWARE__SYSTEM_STATUS             ((uint16_t)0x00E5)
#define VL53L4CD_IDENTIFICATION__MODEL_ID            ((uint16_t)0x010F)

// Default I2C address (7-bit)
#define VL53L4CD_DEFAULT_I2C_ADDRESS                 ((uint8_t)0x29)

// ---------------------------------------------------------------------------
// Result data structure  (mirrors ST's VL53L4CD_ResultsData_t)
// ---------------------------------------------------------------------------

/** Full ranging result returned by getResult(). */
struct VL53L4CD_Result_t {
    uint8_t  range_status;           ///< 0 = valid measurement
    uint16_t distance_mm;            ///< Distance in millimetres
    uint32_t ambient_rate_kcps;      ///< Ambient noise (kcps)
    uint32_t ambient_per_spad_kcps;  ///< Ambient noise per SPAD (kcps)
    uint32_t signal_rate_kcps;       ///< Signal rate (kcps)
    uint32_t signal_per_spad_kcps;   ///< Signal rate per SPAD (kcps)
    uint16_t number_of_spad;         ///< Number of enabled SPADs
    uint16_t sigma_mm;               ///< Std deviation of pulse (mm)
};

// ---------------------------------------------------------------------------
// VL53L4CD class
// ---------------------------------------------------------------------------

class VL53L4CD {
public:

    // -----------------------------------------------------------------------
    // Error codes returned by getRange()
    //
    // All values are negative so they cannot be confused with a real distance.
    // -----------------------------------------------------------------------

    /** Signal too low – nothing detected in range, or target surface absorbs
     *  too much light. */
    static const int16_t ERR_NO_TARGET   = -1;

    /** Measurement noise (sigma) above threshold – result exists but is
     *  unreliable. Try a longer timing budget or clean the lens. */
    static const int16_t ERR_SIGMA_HIGH  = -2;

    /** Target may be beyond the sensor's ~1300 mm unambiguous range;
     *  the reflected pulse has wrapped around. */
    static const int16_t ERR_WRAP_AROUND = -3;

    /** Sensor reported a hardware or algorithm fault. */
    static const int16_t ERR_HARDWARE    = -4;

    // -----------------------------------------------------------------------
    // Constructor
    // -----------------------------------------------------------------------

    /**
     * @brief Create a VL53L4CD driver instance.
     * @param wire    I2C bus to use (default: Wire).
     * @param address 7-bit I2C address (default: 0x29).
     */
    VL53L4CD(TwoWire &wire = Wire, uint8_t address = VL53L4CD_DEFAULT_I2C_ADDRESS);

    // -----------------------------------------------------------------------
    // Initialisation
    // -----------------------------------------------------------------------

    /**
     * @brief Initialise the sensor. Must be called once in setup(), after
     *        Wire.begin().
     *
     * Waits for the sensor firmware to boot, loads the default configuration
     * blob, runs VHV calibration, and sets a 50 ms timing budget in
     * continuous mode.
     *
     * @return true if initialisation succeeded, false if the sensor did not
     *         respond or calibration timed out.
     */
    bool begin();

    // -----------------------------------------------------------------------
    // Ranging control
    // -----------------------------------------------------------------------

    /**
     * @brief Start continuous or autonomous ranging.
     *
     * Uses continuous mode when inter_measurement_ms is 0 (the default after
     * begin()), or autonomous (low-power) mode when a non-zero inter-
     * measurement period has been set via setRangeTiming().
     */
    void startRanging();

    /** @brief Stop an ongoing ranging session. */
    void stopRanging();

    /**
     * @brief Returns true when a new measurement result is ready to be read.
     *
     * Use this for non-blocking polling. When it returns true, call
     * getResult() followed by clearInterrupt().
     */
    bool dataReady();

    /**
     * @brief Clear the data-ready interrupt.
     *
     * Must be called after every getResult() call to re-arm the interrupt for
     * the next measurement. Called automatically by getRange().
     */
    void clearInterrupt();

    // -----------------------------------------------------------------------
    // Reading results
    // -----------------------------------------------------------------------

    /**
     * @brief Simple blocking distance read – the easiest way to use the sensor.
     *
     * Waits (blocking) until a measurement is ready, reads it, clears the
     * interrupt, and returns one of:
     *
     *   >= 0              Valid distance in millimetres
     *   ERR_NO_TARGET     Signal too low – nothing in range
     *   ERR_SIGMA_HIGH    Measurement too noisy – result unreliable
     *   ERR_WRAP_AROUND   Target may be beyond ~1300 mm unambiguous range
     *   ERR_HARDWARE      Sensor hardware or algorithm fault
     *
     * Example:
     * @code
     *   int16_t dist = tof.getRange();
     *   if (dist >= 0) {
     *     Serial.print(dist); Serial.println(" mm");
     *   } else if (dist == VL53L4CD::ERR_NO_TARGET) {
     *     Serial.println("Nothing detected");
     *   }
     * @endcode
     */
    int16_t getRange();

    /**
     * @brief Read the full ranging result (non-blocking).
     *
     * Call dataReady() first. After reading, call clearInterrupt() to arm
     * the sensor for the next measurement.
     *
     * @param result Reference to a VL53L4CD_Result_t struct to fill.
     * @return true if the read succeeded.
     */
    bool getResult(VL53L4CD_Result_t &result);

    // -----------------------------------------------------------------------
    // Timing
    // -----------------------------------------------------------------------

    /**
     * @brief Set the timing budget and inter-measurement period.
     *
     * @param timing_budget_ms      VCSEL on-time per measurement, 10–200 ms
     *                              (default 50). Longer budgets improve
     *                              accuracy and range but reduce update rate.
     * @param inter_measurement_ms  0 = continuous mode (back-to-back
     *                              measurements). Any value greater than
     *                              timing_budget_ms enables autonomous
     *                              (low-power) mode with that period between
     *                              measurements.
     * @return true if the parameters were valid and applied successfully.
     */
    bool setRangeTiming(uint32_t timing_budget_ms,
                        uint32_t inter_measurement_ms = 0);

    /**
     * @brief Get the current timing budget and inter-measurement period.
     * @param timing_budget_ms      Filled with the current budget in ms.
     * @param inter_measurement_ms  Filled with the current period in ms.
     * @return true on success.
     */
    bool getRangeTiming(uint32_t &timing_budget_ms,
                        uint32_t &inter_measurement_ms);

    // -----------------------------------------------------------------------
    // Calibration
    // -----------------------------------------------------------------------

    /**
     * @brief Set range offset correction in mm (–1024 to +1023).
     *
     * Compensates for a fixed distance error introduced by the optical stack
     * or a coverglass. Measure against a known-distance target and pass the
     * difference to this function.
     */
    bool setOffset(int16_t offset_mm);

    /**
     * @brief Get the current range offset in mm.
     * @param offset_mm  Filled with the current offset value.
     */
    bool getOffset(int16_t &offset_mm);

    /**
     * @brief Set cross-talk correction (0–128 kcps; 0 = no coverglass).
     *
     * Compensates for light reflected from a coverglass back into the sensor.
     */
    bool setXtalk(uint16_t xtalk_kcps);

    /**
     * @brief Get the current cross-talk value in kcps.
     * @param xtalk_kcps  Filled with the current cross-talk value.
     */
    bool getXtalk(uint16_t &xtalk_kcps);

    /**
     * @brief Recalibrate VHV when temperature has changed by more than 8 °C.
     *
     * The sensor must not be ranging when this is called.
     * @return true if the update completed successfully.
     */
    bool startTemperatureUpdate();

    // -----------------------------------------------------------------------
    // Detection thresholds
    // -----------------------------------------------------------------------

    /**
     * @brief Configure the distance-threshold interrupt.
     *
     * @param distance_low_mm   Lower threshold in mm.
     * @param distance_high_mm  Upper threshold in mm.
     * @param window            Trigger condition:
     *                            0 – below distance_low_mm
     *                            1 – above distance_high_mm
     *                            2 – outside [low, high]
     *                            3 – inside  [low, high]
     */
    bool setDetectionThresholds(uint16_t distance_low_mm,
                                uint16_t distance_high_mm,
                                uint8_t  window);

    /**
     * @brief Get the current detection threshold settings.
     */
    bool getDetectionThresholds(uint16_t &distance_low_mm,
                                uint16_t &distance_high_mm,
                                uint8_t  &window);

    // -----------------------------------------------------------------------
    // Signal / sigma thresholds
    // -----------------------------------------------------------------------

    /**
     * @brief Set minimum signal threshold (0–16384 kcps; default 1024).
     *
     * Measurements whose signal falls below this value report range_status 2.
     */
    bool setSignalThreshold(uint16_t signal_kcps);

    /** @brief Get the current minimum signal threshold in kcps. */
    bool getSignalThreshold(uint16_t &signal_kcps);

    /**
     * @brief Set sigma (std deviation) threshold in mm (0–16383; default 15).
     *
     * Measurements whose sigma exceeds this value report range_status 1.
     */
    bool setSigmaThreshold(uint16_t sigma_mm);

    /** @brief Get the current sigma threshold in mm. */
    bool getSigmaThreshold(uint16_t &sigma_mm);

    // -----------------------------------------------------------------------
    // Utility
    // -----------------------------------------------------------------------

    /**
     * @brief Read the sensor model ID.
     * @param id  Filled with the model ID (should be 0xEBAA).
     */
    bool getSensorId(uint16_t &id);

    /**
     * @brief Change the sensor's I2C address.
     * @param new_address  New 7-bit address. Update the Wire bus address to
     *                     match before calling any further methods.
     */
    bool setI2CAddress(uint8_t new_address);

private:
    TwoWire *_wire;
    uint8_t  _addr;

    // I2C register primitives
    bool     _wrByte (uint16_t reg, uint8_t  val);
    bool     _wrWord (uint16_t reg, uint16_t val);
    bool     _wrDWord(uint16_t reg, uint32_t val);
    bool     _rdByte (uint16_t reg, uint8_t  &val);
    bool     _rdWord (uint16_t reg, uint16_t &val);
    bool     _rdDWord(uint16_t reg, uint32_t &val);
};

#endif // VL53L4CD_H
