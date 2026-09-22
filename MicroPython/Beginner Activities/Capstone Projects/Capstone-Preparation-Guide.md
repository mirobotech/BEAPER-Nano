# Capstone Project Preparation Guide

## mirobo.tech Microcontroller Core Curriculum - Beginner Activities

---

## Introduction

You have now completed twelve activities covering every major concept
you need to build a working embedded system from scratch: digital and
analog input and output, program structure, functions, loops, decisions,
state machines, and non-blocking timing. Your capstone project is the
opportunity to combine these tools to solve a problem you choose.

Experienced embedded developers rarely sit down and start writing code
immediately. Before opening their editor they ask a series of questions
about what the system needs to do, what hardware it will use, and how
it will be structured. This guide leads you through that same process.
Work through each section in order and complete the template before
writing any code. The time you spend planning will save far more time
during development and debugging.

The worked example at the end shows how the Activity 12 combination
lock would look if it had been planned using this template. Read it
alongside your own planning to check that your answers are at the
right level of detail. The combination lock is purely event-driven -
if your project also needs timed transitions or event flags recorded
in one state and used in another, look at the Traffic Light
Controller project from Activity 12 for that pattern instead.

---

## Part 1 — Project Description

Write two or three sentences describing how your project works **from
the perspective of someone using it** — not how it works internally.

Describe what users would see and how they would interact with it – what 
does it control, how would it be used, and what problem does it solve?

Writing from the user's perspective forces you to think about what
the system must do rather than how you intend to build it. It also
often reveals ambiguities — if you cannot describe the behaviour in
plain language, the design is not yet clear enough to code.

> **Example:** "A motion-activated security light that turns on
> when someone enters the backyard at night, stays on for 30 seconds,
> and then turns off automatically. A switch on the back of the unit
> enables or disables the sensor so the light can be left on manually."

**Your description:**

&nbsp;

&nbsp;

&nbsp;

---

## Part 2 — Hardware Inventory

List every input and output your project uses. Be specific — name the
sensor or component, the type of signal it uses (digital or analog), 
and the pin or connector it connects to.

Working through this list often reveals problems before any code is
written: two components needing the same pin, an output the circuit
does not support, or a sensor that requires a library you have not
yet found.

### Inputs

| Component | Signal type | Pin / connector | Notes |
|-----------|-------------|-----------------|-------|
| | | | |
| | | | |
| | | | |
| | | | |

### Outputs

| Component | Signal type | Pin / connector | Notes |
|-----------|-------------|-----------------|-------|
| | | | |
| | | | |
| | | | |
| | | | |

### Timing requirements

List any actions that must happen at a specific rate, after a specific
delay, or for a specific duration (e.g. "sensor is read every 500 ms",
"motor runs for 2 s after button press", "LED blinks at 2 Hz").

&nbsp;

&nbsp;

---

## Part 3 — State Identification

A state is a distinct situation your program can be in **where the
correct response to an input might be different from another
situation**. This is the key test: if pressing a button does
something different depending on the situation, those situations are
different states.

Ask yourself: "What are all the distinct modes or phases my program
can be in?" Write each one as a short name (one or two words) and a
plain-language description of what is happening during that state.

Start with obvious states from your project description, then look
for implied states you may have missed. Edge cases often reveal hidden
states — what happens when the system is initialising, when an error
occurs, when a timeout expires, or when a safety condition is active?

| State name | Description — what is happening during this state? |
|------------|-----------------------------------------------------|
| | |
| | |
| | |
| | |
| | |

**Hint:** Most beginner capstone projects have between 3 and 6 states.
If you have more than 8, look for states that could be merged. If you
have fewer than 3, look for situations where the same input produces
different results.

---

## Part 4 — State Details Table

Complete one row for each state. For each state, identify:

- **Active outputs:** which LEDs, motors, speakers, or other outputs
  are on or active while in this state
- **Transition events:** what input or timing condition causes a
  transition out of this state (there may be more than one)
- **Next state:** which state each transition leads to

This table is the heart of your design. Every row must have at least
one transition — a state with no exit is a program that gets stuck.
Every state must be reachable from at least one other state — a state
with no entry will never run.

| State name | Active outputs | Transition event or condition | Next state |
|------------|---------------|-------------------------------|------------|
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |

**Check your table:**
- Does every state have at least one way out?
- Does every state (except your initial state) have at least one way in?
- Is there a path from the initial state to every other state?
- Is there a path back to a safe state if something goes wrong?

---

## Part 5 — State Diagram

Draw your state diagram from the completed table in Part 4. Use
circles for states and arrows for transitions. Label each arrow with
the event or condition that triggers it.

**Notation:**

```
        timed out (5 s)
  GREEN ─────────────────> YELLOW

        SW2 pressed
  IDLE ──────────────────> RUNNING

        elapsed >= 2000 ms
  ARMED ─────────────────> TRIGGERED
```

Your diagram is a visual check that your table is complete and
consistent. If you cannot draw a clean diagram from your table,
the table needs more work before you start coding.

**Draw your diagram here (or on a separate sheet):**

&nbsp;

&nbsp;

&nbsp;

&nbsp;

&nbsp;

---

## Part 6 — Code Planning

With your states and transitions defined, the program structure
will reflect it. Answer each question before opening your editor.

**Initial state:** Which state does the program start in, and what
outputs must be set on startup?

The first part of every example program has been the constant and
variables definitions, followed by program and helper functions.
Think through and start to plane these for your program, now.

**Constants:** List the named constants your program will need —
timing values, thresholds, pin assignments (if not in a header
file), and state names.

| Constant name | Value | Purpose |
|---------------|-------|---------|
| `STATE_` ... | 0, 1, 2 ... | State identifiers |
| `LOOP_DELAY` | 1 ms | Main loop rate |
| | | |
| | | |
| | | |

**Variables:** List the variables that track program state across
loop iterations. For each variable, note its type, initial value,
and what it represents.

| Variable name | Type | Initial value | Purpose |
|---------------|------|---------------|---------|
| `state` | int | initial state | Current state |
| `state_start` | timestamp | 0 | Time current state began |
| | | | |
| | | | |
| | | | |

**Functions:** List any helper functions that will make your main
loop cleaner. The `enter_state()` and `all_outputs_off()` pattern
from Activity 12 is worth using in any state machine project.

| Function name | Purpose |
|---------------|---------|
| `enter_state(new_state, time, reason)` | Handle state transition, clear outputs, print diagnostic |
| `all_outputs_off()` | Turn off all LEDs, motors, and other outputs |
| | |
| | |

**Main loop structure:** Sketch the structure of your main loop in
pseudocode — not real code, just the shape of the logic.

```
loop:
    current_time = now()
    elapsed = current_time - state_start

    if state == STATE_A:
        ...

    elif state == STATE_B:
        ...
```

&nbsp;

---

## Part 7 — Testing Plan

Before your project is complete you need to verify that every
transition works correctly. Write one test case for each transition
in your state diagram — describe exactly what you will do and what
you expect to observe.

| Starting state | Action / condition | Expected next state | Expected outputs |
|----------------|-------------------|---------------------|------------------|
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |

**Debugging tip:** If a transition does not work as expected, add a
`print()` statement inside `enter_state()` (if you are using it) and
watch the serial output. The transition-on-print pattern from
Activity 12 — printing the state name and the reason for each
transition — is the most efficient way to find unexpected behaviour.
Print variable values immediately before a transition that is not
firing to see what the program actually sees at that moment.

---

## Capstone Example — Combination Lock

The following shows how the Activity 12 combination lock program
would look if it had been planned using this template.

### Part 1 — Project Description

A digital combination lock styled after a hotel-safe keypad. The
user presses three buttons in sequence; each press beeps and lights
the next progress LED, whether or not it is correct. Once three
presses have been entered, the lock either opens (correct
combination) or sounds an alarm (wrong combination) and returns to
the start automatically. A reset button restarts entry at any time
before the lock has opened.

### Part 2 — Hardware Inventory

**Inputs**

| Component | Signal type | Pin / connector | Notes |
|-----------|-------------|-----------------|-------|
| Combination button 1 (SW2) | Digital | SW2 | Active LOW, INPUT_PULLUP |
| Combination button 2 (SW3) | Digital | SW3 | Active LOW, INPUT_PULLUP |
| Combination button 3 (SW4) | Digital | SW4 | Active LOW, INPUT_PULLUP |
| Reset button (SW5) | Digital | SW5 | Active LOW, INPUT_PULLUP |

**Outputs**

| Component | Signal type | Pin / connector | Notes |
|-----------|-------------|-----------------|-------|
| Progress LED 1 (LED2) | Digital | LED2 | On from the first press onward |
| Progress LED 2 (LED3) | Digital | LED3 | On from the second press onward |
| Progress LED 3 (LED4) | Digital | LED4 | On from the third press onward |
| Unlocked LED (LED5) | Digital | LED5 | On only when unlocked |
| Speaker (LS1) | PWM (tone) | LS1 | Entry beep, unlock beep, alarm beep |

**Timing requirements**

- Entry beep: 80 ms per press
- Unlock beep: 300 ms
- Alarm: flashes every 150 ms, beeps 3 times (150 ms on / 150 ms off) then returns to entry
- Main loop: 10 ms (button presses are handled with a brief blocking
  wait for release, not non-blocking timing, so a fast loop is not
  required here the way it was in the traffic light)

### Part 3 — State Identification

| State name | Description |
|------------|-------------|
| `ENTRY_1` | Ready; waiting for the first button press |
| `ENTRY_2` | One press entered; waiting for the second |
| `ENTRY_3` | Two presses entered; waiting for the third |
| `UNLOCKED` | Correct combination entered; lock open |
| `ALARM` | Wrong combination entered; flashing and beeping |

### Part 4 — State Details Table

| State name | Active outputs | Transition event or condition | Next state |
|------------|---------------|-------------------------------|------------|
| `ENTRY_1` | LED2 on | any of SW2/SW3/SW4 pressed | `ENTRY_2` |
| `ENTRY_2` | LED2 + LED3 on | any of SW2/SW3/SW4 pressed | `ENTRY_3` |
| `ENTRY_3` | LED2 + LED3 + LED4 on | any button pressed, sequence correct | `UNLOCKED` |
| `ENTRY_3` | LED2 + LED3 + LED4 on | any button pressed, sequence wrong | `ALARM` |
| `UNLOCKED` | LED5 on | (none in the base activity - see EA1) | — |
| `ALARM` | LED2-LED5 flashing | 3 beeps completed | `ENTRY_1` |
| any except `UNLOCKED` | — | SW5 pressed | `ENTRY_1` |

Note: the combination itself (which specific button is correct at
each step) is only checked once, in `ENTRY_3`, after all three
presses have been recorded - not as each button is pressed. See
Activity 12 GE6 for why this matters.

### Part 5 — State Diagram

```
                any button                any button
  +---------+ -------------> +---------+ -------------> +---------+
  | ENTRY_1 |                | ENTRY_2 |                | ENTRY_3 |
  +---------+ <------------- +---------+ <------------- +---------+
       ^           SW5            ^           SW5          |    |
       |                          |                        |    |
       |                          +------------------------+    |
       |                              SW5                       |
       |                                                        |
       |  correct sequence                       wrong sequence |
       |                                                        v
  +----------+                                            +-------+
  | UNLOCKED | <----------------------------------------- | ALARM |
  +----------+          (not shown: no exit in base        +-------+
                          activity - see EA1)         3 beeps done |
       ^                                                           |
       +-----------------------------------------------------------+
```

SW5 (not shown for every state to keep the diagram readable) returns
any state except `UNLOCKED` to `ENTRY_1`.

### Part 6 — Code Planning

**Initial state:** `ENTRY_1` — set `LED2` on at startup.

**Constants**

| Constant | Value | Purpose |
|----------|-------|---------|
| `STATE_ENTRY_1` | 0 | First entry state identifier |
| `STATE_ENTRY_2` | 1 | Second entry state identifier |
| `STATE_ENTRY_3` | 2 | Third entry state identifier |
| `STATE_UNLOCKED` | 3 | Unlocked state identifier |
| `STATE_ALARM` | 4 | Alarm state identifier |
| `CORRECT_1`, `CORRECT_2`, `CORRECT_3` | 2, 3, 4 | The correct combination |
| `LOOP_DELAY` | 10 ms | Main loop rate |
| `ENTRY_BEEP_FREQ` / `ENTRY_BEEP_MS` | 1500 Hz / 80 ms | Beep per digit entered |
| `UNLOCK_FREQ` / `UNLOCK_BEEP_MS` | 2000 Hz / 300 ms | Access-granted beep |
| `ALARM_FREQ` | 2500 Hz | Alarm beep frequency |
| `ALARM_BEEP_ON` / `ALARM_BEEP_OFF` | 150 ms / 150 ms | Alarm beep pattern |
| `ALARM_BEEP_COUNT` | 3 | Beeps before returning to entry |
| `FLASH_INTERVAL` | 150 ms | Alarm LED flash toggle rate |

**Variables**

| Variable | Type | Initial | Purpose |
|----------|------|---------|---------|
| `state` | int | `STATE_ENTRY_1` | Current state |
| `state_start` | timestamp | `now()` | Time current state began |
| `entered_1`, `entered_2`, `entered_3` | int | 0 | Buttons pressed so far this attempt |
| `last_flash_time` | timestamp | `now()` | Alarm: last LED toggle |
| `flash_on` | bool | `False` | Alarm: current LED flash state |
| `last_beep_time` | timestamp | `now()` | Alarm: last beep toggle |
| `beep_on` | bool | `False` | Alarm: current beep on/off state |
| `alarm_beep_count` | int | 0 | Alarm: beeps completed so far |

**Functions**

| Function | Purpose |
|----------|---------|
| `all_leds_off()` | Turn off LED2-LED5 |
| `enter_state(new_state, time, reason)` | Clear outputs, update state, record time, print diagnostic |
| `read_button()` | Return which of SW2/SW3/SW4 is pressed (or 0) |
| `wait_for_release()` | Block until SW2/SW3/SW4 are all released |

**Main loop structure**

```
loop:
    current_time = now()

    if SW5 pressed and state != UNLOCKED:
        wait for SW5 release
        enter ENTRY_1

    elif state == ENTRY_1:
        pressed = read_button()
        if pressed: record entered_1, beep, wait for release, enter ENTRY_2

    elif state == ENTRY_2:
        pressed = read_button()
        if pressed: record entered_2, beep, wait for release, enter ENTRY_3

    elif state == ENTRY_3:
        pressed = read_button()
        if pressed:
            record entered_3, beep, wait for release
            if entered_1/2/3 match CORRECT_1/2/3: enter UNLOCKED
            else: enter ALARM

    elif state == UNLOCKED:
        pass  # no exit in base activity

    elif state == ALARM:
        flash LEDs if FLASH_INTERVAL elapsed
        toggle beep if its interval elapsed; count completed beeps
        if 3 beeps completed: enter ENTRY_1
```

### Part 7 — Testing Plan

| Starting state | Action | Expected next state | Expected outputs |
|----------------|--------|---------------------|------------------|
| `ENTRY_1` | Press SW2 | `ENTRY_2` | LED2+LED3 on, short beep |
| `ENTRY_2` | Press SW3 | `ENTRY_3` | LED2+LED3+LED4 on, short beep |
| `ENTRY_3` | Press SW4 (correct combination) | `UNLOCKED` | LED5 on, unlock beep |
| `ENTRY_3` | Press SW2 (wrong combination) | `ALARM` | LEDs flashing |
| `ALARM` | Wait for 3 beeps | `ENTRY_1` | LED2 on, all else off |
| `ENTRY_2` | Press SW5 | `ENTRY_1` | LED2 on, all else off |
| `UNLOCKED` | Press SW5 | `UNLOCKED` (no change) | LED5 stays on |

---

*mirobo.tech Microcontroller Core Curriculum — Capstone Preparation Guide*