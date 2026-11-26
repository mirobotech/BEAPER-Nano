/* =============================================================================
BEAPER Nano I/O Test project [BEAPER_Nano_v1_2_IO_Test.ino]
Version: 1.2
Updated: November 24, 2026

BEAPER Nano v1.2 I/O functional test. This program tests:
  - inputs (pushbuttons, ambient light sensor Q4, temperature sensor U4,
    potentiometers RV1 and RV2)
  - outputs (LEDs, RGB LED, piezo speaker)
  - QWIIC/I2C connector (J4)
  - SONAR module (connect a 3.3V HC-SR04P to H2/H3)

Each pushbutton lights its own LED and plays its own note while held:
  SW1 - LED1, note C5, and the Arduino Nano ESP32 on-board LED
  SW2 - LED2, note E5, and the RGB LED red element
  SW3 - LED3, note G5, and the RGB LED green element
  SW4 - LED4, note C6, and the RGB LED blue element

Jumper settings:
  Set JP1-JP4 to Enviro. to select analog input devices Q4, U4, RV1,
  and RV2. If floor sensors and voltage divider resistors are
  installed, jumpers can be moved to Robot to test Q1, Q2, Q3, inputs.
  Testing VDIV requires an external power supply to be attached to
  VDC In inputs on CON1.

See the https://mirobo.tech/beaper webpage for additional BEAPER Nano starter
progams and beginner programming activities.
============================================================================= */

#include <Wire.h>

// BEAPER Nano v1.2 Educational Starter I/O devices
const uint8_t SW1 = 0;
const uint8_t SW2 = 1;
const uint8_t SW3 = 2;
const uint8_t SW4 = 3;

const uint8_t LED1 = 4;   // Also M1A
const uint8_t LED2 = 5;   // Also M1B
const uint8_t LED3 = 6;
const uint8_t LED4 = 7;

const uint8_t LS1 = 8;

// BEAPER Nano optional analog input devices
const uint8_t Q4  = A0;
const uint8_t U4  = A1;
const uint8_t RV1 = A2;
const uint8_t RV2 = A3;

// QWIIC/I2C optional connector J4 (H1 = SDA, H4 = SCL) - handled by Wire.begin()

// SONAR module connections (H2 = TRIG, H3 = ECHO)
const uint8_t TRIG = A6;
const uint8_t ECHO = A7;

// Note frequencies for the C major chord played by SW1-SW4
const unsigned int NOTE_C5 = 523;
const unsigned int NOTE_E5 = 659;
const unsigned int NOTE_G5 = 784;
const unsigned int NOTE_C6 = 1047;

// Pushbutton switch variables
bool SW1_pressed;
bool SW2_pressed;
bool SW3_pressed;
bool SW4_pressed;

unsigned long sensorTimer;

// SONAR range function with maximum range limit and ECHO pin error checking.
// Returns the range of the closest target in cm. The 'maxRange' parameter
// limits the search range to objects no farther than 'maxRange' cm. The
// function returns -1 if a previous ranging operation is still in progress
// or if ECHO never starts, 0 if no target is found within the specified max
// range, or returns the range to the closest target in cm.
// Example application:
//   long rangeCm = sonarRange(100);   // Find closest target within 100 cm
long sonarRange(int maxRange)
{
    // Check if a previous ECHO pulse is still in progress
    if (digitalRead(ECHO) == HIGH)
        return -1;   // ECHO in progress (wait 10ms after ECHO ends before re-triggering)

    // Create TRIG pulse
    digitalWrite(TRIG, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG, LOW);

    // Wait for ECHO to go high. HC-SR04P (3.3V-capable modules, also labelled as
    // RCWL-9610A 2022) delay for approximately 2300us after TRIG pulse ends
    // before ECHO pulse starts.
    unsigned long startUs = micros();
    while (digitalRead(ECHO) == LOW)
    {
        if (micros() - startUs > 2500)
            return -1;   // ECHO didn't start
    }

    // Time ECHO pulse. Set time-out value to max range.
    unsigned long maxUs = (unsigned long)(maxRange + 1) * 58;
    startUs = micros();
    while (digitalRead(ECHO) == HIGH)
    {
        if (micros() - startUs > maxUs)
            return 0;   // No target within maxRange
    }

    // Return range to target in cm
    return (micros() - startUs) / 58;
}

// Scan the QWIIC connector once for any connected I2C device
void i2cScan()
{
    bool found = false;
    Serial.print("I2C devices found: ");
    for (uint8_t address = 1; address < 127; address++)
    {
        Wire.beginTransmission(address);
        if (Wire.endTransmission() == 0)
        {
            if (found)
                Serial.print(", ");
            Serial.print("0x");
            Serial.print(address, HEX);
            found = true;
        }
    }
    if (!found)
        Serial.print("none");
    Serial.println();
}

void setup()
{
    Serial.begin(115200);

    // Built-in Arduino Nano ESP32 LEDs
    pinMode(LED_BUILTIN, OUTPUT);
    pinMode(LED_RED, OUTPUT);
    pinMode(LED_GREEN, OUTPUT);
    pinMode(LED_BLUE, OUTPUT);
    digitalWrite(LED_BUILTIN, LOW);
    digitalWrite(LED_RED, HIGH);    // Active-LOW - start off
    digitalWrite(LED_GREEN, HIGH);
    digitalWrite(LED_BLUE, HIGH);

    // BEAPER Nano v1.2 I/O
    pinMode(SW1, INPUT_PULLUP);
    pinMode(SW2, INPUT_PULLUP);
    pinMode(SW3, INPUT_PULLUP);
    pinMode(SW4, INPUT_PULLUP);
    pinMode(LED1, OUTPUT);
    pinMode(LED2, OUTPUT);
    pinMode(LED3, OUTPUT);
    pinMode(LED4, OUTPUT);
    pinMode(TRIG, OUTPUT);
    digitalWrite(TRIG, LOW);
    pinMode(ECHO, INPUT);

    // Use 16-bit ADC results throughout, matching the MicroPython version
    analogReadResolution(16);

    Wire.begin();

    // Start-up sound and text
    Serial.println("Starting BEAPER Nano");
    tone(LS1, 1000, 100);

    // Scan the QWIIC connector once for any connected I2C device
    i2cScan();

    // Print brief instructions
    Serial.println("SW1 - LED1, note C5, and the module LED");
    Serial.println("SW2 - LED2, note E5, and the RGB LED red element");
    Serial.println("SW3 - LED3, note G5, and the RGB LED green element");
    Serial.println("SW4 - LED4, note C6, and the RGB LED blue element");
    delay(2000);

    sensorTimer = millis();
}

void loop()
{
    // Update pushbutton states
    SW1_pressed = (digitalRead(SW1) == LOW);
    SW2_pressed = (digitalRead(SW2) == LOW);
    SW3_pressed = (digitalRead(SW3) == LOW);
    SW4_pressed = (digitalRead(SW4) == LOW);

    // Light BEAPER and Arduino Nano module LEDs while buttons are held
    digitalWrite(LED1, SW1_pressed ? HIGH : LOW);
    digitalWrite(LED_BUILTIN, SW1_pressed ? HIGH : LOW);
    digitalWrite(LED2, SW2_pressed ? HIGH : LOW);
    digitalWrite(LED_RED, SW2_pressed ? LOW : HIGH);    // Active-Low
    digitalWrite(LED3, SW3_pressed ? HIGH : LOW);
    digitalWrite(LED_GREEN, SW3_pressed ? LOW : HIGH);  // Active-Low
    digitalWrite(LED4, SW4_pressed ? HIGH : LOW);
    digitalWrite(LED_BLUE, SW4_pressed ? LOW : HIGH);   // Active-Low

    // Play the chord note for whichever button is held (checked in order)
    if (SW1_pressed)
        tone(LS1, NOTE_C5);
    else if (SW2_pressed)
        tone(LS1, NOTE_E5);
    else if (SW3_pressed)
        tone(LS1, NOTE_G5);
    else if (SW4_pressed)
        tone(LS1, NOTE_C6);
    else
        noTone(LS1);

    // Update SONAR range and analog inputs every 500ms
    if (millis() - sensorTimer > 500)
    {
        // Reset sensorTimer
        sensorTimer = millis();
        // Get and print SONAR range
        long rangeCm = sonarRange(100);
        Serial.print("Range: ");
        Serial.print(rangeCm);
        Serial.println(" cm");

        // Read and print analog input levels (labelled for either jumper position)
        Serial.print("Q4/Q1 level: ");
        Serial.println(analogRead(Q4));
        Serial.print("U4/Q2 level: ");
        Serial.println(analogRead(U4));
        Serial.print("RV1/Q3 level: ");
        Serial.println(analogRead(RV1));
        Serial.print("RV2/VDIV level: ");
        Serial.println(analogRead(RV2));
        Serial.println();
    }

    // Add a short loop delay
    delay(20);
}