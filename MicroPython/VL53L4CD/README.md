# VL53L4CD MicroPython Driver

A pure-MicroPython driver for the **ST VL53L4CD** time-of-flight distance sensor. This driver is ported from ST's official C ULD (Ultra-Lite Driver) API v2.2.3.

---

## Hardware

The VL53L4CD ToF sensor connects over **I2C** and measures distances from roughly **1 mm to 1200 mm** with up to ±6 mm of accuracy and at frequencies up to 100 Hz.

Full VL53L4CD details and resources are available from [https://www.st.com/en/imaging-and-photonics-solutions/vl53l4cd.html](https://www.st.com/en/imaging-and-photonics-solutions/vl53l4cd.html).

---

## Driver Features

- Full sensor API: timing, offset, cross-talk, sigma and signal thresholds, detection windows, temperature recalibration
- Non-blocking `data_ready()` / `get_result()` methods
- Simple (blocking) one-call `get_range()` method for beginner projects 
- Meaningful error codes (rather than a bare `-1`)
- No dependencies beyond the MicroPython standard library (`machine`, `time`, `micropython`)

---

## Installation

Copy `VL53L4CD.py` to the root of your microcontroller's filesystem.

---

## Quick Start

```python
from machine import I2C, Pin
from VL53L4CD import VL53L4CD

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400_000)
tof = VL53L4CD(i2c)          # initialises and calibrates automatically
tof.start_ranging()

while True:
    dist = tof.get_range()
    if dist >= 0:
        print(dist, "mm")
    elif dist == VL53L4CD.ERR_NO_TARGET:
        print("Nothing detected")
    elif dist == VL53L4CD.ERR_SIGMA_HIGH:
        print("Noisy measurement – try a longer timing budget")
    elif dist == VL53L4CD.ERR_WRAP_AROUND:
        print("Target may be beyond sensor range")
    else:   # ERR_HARDWARE
        print("Sensor fault")
```

`get_range()` blocks (~50ms) until the sensor has a result ready, clears the interrupt automatically, and returns the distance in millimetres as a plain integer. Negative return values are error codes (see below).

---

## API Reference

### Constructor

```python
tof = VL53L4CD(i2c, address=0x29)
```

| Parameter | Description |
|-----------|-------------|
| `i2c` | An initialised `machine.I2C` instance |
| `address` | 7-bit I2C address (default `0x29`) |

The constructor initializes the sensor, writes the default configuration, runs VHV calibration, and sets a 50 ms timing budget in continuous mode. A `VL53L4CDError` is raised if the sensor does not respond within 1 second.

---

### Ranging control

| Method | Description |
|--------|-------------|
| `start_ranging()` | Begin measurements. Uses continuous mode if `inter_measurement_ms` is 0 (the default), autonomous mode otherwise |
| `stop_ranging()` | Stop measurements |
| `data_ready()` | Returns `True` when a new result is waiting to be read |
| `clear_interrupt()` | Clears the data-ready flag. Must be called after every `get_result()` call (gets called automatically by the simpler `get_range()` method) |

---

### Reading results

#### `get_range()` — simple, blocking range measurement

```python
dist = tof.get_range()
```

Waits for a result, reads it, clears the interrupt, and returns one of:

| Return value | Constant | Meaning |
|---|---|---|
| ≥ 0 | — | Valid distance in mm |
| −1 | `ERR_NO_TARGET` | Signal too low — nothing in range, or target absorbs too much light |
| −2 | `ERR_SIGMA_HIGH` | Measurement noise above threshold — result unreliable; try a longer timing budget or clean the lens |
| −3 | `ERR_WRAP_AROUND` | Target may be beyond ~1300mm unambiguous range |
| −4 | `ERR_HARDWARE` | Sensor hardware or algorithm fault |


#### `get_result()` — full detail, non-blocking

```python
if tof.data_ready():
    result = tof.get_result()
    tof.clear_interrupt()
```

Returns a `dict` with the following keys:

| Key | Description |
|-----|-------------|
| `range_status` | `0` = valid; see status table below |
| `distance_mm` | Distance in mm |
| `sigma_mm` | Standard deviation of the measurement (mm) |
| `signal_rate_kcps` | Returned signal rate (kcps) |
| `ambient_rate_kcps` | Ambient light rate (kcps) |
| `signal_per_spad_kcps` | Signal rate per SPAD (kcps) |
| `ambient_per_spad_kcps` | Ambient rate per SPAD (kcps) |
| `number_of_spad` | Number of enabled SPADs |

**`range_status` values:**

| Status | Meaning |
|--------|---------|
| 0 | Valid measurement |
| 1 | Sigma above threshold (noisy) |
| 2 | Signal below threshold (no target / too dark) |
| 4 | Possible wrap-around |
| 7 | Wrap-around confirmed |
| 9 | Hard-reset required |
| 10 | Phase out of valid limits |
| 11 | Range error |
| 12 | Target below minimum detection threshold |
| 13 | Invalid (raw status undefined) |

---

### Timing

```python
tof.set_range_timing(timing_budget_ms, inter_measurement_ms=0)
budget_ms, inter_ms = tof.get_range_timing()
```

| Parameter | Range | Default | Description |
|-----------|-------|---------|-------------|
| `timing_budget_ms` | 10–200 | 50 | VCSEL on-time per measurement. Longer budgets improve accuracy and range but reduce update rate |
| `inter_measurement_ms` | 0 or > budget | 0 | `0` = continuous (measurements back-to-back). Any value greater than `timing_budget_ms` enables autonomous (low-power) mode with that period between measurements |

`set_range_timing()` must be called while ranging is stopped, or before `start_ranging()`.

---

### Calibration

#### Offset

Compensates for a fixed distance error caused by the optical stack or coverglass.

```python
tof.set_offset(offset_mm)   # –1024 to +1023 mm
value = tof.get_offset()
```

Collect readings against a known target, compare to the true distance, and pass the difference to `set_offset()`.

#### Cross-talk

Compensates for signal reflected off a coverglass back into the sensor.

```python
tof.set_xtalk(xtalk_kcps)   # 0–128 kcps; 0 = no coverglass
value = tof.get_xtalk()
```

Measure the apparent distance to a target placed at the sensor's maximum range with the coverglass fitted, then derive the cross-talk value per ST application note AN5574.

#### Temperature

Recalibrates the VHV circuit if the ambient temperature has changed by more than 8 °C since the last calibration. The sensor must not be ranging.

```python
tof.stop_ranging()
tof.start_temperature_update()   # blocks ~50 ms
tof.start_ranging()
```

---

### Detection thresholds

Configures the interrupt to fire only when the measured distance crosses a window boundary, useful for proximity detection without polling.

```python
tof.set_detection_thresholds(distance_low_mm, distance_high_mm, window)
low, high, window = tof.get_detection_thresholds()
```

| `window` | Trigger condition |
|----------|-------------------|
| 0 | Distance < `distance_low_mm` |
| 1 | Distance > `distance_high_mm` |
| 2 | Distance outside [`low`, `high`] |
| 3 | Distance inside [`low`, `high`] |

---

### Signal and sigma thresholds

Filter out measurements that are too noisy or too faint.

```python
tof.set_signal_threshold(signal_kcps)   # 0–16384; default 1024
value = tof.get_signal_threshold()

tof.set_sigma_threshold(sigma_mm)       # 0–16383; default 15
value = tof.get_sigma_threshold()
```

---

### Utility

```python
model_id = tof.get_sensor_id()          # should return 0xEBAA
tof.set_i2c_address(new_address)        # change 7-bit I2C address
```

---

## Examples

### Continuous ranging with full result detail

```python
from machine import I2C, Pin
from VL53L4CD import VL53L4CD

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400_000)
tof = VL53L4CD(i2c)
tof.start_ranging()

while True:
    if tof.data_ready():
        r = tof.get_result()
        tof.clear_interrupt()
        if r['range_status'] == 0:
            print(f"{r['distance_mm']} mm  sigma={r['sigma_mm']} mm  "
                  f"signal={r['signal_rate_kcps']} kcps")
```

### Autonomous (low-power) mode at 200 ms intervals

```python
from machine import I2C, Pin
from VL53L4CD import VL53L4CD

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400_000)
tof = VL53L4CD(i2c)
tof.set_range_timing(50, 200)   # 50 ms budget, measure every 200 ms
tof.start_ranging()

while True:
    dist = tof.get_range()
    if dist >= 0:
        print(dist, "mm")
```

### Proximity alert using detection thresholds

```python
from machine import I2C, Pin
from VL53L4CD import VL53L4CD

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400_000)
tof = VL53L4CD(i2c)
tof.set_detection_thresholds(0, 300, 0)   # alert when target < 300 mm
tof.start_ranging()

while True:
    if tof.data_ready():
        r = tof.get_result()
        tof.clear_interrupt()
        if r['range_status'] == 0:
            print("ALERT – object at", r['distance_mm'], "mm")
```

---

## Licence

The MicroPython port is provided under the same **BSD Clear** licence as the original ST ULD source. See the licence text in `VL53L4CD.py`.