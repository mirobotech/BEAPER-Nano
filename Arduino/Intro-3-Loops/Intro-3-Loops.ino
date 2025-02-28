/*
Project:  Intro-3-Loops
Activity: mirobo.tech/arps-intro-3
Updated:  February 28, 2025

This introductory programming activity for the mirobo.tech BEAPER Nano
circuit demonstrates the use of both while-loop and for-loop structures
to change the brightness of an LED using PWM (Pulse-Width Modulation).

Additional program analysis and programming activities introduce the
concepts of local and global variables and demonstrate the use of the
analogWrite() function to generate PWM output.

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

// Define program variables
int SW2State;
int SW3State;
int SW4State;
int SW5State;

int LED2Level = 127;  // LED2 brightness (PWM on-time) value
int pwmCounter;       // Counter for PWM generation loop

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

void loop() {
  // Read pushbuttons
  SW3State = digitalRead(SW3);
  SW4State = digitalRead(SW4);

  // Increase brightness
  if(SW4State == LOW && LED2Level < 255) {
    LED2Level += 1;
  }

  // Decrease brightness
  if(SW3State == LOW && LED2Level > 0) {
    LED2Level -= 1;
  }

  // PWM LED2
  pwmCounter = 255;
  while(pwmCounter != 0) {
    if(LED2Level == pwmCounter) {
      digitalWrite(LED2,HIGH);
    }
    pwmCounter --;
    delayMicroseconds(10);
  }
  digitalWrite(LED2,LOW);
}

/* Learn More -- Program Analysis Activities
   
1.  The main loop of this program starts with program statements
    that read two of the circuit's pushbuttons followed by conditional
    statements that modify the value of the LED2Level variable. What
    range of values is the LED2Level variable allowed to be?
   
2.  The main loop() of this program is an infinite, (condition-less)
    loop. Inside the main loop is a while() loop which implements a
    conditional structure -- making it a finite loop -- which is used
    to determine whether or not the loop repeats.

    What condition is being evaluated inside the while() statement's
    brackets? How many times will the code in this inner loop run?
   
3.  What condition is being evaluated by the 'if' condition inside
    the while() loop? With the starting LED2Level value of 127, how
    many times will the loop run before LED D2 turns on?
   
4.  The while() loop turns LED D2 on when the value of LED2Level
    matches the pwmCounter value. As LED2Level changes, LED D2 will
    end up being on for different amounts of time relative to the
    total time taken to execute the loop. Another statement, outside
    of the inner loop, turns LED D2 off before the main loop()
    repeats.
    
    The process of repeatedly turning an output on and off for varying
    proportions of a fixed time period is a technique called PWM
    (Pulse-Width Modulation). If the frequency of pulses is fast
    enough, PWM will cause LED D2 to have appear to have different
    levels of brightness instead of visibly flashing.

    How many different levels of brightness can LED D2 have in this
    program? Calculate the percentage brightness change corresponding
    to a single digit difference in the value of the LED2Level
    variable.
   
5.  Every finite while() loop consists of three parts:

    1) A statement that assigns a value to the loop's conditional
    variable. In this program, the assignment statement is the
    'pwmCounter = 255;' statement just above the while() condition.

    2) A conditional expression that determines whether or not the
    while loop will repeat. The 'while(pwmCounter != 0)' will keep 
    running the loop until pwmCounter is equal to 0. (Unlike 'if'
    statements, which run the code inside their conditional braces
    only once *if* a condition is true, while statements keep
    re-evaluating their conditions and repeating the code inside
    their braces *while* their conditional statements are true.

    3) An expression that updates or modifies the conditional
    variable inside the while() loop. In this program, the statement
    The statement 'pwmCounter --;' uses a decrement operator to
    decrease the value of the loop variable by 1 every time it is
    encountered in the loop. (If the loop variable is never modified,
    the program will appear to get stuck in the loop and will never
    go on to run any other code outside of the loop –- making the
    while structure into an infinite loop!)

    A for() loop is an alternative to a while() loop and incorporates
    the same three parts of a while structure into a single program
    statement. Compare the structure of the while() loop in the
    program above with the for() loop structure, below:

  for(int pwmCounter = 255; pwmCounter != 0; pwmCounter --) {
    if(LED2Level == pwmCounter) {
      digitalWrite(LED2,HIGH);
    }
    delayMicroseconds(10);
  }
  digitalWrite(LED2,LOW);

    The numbers in the for statement's brackets represent the starting
    value, the ending value, and the step between successive values
    of the pwmCounter variable.

    Can you identify at least two advantages of using a for() loop
    structure instead of a while() loop structure? There is one
    potentially important disadvantage of a for() loop, though it
    doesn't impact the for loop used here. Can you think of what
    it might be?

    Replace the entire while90 loop structure in the original
    program with the for() loop structur, above.

    Compile the program and upload it into your circuit to try it
    out. Does it work the same way as the program did when using the
    while() loop?

6.  The pwmCounter variable defined in the program's header is known
    as a 'global' variable because it is accessible from all parts of
    the program. The new for() loop code added above redefines the
    pwmCounter variable as a 'local' variable for use only within
    the for() loop using the for loop's initialization statement:
    
  for(int pwmCounter = 255; pwmCounter != 0; pwmCounter --) {

    While both pwmCounter variables share the same name, they are
    actually different. This means that the contents of the for
    loop's pwmCounter variable won't be accessible outside of the
    for() loop. (As you can imagine, having two different variables
    with the same name can potentially lead to unexpected problems
    in your program and should always be avoided –- it's only being
    done here to prove the point that it really can be a problem!)
    Let's verify that the two pwmCounter variables are actually
    different.

    Add the following line above the for() loop in your program:

  pwmCounter = 128;

    Next, add the following if condition below the for() loop. It
    will be used to indicate whether or not the global pwmCounter
    variable has been modified after running the for() loop:
        
  if(pwmCounter == 128) {
    digitalWrite(LED4,HIGH);
  }
  else {
    digitalWrite(LED4,LOW);
  }
        
    What value should the (local) pwmCounter variable declared in
    the for() loop be when the loop finishes? Should this value
    cause LED D4 to be lit?
    
    Build and upload the program into into your circuit. If LED4 is
    lit, we know that the global pwmCounter variable has not been
    modified by the for() loop. Do you think your prediction of the
    local pwmCounter variable's value was correct?
   
7.  Remove the 'int' declaration from the for() loop's variable
    assignment so that the for() loop initialization statement
    now looks like the one below:
    
   for(pwmCounter = 255; pwmCounter != 0; pwmCounter --) {
    
    Removing the 'int' declaration will cause the for() loop to use
    the existing global pwmCounter variable instead of creating its
    own new local variable.

    Build and upload the program to your circuit and run it again.
    Is the output of LED D4 different now? How would you be able to
    determine if the value of the pwmCounter variable is the value
    you predicted above?
  
8.  The best and safest solution to prevent variable confusion is,
    of course, to use dedicated local variables inside for() loops.
    Doing so always requires the local variable to be initialized
    with a type specifier -- performed by 'int', below:

   for(int pwmCtr = 255; pwmCtr != 0; pwmCtr --) {
    if(LED2Level == pwmCtr) {
      digitalWrite(LED2,HIGH);
    }
    delayMicroseconds(20);
  }
  digitalWrite(LED2,LOW);

    Replace the for() loop code in your program with this new code
    and test it to ensure that it works.

    Next, try removing the 'int' type specifier from the beginning
    of the pwmCtr variable declaration in the for() statement. Try
    to build and upload the program. What happens? Why?
  
9.  Arduino includes an analogWrite() instruction that continuously
    generates PWM outputs on multiple digital output pins. The
    inclusion of an analogWrite() instruction means that all of the
    previous PWM code in this program can be replaced by a single
    analogWrite() statement.
    
    Let's try it! Replace all of the code below the switch input if()
    conditions in the program with these three lines:

   // PWM LED2
  analogWrite(LED2, LED2Level);
  delay(10);

    Upload the program and verify that SW4 and SW5 modify the LED2
    brightness in the same way the program did before.
    
    What purpose does the 'delay(10);' statement serve in this
    program? What do you think will happen if you comment out the
    'delay(10);' statement? Try it and see if you're right!
  
10. All of the work that went into generating and testing our own PWM
    algorithm might seem like wasted effort after realizing that that
    a single instruction can replace all of our code, but that isn't
    necessarily the case. Developing and testing new algorithmd to 
    accomplish specific taskd is an important skill, and this
    exercise hopefully helped you build a better understanding of
    how PWM works. Hopefully, some of the debugging steps introduced
    here will help prepare you to investigate, develop, and verify
    the operation of your new algorithms and functions for different
    or un-supported hardware devices. And in some cases, your code
    developed to implement a specific function may work better than
    pre-made code to do the same thing. This is because pre-created
    functions may have been written with extra code to support
    features or capabilities that may not be needed in our program, 
    so your code will end up being smaller and faster as a result.

    Look up the analogWrite() instruction in the Arduino reference
    documentation. What limitiations does analogWrite() have? Can
    you think of any applications that might benefit from different
    PWM frequencies, different PWM resolution (the number of distinct
    output levels), or more PWM outputs? Could the simple PWM
    technique used in the original program be modified to overcome
    some of the limitations of the built-in analogWrite() function?

    What is one big drawback of using a loop to generate PWM?

Programming Activities
   
1.  Modify your program to control the brightness of two or more LEDs
    simultaneously. Use SW2 and SW5 to increase and decrease the
    brightness of one LED, and SW3 and SW4 to control the brightness
    of a second LED.
  
2.  If you have access to an oscillscope, you can use it to view the
    PWM output waveform being sent to LED D2. Measure the time period
    of the PWM wave and calculate the PWM frequency when using the
    analogWrite() function.

    Compare the frequency of a PWM wave generated using one of the
    original loop functions. How can the PWM frequency of the PWM
    loop functions be changed?
   
3.  A program could use a loop to automatically increase the PWM
    value before sending it into a PWM function. This could be used
    to implement a soft-start for an electric motor, which would
    help to reduce the mechanical stress caused by suddenly applying
    full voltage to the motor.
    
    Create a program that uses a for() loop to slowly increase the
    the brightness of an LED when a buton is pressed (instead of
    requiring the user to hold the button as in the original program).

4.  Add another loop to gradually turn the same LED in the above
    program off using either a second button or re-using the on-button
    as a toggle button.

5.  Make a program that automatically creates a repeated, visual
    'pulse' by continuously brightening and dimming one or more of
    the LEDs.

6.  Try making a 'chirp' or 'pew-pew' sound effect by using a for
    loop to sweep through a range of frequencies from low to high,
    or from high to low, in response to a button press.
*/
