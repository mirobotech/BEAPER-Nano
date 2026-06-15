#include <VL53L4CD.h>

// VL53L4CD_simple.ino
// Reads distance once per measurement cycle using the blocking getRange()
// method. Suitable for beginner projects where other tasks do not need to
// run while waiting for the sensor.

#include <Wire.h>
#include <VL53L4CD.h>

VL53L4CD tof;

void setup() {
  Serial.begin(115200);
  delay(2000);
  
  Wire.begin();

  if (!tof.begin()) {
    Serial.println("VL53L4CD not found – check wiring and power!");
    while (1);   // halt
  }

  Serial.println("VL53L4CD ready.");
  tof.startRanging();
}

void loop() {
  int16_t dist = tof.getRange();   // blocks until a result is ready (~50 ms)

  if (dist >= 0) {
    Serial.print(dist);
    Serial.println(" mm");

  } else if (dist == VL53L4CD::ERR_NO_TARGET) {
    Serial.println("No target detected");

  } else if (dist == VL53L4CD::ERR_SIGMA_HIGH) {
    Serial.println("Noisy measurement – try a longer timing budget");

  } else if (dist == VL53L4CD::ERR_WRAP_AROUND) {
    Serial.println("Target may be beyond sensor range (~1300 mm)");

  } else {  // ERR_HARDWARE
    Serial.println("Sensor fault");
  }
}