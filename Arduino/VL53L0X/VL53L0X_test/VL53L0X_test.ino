/* ================================================================================
VL53L0X Test Program [VL53L0X-Test.ino]
May 6, 2026

Platform: mirobo.tech BEAPER Nano circuit 
Requires: BEAPERNano.h header file
Requires: VL53L0X_mod library 
=================================================================================*/

#include <Wire.h>
#include <VL53L0X_mod.h>

const uint32_t RANGE_PERIOD = 200;  // Ranging period in ms (doesn't work)
uint16_t tofRange;
unsigned long start_time_us;
unsigned long range_time_us;

VL53L0X_mod tof;        // Set up tof sensor instance

void setup()
{
  Serial.begin(9600);
  Wire.begin();

  tof.setTimeout(500);  // Set read time-out to 500ms
  if (!tof.init())      // Intialize the sensor
  {
    Serial.println("Failed to detect or initialize ToF sensor!");
    while (1);
  }

  tof.startContinuous(RANGE_PERIOD);  // Start continuous sensor readings
  start_time_us = micros();
}

void loop()
{
  // Singe conversion
  start_time_us = micros();
  tofRange = tof.readRangeSingleMillimeters();
  range_time_us = micros() - start_time_us;

  // Continuous conversion
  /*
  if(tof.readRangeNoBlocking(tofRange)){
    range_time_us = micros() - start_time_us;
    start_time_us = micros();
  }
  */
  
  Serial.print("Range: ");
  Serial.println(tofRange);
  Serial.print("Range Time: ");
  Serial.println(range_time_us);
  Serial.println("");
  delay(100);

}