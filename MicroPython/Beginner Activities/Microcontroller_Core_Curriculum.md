# Beginner Microcontroller Core Curriculum

This is a comprehensive set of learning activities designed for use in high-school level computer technology classes. The complete set of materials can be used as an introductory self-study course in microcontroller programming, while individual activities may be useful as reference material for robotics clubs and maker spaces. Example code for all activities is available at [https://github.com/mirobotech](https://github.com/mirobotech).

The beginner activities are provided in multiple languages targeting four hardware circuits:

- **Arduino/C++** targeting the Arduino UNO R4 with the ARPS-2 circuit shield (Arduino UNO Rev. 3 works with minor limitations)
- **Arduino/C++** targeting the Arduino Nano ESP32 used in the BEAPER Nano circuit
- **MicroPython** targeting the Arduino Nano ESP32 used in the BEAPER Nano circuit
- **MicroPython** targeting the Raspberry Pi Pico used in the BEAPER Pico circuit
- **MPLAB-X C** targeting the PIC16F1459 microcontroller used in the BEAPER Micro circuit (in development)

All circuits include similar hardware capabilities designed for use with these beginner activities. The BEAPER Nano and BEAPER Pico circuits feature greater hardware expandability, making them more versatile circuits for use with the planned intermediate and advanced activities.

---

## Year 1: Beginner Activities

Guided exploration of fundamental microcontroller programming concepts, statements, and structures.

- Explicit program structure using provided starter code
- Heavy scaffolding and content spiralling
- **Guided Exploration** activities reinforce activity specifics and introduce related concepts
- **Extension Activities** are designed for short, concrete wins
- **Exploration** files (where relevant) extend an activity's core example with a richer version of the same concept, for learners who want more guided practice before moving on
- **Project** files (where relevant) provide an optional, open-ended skeleton challenge that applies an activity's concepts to a larger, self-directed build
- Leads to functional capstone projects based on starter templates

## Year 2: Intermediate Activities

Activities transition to more independent implementation, building on Year 1 concepts.

- Starter templates to guide and emphasise core concepts and program structures
- Greater emphasis on systems thinking and independent code creation
- Learners design algorithms to meet hardware criteria or other specifications
- Leads to open-ended capstone projects

---

## Beginner Activities — Overview

| Activity | Title | Focus | Key New Concepts |
|---|-------|-------|-----------------|
| 1 | Digital Output | Making something happen | GPIO output, program structure, sequential execution |
| 2 | Timing (Blocking) | Controlling when or how long | Blocking delays, tone generation |
| 3 | Digital Input | Reacting to an external input | GPIO input, active-low, `if` / `if-else`, AND operator |
| 4 | Constants and Variables | Remembering and using values | Constants, variables, data types, Boolean, console output |
| 5 | Decision Structures | Making decisions using logic | `else-if` chains, comparison operators, OR and NOT operators |
| 6 | Conditional Loops | Repeating while a condition is true | `while` loops, loop control variables, blocking loop patterns |
| 7 | Counted Loops | Repeating a known number of times | `for` loops, `range()`, loop variable as data, nested loops |
| 8 | Functions | Naming and re-using common actions | `def`, arguments, return values, encapsulation |
| 9 | Analog Input | Measuring real-world inputs | ADC, 16-bit range, `map_range()`, hysteresis |
| 10 | Analog Output (PWM) | Controlling real-world outputs | PWM, duty cycle, 16-bit range, motors, servos, RGB colour |
| 11 | Non-Blocking Timing | Doing more than one thing at a time | `ticks_ms()`, `ticks_diff()`, timestamp pattern, rollover |
| 12 | State Machines | Simplifying programs into modes | States, transitions, `enter_state()`, state diagrams, event flags |
| — | Capstone | Applying all concepts in a project | System design, planning, integration, testing |

---

## Beginner Activities — Detail

---

### Activity 1 — Digital Output

**Focus:** Learning how a microcontroller program makes something happen.

Instructors can use this activity to introduce microcontrollers, GPIO pins and attached I/O devices, IDE operation, and the program upload/run process. Learners are introduced to output operations, basic program structure, and sequential instruction flow.

**Prerequisite Knowledge**
- None (assumes no prior coding experience)

**New Concepts Introduced**
- Program syntax and structure (setup/loop or main while loop)
- GPIO output
- On vs. off (1/0, HIGH/LOW)
- Sequential instruction execution and program flow
- Empty loop termination (MicroPython: `pass`)
- Instruction execution speed

**Program Statements and Structures**
- GPIO on/off control (`value()`, `digitalWrite()`, `LED2 = 1`)
- Sequential on and off statements

**Guided Exploration**
- Controlling a single output (on/off)
- Observing sequential execution and the effect of instruction order
- Understanding run-once vs. repeating loop program structure

**Extension Activities**
- LED pattern output on LED2–LED5
- Microcontroller startup state indicator using the on-board module LED
- RGB LED output (BEAPER Nano)
- External hardware output

**Builds toward:** Activity 2 adds timing to output sequences; the program structure introduced here is used unchanged throughout all twelve activities.

---

### Activity 2 — Timing (Blocking Delays)

**Focus:** Controlling when or how long something happens.

This activity reinforces program flow while introducing blocking time delays to flash LEDs and create audio tones and notes.

**Prerequisite Knowledge**
- Digital output
- Program structure and sequential execution

**New Concepts Introduced**
- Blocking delays and program flow pauses
- Human-visible timing (seconds, milliseconds, microseconds)
- Tone generation using output and time delays
- Tone generation using `tone()` functions

**Program Statements and Structures**
- `delay()` / `sleep_ms()` / `sleep()`
- `tone()` with frequency and duration

**Guided Exploration**
- Blinking a single LED
- Alternating LED blink
- Time delays in sequential and loop code (LED chaser or animation)
- Understanding that blocking delays pause all execution before the next statement runs

**Extension Activities**
- Simulated machine startup using sequential and loop output
- Morse code LED signals
- Creating audio frequencies by controlling delay duration
- Viewing waveform period or frequency on an oscilloscope

**Builds toward:** The limitation that blocking delays prevent concurrent behaviour is explicitly revisited in Activity 11.

---

### Activity 3 — Digital Input

**Focus:** Reacting to an external input.

Learners read input pins and make simple decisions based on input state and combinations of input states.

**Prerequisite Knowledge**
- Program structure
- Digital output and timing

**New Concepts Introduced**
- Digital input
- Active-low vs. active-high logic
- Reading button state

**Program Statements and Structures**
- `digitalRead()` / `value()` / `pin ==`
- `if` conditions
- `if-else` conditions
- AND logical operator

**Guided Exploration**
- Reading a button and using its state to control an LED
- Button-controlled beeps and tones
- Combining multiple button states using logical AND

**Extension Activities**
- Multiple buttons controlling multiple outputs
- "Hold to activate" (nested AND) behaviour

**Builds toward:** The `if-else` structure introduced here grows into `else-if` chains in Activity 5. Boolean input state is extended to stored variable comparisons in Activity 4.

---

### Activity 4 — Constants and Variables

**Focus:** Remembering and using values.

Introduces the concepts that data can be stored, modified, and used to change program behaviour — not just read from hardware in the moment.

**Prerequisite Knowledge**
- Digital input and output
- Timing (blocking)

**New Concepts Introduced**
- Constants vs. variables
- Naming and readability
- Numeric data types (introduction to the types needed for the examples)
- Boolean `true` / `false`
- Using variables to modify program behaviour

**Program Statements and Structures**
- Constant definitions (`const()`, `#define`, `const int`)
- Variable declarations and assignment
- Conditions using Boolean variable state
- Console output for debugging (`print()`, `Serial.print()`)

**Guided Exploration**
- Blink delay using named delay constants
- Adjusting blink delay using a variable
- Meaningful constant and variable names
- Toggle button using a Boolean variable
- Changing LED patterns by editing variable values
- Storing timing and pin values as named constants

**Extension Activities**
- Adjustable blink speeds
- Multiple patterns using named constants

**Exploration**
- B04_Constants_Variables_Exploration.py extends the base activity with four named delay constants and four independent button variables, reinforcing the same concepts at greater scale

**Project**
- B04_Level_Indicator_Project.py — an open-ended bar graph/level-indicator challenge combining named constants, a counting variable, and the EA 2 edge-detection pattern

**Builds toward:** Console output introduced here is used for debugging throughout all remaining activities. Named constants for timing and thresholds appear in every subsequent activity.

---

### Activity 5 — Decision Structures

**Focus:** Making decisions using logic and comparisons.

Introduces the idea that decisions can be prioritised and chained, and that comparisons can be made against any data value — not only hardware input states.

**Prerequisite Knowledge**
- Digital input
- Variables
- Single `if-else` decisions

**New Concepts Introduced**
- `else-if` decision chains and decision priority
- Comparison operators (`==`, `!=`, `<`, `>`, `<=`, `>=`)
- Boolean logic operators (AND, OR, NOT)

**Program Statements and Structures**
- `else if` / `elif` branching
- Boolean comparisons against variable values
- Loop counting for button hold detection

**Guided Exploration**
- Output behaviour based on combinations of inputs
- Priority-based decisions using `else-if` ordering
- Mode selection using a counted variable

**Extension Activities**
- Multiple-input truth tables

**Project**
- B05_Rapid_Clicker_Project.py — an open-ended two-player rapid-clicker game combining edge-detected counters, an if/elif chain, and a Boolean game-state variable

**Builds toward:** `else-if` chains are the direct building block of state machine transition logic in Activity 12. The loop counting pattern previews the non-blocking hold detection developed fully in Activity 11.

---

### Activity 6 — Conditional Loops

**Focus:** Repeating actions while a condition is true.

Learners use decision structures in loops to repeat while a condition holds or until a condition changes, and see that loops can exit and that code runs after them.

**Prerequisite Knowledge**
- Conditions
- Digital input

**New Concepts Introduced**
- `while` loops with non-trivial conditions
- Loop control variables (initialise, check, update)
- Input-controlled repetition
- Using loops to replace repetitive code

**Program Statements and Structures**
- `while (condition)`
- Loop exit behaviour
- Blocking loop patterns (wait-for-press, wait-for-release)

**Guided Exploration**
- LED blinks while button held
- Countdown loop with a control variable
- Wait-for-press and wait-for-release patterns
- Wrapping loops in an outer `while True:` to restart behaviour

**Extension Activities**
- Wait for button press and release
- Loop counting
- Reaction timer game

**Project**
- B06_Combination_Lock_Project.py — an open-ended button-sequence lock combining a step counter, edge detection, and conditional loops

**Builds toward:** The loop control variable pattern (initialise, check, update) becomes the `for` loop in Activity 7. The blocking nature of conditional loops motivates the non-blocking timing approach in Activity 11.

---

### Activity 7 — Counted Loops

**Focus:** Repeating actions a known number of times.

Introduces the `for` loop as a cleaner way to handle counted repetition, and explores the loop variable as a source of meaningful data — not just a counter.

**Prerequisite Knowledge**
- Conditional loops and loop control variables
- Variables

**New Concepts Introduced**
- `for` loops and `range()`
- `range(n)`, `range(start, stop)`, `range(start, stop, step)`
- The loop variable as data (using `i` in comparisons and expressions)
- Conditional expressions (`A if condition else B`)
- Counted vs. condition-based looping — choosing the right tool
- Nested loops
- The `_` convention for unused loop variables

**Program Statements and Structures**
- `for i in range(...)`
- Positive and negative step values
- Nested `for` loops

**Guided Exploration**
- Using `range(3)` to replace a manual loop control variable
- Counting up and down through LEDs using the loop variable directly
- Comparing for-loop and while-loop implementations of the same task
- Nested loops: outer loop selects LED, inner loop controls flash count

**Extension Activities**
- LED bar graph with fill and empty using two `for` loops
- Nested loop structured display (flash count equals position)
- Binary counter using bitwise operators

**Project**
- B07_Morse_Code_Project.py — an open-ended message encoder combining a for loop with dot/dash timing (preview of sequence iteration)

**Builds toward:** Iteration over sequences (lists, tuples) instead of ranges is introduced in the Year 2 intermediate activities, where `for led in LEDS:` patterns appear throughout.

---

### Activity 8 — Functions

**Focus:** Naming and re-using common actions.

Introduces user-defined functions as a tool for encapsulating behaviour, reducing repetition, and improving readability. Explores functions with no arguments, with arguments, and with return values.

**Prerequisite Knowledge**
- Counted and conditional loops
- Variables and constants

**New Concepts Introduced**
- Function definition (`def` / `void` / return-type declarations)
- Arguments (input values passed to a function)
- Return values (results produced by a function)
- Encapsulation: hiding implementation detail behind a name
- Functions as a unit of code reuse and readability

**Program Statements and Structures**
- `def name():` with no arguments
- `def name(arg):` with one or more arguments
- `def name():` with a `return` statement
- Calling functions with and without arguments

**Guided Exploration**
- Identifying function calls already used throughout the curriculum (`tone()`, `value()`, `random.randint()`)
- Tracing `clear_leds()`, `indicate_attempts()`, and `read_keypad()` as examples of the three function forms
- Understanding why encapsulation makes the main loop readable
- Exploring default parameter values

**Extension Activities**
- `win_signal()` and `lose_signal()` functions
- `flash_led(led, times)` parameterised signal function
- Adding behaviour to `read_keypad()` without changing its interface
- `choose_target()` — encapsulating selection logic

**Builds toward:** All capstone projects use multiple user-defined functions. The function-as-argument pattern (`calibrate(sensor_fn, samples)`) is previewed in Activity 9.

---

### Activity 9 — Analog Input

**Focus:** Measuring and responding to real-world inputs.

Introduces the ADC and the 16-bit value range used throughout the BEAPER platform, and establishes the `map_range()` and `show_bar()` patterns used in later activities and capstone projects.

**Prerequisite Knowledge**
- Functions (defining and calling)
- Variables and constants
- Conditional decisions

**New Concepts Introduced**
- Analog-to-Digital Conversion (ADC)
- 16-bit input range (0–65535) and its binary basis (BEAPER Nano and BEAPER Pico only — ARPS-2 has no MicroPython counterpart to stay aligned with, so it keeps the Arduino default 10-bit range, 0–1023)
- `map_range()` for scaling values between ranges
- Integer vs. float division (`//` vs. `/`) and the need for `int()` conversion
- Hysteresis for stable threshold switching
- Reading multiple sensors (potentiometer, light, temperature)

**Program Statements and Structures**
- `ADC.read_u16()` / board module analog helper functions
- `map_range(value, in_min, in_max, out_min, out_max)`
- `show_bar(level, max_level)` LED bar graph
- Hysteresis using two thresholds and a state variable

**Guided Exploration**
- Observing raw ADC values from a potentiometer
- Mapping ADC range to a tone frequency (theremin)
- Displaying a bar graph proportional to sensor level
- Reading on-die and external temperature sensors
- Understanding hysteresis and why a single threshold causes flicker

**Extension Activities**
- Inverting `show_bar()` with a default parameter
- Temperature trend detection (`rising`, `falling`, `steady`)
- Min/max data logger with SW5 reset
- `calibrate(sensor_fn, samples)` — passing a function as an argument

**Builds toward:** On BEAPER Nano and BEAPER Pico, the 16-bit ADC range reappears as the PWM duty cycle range in Activity 10's MicroPython track (Arduino's `analogWrite()` uses an 8-bit range instead, and ARPS-2 stays 10-bit throughout). The `map_range()` function is used directly in Activity 10 projects and in capstone analog monitoring.

---

### Activity 10 — Analog Output (PWM)

**Focus:** Controlling real-world outputs at continuously varying levels.

Introduces Pulse Width Modulation as the mechanism underlying LED brightness, motor speed, servo position, and audio output. Learners configure PWM objects directly, stepping outside the board module abstraction for the first time.

**Prerequisite Knowledge**
- Analog input and the ADC range (Activity 9)
- Functions
- Variables and constants

**New Concepts Introduced**
- Pulse Width Modulation (PWM): duty cycle and frequency
- 16-bit PWM range on BEAPER Nano and BEAPER Pico (MicroPython); Arduino's `analogWrite()` uses an 8-bit range (0–255) instead; ARPS-2 stays 10-bit for ADC input throughout
- Creating PWM objects on board-module pins using pin number constants (MicroPython); `analogWrite()` on any PWM-capable pin with no object needed (Arduino C)
- PWM frequency and the flicker threshold
- Clamped output using a `set_brightness()` helper
- Automatic (program-driven) vs. manual (button-driven) output control

**Program Statements and Structures**
- `PWM(Pin(pin_number), freq=f, duty_u16=d)` (MicroPython) / `analogWrite(pin, brightness)` (Arduino C)
- `pwm.duty_u16(value)` and `pwm.freq(value)` (MicroPython)
- `set_brightness(pwm_led, brightness)` with clamping and return value

**Guided Exploration**
- Calculating duty cycle percentage from PWM values
- Why `LED2_PIN` is used rather than the `LED2` Pin object (MicroPython) / which pins support `analogWrite()` (Arduino C)
- Observing flicker at low PWM frequencies
- Manual vs. automatic control: SW3/SW4 stepping vs. fade state variable

**Projects** (each in a separate project file, with its own Extension Activities)
- Sound output using PWM (`B10_Sound_Player_Project`)
- Motor control using PWM (`B10_Motor_Controller_Project`)
- Servo control using PWM (`B10_Servo_Controller_Project`)
- RGB colour output using PWM (`B10_RGB_Controller_Project`) — BEAPER Nano only; BEAPER Pico and ARPS-2 have no on-board RGB LED. The RGB project uses the `colour.py`/`colour.h` conversion modules (HSV-to-RGB, RGBW, RGB565), shared with the future NeoPixel activity.

ARPS-2 has no on-board potentiometers, so its Projects use button-stepped control throughout rather than continuous potentiometer input (the base activity substitutes the Activity 9 floor sensors, Q1 and Q3, for RV1/RV2 instead).

**Builds toward:** Motor, servo, and RGB patterns from the projects are used directly in the robot and NeoPixel capstone projects. The automatic fade state variable is a direct conceptual predecessor to the state machine in Activity 12.

---

### Activity 11 — Non-Blocking Timing

**Focus:** Doing more than one thing at a time.

Introduces the timestamp pattern as a replacement for `sleep_ms()`, enabling multiple independent timed behaviours to coexist in the same loop without blocking each other.

**Prerequisite Knowledge**
- Timing (blocking delays from Activity 2)
- Variables and constants
- Conditional decisions

**New Concepts Introduced**
- `ticks_ms()` (MicroPython) / `millis()` (Arduino C) timestamps
- `ticks_diff(new, old)` and counter rollover (MicroPython); Arduino C handles rollover automatically through unsigned `long` arithmetic instead, with no equivalent function needed
- The non-blocking timing pattern: record, compare, act
- Multiple independent timers running simultaneously
- Button hold detection using timestamps
- Why a fast main loop (`LOOP_DELAY = 1ms`) is necessary

**Program Statements and Structures**
- `current_time = time.ticks_ms()` / `unsigned long current_time = millis();`
- `time.ticks_diff(current_time, last_event_time) >= INTERVAL` / `(current_time - last_event_time) >= INTERVAL`
- `last_event_time = current_time` to reset a timer
- Multiple `last_X_time` variables for independent timing channels

**Guided Exploration**
- Why a 1ms loop delay is needed instead of the 100ms (Activity 9) and 20ms (Activity 10) delays used in earlier activities
- Understanding counter rollover and why plain (signed) subtraction of timestamps fails
- Tracing `button_is_down`, `button_down_time`, and `hold_fired` through all press scenarios
- Two independent LED blink timers running at different rates — and the distinction between toggle rate and blink rate (a full blink cycle is two toggles)

**Extension Activities**
- Software button debounce using a change-timestamp
- Inactivity timeout with LED dim and recovery
- One-shot timed signal (restartable)
- Slow sensor read running independently alongside fast button/blink timing

**Project**
- LED Lighting Controller (`B11_LED_Lighting_Controller`) — re-implements Activity 10's PWM brightness controls with independent per-control timing rates instead of one shared loop delay

ARPS-2 has no on-board potentiometers, so its version of the project reuses Q1 and Q3 (as in Activity 10) for continuous input. The base activity's three independent single-button behaviours (tap/hold, debounce, one-shot signal) don't fit within ARPS-2's two Rev-3-safe buttons, so they're distributed across all three of SW3/SW4/SW5 rather than eliminating the Rev 3 caveat entirely — the main tap/hold content gets the safest button, with the caveat isolated to one optional Extension Activity.

**Builds toward:** The non-blocking timestamp pattern is used in every capstone project for animation frame rates, hold-and-repeat, countdown timers, and state duration tracking. Activity 12's `state_start` timer is a direct application.

---

### Activity 12 — State Machines

**Focus:** Organising complex programs into clearly defined modes of operation.

Introduces the state machine as a design pattern that makes multi-mode programs predictable and maintainable. The base activity is a hotel-safe-style combination lock — deliberately chosen over a traffic light for the first exposure, since it is purely event-driven (no simultaneous timers, no dynamically recalculated durations) and lets learners focus on the core idea (named states, explicit transitions, per-state outputs) without several other new ideas competing for attention at once. Learners draw state diagrams and connect every branch in the code to a specific arrow in the diagram. This is the third time learners solve this same combination-lock problem — a step-counter in Activity 6, refactored with functions in Activity 8, and now formalised as a state machine — a deliberate callback that lets the activity's own Guided Exploration ask learners to compare all three approaches directly.

**Prerequisite Knowledge**
- Non-blocking timing
- Variables, constants, and Boolean flags
- Functions

**New Concepts Introduced**
- States as named integer constants
- State diagrams: circles for states, labelled arrows for transitions
- `enter_state()` as the single point of output change and timer/flag reset
- State name lookup for readable console output — a dictionary keyed by state (MicroPython) or a `const char*` array indexed by state (Arduino C)
- Checking a multi-step input only after it is complete, rather than on each step — and why this is a meaningful security property, not just a style choice
- A state transition triggered from inside a state's own logic (the alarm's beep counter) rather than only from a button press
- Multiple independent timers running inside a single state (reapplying Activity 11's pattern one level down)

**Program Statements and Structures**
- `STATE_X = const(n)` (MicroPython) / `const int STATE_X = n;` (Arduino C)
- `enter_state(new_state, current_time, reason="")` function pattern, including a default parameter
- `state_start` timestamp for timed transitions
- `read_button()` / `wait_for_release()` — a simplified, single-purpose relative of Activity 8's `read_keypad()`
- Boolean flag variables (`car_waiting`, `walk_requested`) in the Traffic Light project

**Guided Exploration**
- Drawing and comparing the state diagram to the code structure
- Why named constants matter when states are renumbered or added
- Why `enter_state()` produces cleaner behaviour than setting outputs continuously
- Why blocking briefly with `wait_for_release()` is acceptable in the entry states but would break the alarm state's independent timers
- Tracing the happy path and an incorrect attempt through all three entry states
- Comparing this version against the learner's own Activity 6 and Activity 8 solutions to the same problem

**Extension Activities**
- Hold-to-relock from `UNLOCKED`, reusing Activity 11's hold-detection pattern
- Lockout state after three failed attempts
- Extending to a four-button combination using one more independent variable (not a list/array — deferred to the intermediate activities)
- Sketching a full security-alarm capstone's state diagram, with the combination lock nested inside it

**Project**
- Traffic Light Controller (`B12_Traffic_Light_Controller_Project`) — a skeleton reapplying the same `enter_state()` pattern to a state machine driven mostly by elapsed time, with button presses setting flags checked later rather than triggering immediate transitions. Includes a fix for a duplicated duration calculation from an earlier draft, now centralised in `calculate_green_time()`.

ARPS-2 has no clean way to avoid the Rev 3-shared buttons in the combination lock — `read_button()` genuinely needs SW2/SW3/SW4 as a three-way input, the same situation as Activity 8's `read_keypad()`. The Traffic Light project only needs two independent button roles, though, so its ARPS-2 version remaps both onto SW4/SW5 and needs no Rev 3 caveat at all in its base form.

**Builds toward:** Every capstone project uses this exact state machine pattern — named states, `enter_state()`, `state_start` timestamps, and event flags. The Traffic Light Controller project is the architectural template most capstones extend from directly.

---

## System Design Challenge (Capstone)

Learners apply all twelve activities to design and build a complete working project, using a starter template as the structural foundation. The capstone preparation guide leads learners through planning before writing any code: writing a user-perspective description, listing states and transitions, identifying hardware, planning the testing sequence, and writing the state diagram.

Available capstone projects:

- **Alarm System** — PIR or contact sensor triggers an arming/armed/tripped/alarm cycle with entry and exit delays and a secret arm/disarm code
- **Combination Safe** — four-digit code entry with a servo-driven lock and an auto-locking door sensor; wrong attempts are logged and reset silently, with no alarm, so a would-be intruder learns nothing about which digit was wrong (attempt limiting and lockout are Extension Activities, not base behaviour)
- **Simon Game** — memory sequence game with randomised patterns of increasing length
- **Analog Monitor** — multi-sensor display with threshold alerts, bar graphs, and logging
- **Sumo Robot** — autonomous ring-boundary detection and opponent-seeking with a mandatory countdown and emergency stop
- **Line Follower** — differential steering from floor-contrast sensors with a lost-line recovery state
- **NeoPixel Controller** — multi-mode LED strip display controller with selectable animations, hue and speed adjustment, and non-blocking frame timing
- **Wall Follower** — SONAR-guided navigation that follows a wall at a target distance, steering into gaps and away from obstacles ahead
- **Animatronic Controller** — three-servo puppet with recordable pose sequences and an instant emergency-stop hold that does not reset to a home position
- **Stepper Controller** — bipolar stepper motor driven through the on-board H-bridge, rotating to a time-based target position that keeps advancing even while stopped
- **Reaction Time Game** — simple and timing-based reaction tests measuring response speed against an unpredictable or predictable stimulus, with session-best tracking
- **Rock-Paper-Scissors** — countdown-timed hand game against the computer, with win/loss/tie tracking and a modular-arithmetic refactor available as an Extension Activity
- **Morse Code Trainer** — tap-to-dot/dash transmit and receive practice modes sharing a single timing-based tap-reading mechanism, with an external Morse key supported alongside the on-board button

The Combination Safe's ARPS-2 version assumes an Arduino UNO R4 (Minima or WiFi) rather than Rev 3. Every other ARPS-2 activity and capstone in this curriculum works around Rev 3's USB-serial pin sharing by avoiding or remapping SW2/SW3, but Combination Safe genuinely needs all four buttons as independent code digits, with no button left over to sacrifice — the same constraint Activity 8's `read_keypad()` and Activity 12's combination lock hit, but here there is no third safe button to fall back on either. Rev 3 users would need to give up two of the four code digits or find another way to read them. Reaction Time Game, Rock-Paper-Scissors, and Morse Code Trainer make the same assumption for the same reason — each uses all four buttons for genuinely distinct roles, rather than the two- or three-button designs most other ARPS-2 capstones remap around.

---

## Reach-Ahead Activities

Optional, self-contained previews of Year 2 hardware capabilities, each built by taking an existing Year 1 capstone a learner already understands and adding one new capability on top of it, rather than teaching the underlying technology from scratch. Each reach-ahead is a complete, working program (not a TODO-based teaching exercise the way the capstones are), so it can be read, run, and enjoyed immediately, without displacing Year 2's own, more thorough treatment of the same concepts later — Activity I01, for example, teaches the LCD driver's framebuffer model, layout arithmetic, and colour-coded status indicators in depth; the LCD reach-ahead deliberately stays narrower than that so it doesn't blunt I01's own teaching moments.

Reach-aheads require optional hardware beyond the base circuits: an ST7789-based 240x240 LCD module for the LCD reach-ahead, and either BEAPER Nano's built-in ESP32-S3 radio, a Raspberry Pi Pico W/Pico 2 W (for BEAPER Pico), or an Arduino UNO R4 WiFi specifically, not Minima (for ARPS-2) for the WiFi reach-ahead.

Available reach-ahead activities:

- **Reaction Time Game with LCD Display** (BEAPER Nano and BEAPER Pico MicroPython; BEAPER Nano Arduino C) — the Reaction Time Game capstone's result screen shown on a real display instead of only the Serial Monitor, using large text and a bar chart comparing each round against the session best
- **WiFi NeoPixel Controller** (BEAPER Nano and BEAPER Pico MicroPython; BEAPER Nano and ARPS-2 Arduino C) — the NeoPixel Controller capstone controlled from a phone or laptop browser over the board's own self-hosted WiFi network, alongside its existing physical buttons, with a slider offering smoother direct control than the physical button's one-step-at-a-time adjustment

Each platform's WiFi setup differs enough to be worth knowing about before extending these further: BEAPER Nano's Arduino ESP32 core includes a built-in `WebServer` library with route handlers; BEAPER Pico's rp2040 port requires `config()` before `active(True)` (the reverse of BEAPER Nano's order) and a `security=` parameter rather than `authmode=`; and UNO R4 WiFi's `WiFiS3` library has no built-in route-handler library at all, requiring manual character-by-character HTTP request parsing instead.

Bluetooth-based reach-ahead activities (a BLE-controlled robot, extending Wall Follower or Sumo Robot with phone control) are planned but not yet developed.