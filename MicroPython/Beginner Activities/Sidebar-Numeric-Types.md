# Sidebar: How Computers Store Numbers

## A Reference for mirobo.tech Year 1 Microcontroller Programming

---

At several points in this curriculum — when you first saw `analogRead()`
return 1023, when the ADC returned 65535, when `millis()` was declared
`unsigned long`, when the header files used `uint8_t` — you encountered
the fact that computers don't store numbers the way humans think about
them. This sidebar explains why, and what it means for the programs
you write.

---

## Why Computers Use Binary

A computer's memory is built from electronic switches. Each switch has
exactly two stable states: on or off. One switch stores one **bit** of
information — a single 0 or 1.

To store larger numbers, computers group bits together. With 2 bits you
can represent 4 different values (00, 01, 10, 11). With 8 bits you can
represent 256 different values (0 through 255). Each additional bit
doubles the number of representable values:

| Bits | Number of values | Range (unsigned) |
|------|-----------------|------------------|
| 1    | 2               | 0–1              |
| 4    | 16              | 0–15             |
| 8    | 256             | 0–255            |
| 10   | 1 024           | 0–1 023          |
| 12   | 4 096           | 0–4 095          |
| 16   | 65 536          | 0–65 535         |
| 32   | 4 294 967 296   | 0–4 294 967 295  |

This is why the numbers you encounter in microcontroller programming
are almost never round decimals. When the ARPS-2's ADC returns values
from 0 to 1023, it is using 10 bits (2¹⁰ = 1024 values). When the
BEAPER Nano's ADC returns 0 to 65535, it is using 16 bits (2¹⁶ = 65536
values). These ranges are not arbitrary — they are the natural
consequence of the hardware's bit width.

---

## Integer Types

An **integer** is a whole number with no fractional part. Most values
in microcontroller programs are integers: pin numbers, sensor readings,
timing values, loop counters, LED states. Integers are fast to compute,
take up a predictable amount of memory, and map directly onto the
hardware operations of the processor.

### Signed and Unsigned

Every integer type is either **signed** (can represent negative numbers)
or **unsigned** (only zero and positive numbers).

A signed 8-bit integer uses one of its bits to indicate the sign,
leaving 7 bits for the magnitude. This gives a range of −128 to +127.
An unsigned 8-bit integer uses all 8 bits for the value, giving a range
of 0 to 255.

Most quantities in embedded programming are naturally non-negative —
pin numbers, ADC readings, elapsed times, PWM duty cycles — so unsigned
types are preferred wherever the value cannot be negative. Signed types
are appropriate when a value can meaningfully go below zero: motor
speeds (forward and reverse), temperature in degrees Celsius, error
corrections.

### The Types You Have Seen

**In Arduino (C/C++)**, integer types are named explicitly:

| Type | Bits | Signed? | Range |
|------|------|---------|-------|
| `bool` | 1 | No | `false` / `true` (0 or 1) |
| `uint8_t` | 8 | No | 0–255 |
| `int8_t` | 8 | Yes | −128–127 |
| `int` | 16 or 32 | Yes | Platform-dependent |
| `unsigned int` | 16 or 32 | No | Platform-dependent |
| `long` | 32 | Yes | −2 147 483 648–2 147 483 647 |
| `unsigned long` | 32 | No | 0–4 294 967 295 |

The `uint8_t` type in the header files — `const uint8_t LED2 = 3;` —
means "unsigned integer, exactly 8 bits wide." Using 8 bits for a pin
number makes sense: the boards in this curriculum have far fewer than
256 pins, and 8 bits uses less memory than 32. The `u` prefix means
unsigned, `8` means 8 bits, and `_t` is a C convention meaning "type."

The `unsigned long` type for timing variables — `unsigned long
button_down_time = 0;` — is chosen because `millis()` returns an
`unsigned long`. Timing values start at zero and grow as the program
runs, so unsigned is appropriate. Using 32 bits gives a maximum value
of about 4.3 billion milliseconds — roughly 49 days of continuous
running before the counter rolls over.

**In MicroPython**, the type system is simpler: there is only one
integer type, called `int`, and it automatically grows as large as
needed. You rarely need to think about bit width in MicroPython, but
the numbers the hardware returns are still determined by the hardware's
bit width — `RV1_level()` still returns values from 0 to 65535 because
the ADC is 16 bits wide, regardless of how MicroPython stores that
value internally.

### Out-of-Range Values and Wrapping

In Arduino (C/C++), assigning a value outside a type's range does not
cause an error — the value silently **wraps around** to fit within the
type's bit width. For example, assigning 300 to a `uint8_t` variable
gives 44, because 300 − 256 = 44 (300 exceeds the 8-bit range of
0–255 by 44). This wrapping behaviour follows from the way binary
arithmetic works at the hardware level.

```cpp
uint8_t x = 300;   // x becomes 44, not 300 — no error or warning
uint8_t y = 256;   // y becomes 0
uint8_t z = 255 + 1;  // z becomes 0 (wraps from maximum back to zero)
```

This is one of the most confusing bugs a beginner can encounter: the
program compiles and runs without complaint, but a variable quietly
holds the wrong value. If you ever see an unexpectedly small value
where you expected a large one — or a value near zero where you
expected a value near the maximum — out-of-range wrapping is a likely
cause. The fix is to use a wider type (`int` or `unsigned int`) that
can hold the full range of values the variable will actually take.

MicroPython's `int` type grows automatically and never wraps, so this
problem does not arise there.

---

## Float Types

A **float** (floating-point number) can represent numbers with
fractional parts: 3.14, −0.5, 98.6. Floats are essential for
real-world measurements where precision matters — temperature
conversions, voltage calculations, percentages.

Floats are stored in a fixed number of bits using a format similar to
scientific notation: some bits store the significant digits, and some
store the exponent. A 32-bit float can represent numbers across an
enormous range but with limited precision — roughly 7 significant
decimal digits.

Floats are slower to compute than integers on most microcontrollers,
and some operations that seem exact can accumulate small errors. For
this reason, embedded programs use integers wherever possible and
switch to floats only when fractional values are genuinely needed.

---

## Integer vs Float in Practice

The most practically important thing to understand is what happens when
you mix integers and floats in calculations — and this differs between
MicroPython and Arduino.

### In MicroPython

The `/` operator always produces a float, even when both operands
are integers and the result is a whole number:

```python
print(10 / 2)       # 5.0  (float)
print(10 // 2)      # 5    (int)
print(type(10 / 2)) # <class 'float'>
```

The `//` operator (floor division) always produces an integer, discarding
any fractional remainder:

```python
print(7 // 2)       # 3    (not 3.5)
print(-7 // 2)      # -4   (rounds toward negative infinity)
```

This matters when calling hardware functions. The `tone()` function
requires an integer frequency in hertz. Passing a float may cause
an error or be silently ignored depending on the firmware version.
This is why `map_range()` in Activity 9 returns a float but the main
loop converts it before use:

```python
frequency = int(map_range(rv2, 0, 65535, TONE_MIN, TONE_MAX))
beaper.tone(frequency)
```

Temperature and voltage calculations should use float division because
precision matters — a 0.5 V offset and a 0.01 V/°C slope require
decimal arithmetic to produce a meaningful result:

```python
voltage = beaper.temp_level() * 3.3 / 65535   # float result needed
temp_c  = (voltage - 0.5) / 0.01
```

If `//` were used here, the voltage calculation would round to the
nearest whole number (0 or 3, for any sensor reading) and the
temperature result would be meaningless.

### In Arduino (C/C++)

In C, dividing two integers with `/` gives an integer result with the
remainder silently discarded — this is called **integer division** and
it is the default, unlike MicroPython:

```cpp
int result = 10 / 3;    // result is 3, not 3.333...
int result = 7 / 2;     // result is 3, not 3.5
```

To get a float result in C, at least one operand must be a float:

```cpp
float result = 10.0 / 3;    // result is 3.333...
float result = (float)10 / 3;   // cast forces float division
```

This means scaling operations like `analogRead(A0) / 4` in Arduino
are integer divisions — which is often exactly what you want (mapping
0–1023 to 0–255 cleanly), but can cause subtle bugs if you expect
a fractional result.

---

## Counter Rollover

Every integer type has a maximum value determined by its bit width.
When a counter exceeds that maximum, it wraps back to zero — this is
called **rollover** (or overflow).

The `millis()` function in Arduino returns an `unsigned long` that
counts milliseconds since the program started. After approximately
49 days it reaches its maximum value (4 294 967 295) and wraps back
to zero. For most programs this is irrelevant, but timing code that
compares timestamps must handle it correctly.

The safe way to measure elapsed time with `millis()` is subtraction
of two `unsigned long` values:

```cpp
unsigned long elapsed = current_time - start_time;
```

This works correctly even across a rollover. If `current_time` has
just wrapped to a small value (say 10) and `start_time` is still a
large value (say 4 294 967 290), unsigned arithmetic gives:

```
10 - 4 294 967 290 = 16  (in unsigned 32-bit arithmetic)
```

This correctly tells you that 16 milliseconds have elapsed. Signed
arithmetic would give a large negative number and break the timing
logic. This is why all timestamp variables in Activity 11 and 12 are
declared `unsigned long` — not just `int`.

In MicroPython, `time.ticks_ms()` also rolls over, but unlike C's
unsigned arithmetic, plain subtraction of MicroPython integers does
not handle rollover automatically. This is why MicroPython provides
the dedicated `time.ticks_diff(new, old)` function, which is designed
to give correct results across rollover. Always use `ticks_diff()`
rather than subtracting ticks values directly:

```python
# Correct:
elapsed = time.ticks_diff(current_time, start_time)

# Wrong - gives incorrect results after rollover:
elapsed = current_time - start_time
```

---

## Bit Width and ADC Resolution

The resolution of an analog-to-digital converter is determined by
how many bits it uses to represent the measured voltage. A wider ADC
distinguishes finer voltage differences:

| ADC bits | Steps | Voltage resolution (0–3.3 V) |
|----------|-------|------------------------------|
| 8-bit    | 256   | ~12.9 mV per step            |
| 10-bit   | 1 024 | ~3.2 mV per step             |
| 12-bit   | 4 096 | ~0.8 mV per step             |
| 16-bit   | 65 536 | ~0.05 mV per step           |

The ARPS-2 (Arduino UNO R4) uses a 10-bit ADC by default, returning
0–1023. The BEAPER Nano (Arduino Nano ESP32) and BEAPER Pico use
16-bit ADC readings, returning 0–65535. The board module functions
`RV1_level()`, `light_level()`, and `temp_level()` all return values
in the range appropriate for the platform they run on.

When scaling an ADC reading to control a PWM output — mapping a
potentiometer to LED brightness, for example — you need to account
for this difference:

```python
# MicroPython (BEAPER Nano/Pico): ADC is 16-bit (0-65535)
# PWM is also 16-bit (0-65535) - no scaling needed
led_pwm.duty_u16(beaper.RV1_level())
```

```cpp
// Arduino (ARPS-2): ADC is 10-bit (0-1023)
// analogWrite() accepts 8-bit (0-255) - scale by dividing by 4
analogWrite(LED2, analogRead(RV1) / 4);
```

The factor of 4 in the Arduino version comes from the bit width
difference: 1024 steps ÷ 256 steps = 4. This is integer division
in C — which works correctly here because both ranges divide evenly.

---

## PWM and Duty Cycle Resolution

PWM (Pulse Width Modulation) output also has a bit-width resolution
that determines how many distinct brightness levels are available.
Arduino's `analogWrite()` accepts 8-bit values (0–255), giving 256
brightness levels. MicroPython's `PWM.duty_u16()` accepts 16-bit
values (0–65535), giving 65 536 levels.

The finer resolution of 16-bit PWM produces smoother fades — the
step size `FADE_STEP = 500` in Activity 10 (MicroPython) produces
imperceptibly small changes, while the equivalent `FADE_STEP = 2`
in the Arduino version (8-bit) produces visible steps at low
brightness levels.

---

## Choosing the Right Type

A useful habit when declaring any variable or constant is to ask:
what is the range of values this can take, and does it need to be
a whole number or can it be fractional?

- **Button states, LED states, flags:** use `bool` (Arduino) or
  a plain integer 0/1 (MicroPython)
- **Pin numbers, small counts:** use `uint8_t` (Arduino) or `int`
  (MicroPython)
- **ADC readings, PWM values, sensor levels:** use `int` or
  `unsigned int` matching the hardware range
- **Timestamps, elapsed times:** use `unsigned long` (Arduino) or
  the result of `time.ticks_ms()` (MicroPython)
- **Temperature, voltage, percentages:** use `float`
- **State identifiers:** use named integer constants

When in doubt in Arduino, `int` is a reasonable default for values
that fit in its range and `unsigned long` for any timing variable.
In MicroPython, you rarely need to think about type explicitly —
but you do need to think about whether you want `/` (float result)
or `//` (integer result) when dividing.

---

## Quick Reference

### MicroPython

| Operation | Result type | Example |
|-----------|-------------|---------|
| `10 / 3` | `float` | `3.3333...` |
| `10 // 3` | `int` | `3` |
| `int(3.7)` | `int` | `3` (truncates) |
| `float(5)` | `float` | `5.0` |
| `type(x)` | — | Shows the type of `x` |
| `time.ticks_ms()` | `int` | Milliseconds since boot |
| `time.ticks_diff(new, old)` | `int` | Elapsed ms (rollover-safe) |

### Arduino (C/C++)

| Type | Bits | Range | Typical use |
|------|------|-------|-------------|
| `bool` | 1 | `false`/`true` | Flags, button states |
| `uint8_t` | 8 | 0–255 | Pin numbers, PWM values |
| `int` | 32* | −2M to +2M | General integers |
| `unsigned int` | 32* | 0–4M | Non-negative integers |
| `unsigned long` | 32 | 0–4 294 967 295 | Timestamps (`millis()`) |
| `float` | 32 | ±3.4×10³⁸ | Sensor conversions |

*On the Arduino boards used in this curriculum (UNO R4, Nano ESP32),
`int` and `unsigned int` are 32 bits. On older 8-bit Arduino boards,
`int` was 16 bits — one reason to use `long` explicitly when you need
32 bits.

| Operation | Result | Example |
|-----------|--------|---------|
| `10 / 3` | `int` → `3` | Integer division (remainder discarded) |
| `10.0 / 3` | `float` → `3.333...` | Float division |
| `(float)10 / 3` | `float` → `3.333...` | Cast forces float division |
| `(int)3.7` | `int` → `3` | Cast truncates toward zero |
| `millis()` | `unsigned long` | Ms since startup |
| `current - start` | `unsigned long` | Elapsed ms (rollover-safe if both unsigned) |

---

*mirobo.tech Year 1 Microcontroller Programming — Numeric Types Sidebar*
