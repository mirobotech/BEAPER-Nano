/* ================================================================================
BEAPER Nano SONAR Timing Test Program [SONAR-Timing-Test.ino]
May 4, 2026

Platform: mirobo.tech BEAPER Nano circuit (any configuration)
Requires: BEAPERNano.h header file
=================================================================================*/
// IMPORTANT: Make sure that BEAPERNano.h is accessible as a tab in this project.
#include "BEAPERNano.h"   // Define BEAPER Nano I/O devices

// ---- Program Variables ----------------
float sonar_range_cm;
unsigned long start_time_us;
unsigned long trig_time_us;
unsigned long echo_time_us;
unsigned long sonar_time_us;

unsigned long sonar_range_trig(void)
{
    // Make a 10 us TRIG pulse to start a range measurement
    digitalWrite(TRIG, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG, LOW);

    // Wait up to 2500us for ECHO to go HIGH after TRIG.
    // (Necessary for 3.3V HC-SR04P/RCWL-9610A SONAR modules.)
    unsigned long start_us = micros();
    while (digitalRead(ECHO) == LOW)
    {
        if (micros() - start_us > 2500)
            return -1;      // ECHO did not start
    }
    return micros() - start_us;
}

unsigned long sonar_range_echo(void) {
    // Measure ECHO pulse duration. 
    unsigned long start_us = micros();
    while (digitalRead(ECHO) == 1)
    {
        if (micros() - start_us > 5800)  // Set max range to 1m
        {
            return 0;       // No target within max_range
        }
    }

    return micros() - start_us;
}


void setup()
{
    // Configure BEAPER Nano LEDs as outputs
    pinMode(LED2, OUTPUT);
    pinMode(LED3, OUTPUT);
    pinMode(LED4, OUTPUT);
    pinMode(LED5, OUTPUT);

    // Configure BEAPER Nano pushbuttons as inputs
    pinMode(SW2, INPUT_PULLUP);
    pinMode(SW3, INPUT_PULLUP);
    pinMode(SW4, INPUT_PULLUP);
    pinMode(SW5, INPUT_PULLUP);

    Serial.begin(9600);
    delay(2000);                        // Delay for serial port start-up

    sonar_setup();                      // Initialize SONAR module I/O pins
    Serial.println("SONAR module initialized.");
}

 void loop()
{
    trig_time_us = sonar_range_trig();
    echo_time_us = sonar_range_echo();
    sonar_range_cm = echo_time_us / 58.2;
    sonar_time_us = trig_time_us + echo_time_us;

    Serial.print("SONAR range: ");
    Serial.print(sonar_range_cm);
    Serial.println("cm");

    Serial.print("TRIG delay: ");
    Serial.print(int(trig_time_us));
    Serial.println("us");

    Serial.print("Total time: ");
    Serial.print(int(sonar_time_us));
    Serial.println("us");

    Serial.println("");
    delay(200);
}
