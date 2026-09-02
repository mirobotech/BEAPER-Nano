/* ================================================================================
VL53L4CD Non-blocking Test Program [VL53L4CD_nonblocking.ino]
July 21, 2026

Polls dataReady() without blocking so that other code (motor control, button
eading, display updates, etc.) continues to run between sensor measurements.

Platform: mirobo.tech BEAPER Nano circuit 
Requires: BEAPERNano.h header file
Requires: mirobo VL53L4CD library
=================================================================================*/

#include <Wire.h>
#include <VL53L4CD.h>

VL53L4CD tof;  // Initialize VL53L4CD as tof

VL53L4CD_Result_t result;  // Result data array

void setup() {
  Serial.begin(115200);
  delay(2000);

  Wire.begin();

  if (!tof.begin()) {
    Serial.println("VL53L4CD not found - check wiring and power!");
    while (1);  // halt
  }

  Serial.println("VL53L4CD ready.");

  // Optionally set range timing budget from 10ms (faster, less accurate) to 200ms.
  // The default timing budget is 50ms.
  // tof.setRangeTiming(20);

  tof.startRanging();
}

void loop() {
  // Check for a new reading without blocking
  if (tof.dataReady()) {
    tof.getResult(result);  // Get result data
    tof.clearInterrupt();   // Interrupt must be cleared after every getResult()

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