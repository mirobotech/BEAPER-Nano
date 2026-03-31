/* =============================================================================
BEAPERNano.h
March 14, 2026

Board header file for the mirobo.tech BEAPER Nano circuit.

This header defines Arduino Nano ESP32's GPIO pins for BEAPER Nano's
on-board circuits and provides simple helper functions to enable
beginners to focus on learning programming concepts more quickly.
(A similar MicroPython board module is also available for BEAPER Nano.)

BEAPER Nano hardware notes:
- Button switches use internal pull-up resistors (so pressed == LOW)
- LEDs and motor driver inputs share I/O pins
- Headers H1-H4 and H5-H8 share I/O pins (so much I/O, too few pins!)
- Analog jumpers on BEAPER Nano must be set to connect sensors to pins:
  - Enviro. position selects sensors Q4, U4, and pots RV1 and RV2
  - Robot position selects floor/line phototransistors Q1, Q2, Q3,
    and voltage divider resistor circuit (VDIV)
==============================================================================*/

#ifndef BEAPERNANO_H
#define BEAPERNANO_H

/* =====================================
 * Arduino Nano ESP32 Module LEDs
 * ====================================*/
// Arduino Nano ESP32 LEDs pre-defined in the Arduino ESP32 boards package.

// LED_BUILTIN (D13)      // On-board LED (shared as SPI SCK pin)
// LED_BLUE               // RGB LED blue element (active-LOW)
// LED_GREEN              // RGB LED green element (active-LOW)
// LED_RED                // RGB LED red element (active-LOW)


/* =====================================
 * LED Pins
 * ====================================*/
// IMPORTANT: LED pins are shared with the motor controller. Using the
// LEDs while the motors are active will affect motor behavior!

const uint8_t LED2 = 4;   // M1A
const uint8_t LED3 = 5;   // M1B
const uint8_t LED4 = 6;   // M2A
const uint8_t LED5 = 7;   // M2B

const uint8_t LEDS[] = {LED2, LED3, LED4, LED5};  // Array of all LED pins
const uint8_t NUM_LEDS = 4;

inline void leds_on()
{
    digitalWrite(LED2, HIGH);
    digitalWrite(LED3, HIGH);
    digitalWrite(LED4, HIGH);
    digitalWrite(LED5, HIGH);
}

inline void leds_off()
{
    digitalWrite(LED2, LOW);
    digitalWrite(LED3, LOW);
    digitalWrite(LED4, LOW);
    digitalWrite(LED5, LOW);
}


/* =====================================
 * Pushbutton Pins (Active LOW)
 * ====================================*/

const uint8_t SW2 = 0;
const uint8_t SW3 = 1;
const uint8_t SW4 = 2;
const uint8_t SW5 = 3;

const uint8_t SWITCHES[] = {SW2, SW3, SW4, SW5};  // Array of all switch pins
const uint8_t NUM_SWITCHES = 4;


/* =====================================
 * Motor Pins
 * ====================================*/
// IMPORTANT: Motor output pins aare shared with the LEDs. Using the LEDs
// while driving the motors will affect motor behaviour!

const uint8_t M1A = 4;    // Left motor terminal A
const uint8_t M1B = 5;    // Left motor terminal B
const uint8_t M2A = 6;    // Right motor terminal A
const uint8_t M2B = 7;    // Right motor terminal B

// Motor helper functions
// Call pinMode() for all motor pins in setup() before using these
// functions. Motor pins share I/O with LED pins, so a single set
// of pinMode() calls covers both LEDs and motors.
//
// Suggested setup() pinMode calls:
//   pinMode(LED2, OUTPUT);   // LED2 / M1A
//   pinMode(LED3, OUTPUT);   // LED3 / M1B
//   pinMode(LED4, OUTPUT);   // LED4 / M2A
//   pinMode(LED5, OUTPUT);   // LED5 / M2B

inline void motors_stop()
{
    digitalWrite(M1A, LOW);
    digitalWrite(M1B, LOW);
    digitalWrite(M2A, LOW);
    digitalWrite(M2B, LOW);
}

inline void left_motor_forward()
{
    digitalWrite(M1A, HIGH);
    digitalWrite(M1B, LOW);
}

inline void left_motor_reverse()
{
    digitalWrite(M1A, LOW);
    digitalWrite(M1B, HIGH);
}

inline void left_motor_stop()
{
    digitalWrite(M1A, LOW);
    digitalWrite(M1B, LOW);
}

inline void right_motor_forward()
{
    digitalWrite(M2A, LOW);
    digitalWrite(M2B, HIGH);  // Opposite of left_motor_forward()
}

inline void right_motor_reverse()
{
    digitalWrite(M2A, HIGH);  // Opposite of left_motor_reverse()
    digitalWrite(M2B, LOW);
}

inline void right_motor_stop()
{
    digitalWrite(M2A, LOW);
    digitalWrite(M2B, LOW);
}


/* =====================================
 * Piezo Beeper Pin
 * ====================================*/

const uint8_t LS1 = 8;    // BEAPER Nano Piezo beeper LS1

inline void beep()
{
    tone(LS1, 1000, 100); // Play a short beep
}

/* =====================================
 * 3.3V I/O Expansion Header Pins
 * ====================================*/
// NOTE: I/O headers H1-H4 are shared between analog, I2C, and 5V output headers H5-H8.

const uint8_t H1 = A4;    // Header H1 (shared with I2C SDA and 5V output header H5)

const uint8_t H2 = A6;    // Header H2 (shared with SONAR TRIG and 5V output header H7)
const uint8_t TRIG = A6;  // Ultrasonic SONAR distance sensor TRIG(ger) output

const uint8_t H3 = A7;    // Header H3 (shared with SONAR ECHO and 5V output header H8)
const uint8_t ECHO = A7;  // Ultrasonic SONAR distance sensor ECHO input

const uint8_t H4 = A5;    // Header H4 (shared with I2C SCL and 5V output header H6)


/* =====================================
 * 5V Output Expansion Header Pins
 * ====================================*/
// NOTE: Designed as Servo outputs, shared with 3.3V I/O headers H1-H4.

const uint8_t H5 = A4;    // H1
const uint8_t H6 = A5;    // H4
const uint8_t H7 = A6;    // H2
const uint8_t H8 = A7;    // H3


/* =====================================
 * SONAR Distance Sensor Functions
 * ====================================*/
 
// Call sonar_setup() once in setup() to configure the SONAR pins.
inline void sonar_setup()
{
    pinMode(TRIG, OUTPUT);
    digitalWrite(TRIG, LOW);
    pinMode(ECHO, INPUT);
}

// sonar_range(max_range) - Returns the distance to the nearest
//     target within max_range in cm (defaults to 1m)
//
// Returns either:
//     distance (cm) - closest target within max_range
//     0             - no target detected within max_range
//     -1            - time-out waiting for ECHO to start
//     -2            - previous ECHO is still in progress

inline float sonar_range(int max_range = 100)
{
    // Return -2 if a previous ECHO pulse is still in progress
    if (digitalRead(ECHO) == HIGH)
        return -2;
 
    // Make a 10 us TRIG pulse to start a range measurement
    digitalWrite(TRIG, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG, LOW);

    // Convert max_range plus 1cm margin to round trip time
    // in microseconds (~29us/cm one way)
    unsigned long max_us = (max_range + 1) * 58;

    // Wait up to 2500us for ECHO to go HIGH after TRIG.
    // (Necessary for 3.3V HC-SR04P/RCWL-9610A SONAR modules.)
    unsigned long start_us = micros();
    while (digitalRead(ECHO) == LOW)
    {
        if (micros() - start_us > 2500)
            return -1;      // ECHO did not start
    }

    // Measure ECHO pulse duration. 
    start_us = micros();
    while (digitalRead(ECHO) == 1)
    {
        if (micros() - start_us > max_us)
        {
            return 0;       // No target within max_range
        }
    }

    // Convert ECHO duration to distance. (~29us/cm one way)
    return (micros() - start_us) / 58.0f;
}


/* =====================================
 * Analog I/O Pins
 * ====================================*/
// IMPORTANT: On-board analog jumpers must be set to select each input.

const uint8_t Q1 = A0;    // Left floor/line sensor phototransistor Q1 (JP1 - Robot)
const uint8_t Q4 = A0;    // Ambient light sensor Q4 (JP1 - Enviro.)
const uint8_t Q2 = A1;    // Left line sensor phototransistor Q2 (JP2 - Robot)
const uint8_t U4 = A1;    // Analog temperature sensor U4 (JP2 - Enviro.)
const uint8_t Q3 = A2;    // Right floor/line sensor phototransistor Q3 (JP3 - Robot)
const uint8_t RV1 = A2;   // Potentiometer RV1 (JP3 - Enviro.)
const uint8_t VDIV = A3;  // Resistor voltage divider (JP4 - Robot)
const uint8_t RV2 = A3;   // Potentiometer RV2 (JP4 - Enviro.)

// NOTE: Arduino Nano ESP32 supports 10-bit (default 0-1023) or
// 12-bit (0-4095) ADC resolution - via analogReadResolution(12)
// in setup(). See intermediate activities for higher resolution use.

// Analog helper functions: these analog helper functions return 10-bit
// (0-1023) values and require modification if analog resolution is changed.

inline int light_level() { return 1023 - analogRead(Q4); }    // Brighter -> higher values (JP1 - Enviro.)
inline int temp_level()  { return analogRead(U4); }           // Warmer -> higher values  (JP2 - Enviro.)
inline int RV1_level()   { return analogRead(RV1); }          // Clockwise -> higher values (JP3 - Enviro.)
inline int RV2_level()   { return analogRead(RV2); }          // Clockwise -> higher values (JP4 - Enviro.)
inline int Q1_level()    { return 1023 - analogRead(Q1); }    // Higher reflectivity -> higher values (JP1 - Robot)
inline int Q2_level()    { return 1023 - analogRead(Q2); }    // Higher reflectivity -> higher values (JP2 - Robot)
inline int Q3_level()    { return 1023 - analogRead(Q3); }    // Higher reflectivity -> higher values (JP3 - Robot)
inline int VDIV_level()  { return analogRead(VDIV); }         // Voltage divider tap (JP4 - Robot)


/* =====================================
 * TFT LCD (SPI Interface) Pins
 * ====================================*/
// NOTE: TFT LCD pins are only relevant when using the optional TFT LCD display.

const uint8_t TFT_DC = 9;   // TFT Data/Command pin
const uint8_t TFT_CS = 10;  // TFT CS pin
const uint8_t TFT_COPI = 11;
const uint8_t TFT_BL = 12;  // TFT backlight control (unused TFT CIPO pin)
const uint8_t TFT_SCK = 13; // (Shared with LED_BUILTIN)

#endif