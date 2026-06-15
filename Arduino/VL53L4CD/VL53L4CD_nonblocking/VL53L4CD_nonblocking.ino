// VL53L4CD_nonblocking.ino
// Polls dataReady() without blocking so that other code (motor control,
// button reading, display updates, etc.) continues to run between sensor
// measurements.

#include <Wire.h>
#include <VL53L4CD.h>

VL53L4CD tof;
VL53L4CD_Result_t result;

void setup() {
  Serial.begin(115200);
  Wire.begin();

  if (!tof.begin()) {
    Serial.println("VL53L4CD not found – check wiring and power!");
    while (1);
  }

  Serial.println("VL53L4CD ready.");
  tof.startRanging();
}

void loop() {
  // --- Sensor: check for a new reading without blocking ---
  if (tof.dataReady()) {
    tof.getResult(result);
    tof.clearInterrupt();   // must be called after every getResult()

    if (result.range_status == 0) {
      // Valid measurement
      Serial.print("Distance: ");
      Serial.print(result.distance_mm);
      Serial.print(" mm  |  sigma: ");
      Serial.print(result.sigma_mm);
      Serial.print(" mm  |  signal: ");
      Serial.print(result.signal_rate_kcps);
      Serial.println(" kcps");

    } else {
      Serial.print("Range status: ");
      Serial.println(result.range_status);
    }
  }

  // --- Other tasks run here every loop iteration ---
  // e.g. read buttons, update motors, refresh a display, blink an LED…
}