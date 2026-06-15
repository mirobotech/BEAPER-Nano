/**
 * VL53L4CD.cpp  –  Arduino library for the ST VL53L4CD time-of-flight sensor
 * Updated: June 15, 2026
 *
 * Ported from ST's VL53L4CD_ULD_DRIVER v2.2.3 (VL53L4CD_api.c)
 * Copyright (c) 2023 STMicroelectronics. All rights reserved.
 * See licence header in VL53L4CD.h.
 */

#include "VL53L4CD.h"

// ---------------------------------------------------------------------------
// Default configuration blob (registers 0x2D – 0x87)
// Copied verbatim from ST's VL53L4CD_api.c, VL53L4CD_DEFAULT_CONFIGURATION[].
// Byte at index N is written to register (0x2D + N).
// ---------------------------------------------------------------------------
static const uint8_t VL53L4CD_DEFAULT_CONFIGURATION[] = {
    0x00, /* 0x2D : set bit 2 and 5 to 1 for fast plus mode (1MHz I2C),
              else don't touch */
    0x00, /* 0x2E : bit 0 if I2C pulled up at 1.8V, else set bit 0 to 1
              (pull up at AVDD) */
    0x00, /* 0x2F : bit 0 if GPIO pulled up at 1.8V, else set bit 0 to 1
              (pull up at AVDD) */
    0x11, /* 0x30 : set bit 4 to 0 for active high interrupt and 1 for
              active low (bits 3:0 must be 0x1), use setInterruptPolarity() */
    0x02, /* 0x31 : bit 1 = interrupt depending on the polarity,
              use dataReady() */
    0x00, /* 0x32 : not user-modifiable */
    0x02, /* 0x33 : not user-modifiable */
    0x08, /* 0x34 : not user-modifiable */
    0x00, /* 0x35 : not user-modifiable */
    0x08, /* 0x36 : not user-modifiable */
    0x10, /* 0x37 : not user-modifiable */
    0x01, /* 0x38 : not user-modifiable */
    0x01, /* 0x39 : not user-modifiable */
    0x00, /* 0x3A : not user-modifiable */
    0x00, /* 0x3B : not user-modifiable */
    0x00, /* 0x3C : not user-modifiable */
    0x00, /* 0x3D : not user-modifiable */
    0xFF, /* 0x3E : not user-modifiable */
    0x00, /* 0x3F : not user-modifiable */
    0x0F, /* 0x40 : not user-modifiable */
    0x00, /* 0x41 : not user-modifiable */
    0x00, /* 0x42 : not user-modifiable */
    0x00, /* 0x43 : not user-modifiable */
    0x00, /* 0x44 : not user-modifiable */
    0x00, /* 0x45 : not user-modifiable */
    0x20, /* 0x46 : interrupt configuration 0->level low detection,
              1->level high, 2->out of window, 3->in window,
              0x20->new sample ready */
    0x0B, /* 0x47 : not user-modifiable */
    0x00, /* 0x48 : not user-modifiable */
    0x00, /* 0x49 : not user-modifiable */
    0x02, /* 0x4A : not user-modifiable */
    0x14, /* 0x4B : not user-modifiable */
    0x21, /* 0x4C : not user-modifiable */
    0x00, /* 0x4D : not user-modifiable */
    0x00, /* 0x4E : not user-modifiable */
    0x05, /* 0x4F : not user-modifiable */
    0x00, /* 0x50 : not user-modifiable */
    0x00, /* 0x51 : not user-modifiable */
    0x00, /* 0x52 : not user-modifiable */
    0x00, /* 0x53 : not user-modifiable */
    0xC8, /* 0x54 : not user-modifiable */
    0x00, /* 0x55 : not user-modifiable */
    0x00, /* 0x56 : not user-modifiable */
    0x38, /* 0x57 : not user-modifiable */
    0xFF, /* 0x58 : not user-modifiable */
    0x01, /* 0x59 : not user-modifiable */
    0x00, /* 0x5A : not user-modifiable */
    0x08, /* 0x5B : not user-modifiable */
    0x00, /* 0x5C : not user-modifiable */
    0x00, /* 0x5D : not user-modifiable */
    0x01, /* 0x5E : not user-modifiable */
    0xCC, /* 0x5F : not user-modifiable */
    0x07, /* 0x60 : not user-modifiable */
    0x01, /* 0x61 : not user-modifiable */
    0xF1, /* 0x62 : not user-modifiable */
    0x05, /* 0x63 : not user-modifiable */
    0x00, /* 0x64 : Sigma threshold MSB (mm in 14.2 format for MSB+LSB),
              use setSigmaThreshold(), default value 90 mm */
    0xA0, /* 0x65 : Sigma threshold LSB */
    0x00, /* 0x66 : Min count Rate MSB (MCPS in 9.7 format for MSB+LSB),
              use setSignalThreshold() */
    0x80, /* 0x67 : Min count Rate LSB */
    0x08, /* 0x68 : not user-modifiable */
    0x38, /* 0x69 : not user-modifiable */
    0x00, /* 0x6A : not user-modifiable */
    0x00, /* 0x6B : not user-modifiable */
    0x00, /* 0x6C : Intermeasurement period MSB, 32-bit register,
              use setRangeTiming() */
    0x00, /* 0x6D : Intermeasurement period */
    0x0F, /* 0x6E : Intermeasurement period */
    0x89, /* 0x6F : Intermeasurement period LSB */
    0x00, /* 0x70 : not user-modifiable */
    0x00, /* 0x71 : not user-modifiable */
    0x00, /* 0x72 : distance threshold high MSB (in mm, MSB+LSB),
              use setDetectionThresholds() */
    0x00, /* 0x73 : distance threshold high LSB */
    0x00, /* 0x74 : distance threshold low MSB (in mm, MSB+LSB),
              use setDetectionThresholds() */
    0x00, /* 0x75 : distance threshold low LSB */
    0x00, /* 0x76 : not user-modifiable */
    0x01, /* 0x77 : not user-modifiable */
    0x07, /* 0x78 : not user-modifiable */
    0x05, /* 0x79 : not user-modifiable */
    0x06, /* 0x7A : not user-modifiable */
    0x06, /* 0x7B : not user-modifiable */
    0x00, /* 0x7C : not user-modifiable */
    0x00, /* 0x7D : not user-modifiable */
    0x02, /* 0x7E : not user-modifiable */
    0xC7, /* 0x7F : not user-modifiable */
    0xFF, /* 0x80 : not user-modifiable */
    0x9B, /* 0x81 : not user-modifiable */
    0x00, /* 0x82 : not user-modifiable */
    0x00, /* 0x83 : not user-modifiable */
    0x00, /* 0x84 : not user-modifiable */
    0x01, /* 0x85 : not user-modifiable */
    0x00, /* 0x86 : clear interrupt, use clearInterrupt() */
    0x00, /* 0x87 : start ranging, use startRanging() / stopRanging() */
};

// ---------------------------------------------------------------------------
// Range-status translation table (mirrors status_rtn[] in VL53L4CD_api.c)
// Index = raw hardware status byte; value = reported status code.
// ---------------------------------------------------------------------------
static const uint8_t STATUS_RTN[24] = {
    255, 255, 255, 5, 2, 4, 1, 7, 3,
    0, 255, 255, 9, 13, 255, 255, 255, 255, 10, 6,
    255, 255, 11, 12
};

// ===========================================================================
// Constructor
// ===========================================================================

VL53L4CD::VL53L4CD(TwoWire &wire, uint8_t address)
    : _wire(&wire), _addr(address) {}

// ===========================================================================
// Initialisation  (mirrors VL53L4CD_SensorInit)
// ===========================================================================

bool VL53L4CD::begin()
{
    uint8_t tmp = 0;
    uint16_t i  = 0;

    // Wait for firmware boot (register 0xE5 == 0x03), up to 1000 ms
    do {
        if (!_rdByte(VL53L4CD_FIRMWARE__SYSTEM_STATUS, tmp)) return false;
        if (tmp == 0x03) break;
        if (i >= 1000)   return false;  // timeout
        i++;
        delay(1);
    } while (true);

    // Load default configuration blob (registers 0x2D–0x87)
    for (uint8_t addr = 0x2D; addr <= 0x87; addr++) {
        if (!_wrByte(addr, VL53L4CD_DEFAULT_CONFIGURATION[addr - 0x2D]))
            return false;
    }

    // Start VHV calibration
    if (!_wrByte(VL53L4CD_SYSTEM_START, 0x40)) return false;

    i = 0;
    do {
        if (!dataReady()) {
            if (i >= 1000) return false;  // timeout
            i++;
            delay(1);
        } else {
            break;
        }
    } while (true);

    clearInterrupt();
    stopRanging();

    _wrByte(VL53L4CD_VHV_CONFIG__TIMEOUT_MACROP_LOOP_BOUND, 0x09);
    _wrByte(0x0B, 0x00);
    _wrWord(0x0024, 0x0500);

    return setRangeTiming(50, 0);
}

// ===========================================================================
// Ranging control
// ===========================================================================

void VL53L4CD::startRanging()
{
    uint32_t tmp = 0;
    _rdDWord(VL53L4CD_INTERMEASUREMENT_MS, tmp);
    // Continuous mode when inter-measurement register is 0,
    // autonomous mode otherwise  (mirrors VL53L4CD_StartRanging)
    if (tmp == 0) {
        _wrByte(VL53L4CD_SYSTEM_START, 0x21);
    } else {
        _wrByte(VL53L4CD_SYSTEM_START, 0x40);
    }
}

void VL53L4CD::stopRanging()
{
    _wrByte(VL53L4CD_SYSTEM_START, 0x80);
}

bool VL53L4CD::dataReady()
{
    // Mirrors VL53L4CD_CheckForDataReady:
    // Read interrupt polarity from GPIO_HV_MUX__CTRL bit 4, then compare
    // against the current GPIO status bit 0.
    uint8_t temp = 0;
    _rdByte(VL53L4CD_GPIO_HV_MUX__CTRL, temp);
    uint8_t int_pol = ((temp & 0x10) >> 4) == 1 ? 0 : 1;
    _rdByte(VL53L4CD_GPIO__TIO_HV_STATUS, temp);
    return (temp & 0x01) == int_pol;
}

void VL53L4CD::clearInterrupt()
{
    _wrByte(VL53L4CD_SYSTEM__INTERRUPT_CLEAR, 0x01);
}

// ===========================================================================
// Reading results
// ===========================================================================

bool VL53L4CD::getResult(VL53L4CD_Result_t &result)
{
    // Mirrors VL53L4CD_GetResult
    uint8_t  temp_8  = 0;
    uint16_t temp_16 = 0;
    uint16_t raw_spads = 0;

    if (!_rdByte(VL53L4CD_RESULT__RANGE_STATUS, temp_8)) return false;
    temp_8 &= 0x1F;
    if (temp_8 < 24) temp_8 = STATUS_RTN[temp_8];
    result.range_status = temp_8;

    _rdWord(VL53L4CD_RESULT__SPAD_NB, temp_16);
    raw_spads = temp_16;
    result.number_of_spad = temp_16 / 256;

    _rdWord(VL53L4CD_RESULT__SIGNAL_RATE, temp_16);
    result.signal_rate_kcps = (uint32_t)temp_16 * 8;

    _rdWord(VL53L4CD_RESULT__AMBIENT_RATE, temp_16);
    result.ambient_rate_kcps = (uint32_t)temp_16 * 8;

    _rdWord(VL53L4CD_RESULT__SIGMA, temp_16);
    result.sigma_mm = temp_16 / 4;

    _rdWord(VL53L4CD_RESULT__DISTANCE, temp_16);
    result.distance_mm = temp_16;

    if (raw_spads > 0) {
        result.signal_per_spad_kcps  = result.signal_rate_kcps  * 256
                                       / (uint32_t)raw_spads;
        result.ambient_per_spad_kcps = result.ambient_rate_kcps * 256
                                       / (uint32_t)raw_spads;
    } else {
        result.signal_per_spad_kcps  = 0;
        result.ambient_per_spad_kcps = 0;
    }

    return true;
}

int16_t VL53L4CD::getRange()
{
    // Block until data is ready
    while (!dataReady()) {
        delay(1);
    }

    VL53L4CD_Result_t result;
    if (!getResult(result)) {
        clearInterrupt();
        return ERR_HARDWARE;
    }
    clearInterrupt();

    switch (result.range_status) {
        case 0:  return (int16_t)result.distance_mm;
        case 2:  return ERR_NO_TARGET;
        case 1:  return ERR_SIGMA_HIGH;
        case 4:
        case 7:  return ERR_WRAP_AROUND;
        default: return ERR_HARDWARE;
    }
}

// ===========================================================================
// Timing  (mirrors VL53L4CD_SetRangeTiming / VL53L4CD_GetRangeTiming)
// ===========================================================================

bool VL53L4CD::setRangeTiming(uint32_t timing_budget_ms,
                               uint32_t inter_measurement_ms)
{
    uint16_t osc_frequency = 0;
    uint16_t clock_pll     = 0;
    uint16_t ms_byte       = 0;
    uint32_t macro_period_us   = 0;
    uint32_t timing_budget_us  = 0;
    uint32_t ls_byte = 0;
    uint32_t tmp     = 0;

    if (!_rdWord(0x0006, osc_frequency)) return false;
    if (osc_frequency == 0)              return false;

    if (timing_budget_ms < 10 || timing_budget_ms > 200) return false;

    timing_budget_us = timing_budget_ms * 1000UL;
    macro_period_us  = ((uint32_t)2304 *
                        ((uint32_t)0x40000000 / (uint32_t)osc_frequency)) >> 6;

    if (inter_measurement_ms == 0) {
        // Continuous mode
        _wrDWord(VL53L4CD_INTERMEASUREMENT_MS, 0);
        timing_budget_us -= 2500UL;

    } else if (inter_measurement_ms > timing_budget_ms) {
        // Autonomous mode
        _rdWord(VL53L4CD_RESULT__OSC_CALIBRATE_VAL, clock_pll);
        clock_pll &= 0x3FF;
        float inter_meas_factor = 1.055f * (float)inter_measurement_ms
                                         * (float)clock_pll;
        _wrDWord(VL53L4CD_INTERMEASUREMENT_MS, (uint32_t)inter_meas_factor);
        timing_budget_us -= 4300UL;
        timing_budget_us /= 2;

    } else {
        return false;  // inter_measurement_ms must be 0 or > timing_budget_ms
    }

    // Encode timing budget into RANGE_CONFIG_A (macro_period * 16)
    ms_byte = 0;
    timing_budget_us <<= 12;
    tmp     = macro_period_us * 16UL;
    ls_byte = ((timing_budget_us + ((tmp >> 6) >> 1)) / (tmp >> 6)) - 1;
    while ((ls_byte & 0xFFFFFF00UL) > 0) { ls_byte >>= 1; ms_byte++; }
    _wrWord(VL53L4CD_RANGE_CONFIG_A,
            (uint16_t)(ms_byte << 8) | (uint16_t)(ls_byte & 0xFF));

    // Encode timing budget into RANGE_CONFIG_B (macro_period * 12)
    ms_byte = 0;
    tmp     = macro_period_us * 12UL;
    ls_byte = ((timing_budget_us + ((tmp >> 6) >> 1)) / (tmp >> 6)) - 1;
    while ((ls_byte & 0xFFFFFF00UL) > 0) { ls_byte >>= 1; ms_byte++; }
    _wrWord(VL53L4CD_RANGE_CONFIG_B,
            (uint16_t)(ms_byte << 8) | (uint16_t)(ls_byte & 0xFF));

    return true;
}

bool VL53L4CD::getRangeTiming(uint32_t &timing_budget_ms,
                               uint32_t &inter_measurement_ms)
{
    uint16_t osc_frequency          = 1;
    uint16_t range_config_macrop_h  = 0;
    uint16_t clock_pll              = 1;
    uint32_t tmp          = 0;
    uint32_t ls_byte      = 0;
    uint32_t ms_byte      = 0;
    uint32_t macro_period = 0;

    // Inter-measurement period
    _rdDWord(VL53L4CD_INTERMEASUREMENT_MS, tmp);
    _rdWord(VL53L4CD_RESULT__OSC_CALIBRATE_VAL, clock_pll);
    clock_pll &= 0x3FF;
    uint16_t clock_pll_scaled = (uint16_t)(1.065f * (float)clock_pll);
    inter_measurement_ms = (clock_pll_scaled > 0)
                           ? (tmp / (uint32_t)clock_pll_scaled) : 0;

    // Timing budget
    _rdWord(0x0006, osc_frequency);
    _rdWord(VL53L4CD_RANGE_CONFIG_A, range_config_macrop_h);

    macro_period = ((uint32_t)2304 *
                    ((uint32_t)0x40000000 / (uint32_t)osc_frequency)) >> 6;
    ls_byte = ((uint32_t)(range_config_macrop_h & 0x00FF)) << 4;
    ms_byte = ((uint32_t)(range_config_macrop_h & 0xFF00)) >> 8;
    ms_byte = 0x04UL - (ms_byte - 1UL) - 1UL;

    macro_period       *= 16UL;
    timing_budget_ms    = (((ls_byte + 1UL) * (macro_period >> 6))
                          - ((macro_period >> 6) >> 1)) >> 12;

    if (ms_byte < 12) timing_budget_ms >>= ms_byte;

    if (tmp == 0) {
        timing_budget_ms += 2500UL;       // continuous
    } else {
        timing_budget_ms  = timing_budget_ms * 2UL + 4300UL;  // autonomous
    }
    timing_budget_ms /= 1000UL;

    return true;
}

// ===========================================================================
// Calibration
// ===========================================================================

bool VL53L4CD::setOffset(int16_t offset_mm)
{
    uint16_t temp = (uint16_t)((uint16_t)offset_mm * 4);
    _wrWord(VL53L4CD_RANGE_OFFSET_MM, temp);
    _wrWord(VL53L4CD_INNER_OFFSET_MM, 0);
    _wrWord(VL53L4CD_OUTER_OFFSET_MM, 0);
    return true;
}

bool VL53L4CD::getOffset(int16_t &offset_mm)
{
    uint16_t temp = 0;
    if (!_rdWord(VL53L4CD_RANGE_OFFSET_MM, temp)) return false;
    temp     = temp << 3;
    temp     = temp >> 5;
    offset_mm = (int16_t)temp;
    if (offset_mm > 1024) offset_mm -= 2048;
    return true;
}

bool VL53L4CD::setXtalk(uint16_t xtalk_kcps)
{
    _wrWord(VL53L4CD_XTALK_X_PLANE_GRADIENT_KCPS, 0x0000);
    _wrWord(VL53L4CD_XTALK_Y_PLANE_GRADIENT_KCPS, 0x0000);
    _wrWord(VL53L4CD_XTALK_PLANE_OFFSET_KCPS, (uint16_t)(xtalk_kcps << 9));
    return true;
}

bool VL53L4CD::getXtalk(uint16_t &xtalk_kcps)
{
    if (!_rdWord(VL53L4CD_XTALK_PLANE_OFFSET_KCPS, xtalk_kcps)) return false;
    xtalk_kcps = (uint16_t)roundf((float)xtalk_kcps / 512.0f);
    return true;
}

bool VL53L4CD::startTemperatureUpdate()
{
    // Mirrors VL53L4CD_StartTemperatureUpdate
    _wrByte(VL53L4CD_VHV_CONFIG__TIMEOUT_MACROP_LOOP_BOUND, 0x81);
    _wrByte(0x0B, 0x92);
    startRanging();

    uint16_t i = 0;
    while (!dataReady()) {
        if (i >= 1000) return false;
        i++;
        delay(1);
    }

    clearInterrupt();
    stopRanging();
    _wrByte(VL53L4CD_VHV_CONFIG__TIMEOUT_MACROP_LOOP_BOUND, 0x09);
    _wrByte(0x0B, 0x00);
    return true;
}

// ===========================================================================
// Detection thresholds
// ===========================================================================

bool VL53L4CD::setDetectionThresholds(uint16_t distance_low_mm,
                                       uint16_t distance_high_mm,
                                       uint8_t  window)
{
    _wrByte(VL53L4CD_SYSTEM__INTERRUPT, window);
    _wrWord(VL53L4CD_THRESH_HIGH, distance_high_mm);
    _wrWord(VL53L4CD_THRESH_LOW,  distance_low_mm);
    return true;
}

bool VL53L4CD::getDetectionThresholds(uint16_t &distance_low_mm,
                                       uint16_t &distance_high_mm,
                                       uint8_t  &window)
{
    uint8_t w = 0;
    _rdWord(VL53L4CD_THRESH_HIGH, distance_high_mm);
    _rdWord(VL53L4CD_THRESH_LOW,  distance_low_mm);
    _rdByte(VL53L4CD_SYSTEM__INTERRUPT, w);
    window = w & 0x07;
    return true;
}

// ===========================================================================
// Signal / sigma thresholds
// ===========================================================================

bool VL53L4CD::setSignalThreshold(uint16_t signal_kcps)
{
    return _wrWord(VL53L4CD_MIN_COUNT_RATE_RTN_LIMIT_MCPS, signal_kcps >> 3);
}

bool VL53L4CD::getSignalThreshold(uint16_t &signal_kcps)
{
    if (!_rdWord(VL53L4CD_MIN_COUNT_RATE_RTN_LIMIT_MCPS, signal_kcps))
        return false;
    signal_kcps <<= 3;
    return true;
}

bool VL53L4CD::setSigmaThreshold(uint16_t sigma_mm)
{
    if (sigma_mm > (0xFFFF >> 2)) return false;
    return _wrWord(VL53L4CD_RANGE_CONFIG__SIGMA_THRESH,
                   (uint16_t)(sigma_mm << 2));
}

bool VL53L4CD::getSigmaThreshold(uint16_t &sigma_mm)
{
    if (!_rdWord(VL53L4CD_RANGE_CONFIG__SIGMA_THRESH, sigma_mm)) return false;
    sigma_mm >>= 2;
    return true;
}

// ===========================================================================
// Utility
// ===========================================================================

bool VL53L4CD::getSensorId(uint16_t &id)
{
    return _rdWord(VL53L4CD_IDENTIFICATION__MODEL_ID, id);
}

bool VL53L4CD::setI2CAddress(uint8_t new_address)
{
    if (!_wrByte(VL53L4CD_I2C_SLAVE__DEVICE_ADDRESS,
                 (uint8_t)(new_address >> 1)))
        return false;
    _addr = new_address;
    return true;
}

// ===========================================================================
// Private: I2C register primitives
//
// The VL53L4CD uses 16-bit big-endian register addresses.
// All write transactions: START | addr | reg_hi | reg_lo | data... | STOP
// All read transactions:  START | addr | reg_hi | reg_lo | STOP
//                         START | addr+R | data... | STOP
// ===========================================================================

bool VL53L4CD::_wrByte(uint16_t reg, uint8_t val)
{
    _wire->beginTransmission(_addr);
    _wire->write((uint8_t)(reg >> 8));
    _wire->write((uint8_t)(reg & 0xFF));
    _wire->write(val);
    return _wire->endTransmission() == 0;
}

bool VL53L4CD::_wrWord(uint16_t reg, uint16_t val)
{
    _wire->beginTransmission(_addr);
    _wire->write((uint8_t)(reg >> 8));
    _wire->write((uint8_t)(reg & 0xFF));
    _wire->write((uint8_t)(val >> 8));
    _wire->write((uint8_t)(val & 0xFF));
    return _wire->endTransmission() == 0;
}

bool VL53L4CD::_wrDWord(uint16_t reg, uint32_t val)
{
    _wire->beginTransmission(_addr);
    _wire->write((uint8_t)(reg >> 8));
    _wire->write((uint8_t)(reg & 0xFF));
    _wire->write((uint8_t)(val >> 24));
    _wire->write((uint8_t)(val >> 16));
    _wire->write((uint8_t)(val >>  8));
    _wire->write((uint8_t)(val & 0xFF));
    return _wire->endTransmission() == 0;
}

bool VL53L4CD::_rdByte(uint16_t reg, uint8_t &val)
{
    _wire->beginTransmission(_addr);
    _wire->write((uint8_t)(reg >> 8));
    _wire->write((uint8_t)(reg & 0xFF));
    if (_wire->endTransmission(false) != 0) return false;
    if (_wire->requestFrom(_addr, (uint8_t)1) != 1) return false;
    val = _wire->read();
    return true;
}

bool VL53L4CD::_rdWord(uint16_t reg, uint16_t &val)
{
    _wire->beginTransmission(_addr);
    _wire->write((uint8_t)(reg >> 8));
    _wire->write((uint8_t)(reg & 0xFF));
    if (_wire->endTransmission(false) != 0) return false;
    if (_wire->requestFrom(_addr, (uint8_t)2) != 2) return false;
    val  = (uint16_t)_wire->read() << 8;
    val |= (uint16_t)_wire->read();
    return true;
}

bool VL53L4CD::_rdDWord(uint16_t reg, uint32_t &val)
{
    _wire->beginTransmission(_addr);
    _wire->write((uint8_t)(reg >> 8));
    _wire->write((uint8_t)(reg & 0xFF));
    if (_wire->endTransmission(false) != 0) return false;
    if (_wire->requestFrom(_addr, (uint8_t)4) != 4) return false;
    val  = (uint32_t)_wire->read() << 24;
    val |= (uint32_t)_wire->read() << 16;
    val |= (uint32_t)_wire->read() <<  8;
    val |= (uint32_t)_wire->read();
    return true;
}
