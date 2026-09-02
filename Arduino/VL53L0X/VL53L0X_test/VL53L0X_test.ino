/* ================================================================================
VL53L0X Test Program [VL53L0X-Test.ino]
July 21, 2026

Platform: mirobo.tech BEAPER Nano circuit 
Requires: BEAPERNano.h header file
Requires: Pololu VL53L0X library
=================================================================================*/

#include <Wire.h>
#include <VL53L0X.h>

uint16_t tofRange;
unsigned long start_time_us;
float range_time_ms;

VL53L0X tof;            // Initialize VL53L0X as tof

// Uncomment one of these two lines below to get:
// - higher speed (20ms) at the cost of lower accuracy OR
// - higher accuracy at the cost of lower speed (200ms)

//#define HIGH_SPEED
//#define HIGH_ACCURACY


void setup()
{
  Serial.begin(115200);
  delay(2000);
  Wire.begin();

  tof.setTimeout(500);  // Set read time-out to 500ms
  if (!tof.init())      // Intialize the sensor
  {
    Serial.println("Failed to detect or initialize ToF sensor!");
    while (1);
  }

  tof.startContinuous();

#if defined HIGH_SPEED
  // Reduce timing budget to 20ms (default is about 35 ms)
  tof.setMeasurementTimingBudget(20000);
#elif defined HIGH_ACCURACY
  // Increase timing budget (up to 200ms)
  tof.setMeasurementTimingBudget(200000);
#endif
}

void loop()
{
  start_time_us = micros();

  // Uncomment one of the two lines below to get single or continuous measurements: 
  tofRange = tof.readRangeSingleMillimeters();  // Start and read single measurement
  // tofRange = tof.readRangeContinuousMillimeters();  // Read current measurement

  range_time_ms = (micros() - start_time_us) / 1000.0f;

  Serial.print("Range: ");
  Serial.print(tofRange);
  Serial.println("mm");
  Serial.print("Ranging Time: ");
  Serial.print(range_time_ms);
  Serial.println("ms");
  Serial.println("");

  delay(200);
}