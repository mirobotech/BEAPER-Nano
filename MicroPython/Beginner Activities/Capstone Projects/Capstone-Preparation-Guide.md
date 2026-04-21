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

The worked example at the end shows how the Activity 12 traffic light
controller would look if it had been planned using this template. Read
it alongside your own planning to check that your answers are at the
right level of detail.

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

## Capstone Example — Traffic Light Controller

The following shows how the Activity 12 traffic light program would
look if it had been planned using this template.

### Part 1 — Project Description

A traffic light controller for a single intersection with a left-turn
lane. The light cycles through red, green, and yellow. A car sensor
on the left-turn lane can request an advanced green turn signal at
the start of the green phase. A pedestrian walk button extends the
green phase and shows a walk signal so pedestrians can cross safely.

### Part 2 — Hardware Inventory

**Inputs**

| Component | Signal type | Pin / connector | Notes |
|-----------|-------------|-----------------|-------|
| Car sensor (SW2) | Digital | SW2 | Active LOW, INPUT_PULLUP |
| Walk button (SW5) | Digital | SW5 | Active LOW, INPUT_PULLUP |

**Outputs**

| Component | Signal type | Pin / connector | Notes |
|-----------|-------------|-----------------|-------|
| Left turn LED (LED2) | Digital | LED2 | Flashes during advanced green |
| Green LED (LED3) | Digital | LED3 | On during regular green |
| Yellow LED (LED4) | Digital | LED4 | On during yellow |
| Red LED (LED5) | Digital | LED5 | On during red and advanced green |
| Walk signal (on-board LED) | Digital | LED_BUILTIN | On during extended green |

**Timing requirements**

- Advanced green: 5 000 ms, LED2 flashes at 400 ms toggle interval
- Regular green: 6 000 ms (extended by 4 000 ms if walk requested)
- Yellow: 2 000 ms
- Red: 5 000 ms
- Main loop: 1 ms (needed for accurate timing of all intervals)

### Part 3 — State Identification

| State name | Description |
|------------|-------------|
| `ADV_GREEN` | Left turn signal flashing; cross traffic still stopped (red on) |
| `GREEN` | Straight-through traffic flowing; walk signal on if requested |
| `YELLOW` | All traffic preparing to stop |
| `RED` | All traffic stopped; car and walk requests recorded |

### Part 4 — State Details Table

| State name | Active outputs | Transition event or condition | Next state |
|------------|---------------|-------------------------------|------------|
| `ADV_GREEN` | LED2 flashing, LED5 on | `elapsed >= ADV_GREEN_TIME` | `GREEN` |
| `GREEN` | LED3 on, on-board LED if walk active | `elapsed >= effective_green` | `YELLOW` |
| `YELLOW` | LED4 on | `elapsed >= YELLOW_TIME` | `RED` |
| `RED` | LED5 on | `elapsed >= RED_TIME` and `car_waiting` | `ADV_GREEN` |
| `RED` | LED5 on | `elapsed >= RED_TIME` and not `car_waiting` | `GREEN` |

Note: `effective_green` equals `GREEN_TIME + WALK_EXTENSION` if
`walk_requested` is true at the time of the red-to-green transition,
otherwise `GREEN_TIME`.

### Part 5 — State Diagram

```
    elapsed >= RED_TIME
  +-----+             +-----------+ elapsed >= ADV_GREEN_TIME +-------+
  | RED | ----------> | ADV_GREEN | ------------------------> | GREEN |
  |     | car_waiting +-----------+                           |       |
  |     |                                                     |       |
  |     | --------------------------------------------------> |       |
  +-----+    not car_waiting                                  +-------+
     ^                                                            |
     | elapsed >= YELLOW_TIME          elapsed >= effective_green |
     |                                                            |
  +--------+                                                      |
  | YELLOW | <----------------------------------------------------+
  +--------+
```

Car and walk requests are recorded during `RED` and applied at the
red-to-green transition. The `ADV_GREEN` → `GREEN` transition also
applies a pending walk request.

### Part 6 — Code Planning

**Initial state:** `RED` — set `LED5` on at startup.

**Constants**

| Constant | Value | Purpose |
|----------|-------|---------|
| `STATE_ADV_GREEN` | 0 | Advanced green state identifier |
| `STATE_GREEN` | 1 | Green state identifier |
| `STATE_YELLOW` | 2 | Yellow state identifier |
| `STATE_RED` | 3 | Red state identifier |
| `LOOP_DELAY` | 1 ms | Main loop rate |
| `ADV_GREEN_TIME` | 5 000 ms | Advanced green duration |
| `GREEN_TIME` | 6 000 ms | Base green duration |
| `YELLOW_TIME` | 2 000 ms | Yellow duration |
| `RED_TIME` | 5 000 ms | Red duration |
| `FLASH_INTERVAL` | 400 ms | Advanced green LED toggle rate |
| `WALK_EXTENSION` | 4 000 ms | Extra green time for pedestrians |

**Variables**

| Variable | Type | Initial | Purpose |
|----------|------|---------|---------|
| `state` | int | `STATE_RED` | Current state |
| `state_start` | timestamp | `now()` | Time current state began |
| `last_flash_time` | timestamp | `now()` | Last advanced green LED toggle |
| `flash_on` | bool | `False` | Current flash LED state |
| `car_waiting` | bool | `False` | Car request recorded during red |
| `walk_requested` | bool | `False` | Walk request recorded during red |
| `effective_green` | int | `GREEN_TIME` | Green duration this cycle |

**Functions**

| Function | Purpose |
|----------|---------|
| `all_leds_off()` | Turn off LED2–LED5 and on-board LED |
| `enter_state(new_state, time, reason)` | Clear outputs, update state, record time, print diagnostic |

**Main loop structure**

```
loop:
    current_time = now()
    elapsed = diff(current_time, state_start)

    if state == ADV_GREEN:
        flash LED2 if FLASH_INTERVAL elapsed
        if elapsed >= ADV_GREEN_TIME: enter GREEN

    elif state == GREEN:
        if elapsed >= effective_green: enter YELLOW

    elif state == YELLOW:
        if elapsed >= YELLOW_TIME: enter RED

    elif state == RED:
        record car_waiting if SW2 pressed
        record walk_requested if SW5 pressed
        if elapsed >= RED_TIME:
            if car_waiting: enter ADV_GREEN
            else: enter GREEN
```

### Part 7 — Testing Plan

| Starting state | Action | Expected next state | Expected outputs |
|----------------|--------|---------------------|------------------|
| `RED` | Wait 5 000 ms, no buttons | `GREEN` | LED3 on, LED5 off |
| `RED` | Press SW2, wait 5 000 ms | `ADV_GREEN` | LED2 flashing, LED5 on |
| `ADV_GREEN` | Wait 5 000 ms | `GREEN` | LED3 on, LED5 off |
| `GREEN` | Wait 6 000 ms | `YELLOW` | LED4 on, LED3 off |
| `YELLOW` | Wait 2 000 ms | `RED` | LED5 on, LED4 off |
| `RED` | Press SW5, wait 5 000 ms | `GREEN` (extended) | LED3 on, on-board LED on |
| `RED` | Press SW2 and SW5, wait | `ADV_GREEN` then `GREEN` (extended) | Walk signal after adv. green |

---

*mirobo.tech Microcontroller Core Curriculum — Capstone Preparation Guide*
