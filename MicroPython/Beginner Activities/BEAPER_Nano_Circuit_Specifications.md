# BEAPER Nano Circuit Specifications

# BEAPER Nano Circuit Introduction

BEAPER stands for Beginner Electronics and Programming Educational Robot, and Nano refers to its use of the Arduino Nano ESP332 circuit that it was designed for. 

BEAPER Nano is a fully-integrated beginner circuit designed for teaching programming and robotics using Arduino Nano ESP32. BEAPER Nano can be programmed using MicroPython in the Arduino Lab for MicroPython software or other MicroPython IDEs, or using Arduino C/C++ in the Arduino IDE and other IDEs designed for Arduino programming.

# BEAPER Nano Circuit Hardware

BEAPER Nano includes the following on-board hardware devices:
- Arduino Nano ESP32 module
- 5V low-drop-out voltage regulator (U1)
- reset pushbutton (SW1)
- four user pushbuttons (SW2 - SW5)
- power LED (LED1)
- four user LEDs (LED2 - LED5)
- piezo buzzer (LS1)
- TEPT4400 ambient light sensor (Q4)
- MCP9700A analog temperature sensor (U4)
- SH754410NE motor driver (U3) capable of driving two DC motors in forward and reverse (or one bi-polar stepper motor)
- two analog potentiometers (RV1, RV2)
- two break-away optical sensor modules containing IR LEDs and phototransistor (the left module uses one LED (LED6) and one phototransistor (Q1) to act as a robot floor sensor, the right module can use one LED (LED7) and either one phototransistor (Q3) to act as a matching floor sensor, or two phototransistors (Q2, Q3) to act as a single line sensor)
- a 3.3V I/O expansion header consisting of four parallel 3-pin headers (H1 - H4) allowing an optional HC-SR04 SONAR distance sensor module to be mounted on-board
- a JST-SH I2C/QWIIC connector (J4) allowing external I2C devices to be connected
- four 5V servo/output headers (H5 - H8)
- an SPI header to connect an optional 1.54”, 240x240 pixel TFT LCD display (supports LCDs using ST7789 controllers)

## Arduino Nano ESP32 GPIO Pin Mapping using MicroPython GPIO Pin Naming

GP48 - built-in Arduino Nano ESP32 LED
GP45 - built-in Arduino Nano ESP32 RGB LED blue element (active-low)
GP0 - built-in Arduino Nano ESP32 RGB LED green element (active-low)
GP46 - built-in Arduino Nano ESP32 RGB LED red element (active-low)

GP44 - pushbutton SW2 input using internal pull-up
GP43 - pushbutton SW3 input using internal pull-up
GP5 - pushbutton SW4 input using internal pull-up
GP6 - pushbutton SW5 input using internal pull-up

GP11/SDA - main function as I2C/QWIIC connector J4 SDA and also shared as 3.3V I/O header H1, and 5V servo/output header H5
GP12/SCL - main function as I2C/QUIIC connector J4 SCL and also shared as 3.3V I/O header H4, and 5V servo output header H6
GP13 - main function is 3.3V I/O header H2 (used as TRIG pin when an optional HC-SR04P SONAR module is installed) and also shared as 5V servo output header H7
GP14 - 3.3V I/O header H3 (used as ECHO pin when an optional HC-SR04P SONAR module is installed) and also shared as 5V servo output header H8)

GP7 - LED D2 output, shared with motor driver 1A input (motor driver 1Y output becomes M1A - motor 1 (left motor), terminal A)
GP8 - LED D3 output, shared with motor driver 2A input (motor driver 2Y output becomes M1B - motor 1 (left motor), terminal B)
GP9 - LED D4 output, shared with motor driver 3A input (motor driver 3Y output become M2A - motor 2 (right motor), terminal A)
GP10 - LED D5 output, shared with motor driver 4A input (motor driver 4Y output becomes M2B - motor 2 (right motor), terminal B)

GP17 - piezo buzzer LS1 output

GP18 - LCD/SPI DC pin
GP47 - LCD/SPI CIPO/BL pin (used to control LCD backlight)
GP21 - LCD/SPI CS pin
GP48 - LCD/SPI SCK pin
GP38 - LCD/SPI COPI pin

GP1 - jumper selectable between ambient light sensor Q4 input and left floor sensor phototransistor Q1 input
GP2 -  jumper selectable between analog temperature sensor U4 input and left line sensor phototransistor Q2 input
GP3 - jumper selectable between potentiometer RV1 input and right floor/line sensor phototransistor Q3 input
GP4 - jumper selectable between potentiometer RV2 input and battery voltage divider

## Arduino Nano ESP32 Arduino Pin Mapping using Arduino C/C++ Pin Naming

D13/LED_BUILTIN - built-in Arduino Nano ESP32 LED (also shared as SPI SCK pin)
LED_BLUE - built-in Arduino Nano ESP32 RGB LED blue element (active-low)
LED_GREEN - built-in Arduino Nano ESP32 RGB LED green element (active-low)
LED_RED - built-in Arduino Nano ESP32 RGB LED red element (active-low)

D0 - pushbutton SW2 input using internal pull-up
D1 - pushbutton SW3 input using internal pull-up
D2 - pushbutton SW4 input using internal pull-up
D3 - pushbutton SW5 input using internal pull-up

A4/SDA - main function as I2C/QWIIC connector J4 SDA and also shared as 3.3V I/O header H1, and 5V servo output header H5
A5/SCL - main function as I2C/QUIIC connector J4 SCL and also shared as 3.3V I/O header H4, and 5V servo output header H6
A6 - main function is 3.3V I/O header H2 (used as TRIG pin when an optional HC-SR04P SONAR module is installed) and also shared as 5V servo output header H7
A7 - 3.3V I/O header H3 (used as ECHO pin when an optional HC-SR04P SONAR module is installed) and also shared as 5V servo output header H8)

D4 - LED D2 output, shared with motor driver 1A input (motor driver 1Y output becomes M1A - motor 1 (left motor), terminal A)
D5 - LED D3 output, shared with motor driver 2A input (motor driver 2Y output becomes M1B - motor 1 (left motor), terminal B)
D6 - LED D4 output, shared with motor driver 3A input (motor driver 3Y output become M2A - motor 2 (right motor), terminal A)
D7 - LED D5 output, shared with motor driver 4A input (motor driver 4Y output becomes M2B - motor 2 (right motor), terminal B)

D8 - piezo buzzer LS1 output

D9 - LCD/SPI DC pin
D12 - LCD/SPI CIPO/BL pin (used to control LCD backlight)
D10 - LCD/SPI CS pin
D13 - LCD/SPI SCK pin
D11 - LCD/SPI COPI pin

A0 - jumper selectable between ambient light sensor Q4 input and left floor sensor phototransistor Q1 input
A1 -  jumper selectable between analog temperature sensor U4 input and left line sensor phototransistor Q2 input
A2 - jumper selectable between potentiometer RV1 input and right floor/line sensor phototransistor Q3 input
A3 - jumper selectable between potentiometer RV2 input and battery voltage divider
