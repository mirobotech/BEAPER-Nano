/*
Project:  BEAPER-Nano-IO-Test
Date:     February 5, 2025
 
Functional test of on-board BEAPER Nano I/O devices.

This program includes a SONAR range function designed to test an
optional 3.3V HC-SR04P ultrasonic distance sensor module plugged
into headers H1-H4, as well as a servo pulse function to use RV1
and RV2 to to control two servos connected to H5 and H6.

The Arduino IDE Serial Monitor displays the SONAR range and analog
input values of the ambient light sensor, temperature sensor and
two potentiometers. Set the jumpers to select the environmental
inputs (labelled Enviro.) on the BEAPER Nano PCB.

See the https://mirobo.tech/beaper webpage for additional BEAPER
Nano programming activities and starter progams.
*/

// Pre-defined Arduino Nano ESP32 LEDS
// LED_BUILTIN (D13)    // Yellow LED (shared with SPI SCK)
// LED_BLUE             // RGB LED blue element (active LOW)
// LED_GREEN            // RGB LED green element (active LOW)
// LED_RED              // RGB LED red element(acive LOW)

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

// BEAPER Nano analog input devices
const int Q1 = A0;      // Left floor sensor phototransistor Q1
const int Q2 = A1;      // Left line sensor phototransistor Q2
const int Q3 = A2;      // Right floor/line sensor phototransistor Q3
const int Q4 = A0;      // Ambient light sensor Q4 (shared with Q1)
const int RV1 = A2;     // Potentiometer RV1 (shared with Q3)
const int RV2 = A3;     // Potentiometer RV2 (shared with VDIV)
const int U4 = A1;      // Analog temperature sensor U4
const int VDIV = A3;    // Voltage divider resistor tap

// BEAPER Nano motor output pins (same I/O pins as LEDs)
const int M1A = 4;      // Motor 1 - output A
const int M1B = 5;      // Motor 1 - output B
const int M2A = 6;      // Motor 2 - output A
const int M2B = 7;      // Motor 2 - output B

// BEAPER Nano 3.3V analog/digital I/O (shared with 5V digital outputs)
const int H1 = 21;      // Header H1 (shared with H5OUT)
const int H2 = 23;      // Header H2 (shared with SONAR TRIG and H7OUT)
const int TRIG = 23;    // SONAR module TRIG pin (same as H2)
const int H3 = 24;      // Header H3 (shared with SONAR ECHO and H8OUT)
const int ECHO = 24;    // SONAR module ECHO pin (same as H3)
const int H4 = 22;      // Header H4 (shared with H6OUT)

// BEAPER Nano 5V digital/servo outputs (shared with 3.3V analog I/O)
const int H5OUT = 21;   // Header H5 (shared with H1)
const int H6OUT = 22;   // Header H6 (shared with H4)
const int H7OUT = 23;   // Header H7 (shared with H2)
const int H8OUT = 24;   // Header H8 (shared with H3)

// Define variables
int SW2State;           // Pushbutton states
int SW3State;
int SW4State;
int SW5State;

int rawLightLevel;      // Analog input levels
int rawTemp;
int posRV1;
int posRV2;

unsigned long servoTimer; // Servo pulse timer in milliseconds
unsigned long sonarTimer; // SONAR range timer in milliseconds

int range_cm;           // SONAR range

void setup() {
  Serial.begin(115200); // Start the serial port at 115200 bps

  // Initialize I/O pin directions/types
  pinMode(SW2, INPUT_PULLUP);
  pinMode(SW3, INPUT_PULLUP);
  pinMode(SW4, INPUT_PULLUP);
  pinMode(SW5, INPUT_PULLUP);
  pinMode(LED2, OUTPUT);
  pinMode(LED3, OUTPUT);
  pinMode(LED4, OUTPUT);
  pinMode(LED5, OUTPUT);
  pinMode(BEEPER, OUTPUT);
  pinMode(H1, OUTPUT);
  pinMode(ECHO, INPUT);
  pinMode(TRIG, OUTPUT);
  pinMode(H4, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_BLUE, OUTPUT);

  servoTimer = millis();  // Set starting timer states
  sonarTimer = millis();

  tone(BEEPER, 4000, 100);  // Say hello and print startup messages

  Serial.println(F("Starting BEAPER Nano"));
  Serial.println(F("SW2 - LED sequence and tones"));
  Serial.println(F("SW3 - light Arduino Nano ESP32 red LED"));
  Serial.println(F("SW4 - light Arduino Nano ESP32 green LED"));
  Serial.println(F("SW5 - light Arduino Nano ESP32 blue LED"));
  delay(1000);
}

void loop() {
  SW2State = digitalRead(SW2);
  SW3State = digitalRead(SW3);
  SW4State = digitalRead(SW4);
  SW5State = digitalRead(SW5);

  // Sequence LEDs while playing tones
  if(SW2State == LOW) {
    digitalWrite(LED2, HIGH);
    tone(BEEPER, 523);
    delay(100);
    digitalWrite(LED3, HIGH);
    tone(BEEPER, 659);
    delay(100);
    digitalWrite(LED4, HIGH);
    tone(BEEPER, 784);
    delay(100);
    digitalWrite(LED5, HIGH);
    tone(BEEPER, 1047);
    delay(100);

    digitalWrite(LED2, LOW);
    tone(BEEPER, 2093);
    delay(100);
    digitalWrite(LED3, LOW);
    tone(BEEPER, 4186);
    delay(100);
    digitalWrite(LED4, LOW);
    tone(BEEPER, 8372);
    delay(100);
    digitalWrite(LED5, LOW);
    noTone(BEEPER);
    delay(100);
  }

  if(SW3State == LOW) {         // Arduino Nano ESP32 red RGB LED
    digitalWrite(LED_RED, LOW);
  }
  else {
    digitalWrite(LED_RED, HIGH);
  }

  if(SW4State == LOW) {         // Arduino Nano ESP32 green RGB LED
    digitalWrite(LED_GREEN, LOW);
  }
  else {
    digitalWrite(LED_GREEN, HIGH);
  }

  if(SW5State == LOW) {         // Arduino Nano ESP32 blue RGB LED
    digitalWrite(LED_BLUE, LOW);
  }
  else {
    digitalWrite(LED_BLUE, HIGH);
  }

  if(millis() - servoTimer > 15) {
    servoTimer = millis();
    posRV1 = analogRead(RV1);
    posRV2 = analogRead(RV2);

    // Update servos from potentiometer positions
    servoPulse(H5OUT, map(posRV1, 0, 4095, 0, 180));
    servoPulse(H6OUT, map(posRV2, 0, 4095, 180, 0));
  }

  if(millis() - sonarTimer > 1000) {
    sonarTimer = millis();

    // Get and print SONAR range
    range = sonarRange(50);
    Serial.print("Range: ");
    Serial.print(range_cm);
    Serial.println("cm");

    // Read and print analog input levels
    rawLightLevel = analogRead(Q4);
    rawTemp = analogRead(U4);

    Serial.print("Light level: ");
    Serial.println(rawLightLevel);
    Serial.print("Temperature: ");
    Serial.println(rawTemp);
    Serial.print("RV1 position: ");
    Serial.println(posRV1);
    Serial.print("RV2 position: ");
    Serial.println(posRV2);
    Serial.println();
  }

}

// Servo pulse funtion creates a single servo pulse on the specified
// servo output pin. The function allows the user to choose both the
// input and output mapping of the servo position to its pulse duration.
// Example application: servoPulse(H5OUT, 45);
// -> creates a 1500us servo pulse on BEAPER Nano header pin H5 (using 90 deg servos).
void servoPulse(int servo, int deg) {
  // int pulse = map(deg, 0, 90, 1000, 2000);  // For 90 degree (standard, 1-2ms) servos
  int pulse = map(deg, 0, 180, 500, 2500);  // For 180 degree servos
  digitalWrite(servo, HIGH);
  delayMicroseconds(pulse);
  digitalWrite(servo, LOW);
}

// SONAR range function with maximum range limit and error checking.
// Returns the distance to the closest target in cm. The 'max' parameter
// limits the search range to objects no farther than 'max' (cm). The
// function returns -1 if previous ranging operation is still in
// progress, 0 if no target is found within the specified max range,
// or the range of the closest target in cm. Example application:
// range = sonarRange(100);  // Find closest target within 100 cm

int sonarRange(int max) {
  if(digitalRead(ECHO) == HIGH) {
    return -1;                // ECHO in progress. Return error code.
  }
  digitalWrite(TRIG, HIGH);   // All clear? Trigger a new SONAR ping
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW);
  // Time ECHO pulse duration. Includes TRIG setup and transmit time
  // in the time-out value.
  unsigned long duration = pulseIn(ECHO, HIGH, max * 58 + 320);
  // Some 3.3V HC-SR04P modules may have much longer setup times than
  // 5V HC-SR04 modules. Use the line below (commenting out the line
  // above) when using a 3.3V HC-SR04P module.
  // unsigned long duration = pulseIn(ECHO, HIGH, max * 58 + 2320);
  if(duration == 0) {
    return 0;                 // Return 0 if no target is within max range
  }
  return (int(duration / 58));	// Return distance to target
}
