# Guided Exploration

Guided exploration (GE) activities and questions highlight the key ideas
introduced in the program. In a classroom, instructors can use them to guide
discussion, demonstration, prediction, and troubleshooting. Independent
learners can use the guided exploration activities as checkpoints to test
their understanding before moving on.

This first beginner activity introduces the basic structure of Arduino
programs, which are also referred to as program sketches. In certain guided
exploration activities, you'll be asked to modify or add code to the starter
program presented above.

The contents of this entire comment block are formatted in Markdown syntax.
Example program code will be presented like this:

**Example code:**
```cpp
digitalWrite(LED2, HIGH);
```

Double-asterisks are Markdown syntax for bold text, so a Markdown editor
would display the words `Example code:` bolded. The three backtick (```)
characters, often followed by a language description like `python` or
`cpp`, are used to format code blocks, making it stand out. They are not
part of the code, so when you use an example just select the text between
the sets of backticks. In this example the code being referenced is the
single line instruction: `digitalWrite(LED2, HIGH);`.

Words shown in single backticks within the guided exploration sections,
like `LED2`, are also code - they show you the exact spelling and
capitalization to use. Are you ready to start exploring? Let's go!

## GE 1 - Comments and program statements

Most computer programs contain both text comments (to help anyone reading the
program understand it) and the actual program statements that the computer will
compile and run.

Single-line comments in Arduino C follow double slashes `//`. The compiler ignores
everything that follows double slashes in a single row of text.

Multi-line comments ignore all of the text between an opening block-comment marker
and a closing block-comment marker, as seen at the very top of this program and in
this section of text.

Look at the starter program. How does the Arduino IDE treat the comments differently
from the actual program code?

## GE 2 - Including the BEAPER Nano header file

The first real statement in this program includes a header file for your BEAPER Nano
circuit named `BEAPERNano.h`:

**Example code:**
```cpp
#include "BEAPERNano.h"
```

The `BEAPERNano.h` header file must be accessible as a tab in the same Arduino
project as this program. If the header file is not accessible when the sketch is
compiled, the sketch will fail to compile, and an error message will be shown in
the messages area below.

The header file contains ordinary Arduino C code that defines BEAPER Nano's I/O
devices and microcontroller pins for you, helping you to start writing programs
more quickly. You can click the `BEAPERNano.h` tab in the Arduino IDE to explore
all of the code it contains.

The header file includes the pin numbers and names of all I/O devices on the
circuit, including `LED2`. This lets program statements, like the ones below, use
the name `LED2` to control its operation instead of us needing to know the pin
number LED2 is connected to.

**Example code:**
```cpp
pinMode(LED2, OUTPUT);
digitalWrite(LED2, HIGH);
```

Let's break these statements down: `LED2` is one of the pin constants defined in
`BEAPERNano.h` and refers to the pin number LED2 connects to. The `pinMode()`
statement configures the LED2 pin as an `OUTPUT`, and the `digitalWrite()`
statement sets its output voltage to either `HIGH` (approximately 3.3V) or `LOW`
(0V). Setting the LED2 pin `HIGH` will turn LED2 on.

All of BEAPER Nano's other LEDs (`LED3` - `LED5`) can be controlled in exactly the
same way. Let's try it.

Add statements to configure LED3 as an output and then turn it on. Run the updated
program to verify that it works as expected.

## GE 3 - Sequential execution

After a program sketch is compiled and uploaded into the microcontroller, it runs
each program statement in the order written.

So, after adding a statement to light LED3 below the existing statement that
lights LED2 in GE 2, LED2 would turn on first, followed by LED3. Though this
happens sequentially, it happens so fast that, to us at least, it looks like both
LEDs turn on simultaneously.

## GE 4 - setup(), loop(), and repeating programs

If all that we wanted the program to do was to turn two LEDs on, it could end after
these two statements have run. In reality, microcontroller programs usually don't
end. Instead, they continue running the task they were designed to do over and over
again in what is called a main program loop.

In Arduino sketches, program statements inside the `setup()` function run once at
power-up, while program statements inside the `loop()` function are repeated
forever. All Arduino programs must contain both `setup()` and `loop()` functions,
and all of the code that is part of `setup()` or `loop()` must be contained within
the curly braces `{ }` that follow either `setup()` or `loop()`.

Would it make sense to move the `digitalWrite()` statement that turns LED2 on into
`loop()`? Why or why not? What would the program be doing if the statement used to
turn LED2 on was moved into `loop()`?

## GE 5 - The required loop() function

Since `loop()` contains no program code, you might think it would be possible to
simply get rid of it. Instead of deleting `loop()`, comment each line of it out
using double slashes, like this. Then, try to compile the program.

**Example code:**
```cpp
// void loop()
// {
//     // Nothing here for now
// }
```

The compiler ignores anything following double slashes, so all of the loop code
will be commented out and ignored. Try to compile the program and describe the
result. Why do you think this is?

What role does this empty `loop()` serve? How might an empty loop be useful to us
later?

## GE 6 - Fast output changes

Let's try to blink LED3 on and off. Replace the contents of the `loop()` function
with the following two statements: one to turn the LED on, followed by a second
one to turn the LED off.

**Example code:**
```cpp
void loop()
{
    digitalWrite(LED3, HIGH);   // LED3 on
    digitalWrite(LED3, LOW);    // LED3 off
}
```

The loop will run each statement once, first turning LED3 on, and then turning
LED3 off. After that, the loop will repeat from the top, turning LED3 on again,
and then off again... forever.

Run the program and observe LED3. Is LED3 on, off, or flashing? What should be
happening? Is it? How could you test your prediction?


# Extension Activities

Extension activities give learners a chance to apply the concepts and ideas
presented in the guided exploration activities in new contexts, or as new
challenges. Instructors may assign selected extensions for practice, enrichment,
or assessment. Independent learners can use them to help solidify understanding
and to apply their skills.

## EA 1 - Turn an LED on, then off

The `setup()` function includes a statement to turn LED2 on. What do you think
will happen if this statement is immediately followed by a second statement to
turn LED2 off?

Try it. Do you see LED2 turning on and then off? Explain what is happening and
why you think this happens.

## EA 2 - Reverse the order

Predict what will happen if the order of the two LED2 statements in EA 1 is
reversed so that LED2 is first turned off, and then turned on.

Try it. Does the state of LED2 match your prediction?

## EA 3 - Create an LED pattern

Create a program that lights a pattern using at least two of the on-board BEAPER
Nano LEDs. Run your program to verify that it works as expected.

## EA 4 - Use the microcontroller module LED

The `BEAPERNano.h` header file also refers to the pin definitions of the Arduino
Nano ESP32 module's on-board LEDs. It does not need to define them because the
Arduino IDE already knows that they are part of the Arduino Nano ESP32 module.

One of the Arduino Nano ESP32's on-board LEDs is called `LED_BUILTIN`. To use it,
first configure it as an output, then turn it on using `digitalWrite()`, exactly
as was done with BEAPER Nano's other LEDs:

**Example code:**
```cpp
pinMode(LED_BUILTIN, OUTPUT);
digitalWrite(LED_BUILTIN, HIGH);
```

Add these statements to your program so that the Arduino Nano ESP32's LED acts as
a status indicator to show you that your program is running. Run the program to
verify that it works.

## EA 5 - Explore the Arduino Nano ESP32 RGB LED

The Arduino Nano ESP32 module also includes a built-in RGB LED. The Arduino IDE
already defines the names `LED_RED`, `LED_GREEN`, and `LED_BLUE` for the red,
green, and blue parts of this LED.

Unlike the BEAPER Nano LEDs used earlier in this activity, the built-in RGB LED is
active-low. That means writing `LOW` turns that colour on, and writing `HIGH`
turns that colour off.

Configure each RGB LED pin as an output, then try turning on one colour at a time:

**Example code:**
```cpp
pinMode(LED_RED, OUTPUT);
pinMode(LED_GREEN, OUTPUT);
pinMode(LED_BLUE, OUTPUT);

digitalWrite(LED_RED, LOW);      // Red on
digitalWrite(LED_GREEN, HIGH);   // Green off
digitalWrite(LED_BLUE, HIGH);    // Blue off
```

Try changing the `HIGH` and `LOW` values to turn on green, blue, or combinations
of colours. What colour do you see when more than one RGB LED element is turned
on?

Before moving on, write `HIGH` to all three RGB LED pins to turn the RGB LED off:

**Example code:**
```cpp
digitalWrite(LED_RED, HIGH);
digitalWrite(LED_GREEN, HIGH);
digitalWrite(LED_BLUE, HIGH);
```

