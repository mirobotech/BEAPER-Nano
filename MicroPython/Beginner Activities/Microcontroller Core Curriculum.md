# Microcontroller Core Curriculum

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
- Two-player rapid clicker game

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
- Combination lock preview

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
- Morse code output (preview of list iteration)

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
- 16-bit input range (0–65535) and its binary basis
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

**Builds toward:** The 16-bit ADC range reappears as the PWM duty cycle range in Activity 10. The `map_range()` function is used directly in Activity 10 projects and in capstone analog monitoring.

---

### Activity 10 — Analog Output (PWM)

**Focus:** Controlling real-world outputs at continuously varying levels.

Introduces Pulse Width Modulation as the mechanism underlying LED brightness, motor speed, servo position, and audio output. Learners configure PWM objects directly, stepping outside the board module abstraction for the first time.

**Prerequisite Knowledge**
- Analog input and the 16-bit range
- Functions
- Variables and constants

**New Concepts Introduced**
- Pulse Width Modulation (PWM): duty cycle, frequency, and 16-bit range
- Creating PWM objects on board-module pins using pin number constants
- PWM frequency and the flicker threshold
- Clamped output using a `set_brightness()` helper
- Automatic (program-driven) vs. manual (button-driven) output control

**Program Statements and Structures**
- `PWM(Pin(pin_number), freq=f, duty_u16=d)`
- `pwm.duty_u16(value)` and `pwm.freq(value)`
- `set_brightness(pwm_led, brightness)` with clamping and return value

**Guided Exploration**
- Calculating duty cycle percentage from 16-bit values
- Why `LED2_PIN` is used rather than the `LED2` Pin object
- Observing flicker at low PWM frequencies
- Manual vs. automatic control: SW3/SW4 stepping vs. fade state variable

**Extension Activities** (each in a separate project file)
- Sound output using PWM (`B10_Sound_Player_Project`)
- Motor control using PWM (`B10_Motor_Controller_Project`)
- Servo control using PWM (`B10_Servo_Controller_Project`)
- RGB colour output using PWM (`B10_RGB_Controller_Project`)

**Builds toward:** Motor, servo, and RGB patterns from the extension projects are used directly in the robot and NeoPixel capstone projects. The automatic fade state variable is a direct conceptual predecessor to the state machine in Activity 12.

---

### Activity 11 — Non-Blocking Timing

**Focus:** Doing more than one thing at a time.

Introduces the timestamp pattern as a replacement for `sleep_ms()`, enabling multiple independent timed behaviours to coexist in the same loop without blocking each other.

**Prerequisite Knowledge**
- Timing (blocking delays from Activity 2)
- Variables and constants
- Conditional decisions

**New Concepts Introduced**
- `ticks_ms()` and `millis()` timestamps
- `ticks_diff(new, old)` and counter rollover
- The non-blocking timing pattern: record, compare, act
- Multiple independent timers running simultaneously
- Button hold detection using timestamps
- Why a fast main loop (`LOOP_DELAY = 1ms`) is necessary

**Program Statements and Structures**
- `current_time = time.ticks_ms()`
- `time.ticks_diff(current_time, last_event_time) >= INTERVAL`
- `last_event_time = current_time` to reset a timer
- Multiple `last_X_time` variables for independent timing channels

**Guided Exploration**
- Why a 1ms loop delay is needed instead of the 20ms used in earlier activities
- Understanding counter rollover and why plain subtraction of timestamps fails
- Tracing `button_is_down`, `button_down_time`, and `hold_fired` through all press scenarios
- Two independent LED blink timers running at different rates

**Extension Activities**
- Software button debounce using a change-timestamp
- Inactivity timeout with LED dim and recovery
- One-shot timed signal (restartable)
- Slow sensor read running independently alongside fast button/blink timing

**Builds toward:** The non-blocking timestamp pattern is used in every capstone project for animation frame rates, hold-and-repeat, countdown timers, and state duration tracking. Activity 12's `state_start` timer is a direct application.

---

### Activity 12 — State Machines

**Focus:** Organising complex programs into clearly defined modes of operation.

Introduces the state machine as a design pattern that makes multi-mode programs predictable and maintainable. Learners draw state diagrams, implement a traffic light controller, and connect every `if` statement in the code to a specific arrow in the diagram.

**Prerequisite Knowledge**
- Non-blocking timing
- Variables, constants, and Boolean flags
- Functions

**New Concepts Introduced**
- States as named integer constants
- Transitions as timed or event-driven conditions
- `enter_state()` as the single point of output change and timer reset
- State diagrams: circles for states, labelled arrows for transitions
- Event flags: recording inputs during one state for use in another
- State name dictionaries for readable console output

**Program Statements and Structures**
- `STATE_X = const(n)` named state constants
- `STATE_NAMES = { STATE_X: "X", ... }` dictionary
- `enter_state(new_state)` function pattern
- `state_start` timestamp for timed transitions
- Boolean flag variables (`car_waiting`, `walk_requested`)

**Guided Exploration**
- Drawing and comparing the state diagram to the code structure
- Why named constants matter when states are renumbered or added
- How two simultaneous timers coexist inside one state
- Why `enter_state()` produces cleaner behaviour than setting outputs continuously
- Tracing event flags through a multi-event scenario

**Extension Activities**
- Train crossing sensor: interrupt-driven transition from any green state
- Crosswalk extension: walk signal timeout and walk request during green
- Combination lock state machine — event-driven rather than time-driven (`B12_Combination_Lock_Project`)

**Builds toward:** Every capstone project uses this exact state machine pattern — named states, `enter_state()`, `state_start` timestamps, and event flags. The traffic light program is the architectural template for all capstone starter code.

---

## System Design Challenge (Capstone)

Learners apply all twelve activities to design and build a complete working project, using a starter template as the structural foundation. The capstone preparation guide leads learners through planning before writing any code: writing a user-perspective description, listing states and transitions, identifying hardware, planning the testing sequence, and writing the state diagram.

Available capstone projects:

- **Alarm System** — PIR or contact sensor triggers an arming/armed/tripped/alarm cycle with entry and exit delays and a secret arm/disarm code
- **Combination Safe** — multi-button code entry with attempt limiting and an alarm state
- **Simon Game** — memory sequence game with randomised patterns of increasing length
- **Analog Monitor** — multi-sensor display with threshold alerts, bar graphs, and logging
- **Sumo Robot** — autonomous ring-boundary detection and opponent-seeking with a mandatory countdown and emergency stop
- **Line Follower** — differential steering from floor-contrast sensors with a lost-line recovery state
- **NeoPixel Controller** — multi-mode LED strip display controller with selectable animations, hue and speed adjustment, and non-blocking frame timing