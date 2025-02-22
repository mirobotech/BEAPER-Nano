/*
Project:  Intro-2-Variables
Activity: mirobo.tech/beaper-nano-intro-2
Updated:  February 21, 2025

This introductory programming activity for the mirobo.tech BEAPER Nano
circuit demonstrates the use of a variable to count button presses and
comparisons between constants and varaibles to trigger an action when
a limit is reached.
 
Additional program analysis and programming activities demonstrate the
use of Boolean (or bool) variables to store state during successive
program loops, the creation of a two-player rapid-clicker game,
simulation of real-world toggle and multi-function buttons, and
the investigation and mitigation of switch contact bounce.

See the https://mirobo.tech/beaper webpage for additional BEAPER Nano
programming activities and starter progams.
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

// Define program constants
const int maxCount = 50;

// Define program variables
int SW2State;
int SW3State;
int SW4State;
int SW5State;

int SW3Count = 0;
bool SW3Pressed = false;

// Setup code runs once to configure I/O pins before running the main loop
void setup(void) {
  pinMode(SW2, INPUT_PULLUP);
  pinMode(SW3, INPUT_PULLUP);
  pinMode(SW4, INPUT_PULLUP);
  pinMode(SW5, INPUT_PULLUP);
  pinMode(LED2, OUTPUT);
  pinMode(LED3, OUTPUT);
  pinMode(LED4, OUTPUT);
  pinMode(LED5, OUTPUT);
  pinMode(BEEPER, OUTPUT);
  tone(BEEPER,4000,100);  // Say hello!
}

// Main loop code repeats forever
void loop() {
  SW3State = digitalRead(SW3);
  SW5State = digitalRead(SW5);
  
  // Count SW3 button presses
  if(SW3State == LOW) {
    digitalWrite(LED2,HIGH);
    SW3Count = SW3Count + 1;
  }
  else {
    digitalWrite(LED2,LOW);
  }
  
  // Light LED D3 when the maximum count has been reached
  if(SW3Count >= maxCount) {
    digitalWrite(LED3,HIGH);
  }
  
  // Turn off LED D3 and reset count if SW5 is pressed
  if(SW5State == LOW) {
    digitalWrite(LED3,LOW);
    SW3Count = 0;
  }
  
  delay(10);  // Limit the loop cycle rate
}

/* Learn More -- Program Analysis Activities

1.  The 'SW3Count' variable is defined as a 16-bit memory location 
    within the microcontroller's RAM by the program declaration:
    
  int SW3Count = 0;
   
    What range of numbers can a 16-bit int variable? What will
    happen if you try to store a number larger than the upper limit
    of an 'int' in the SW3Count variable?
   
2.  The program statement 'const int maxCount = 50;' defines a program
    constant using the exact same type of declaration as was used to
    define the microcontroller's I/O pins. How do you think the
    Arduino IDE knows that 'SW3' is a hardware I/O pin, and that
    'maxCount' is a number? There doesn't seem to be any real
    difference betwee the two declarations, so what else could lead
    to SW3 and maxCount being interpreted differently?

3.  The maxCount constant is at the start of an if condition:

  if(SW3Count >= maxCount) {

    The condition compares the value of the SW3Count variable with
    the maxCount constant to check if a limit has been reached.
    
    Defining a constant to be used here seems like extra work when
    the conditional statement could simply have been written as:

  if(SW3Count >= 50) {
  
    Can you think of any advantages of defining and using the maxCount
    constant instead of simply embedding the number 50 into the
    condition? List at least two advantages.
   
4.  At first glance, it seems that this program should light LED D2
    and increment the SW3Count variable every time that SW3 is
    pressed, but that's not the case. 

    Upload the program and run it, mentally counting how many times
    you pressed SW3 until LED D3 turns on. The count, and LED D3, can
    be reset by pressing SW5 so you can try it multiple times.

    Did the count reach 50? If not, can you describe why, or what
    might be happening in the program to make it mis-count? You may
    be able to gain some insight into what might be happeing by
    pressing and quickly releasing SW3 during one attempt to reach
    50, clearing the count using SW5, and then repeating the attempt
    by pressing and slowly releasing SW3.
   
5.  It's okay if you haven't identified any obvious problems with the
    program yet. We can add some debugging code that might help in
    discovering the nature of the problem. It seems like the program
    is counting too quickly. To check, let's another condition to
    turn LED D3 off if the count get very large, say ten times bigger
    than expected. We'll add this new condition right after the 
    existing condition that turns LED D3 on, like this:

  // Light LED D3 when the maximum count has been reached
  if(SW3Count >= maxCount) {
    digitalWrite(LED3,HIGH);
  }
  // Turn off LED D3 if the real count is very large
  if(SW3Count >= maxCount * 10) {
    digitalWrite(LED3,LOW);
  }

    Now, press and hold pushbutton SW3 for at least 10 seconds while
    watching LED D3. LED D3 should stay off until the value of the
    SW3Count variable becomes higher than maxCount. If LED D3 turns
    on, it should stay on until the value of SW3Count becomes ten
    times higher than maxCount. If LED D3 goes off while still holding
    SW3, the SW3Count must be at least ten times the maxCount value. 
    
    If LED D3 does that, can you explain how the count could go that
    high while SW3 was only pressed once?
   
6.  One of the fundamental challenges when creating programs that run
    inside a main program loop is separating input events from input
    state. Since the state of SW3 is sensed every cycle through the
    main loop() function, reading its state as LOW simply means that
    the button happened to be pressed during the current loop cycle.
    Since humans are slow, and microcontrollers can run through a
    simple loop like this very fast, the button will likely be read
    as pressed for many cycles through the loop. This explains why
    SW3Count quickly exceeds maxCount.

    To solve this problem, the program cannot simply read the state
    of the switch and assume that a LOW input is a new button press.
    Instead, the program has to identify the change from a HIGH to
    a LOW input during sucessive loops, as it's this *change* in state
    that is the only reliable indicator of a new button press having
    occurred.

    To do this, a new variable is required to store the state of the
    button from the previous cycle through the loop. The simplest type
    of variable, and one that is ideally suited for this, is a Boolean
    (or, bool) variable. Boolean variables store one of two binary 
    alues -- in the C programming language, the values are represented
    by the words 'false' and 'true'.
    
    Below is a re-written input function incorporating the SW3Pressed
    Boolean variable that has been pre-defined in the header section
    of the program. Replace the first SW3 'if-else' conditional
    structure with the following two new 'if' condition structures:

  // Count SW3 button presses
  if(SW3State == LOW && SW3Pressed == false) {
    digitalWrite(LED2,HIGH);
    SW3Pressed = true;
    SW3Count += 1;
  }

  if(SW3State == HIGH) {
    digitalWrite(LED2,LOW);
    SW3Pressed = false;
  }
        
    The first 'if' condition now logically ANDs both the current
    button state and the SW3Pressed Boolean variable representing
    the button's previous state. Using this logic, the button must
    currently be pressed and it's previous state must be false in
    order to count as a new button press. When both conditions are 
    met, LED D2 will light, the SW3Pressed Boolean variable will be
    set to 'true', and the SW3Count variable will be incremented
    by 1 using the compound operator in the statement 'SW3Count += 1;'
    (this produces the same result using less code than the original 
    'SW3Count = SW3Count + 1;' statement).

    Notice that even if SW3State is still LOW the next time through
    the main loop, the SW3Pressed variable being 'true' will prevent
    the same button press from being counted more than once. A second
    if condition is used to reset the SW3Pressed Boolean variable to
    'false' when the switch has been released. 

    Try these new code blocks in your program and verify that each
    individual button press is now properly counted.
      
7.  The conditional statement in the first if condition can also be
    written:

  if(SW3State == LOW && !SW3Pressed) {

    The expression '!SW3Pressed' is read as 'not SW3Pressed', and is
    equivalent to SW3Pressed being false (or *not* true). Similarly,
    using the SW3Pressed Boolean variable's name by itself is
    equivalent to it being true. Try replacing the first if condition
    in your program with this expression and verify that it works as
    expected.
   
8.  Constant declarations, like those used at the top of the program
    to assign I/O pins and set to set maxCount, can also be used to
    represent a pushbutton's state. Doing this can make the program
    code more easily readable.

    Add the following constant definitions to the 'Define program
    constants' section of the program header:
 
const int pressed = LOW;
const int notPressed = HIGH;

    Now, instead of comparing the pushbutton state to 'LOW' or 'HIGH',
    the button state can be compared to one of these newly-named
    definitions. Try the following code in your program, and then
    modify the SW5 reset button code to use the same 'pressed' and
    'notPressed' definitions.
 
  // Count SW3 button presses
  if(SW3State == pressed && !SW3Pressed) {
    digitalWrite(LED2,HIGH);
    SW3Pressed = true;
    SW3Count += 1;
  }

  if(SW3State == notPressed) {
    digitalWrite(LED2,LOW);
    SW3Pressed = false;
  }
  
9.  Can you create similar constant terms 'on' and 'off' and use them
    to control the LEDs in your circuit? For example, you could write
    'digitalWrite(LED2,on);' instead of 'digitalWrite(LED2,HIGH);'.

    When might it not be a good idea to use 'on' or 'off' instead of
    HIGH or LOW?
   
Programming Activities
   
1.  Create a two-player rapid-clicker style game using this program
    as a starting point. The only purpose of the game will be to see
    which player can press a button the fastest and become the first
    player to reach the maximum count and win the game!

    Use SW4 for the second player, and light LED D5 when their button
    is pressed. Light LED D4 to show when the second player's count
    equals the maxCount.
    
    Start by duplicating the existing program variables to create a
    similar set for the second player. Next, create copies of the
    if condition structures for the second player and modify them to
    use the variables created for the second player. Finally, modify
    SW5 to reset the counts and LEDs for both players.

2.  When two closely-matched players are playing the rapid-clicker
    game it might be hard to tell which player hit the maxCount 
    value first. Use your knowledge of Boolean variables to prevent
    any more presses from increasing the player counts once one
    player has achieved the maximum count.

3.  Use a Boolean variable to create a program that simulates the
    operation of a toggle button. Each new press of the toggle button
    must 'toggle' an LED to its opposite state. (Toggle buttons are
    commonly used as push-on, push-off power buttons in digital
    devices, like the power button that turns a computer monitor on
    and off.)
    
    Pressing and holding the toggle button should only cause the LED
    to switch states, or toggle, once -- and not rapidly cycle on and
    off continuously. Test your button's action for reliability.
   
4.  A multifunction button can be used to initiate one action when
    pressed, and a second or alternate action when it is held for
    a certain length of time. One way to implement a multi-function
    button is by using a variable that counts timed program loops --
    exactly as this program did initially (and unitentionally)!
    
    Create a program that implements a multifunction button to light
    one LED as soon as a button is pressed, and lights a second LED
    if the button is held for more that one second. Have both LEDs
    turn off when the button is released.
   
5.  Do your pushbuttons bounce? Switch bounce is the term used to
    describe switch contacts repeatedly closing and opening before
    settling in their final (closed) state. Switch bounce in a room's
    light switch might not be a big concern because it happens so
    fast that we would not notice the lights briefly flickering
    before staying on. But, switch bounce could be an issue in a
    software button program because a microcontroller's fast operating
    speed lets it see each contact closure as a new, separate event.
    Imagine if a power button set up as a toggle button bounced and
    each press had between 1 and 4 contact closures. The device would
    not be able to turn on or off reliably.
   
    To determine if your circuit's pushbuttons exhibit switch bounce,
    create a program that counts the number of times a pushbutton's
    contacts close, and then displays the count on the LEDs. Comment-
    out the delay(10); statement in the main loop to ensure that
    short bounce events won't be missed. Use a second pushbutton to
    both reset the count, and to turn off the LEDs, so that the test
    can be repeated.
   
6.  Did any of your pushbuttons bounce? Typical switch bounces appear
    as multiple contact closures within 20-30ms after the initial 
    switch activation. Can you think of a simple software technique
    that could easily be implemented to ignore multiple switch
    activations within a 20ms span?

    External switches can be connected to the expansion header pins
    to check them for bounce as well. Try to find a switch that
    exhibits switch bounce and then add your de-bouncing code to the
    bounce counting program you created in the previous step to
    verify its effectiveness.
*/
