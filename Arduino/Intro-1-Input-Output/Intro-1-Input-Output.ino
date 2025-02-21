/*
Project:  BEAPER-Nano-Intro-1-Input-Output
Activity: mirobo.tech/beaper-nano-intro-1
Updated:  February 20, 2025

This introductory programming activity for the mirobo.tech BEAPER Nano
demonstrates pushbutton input, LED outut, the use of time delay
functions, and simple 'if ' condition structures.

Additional programming analysis activities explore I/O pin behaviour,
compare the operation of 'if' and 'while' structures, and demonstrate 
logical conditional operators. Programming activities introduce the
tone() function to create sounds, and encourage learners to create
software-based simulated start-stop buttons and a turn signal program.

See the https://mirobo.tech/beaper webpage for additional BEAPER Nano
resources, programming activities, and starter programs.
*/

// BEAPER Nano Educational Starter I/O devices
const int SW2 = 0;      // Pushbuttons
const int SW3 = 1;
const int SW4 = 2;
const int SW5 = 3;

const int LED2 = 4;     // LEDs
const int LED3 = 5;
const int LED4 = 6;
const int LED5 = 7;

const int BEEPER = 8;   // Piezo beeper LS1

// Pre-defined Arduino Nano ESP32 LEDS
// LED_BUILTIN (D13)    // Yellow LED (shared with SPI SCK)
// LED_BLUE             // RGB LED blue element (active LOW)
// LED_GREEN            // RGB LED green element (active LOW)
// LED_RED              // RGB LED red element(acive LOW)

// Define variables
int SW2State;
int SW3State;
int SW4State;
int SW5State;

// Setup code configures the I/O pins before running the main loop
void setup() {
  pinMode(SW2,INPUT_PULLUP);
  pinMode(SW3,INPUT_PULLUP);
  pinMode(SW4,INPUT_PULLUP);
  pinMode(SW5,INPUT_PULLUP);
  pinMode(LED2,OUTPUT);
  pinMode(LED3,OUTPUT);
  pinMode(LED4,OUTPUT);
  pinMode(LED5,OUTPUT);
  pinMode(BEEPER,OUTPUT);
  pinMode(LED_BUILTIN,OUTPUT);
  tone(BEEPER,4000,100);  // Say hello!
}

// Main loop code repeats forever
void loop() {
  SW2State = digitalRead(SW2);

  if(SW2State == LOW) {
    digitalWrite(LED2,HIGH);
    delay(100);
    digitalWrite(LED3,HIGH);
    delay(100);
    digitalWrite(LED4,HIGH);
    delay(100);
    digitalWrite(LED5,HIGH);
    delay(100);

    digitalWrite(LED2,LOW);
    delay(100);
    digitalWrite(LED3,LOW);
    delay(100);
    digitalWrite(LED4,LOW);
    delay(100);
    digitalWrite(LED5,LOW);
    delay(100);
  }

  // Add your Program Analysis Activities and Programming Activities code here:

  delay(10);  // Added delay helps simulators run this program
}

/*  Learn More -- Program Analysis Activities

1.  Let's analyze this program! Program analysis is an important skill
    to develop since it helps you to understand a program's operation.
    Connect the Arduino Nano ESP32 in you BEAPER Nano to your computer.
    Press the Upload button at the top of the IDE screen -- it's the
    large right-facing arrow. The IDE will start compiling the program
    sketch and will upload the program to the Arduino when compilation
    finishes. Once the program has been uploaded, press and release
    pushbutton SW2 on your BEAPER Nano circuit while observing its LEDs.

    What happens? How many LEDs flash? How many times does each LED
    flash? Do the LEDs flash again if SW2 is pressed and released a
    second time? What happens if SW2 is held? Does the flashing
    pattern immediately stop when SW2 is released?

    Examine the program and try to match your observations with the
    program's instructions. Explain why all of the LEDs flash on and
    then off after SW2 is pressed, and why you think flashing pattern
    continues -- instead of stopping immediately -- after pushbutton
    SW2 is released.

2.  The first line of code in the program's main 'loop()' function is:

  SW2State = digitalRead(SW2);

    The digitalRead(SW2) function reads the voltage present on the
    pin defined as SW2, and stores the voltage as one of two possible
    states in the SW2State variable. If the voltage on the pin is
    high, the SW2State variable's value will become HIGH, and if the
    voltage is low, its value will be be LOW.

    The next if (conditional) statement:

  if(SW2State == LOW) {

    compares the value stored in the SW2State variable with the value
    LOW. In C, and many other programming languages, two equal signs
    '==' are the conditional check for equality, while a single equal
    sign assigns a value. If the value stored in SW2State is LOW, the
    condition will be true and all of the program statements enclosed
    within the curly braces '{ ... }' below the if statement will run.
    If SW2State is HIGH, the condition is false, and all of the code
    inside the braces will be skipped.

    Whenever the condition is true, the first output statement that
    runs next is:

    digitalWrite(LED2,HIGH);

    This output statement sets the voltage of the pin defined as LED2
    high, enabling current to flow through LED D2 in the circuit.

    A few lines further down in the program, another LED output
    statement sets the LED2 pin low:

    digitalWrite(LED2,LOW);

    Both the input (digitalRead) and output (digitalWrite) statements
    use the same HIGH and LOW values to represent both input and
    output voltages. What real-world voltages do you think the values
    HIGH and LOW correspond to in the Arduino Nano ESP32 used in your
    BEAPER Nano?

3.  Each digitalWrite statement is followed by a short delay:

    delay(100);

    The 'delay()' function causes the microcontroller to pause for the
    amount of time specified in inside its brackets, in milliseconds.
    Try changing the delay time value to 1000ms (1s) and upload the
    program again. Press SW2 while observing the LEDs. Did you notice
    the change? Experiment with delay values between 1 and 10000 and
    observe the effect it has on your program. How low can you go
    before the delay becomes unnoticable?

4.  Understanding a circuit's operation is just as important as
    understanding the program when analyzing and debugging interface
    circuits (hardware components controlled by or interacting with
    software). If you have access to a voltmeter, you can use it to
    confirm voltage measurements at different points in your circuit,
    and specifically to verify the HIGH or LOW values you predicted
    above. To be able to read the LED voltages, you may need to
    lengthen the time delay after the output statement controlling
    the LED being measured.

    First, try measuring the potential across one of the LEDs. Press
    SW2 and note how the voltage changes. Is the voltage what you
    expected it to be? If not, use the schematic to look up the part
    number of the resistor connected to the LED you were measuring,
    and measure the potential across both the resistor and LED. Is
    this closer to the voltage value you expected?
  
    Next, measure the potential across both leads of one of the
    pushbuttons while it is not being pressed. The microcontroller's
    pushbutton input pins have been configured with internal pull-up
    resistors enabled, so a voltage should be present across every
    pushbutton as soon as the program starts running. Press and hold
    the pushbutton and you should observe a change in the voltage
    across the pushbutton. Does this value match your prediction?
    How does voltage across a pressed pushbutton relate to the value
    used by the SW2 input statement?

5.  Let's compare the operation of 'if' and 'while' structures by
    making two new program blocks that will simulate the operation
    of real-world momentary buttons. Copy and paste the program code,
    listed below, into your program between the existing SW2 'if'
    block and the 10ms sleep delay (shown using a comment in the
    program code).

  // Momentary button using an if structure
  SW3State = digitalRead(SW3);
  if(SW3State == LOW) {
      digitalWrite(LED3,HIGH);
  }
  else {
      digitalWrite(LED3,LOW);
  }

  // Momentary button using a while structure
  SW4State = digitalRead(SW4);
  while(SW4State == LOW) {
      digitalWrite(LED4,HIGH);
      SW4State = digitalRead(SW4);
  }
  digitalWrite(LED4,LOW);

    First, press and release pushbutton SW3. LED D3 should only light
    while SW3 is being pressed.
    
    Next, press and release pushbutton SW4. LED D4 should operate
    exactly the same way as LED D3, staying lit only while SW4 is
    being pressed.
    
    While both program switch blocks are designed to effectively
    mimic the operation of real-world momentary pushbuttons,
    implementing them using a sequence of software steps makes them
    behave differently than physical buttons would. To see the
    difference press and hold SW3, and while holding SW3 press and
    release SW4. Do both switches still operate as expected?
    
    Next, try it in the opposite order. Press and hold SW4, and then
    press and release SW3. Do both switches still operate as expected?
    
    Explain the differences in the operation of the 'if' and 'while'
    blocks used to make the momentary button functions. How does each
    affect the program flow -- the steps taken by the microcontroller
    through the main program loop. Which block should be used when
    creating a prgoram that needs to sense both switches
    simultaneously, as if they were wired as parallel switch circuits?

6.  Comment-out the second 'SW4State = digitalRead(SW4);' statement --
    the one inside the while loop -- by adding two slashes '//' at the
    beginning of the line, like this: '//SW4State = digitalRead(SW4);'.
    Re-upload your program and test SW5 again. After that, try testing
    both SW3 and SW4. Do they still work? If the program seems to be
    getting stuck, press and release the SW1 RESET pushbutton on your
    BEAPER Nano to reset the microcontroller and re-start the program.
    Explain what you think is happening and why the microcontroller
    might be operating that way.

7.  Next, let's try nesting if conditions to mimic an operator safety
    circuit for an industrial machine. To prevent operator injury,
    some machines have two, widely-spaced start buttons that a machine
    operator is required to press at the same time in order to
    activate it. The machine will only start if one button *and* the
    other button are pressed simultaneously. Spacing the buttons far
    enough apart requires the machine operator to press one button
    with each hand, ensuring that both hands are safely away from
    the dangerous parts of the machine when it starts.
    
    Replace the momentary button program blocks added above with the
    new program block, below. This program combines two if conditions
    to light LED4 (representing our machine) when both SW3 and
    SW4 are pressed.

  SW3State = digitalRead(SW3);
  SW4State = digitalRead(SW4);

  if(SW3State == LOW) {
    if(SW4State == LOW) {
      digitalWrite(LED4,HIGH);
    }
    else {
      digitalWrite(LED4,LOW);
    }
  }
  else {
    digitalWrite(LED4,LOW);
  }

    Test the code to ensure it works as expected. Does the order of
    button presses matter? Do you think the order of the conditional
    checks in the program matters? Try swapping the conditional input
    checks for SW3 and SW4 and test it again if you are unsure.

8.  As shown in the example above, nesting conditional statements
    does work to ensure the light turns on when both switches are
    pressed. There is an easier and shorter way to accomplish the
    same task by implementing the logical AND conditional operator
    represented by in C by using two ampersands '&&'. This software
    conditional operation is the programming equivalent of an AND
    gate logic circuit. Replace the code added in the previous step
    with this new code block using the logical AND operator:

  SW3State = digitalRead(SW3);
  SW4State = digitalRead(SW4);
  
  if(SW3State == LOW && SW4State == LOW) {
    digitalWrite(LED4,HIGH);
  }
  else {
    digitalWrite(LED4,LOW);
  }

    Run the code and test it to ensure it works as expected. Can you
    think of at least two advantages of using a logical conditional
    operator instead of using nested if structures as was done in the
    previous example?
    
9.  If a logical AND operator can implemented using a conditional
    statement, it seems reasonable to expect that a logical OR 
    operator should also exist. In C language programs, the logical
    OR operator is represented by double vertical bars '||'. Replace
    the double ampersand '&&' with double bars to make your program
    implement a logical OR condition. Your code block should now
    look like this:

  SW3State = digitalRead(SW3);
  SW4State = digitalRead(SW4);
  
  if(SW3State == LOW || SW4State == LOW) {
    digitalWrite(LED4,HIGH);
  }
  else {
    digitalWrite(LED4,LOW);
  }

    Run the code and test it. List the conditions under which LED D4
    turns on. Do these conditions match the truth table of an OR gate
    circuit?

10. The equivalent of the XOR logical operation is inequality -- the
    output will be true only when one input is different, or not
    equal, to the other. Inequality in C programs is represented by
    the '!=' (not equal to) conditional operator. Try this:

  SW3State = digitalRead(SW3);
  SW4State = digitalRead(SW4);
  
  if(SW3State != SW4State) {
    digitalWrite(LED4,HIGH);
  }
  else {
    digitalWrite(LED4,LOW);
  }

    Does it correctly mimic the output of an XOR gate? Can you 
    recreate the XOR operation using the quality '==' operator
    instead of using the inequality '!=' operator, and still produce
    the same output? Try it!

Programming Activities

1.  The 'delay(100);' function pauses the microcontroller for 100
    milliseconds, or 0.1 seconds. Since the delay() function can
    only support whole numbers, a different delay function is provided
    for making delays shorter than 1ms:

    delayMicroseconds()  - pauses for the specified number of microseconds

    Look up the delay() and delayMicroseconds() functions in the
    Arduino reference documentation. What is one problem you might
    run into when using the delay() function to make long delays in
    your program? What delay length should not be exceeded when using
    the delayMicroseconds() function?

2.  Microsecond-length time pulses are too short to be seen using our
    eyes but can be measured using an oscilloscope, or heard as an
    audio tone if they are used to turn the piezo speaker on and off.

    Add the following block of code to your program. The delay between
    each change in the BEEPER pin's output voltage is half of the time
    period of one wave of music note A5, so when SW5 is pressed your
    circuit should play a tone at a frequency of approximately 880 Hz.

  SW5State = digitalRead(SW5);    // Make a tone while SW5 is held
  if(SW5State == LOW) {
    digitalWrite(BEEPER,HIGH);
    delayMicroseconds(568);
    digitalWrite(BEEPER,LOW);
    delayMicroseconds(568);
  }

    If you try to run the program after adding this section, you'll
    find that pressing and holding SW5 will make a buzzing noise
    instead of a musical sounding tone. Can you figure out why?
    
    Did you figure it out? After making the output LOW and adding
    the second 568us delay, the delay(10); statement at the end of
    the program's main loop function adds an additional 10ms of delay
    before the BEEPER pin can change back to HIGH again. This creates
    an extra-long LOW output of 10568us instead of the 568us LOW 
    output the program intended! The simplest way to fix the program
    without deleting the line is to comment-out the 10ms delay with
    two slashes, making it into a single-line comment, as shown:

  // delay(10);

    Run the program again and press SW5. Does it sound more like a
    tone now? Try altering both of the delay values, always keeping
    them the same as you increase or decrease the delay. Does the
    pitch of the tone increase or decrease when the delay values are
    made smaller? Does the opposite happen if the delay values are
    made larger?
 
3.  Arduino has a built-in tone() function that can be used to make a
    specified sound frequency without having to calculate a delay
    time period and to create your own wave by making an output pin
    go high and low as you did above. Replace the code above, with
    this code that produces the same sound using the tone() function:
 
  SW5State = digitalRead(SW5);    // Make a tone when SW5 is pressed
  if(SW5State == LOW) {
    tone(BEEPER, 880);
  }

    The tone function specifies the pin (BEEPER) and frequency (880),
    and can be silenced by pressing the RESET button (SW1) on the
    BEAPER Nano, or in your program by adding a 'noTone(BEEPER);'
    statement. Modify your program using either a second 'if'
    condition or an 'else' condition so that it plays a tone only
    while SW5 is held, and stops playing the tone using the 'noTone'
    function when SW5 is released.

4.  The setup() function includes a tone() function that makes a
    sound on start-up. How is the tone function in the setup function
    different than the one in the example above? What does the third
    parameter control? Hint: you can find out more about any Arduino
    functions in the programming reference at: https://docs.arduino.cc
 
5.  BEAPER Nano's LED circuits use 'active-high' logic, meaning each
    LED turns on when its output pin is set HIGH, or is connected to
    the power supply potential by each pin's output transistor. In
    contrast, the individual elements of the RGB (red, green, blue)
    LED built into the Arduino Nano ESP32 microcontroller are 
    controlled using 'active-low' logic. This means that current flows
    through the LED element when its associated output is made LOW, 
    or connected to ground.

    Each of the Arduino Nano ESP32's built-in LEDs have already been
    pre-defined (their commented-out LED definitions are near the top
    of the program, and have been included in the program to let you
    know their names), but won't be usable until their I/O pins have
    been initialized. Let's add an initialization statement for the 
    blue RGB LED element into the program's setup() function, like
    this:

  pinMode(LED_BLUE, OUTPUT);

    The RGB LED can be made to turn blue when the program starts by
    including a digitalWrite() output statement right in the setup()
    function, below the pinMode() statement that was just added:

  digitalWrite(LED_BLUE, LOW);

    Upload the program to verify that the RGB LED turns blue. Create
    addtional pinMode() statements for both the red and green LED
    elements. Then, experiment with all three elements to determine
    all of the possible colours. To help you figure it out, create a
    chart that lists the colour along with the values of the red,
    green, and blue LED elements to make that colour.

    What values correspond to the RGB LED being off? How many colours
    can the RGB LED produce using only simple HIGH and LOW output
    values for control? (We'll explore how to display far more colours
    than this in a later activity!)
    
6.  Create a program that uses each pushbutton to generate either a
    unique flashing pattern using the LEDs, or to play a series of
    tones from the piezo speaker.
    
    Test each of your flashing or sound patterns to verify that it
    works as expected. Describe what happens when multiple buttons
    are held. Do all of the patterns flash the LEDs, or play the
    tones, at the same time, or does each pattern play in sequence?
    Explain why this is the case.
 
7.  Create a new program that uses individual if structures to
    simulate the operation of 'Start' and 'Stop' buttons for an
    industrial machine. Use SW2 as the Start button to turn LED D5
    (representing the machine) on when it is pressed, and ensure
    that LED D5 stays on even after SW2 has been released. Use SW5
    as the Stop button to turn LED D5 off when it is pressed. Test
    your program to ensure that your simulated machine turns on and
    off as expected.
    
8.  Run the Start-Stop program created in the previous step again,
    and describe what happens when both pushbuttons SW2 and SW5 are
    held. Does LED D5 turn on at all when both buttons are pressed?
    Would this be considered safe behaviour for a machine?
    
    Let's do some additional program analysis to try to determine
    what is actually happening. Watch the brightness of LED D5 when
    both buttons are pressed, and compare it with its brightness if
    just the start button is pressed. If the brightness is different,
    there must be some aspect of the program causing the difference.
    Can you explain what the program is doing that might causing the
    brightness to be different? (Hint: pretend to be the computer
    and simulate each step of the program.)

9.  As you can imagine, an industrial machine that is able to turn
    on even while its Stop button is being pressed represents a
    significant safety hazard to its operators! Use one or more of
    the logical conditional operators introduced in the program
    analysis activities, above, to make the start-stop program
    operate safely. The machine should not be able to turn on at
    all while the Stop button is being pressed. Test your program
    to ensure LED D5 stays off while SW5 is being pressed.

10. Let's say that you're ready to apply your newly-acquired
    microcontroller hardware and programming experience to create
    a turn signal circuit for your bicycle. Assume that you have
    designed a 3D-printed holder that holds an Arduino, a battery
    pack, and up to four LEDs, and that this holder is designed
    to be mounted on the bicycle's seat post. The LEDs will be
    controlled by two momentary pushbuttons mounted on the bicycle's
    handlebars. Plan the best way to implement both easy to use and
    easily visible turn signals, and then write a program that uses
    the LEDs and pushbuttons on your circuit board to simulate their
    operation.

11. Modify the bicycle turn signal program, above, to add one or more
    extra features such as a brake signal, a horn or bell function
    using an unused pushbutton, or add a rapidly flashing visibility
    light that blinks constantly until one of the turn signals is
    activated. Test your program to ensure that each of its functions
    works as expected under all operating conditions (e.g. signalling
    and applying the brakes, or using signalling while using the horn).
*/