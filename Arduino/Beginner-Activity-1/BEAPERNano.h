/* =============================================================================
BEAPERNano.h
v1.0 Jan. 28, 2026

Board header file for the mirobo.tech BEAPER Nano circuit.

This header file pre-defines all of the BEAPER Nano I/O devices allowing
beginners to focus on learning programming concepts more quickly.

BEAPER Nano hardware notes:
- Pushutton swithces use internal pull-up resistors (so pressed == LOW)
- LEDs and motor driver share I/O pins (so much I/O, too few I/O pins!)

more details...
==============================================================================*/

#ifndef BEAPERNANO_H
#define BEAPERNANO_H

// Pre-defined Arduino Nano ESP32 LEDs
// LED_BUILTIN (D13)      // On-board LED (shared as SPI SCK pin)
// LED_BLUE               // RGB LED blue element (active-LOW)
// LED_GREEN              // RGB LED green element (active-LOW)
// LED_RED                // RGB LED red element (active-LOW)

/* =====================================
 * Pushbutton Pins (Active LOW)
 * ====================================*/

const uint8_t SW2 = 0; 
const uint8_t SW3 = 1;
const uint8_t SW4 = 2;
const uint8_t SW5 = 3;


/* =====================================
 * LED Pins
 * ====================================*/
// IMPORTANT: LED pins are shared with the motor controller. Using the
// LEDs while the the motors are active will affect motor behavior!

const uint8_t LED2 = 4;   // M1A
const uint8_t LED3 = 5;   // M1B
const uint8_t LED4 = 6;  // M2A
const uint8_t LED5 = 7;  // M2B


/* =====================================
 * Motor Pins
 * ====================================*/
// BEAPER Nano motor output pin definitions (redefines same I/O pins as LEDs)

const uint8_t M1A = 4;    // Left motor terminal A
const uint8_t M1B = 5;    // Left motor terminal B
const uint8_t M2A = 6;   // Right motor terminal A
const uint8_t M2B = 7;   // Right motor terminal B


/* =====================================
 * Piezo Beeper Pin
 * ====================================*/

const uint8_t BEEPER = 8; // BEAPER Nano Piezo beeper LS1


/* =====================================
 * 3.3V I/O Expansion Header Pins
 * ====================================*/
// NOTE: I/O headers H1 - H4 are shared between analog, I2C, and 5V output headers H5 - H8.

const uint8_t H1 = A4;    // Header H1 (shared with I2C SDA and 5V output header H5)

const uint8_t H2 = A6;    // Header H2 (shared with SONAR TRIG and 5V output header H7)
const uint8_t TRIG = A6;  // Ultrasonic SONAR distance sensor TRIG(ger) output

const uint8_t H3 = A7;    // Header H3 (shared with SONAR ECHO and 5V output header H8)
const uint8_t ECHO = A7;  // Ultrasonic SONAR distance sensor ECHO input

const uint8_t H4 = A5;    // Header H4 (shared with I2C SCL and 5V output header H6)


/* =====================================
 * 5V Output Expansion Header Pins
 * ====================================*/
// NOTE: Designed as Servo outputs, shared with 3.3V I/O headers H1 - H4.

const uint8_t H5 = A4;    // H1
const uint8_t H6 = A5;    // H4
const uint8_t H7 = A6;    // H2
const uint8_t H8 = A7;    // H3


/* =====================================
 * Analog I/O Pins
 * ====================================*/
// IMPORTANT: On-board analog jumpers must be set to select each input.

const uint8_t Q1 = A0;    // Left floor/line sensor phototransistor Q1 (JP1 - Robot)
const uint8_t Q4 = A0;    // Ambient light sensor Q1 (JP1 - Enviro.)
const uint8_t Q2 = A1;    // Left line sensor phototransistor Q2 (JP2 - Robot)
const uint8_t U4 = A1;    // Analog temperature sensor U4 (JP2 - Enviro.)
const uint8_t Q3 = A2;    // Right floor/line sensor phototransistor (JP3 - Robot)
const uint8_t RV1 = A2;   // Potentiometer RV1 (JP3 - Enviro.)
const uint8_t VDIV = A3;  // Resistor voltage divider (JP4 - Robot)
const uint8_t RV2 = A3;   // Potentiometer RV2 (JP4 - Enviro.)


/* =====================================
 * TFT LCD (SPI Interface) Pins
 * ====================================*/

const uint8_t TFT_DC = 9;   // TFT Data/Command pin
const uint8_t TFT_CS = 10;  // TFT CS pin
const uint8_t TFT_COPI = 11;
const uint8_t TFT_BL = 12;  // TFT backlight control (unused TFT CIPO pin)
const uint8_t TFT_SCK = 13; // (Shared with LED_BUILTIN)

#endif
