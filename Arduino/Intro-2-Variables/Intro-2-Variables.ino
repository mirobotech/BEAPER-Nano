/*
Project:  Intro-2-Variables
Activity: mirobo.tech/beaper-nano-intro-2
Updated:  February 18, 2025

This introductory programming activity for the mirobo.tech BEAPER Nano
circuit demonstrates the use of a variable to count button presses and
constant comparisons within conditions to trigger an action when a
limit is reached.
 
Additional program analysis and programming activities demonstrate the
use of Boolean (or bool) variables to store state during successive
program loops, the creation of a two-player rapid-clicker game,
simulation of real-world toggle and multi-function buttons, and
encourage learners to create program code to measure and mitigate
switch contact bounce.

See the https://mirobo.tech/arps webpage for additional ARPS2
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

// Define program constants
const int maxCount = 50;

// Define variables
int SW2State;
int SW3State;
int SW4State;
int SW5State;

int SW2Count = 0;
bool SW2Pressed = false;

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
  SW2State = digitalRead(SW2);
  SW5State = digitalRead(SW5);
  
  // Count SW2 button presses
  if(SW2State == LOW) {
    digitalWrite(LED2,HIGH);
    SW2Count = SW2Count + 1;
  }
  else {
    digitalWrite(LED2,LOW);
  }
  
  // Light LED D3 when the maximum count has been reached
  if(SW2Count >= maxCount) {
    digitalWrite(LED3,HIGH);
  }
  
  // Turn off LED D3 and reset count if SW5 is pressed
  if(SW5State == LOW) {
    digitalWrite(LED3,LOW);
    SW2Count = 0;
  }
  
  delay(10);  // Added delay helps simulators run this program
}

/* Learn More -- Program Analysis Activities

1.  The 'SW2Count' variable is defined as a 16-bit memory location 
    within the microcontroller's RAM by the program declaration:
    
  'int SW2Count = 0;'
   
    What range of numbers can a 16-bit int variable store? What will
    happen if you try to store a number larger than the upper limit
    of an 'int' in the SW2Count variable? 
   
2.  The program statement 'const int maxCount = 50;' defines a program constant
    using the same type of declaration used to define the I/O pins. How does
    the Arduino IDE know that 'SW2' is a hardware I/O pin, and that 'maxCount'
    is a number? Is there any difference between the two declarations that 
    would indicate the two declarations represents different things?

3.  The maxCount constant is used by the statement 'if(SW2Count >= maxCount)'
    to check if the maximum count has been reached. Defining a constant first
    and then using the constant in the program seems like extra work when the
    statement could simply have been written as 'if(SW2Count >= 50)' instead. 
   
    Can you think of any advantages of defining a constant first, and then
    using that definition in the program, instead of just embedding the value
    of the desired constant into the program code? List at least two.
   
4.  This program should light LED D2 every time SW2 is pressed, and light
    LED D3 once the count reaches 50. Try the program, mentally counting how
    many times you have pressed SW2 before LED D3 turns on. Pressing SW5
    will reset the count so you can perform repeated attempts.
   
    Did your count reach 50? Can you describe what the program is doing?
    (Hint: Compare what happens when you press and quickly release the 
    button, with what happens when you press and slowly release the button.)
   
5.  Let's add some debugging code after the second conditional block to help
    us figure out exactly what this program is doing. We can add a new 'if'
    structure to the program to override the LED D3 output if the SW2Count
    variable goes way out of range – let's make it a value that is 10 times
    larger than the count we are expecting. Add the new block of code
    directly below the first SW2Count comparison. Here is what your code
    should look like with the existing 'if' condition plus the new 'if'
    condition added:

  // Light LED D3 when the maximum count has been reached
  if(SW2Count >= maxCount) {
    digitalWrite(LED3,HIGH);
  }
  // Turn off LED D3 if the real count is huge.
  if(SW2Count >= maxCount * 10) {
    digitalWrite(LED3,LOW);
  }

    Now, press and hold pushbutton SW2 for at least 10 seconds while watching
    LED D3. When the value of SW2Count becomes higher than maxCount, LED D3
    should stay lit until it reaches ten times maxCount, and if SW2Count
    exceeds ten times maxCount, LED D3 will turn off. Does the count go that
    high? If it does, can you explain how that could possibly happen while
    SW2 is only being pressed once?
   
6.  One of the fundamental challenges that needs to be planned for when
    programming microcontrollers is that the statements in the loop()
    function run repeatedly (and often very fast). This results in the state
    of any inputs (such as pushbutton SW2 for example) being checked again
    and again, every time the main loop re-runs. As a result, the counter
    variable meant to cound SW2 presses increments for every loop during
    which SW2 remains pressed -- instead of actually counting the number of
    times SW2 has been pressed. Since microcontrollers are very fast, the
    counted value can add up very quickly!
   
    To solve this problem, the program needs to be written to respond to a
    a change of button state from one loop to the next, instead of simply
    responding to the button state every loop as it does now. Doing this
    requires the use of a new variable to store the button state over time.
    The simplest type of variable that is ideally suited for this a Boolean
    (or, bool) variable, designed to store one of two binary values -- in
    this case the values 'false' and 'true'.
    
    Below is a re-written program function using the pre-defined SW2Pressed
    Boolean variable which was pre-defined in the original program's header.
    Replace the first SW2 'if-else' conditional structure with the following
    two new 'if' condition structures:

  // Count SW2 button presses
  if(SW2State == LOW && SW2Pressed == false) {
    digitalWrite(LED2,HIGH);
    SW2Pressed = true;
    SW2Count += 1;
  }

  if(SW2State == HIGH) {
    digitalWrite(LED2,LOW);
    SW2Pressed = false;
  }
        
    The first 'if' condition now logically ANDs both the current button
    state and the SW2Pressed Boolean variable representing the SW2 button's
    past state. In this case, the button's past pressed state must be false
    when the button is pressed in order to count as a new button press. When
    both conditions are met, the SW2Pressed Boolean variable will be set to
    'true' and the SW2Count variable will be incremented using the compound
    operator in the statement 'SW2Count += 1;' (this produces the same result
    as the original SW2Count = SW2Count + 1; statement, while using shorter
    code).

    Notice that even if SW2State is low the next time through the loop, the
    SW2Pressed variable will be true, preventing the same button press from
    being counted again. A second if condition, detecting the release of
    pushbutton SW2, is required to reset the SW2Pressed Boolean variable to
    'false' so that the next legitimate press can be detected.

    Try these new code blocks in your program to verify that each individual
    button press is properly counted.
      
7.  The conditional statement in the first if condition can also be written:

  if(SW2State == LOW && !SW2Pressed) {

    The expression '!SW2Pressed' is read as 'not SW2Pressed', and is equivalent
    to SW2Pressed being false (or *not  true). Similarly, using a Boolean
    variable's name by itself in a conditional statement (eg. SW2Pressed)
    would be equivalent to checking it for being true. Try replacing the first
    if condition in your program with this expression and verify that it works
    as expected.
   
8.  A constant declaration, like the ones used at the top of the program to
    assign I/O pins and set to set maxCount, can also be used to represent a
    pushbutton's state. Doing this can make the program code more readable.

    Add the following constant definitions to the 'Define program constants'
    section of the program header:
 
const int pressed = LOW;
const int notPressed = HIGH;

    Now, instead of comparing the pushbutton state to 'LOW' or 'HIGH', the
    button state can be compared to these newly-named definitions. Try this
    code in your program, and then modify the SW3 reset button code to use
    the same 'pressed' and 'notPressed' definitions.
 
  // Count SW2 button presses
  if(SW2State == pressed && !SW2Pressed) {
    digitalWrite(LED2,HIGH);
    SW2Pressed = true;
    SW2Count += 1;
  }

  if(SW2State == notPressed) {
    digitalWrite(LED2,LOW);
    SW2Pressed = false;
  }
  
9.  Can you create similar constants for the terms 'on' and 'off' so that
    the LEDs in your circuit can be controlled using statements like
    'digitalWrite(LED2,on);' instead of 'digitalWrite(LED2,HIGH);'? Try it!
   
Programming Activities
   
1.  Create a two-player rapid-clicker style game using this program as a
    starting point. The only purpose of the game will be to see which user
    can press a button the fastest, and who will be first to reach the
    maximum count!

    Begin by planning which button the second player will use to play, as
    well as which LEDs to light as they play. Then, duplicate the existing
    variables in the program to make a similar set of variables for the
    second player. (If, for example, the second player will use SW5 to play,
    duplicate players one's SW2Count and SW2Pressed variables to create
    similar SW5count and SW5pressed variables.)
    
    Next, duplicate the if condition structures in the program loop and
    modify them so that they use the variables createdd for the second
    player.

    Decide which LEDs will represent each player, and choose a button to
    clear the players' counts, reset the LEDs and restart the game.

2.  Use your new knowledge of Boolean variables and logical conditions to
    create a program that simulates the operation of a toggle button. Each
    new press of the toggle button must 'toggle' an LED to its opposite state.
    (Toggle buttons are commonly used as push-on, push-off power buttons in
    digital devices, like the button to turn your computer monitor on and off.)
    
    Pressing and holding the toggle button should only cause the LED to
    switch states, or toggle, once instead of rapidly cycling on and off
    continuously. Test your button's action for reliability.
   
3.  A multi-function button can be used to initiate one action when pressed,
    and a second or alternate action when it is held. One way to implement a
    multi-function button is by using a variable that counts loop cycles --
    exactly as this original program did unitentionally!
    
    Make a program implementing a multifunction button that lights one LED
    as soon as a button is pressed, lights a second LED if the button is held
    for more that one second, and turns off both LEDs after the button is
    released.
   
4.  Do your pushbuttons bounce? Switch bounce is the term used to describe
    switch contacts repeatedly closing and opening before settling in their
    final (usually closed) state. Switch bounce in a room's light switch
    would not be a big concern, because it happens so fast that we would
    not notice the lights briefly flashing before staying on. But, switch
    bounce could be an issue in a software toggle button program because
    the fast operating speed of a microcontroller it see each contact
    bounce as a new, separate event. This would result in unpredictable
    actions, and performing multiple actions in response to a single button
    press.
   
    To see if your circuit's pushbuttons have switch bounce, create a 
    program that counts the number of times a pushbutton's contacts close,
    and then display the count on the LEDs. Comment-out the delay(10); 
    statement in the main loop to ensure that short bounce events won't be
    missed. Use a second pushbutton to both reset the count, and to turn off
    the LEDs, so that the test can be repeated. To determine if your
    pushbuttons bounce, try pressing them at various speeds and using
    different amounts of force. Most of the small pushbuttons used in circuits
    such as ARPS2 are very reliable and won't bounce, or might occasionally
    bounce just once. Try each of the pushbuttons on your circuit to check if
    any of them exhibit switch bounce.
   
5.  Did any of your pushbuttons bounce? Typical switch bounces appear as
    multiple switch activations within 20-30ms after switch activation.
    Can you think of a simple software technique that could easily be
    implemented to ignore multiple switch activations within a 20ms span?

    External switches can be connected to the ARPS2 header pins or optical
    floor module I/O pins to check for bounce as well. Try to find a switch
    that exhibits switch bounce and then add your de-bouncing code to the
    bounce counting program you created for the previous assignemnt, above,
    to verify the effectiveness of your de-bouncing code.
*/
