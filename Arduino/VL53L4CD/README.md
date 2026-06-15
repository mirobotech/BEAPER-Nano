# VL53L4CD Arduino Library

An Arduino C++ library for the **ST VL53L4CD** time-of-flight distance sensor, ported directly from ST's official C ULD (Ultra-Lite Driver) API v2.2.3.

---

## Features

- Simple one-call `getRange()` for beginner and robotics projects
- Non-blocking `dataReady()` / `getResult()` path for advanced use
- Full sensor API: timing budget, offset, cross-talk, sigma and signal thresholds, detection windows, temperature recalibration
- Meaningful error codes — not just `-1`
- Works with any Arduino-compatible board (Uno, Nano, Pico, ESP32, …)
- Depends only on the built-in `Wire` library

---

## Hardware

The VL53L4CD ToF sensor connects over **I2C** and measures distances from roughly **5 mm to 1200 mm** with up to ±6 mm of accuracy and at frequencies up to 100 Hz.

Full VL53L4CD details and resources are available from [https://www.st.com/en/imaging-and-photonics-solutions/vl53l4cd.html](https://www.st.com/en/imaging-and-photonics-solutions/vl53l4cd.html).

This library was created for the mirobo.tech QWIIC VL53L4CD ToF distance sensor module, but breakout boards from Adafruit, Pololu, SparkFun, and others should all be compatible.

The QWIIC VL53L4CD distance sensor module runs only from a **3.3V** supply and uses 3.3V logic — do not connect it directly to 5V microcontrollers without an appropriate level shifter.

---

## Installation

### Method 1 — Install from ZIP *(recommended)*

1. Download `VL53L4CD.zip`.
2. In the Arduino IDE open **Sketch → Include Library → Add .ZIP Library…**
3. Select `VL53L4CD.zip` and click **Open**.
4. The library is now installed. Add it to a sketch with **Sketch → Include Library → VL53L4CD**, or type the include manually.

### Method 2 — Manual installation

1. Copy the `VL53L4CD` folder (containing `VL53L4CD.h`, `VL53L4CD.cpp`, and `library.properties`) into your Arduino libraries folder:

   | Platform | Path |
   |----------|------|
   | Windows  | `Documents\Arduino\libraries\` |
   | macOS    | `~/Documents/Arduino/libraries/` |
   | Linux    | `~/Arduino/libraries/` |

2. Restart the Arduino IDE.
3. Add `#include <VL53L4CD.h>` to the top of your sketch.

---

## Wiring

| VL53L4CD pin | Arduino Uno / Nano | Raspberry Pi Pico |
|---|---|---|
| VIN / VCC | 3.3 V | 3.3 V |
| GND | GND | GND |
| SDA | A4 | GP4 (or your chosen SDA pin) |
| SCL | A5 | GP5 (or your chosen SCL pin) |

Call `Wire.begin()` in `setup()` before calling `tof.begin()`. On boards with multiple I2C buses you can pass a different `TwoWire` instance to the constructor (see API reference below).

---

## Examples

### Example 1 — Simple blocking ranging

`getRange()` is the easiest way to use the sensor. It waits until a measurement is ready, reads it, clears the interrupt, and returns a single `int16_t` value. A non-negative value is the distance in millimetres; negative values are error codes.

```cpp
// VL53L4CD_simple.ino
// Reads distance once per measurement cycle using the blocking getRange()
// method. Suitable for beginner projects where other tasks do not need to
// run while waiting for the sensor.

#include <Wire.h>
#include <VL53L4CD.h>

VL53L4CD tof;

void setup() {
  Serial.begin(115200);
  Wire.begin();

  if (!tof.begin()) {
    Serial.println("VL53L4CD not found – check wiring and power!");
    while (1);   // halt
  }

  Serial.println("VL53L4CD ready.");
  tof.startRanging();
}

void loop() {
  int16_t dist = tof.getRange();   // blocks until a result is ready (~50 ms)

  if (dist >= 0) {
    Serial.print(dist);
    Serial.println(" mm");

  } else if (dist == VL53L4CD::ERR_NO_TARGET) {
    Serial.println("No target detected");

  } else if (dist == VL53L4CD::ERR_SIGMA_HIGH) {
    Serial.println("Noisy measurement – try a longer timing budget");

  } else if (dist == VL53L4CD::ERR_WRAP_AROUND) {
    Serial.println("Target may be beyond sensor range (~1300 mm)");

  } else {  // ERR_HARDWARE
    Serial.println("Sensor fault");
  }
}
```

---

### Example 2 — Non-blocking ranging with full result detail

`dataReady()` returns immediately so the rest of `loop()` keeps running between measurements. `getResult()` fills a `VL53L4CD_Result_t` struct with distance, signal, noise, and SPAD data.

```cpp
// VL53L4CD_nonblocking.ino
// Polls dataReady() without blocking so that other code (motor control,
// button reading, display updates, etc.) continues to run between sensor
// measurements.

#include <Wire.h>
#include <VL53L4CD.h>

VL53L4CD tof;
VL53L4CD_Result_t result;

void setup() {
  Serial.begin(115200);
  Wire.begin();

  if (!tof.begin()) {
    Serial.println("VL53L4CD not found – check wiring and power!");
    while (1);
  }

  Serial.println("VL53L4CD ready.");
  tof.startRanging();
}

void loop() {
  // --- Sensor: check for a new reading without blocking ---
  if (tof.dataReady()) {
    tof.getResult(result);
    tof.clearInterrupt();   // must be called after every getResult()

    if (result.range_status == 0) {
      // Valid measurement
      Serial.print("Distance: ");
      Serial.print(result.distance_mm);
      Serial.print(" mm  |  sigma: ");
      Serial.print(result.sigma_mm);
      Serial.print(" mm  |  signal: ");
      Serial.print(result.signal_rate_kcps);
      Serial.println(" kcps");

    } else {
      Serial.print("Range status: ");
      Serial.println(result.range_status);
    }
  }

  // --- Other tasks run here every loop iteration ---
  // e.g. read buttons, update motors, refresh a display, blink an LED…
}
```

---

### Example 3 — Autonomous (low-power) mode

Setting an inter-measurement period longer than the timing budget tells the sensor to sleep between measurements. This reduces average current draw and is useful in battery-powered designs.

```cpp
// VL53L4CD_autonomous.ino
// Configures the sensor for autonomous low-power mode with a 200 ms period
// between measurements and a 50 ms timing budget (VCSEL on-time).

#include <Wire.h>
#include <VL53L4CD.h>

VL53L4CD tof;

void setup() {
  Serial.begin(115200);
  Wire.begin();

  if (!tof.begin()) {
    Serial.println("VL53L4CD not found – check wiring and power!");
    while (1);
  }

  // 50 ms timing budget, one measurement every 200 ms
  tof.setRangeTiming(50, 200);

  Serial.println("VL53L4CD ready – autonomous mode, 200 ms period.");
  tof.startRanging();
}

void loop() {
  if (tof.dataReady()) {
    int16_t dist = tof.getRange();
    if (dist >= 0) {
      Serial.print(dist);
      Serial.println(" mm");
    }
  }

  // loop() returns quickly; other work can happen here between measurements
}
```

---

### Example 4 — Proximity alert using detection thresholds

The sensor can be configured to flag measurements only when a target enters or leaves a distance window, useful for simple presence detection.

```cpp
// VL53L4CD_proximity.ino
// Triggers an alert whenever a target is closer than 300 mm.
// range_status 0 inside getResult() confirms it is a valid detection.

#include <Wire.h>
#include <VL53L4CD.h>

VL53L4CD tof;
VL53L4CD_Result_t result;

void setup() {
  Serial.begin(115200);
  Wire.begin();

  if (!tof.begin()) {
    Serial.println("VL53L4CD not found – check wiring and power!");
    while (1);
  }

  // Alert when distance < 300 mm (window mode 0 = below low threshold)
  tof.setDetectionThresholds(0, 300, 0);

  tof.startRanging();
  Serial.println("Watching for targets closer than 300 mm...");
}

void loop() {
  if (tof.dataReady()) {
    tof.getResult(result);
    tof.clearInterrupt();

    if (result.range_status == 0) {
      Serial.print("ALERT – target at ");
      Serial.print(result.distance_mm);
      Serial.println(" mm");
    }
  }
}
```

---

## API Reference

### Constructor

```cpp
VL53L4CD tof;                        // use Wire, address 0x29
VL53L4CD tof(Wire1);                 // use a different I2C bus
VL53L4CD tof(Wire, 0x29);            // explicit bus and address
```

---

### Initialisation

```cpp
bool begin()
```

Call once in `setup()`, after `Wire.begin()`. Waits for the sensor firmware to boot, writes the default hardware configuration, runs VHV calibration, and sets a 50 ms timing budget in continuous mode. Returns `false` if the sensor does not respond or calibration times out (check wiring).

---

### Ranging control

| Method | Description |
|--------|-------------|
| `startRanging()` | Start measurements. Continuous mode when `inter_measurement_ms` is 0 (the default); autonomous otherwise |
| `stopRanging()` | Stop measurements |
| `dataReady()` | Returns `true` when a new result is waiting. Non-blocking |
| `clearInterrupt()` | Re-arms the sensor for the next measurement. Must be called after every `getResult()` call (called automatically by `getRange()`) |

---

### Reading results

#### `getRange()` — simple and blocking

```cpp
int16_t dist = tof.getRange();
```

Waits for a result, reads it, clears the interrupt, and returns:

| Return value | Constant | Meaning |
|---|---|---|
| ≥ 0 | — | Valid distance in mm |
| −1 | `VL53L4CD::ERR_NO_TARGET` | Signal too low — nothing detected, or target absorbs too much light |
| −2 | `VL53L4CD::ERR_SIGMA_HIGH` | Measurement too noisy — try a longer timing budget or clean the lens |
| −3 | `VL53L4CD::ERR_WRAP_AROUND` | Target may be beyond the ~1300 mm unambiguous range |
| −4 | `VL53L4CD::ERR_HARDWARE` | Sensor hardware or algorithm fault |

#### `getResult()` — full detail, non-blocking

```cpp
VL53L4CD_Result_t result;

if (tof.dataReady()) {
    tof.getResult(result);
    tof.clearInterrupt();
}
```

Fills a `VL53L4CD_Result_t` struct:

| Field | Type | Description |
|-------|------|-------------|
| `range_status` | `uint8_t` | `0` = valid; see status table below |
| `distance_mm` | `uint16_t` | Distance in mm |
| `sigma_mm` | `uint16_t` | Std deviation of the measurement (mm) |
| `signal_rate_kcps` | `uint32_t` | Returned signal rate (kcps) |
| `ambient_rate_kcps` | `uint32_t` | Ambient light noise rate (kcps) |
| `signal_per_spad_kcps` | `uint32_t` | Signal rate per SPAD (kcps) |
| `ambient_per_spad_kcps` | `uint32_t` | Ambient rate per SPAD (kcps) |
| `number_of_spad` | `uint16_t` | Number of enabled SPADs |

**`range_status` values:**

| Status | Meaning |
|--------|---------|
| 0 | Valid measurement |
| 1 | Sigma above threshold (noisy) |
| 2 | Signal below threshold (no target or too dark) |
| 4 | Possible wrap-around |
| 7 | Wrap-around confirmed |
| 9 | Hard reset required |
| 10 | Phase outside valid limits |
| 11 | Range error |
| 12 | Target below minimum detection threshold |
| 13 | Undefined raw status |

---

### Timing

```cpp
bool setRangeTiming(uint32_t timing_budget_ms, uint32_t inter_measurement_ms = 0)
bool getRangeTiming(uint32_t &timing_budget_ms, uint32_t &inter_measurement_ms)
```

| Parameter | Range | Default | Description |
|-----------|-------|---------|-------------|
| `timing_budget_ms` | 10–200 | 50 | VCSEL on-time per measurement. Longer values improve accuracy and maximum range but reduce update rate |
| `inter_measurement_ms` | 0 or > budget | 0 | `0` = continuous mode. Any value greater than `timing_budget_ms` = autonomous (low-power) mode with that period between measurements |

Call `setRangeTiming()` before `startRanging()`, or after `stopRanging()`. Both methods return `false` if arguments are out of range.

---

### Calibration

#### Offset

Corrects a fixed distance error caused by the optical stack or a coverglass.

```cpp
bool setOffset(int16_t offset_mm)   // –1024 to +1023 mm
bool getOffset(int16_t &offset_mm)
```

Measure readings against a target at a known distance and pass the difference (true − measured) to `setOffset()`.

#### Cross-talk

Corrects for light reflected from a coverglass back into the sensor.

```cpp
bool setXtalk(uint16_t xtalk_kcps)  // 0–128 kcps; 0 = no coverglass
bool getXtalk(uint16_t &xtalk_kcps)
```

#### Temperature

Recalibrates the VHV circuit if ambient temperature has changed by more than 8 °C. The sensor must be stopped first.

```cpp
tof.stopRanging();
tof.startTemperatureUpdate();   // blocks ~50 ms
tof.startRanging();
```

---

### Detection thresholds

```cpp
bool setDetectionThresholds(uint16_t distance_low_mm,
                             uint16_t distance_high_mm,
                             uint8_t  window)
bool getDetectionThresholds(uint16_t &distance_low_mm,
                             uint16_t &distance_high_mm,
                             uint8_t  &window)
```

| `window` | Interrupt fires when… |
|----------|----------------------|
| 0 | distance < `distance_low_mm` |
| 1 | distance > `distance_high_mm` |
| 2 | distance outside [`low`, `high`] |
| 3 | distance inside [`low`, `high`] |

---

### Signal and sigma thresholds

```cpp
bool setSignalThreshold(uint16_t signal_kcps)   // 0–16384; default 1024
bool getSignalThreshold(uint16_t &signal_kcps)

bool setSigmaThreshold(uint16_t sigma_mm)        // 0–16383; default 15
bool getSigmaThreshold(uint16_t &sigma_mm)
```

Measurements below the signal threshold report `range_status` 2. Measurements above the sigma threshold report `range_status` 1.

---

### Utility

```cpp
bool getSensorId(uint16_t &id)         // expected value: 0xEBAA
bool setI2CAddress(uint8_t new_address)
```

---

## Blocking vs Non-Blocking

| | `getRange()` | `dataReady()` + `getResult()` |
|---|---|---|
| **Complexity** | One function call | Three calls per reading |
| **Blocks `loop()`?** | Yes, ~50 ms per reading | No |
| **Data returned** | Distance in mm (or error code) | Full result struct |
| **Best for** | Simple projects, learning | Robots, multi-task sketches |

In a robot sketch that also drives motors, reads buttons, or updates a display, the non-blocking approach is strongly preferred — a 50 ms block every reading is enough to make motor control noticeably jerky.

---

## Licence

Ported from ST's VL53L4CD ULD C API. The Arduino library is provided under the same **ST BSD Clear licence (SLA0103)** as the original C source. See the licence header in `VL53L4CD.h`.
