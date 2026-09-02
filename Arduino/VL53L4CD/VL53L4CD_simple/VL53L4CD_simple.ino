/* ================================================================================
VL53L4CD Simple One-shot Test Program [VL53L4CD_simple.ino]
July 21, 2026

Reads range once per measurement cycle using the blocking getRange() method.
Suitable for simple projects where other tasks do not need to run while waiting
for a distance measurement. 

Platform: mirobo.tech BEAPER Nano circuit 
Requires: BEAPERNano.h header file
Requires: mirobo VL53L4CD library
=================================================================================*/

#include <Wire.h>
#include <VL53L4CD.h>

unsigned long start_time_us;
float range_time_ms;

VL53L4CD tof;  // Initialize VL53L4CD as tof

void setup() {
  Serial.begin(115200);
  delay(2000);
  
  Wire.begin();

  if (!tof.begin()) {
    Serial.println("VL53L4CD not found - check wiring and power!");
    while (1);   // halt
  }

  Serial.println("VL53L4CD ready.");

  // Optionally set range timing budget from 10ms (faster, less accurate) to 200ms.
  // The default timing budget is 50ms.
  // tof.setRangeTiming(20);

  tof.startRanging();
}

void loop() {
  start_time_us = micros();
  int16_t dist = tof.getRange();   // Get range - blocks until result is ready (~50 ms)
  range_time_ms = (micros() - start_time_us) / 1000.0f;

  if (dist >= 0) {
    Serial.print("Range: ");
    Serial.print(dist);
    Serial.println(" mm");

  } else if (dist == VL53L4CD::ERR_NO_TARGET) {
    Serial.println("No target detected");

  } else if (dist == VL53L4CD::ERR_SIGMA_HIGH) {
    Serial.println("Noisy measurement - try a longer timing budget");

  } else if (dist == VL53L4CD::ERR_WRAP_AROUND) {
    Serial.println("Target may be beyond sensor range (~1300 mm)");

  } else {  // ERR_HARDWARE
    Serial.println("Sensor fault");
  }

  Serial.print("Ranging Time: ");
  Serial.print(range_time_ms);
  Serial.println("ms");
  Serial.println("");

  delay(100);
}