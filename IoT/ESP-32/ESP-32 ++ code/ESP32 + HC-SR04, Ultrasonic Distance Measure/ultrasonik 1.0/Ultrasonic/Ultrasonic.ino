#include <NewPing.h>

#define TRIG_PIN 15  // GPIO pin connected to Trig
#define ECHO_PIN 4   // GPIO pin connected to Echo
#define MAX_DISTANCE 400 // Maximum distance in cm for the sensor

NewPing sonar(TRIG_PIN, ECHO_PIN, MAX_DISTANCE);

void setup() {
  Serial.begin(115200); // Initialize serial communication at 115200 baud rate
}

void loop() {
  delay(50); // Delay between sensor readings
  unsigned int distance = sonar.ping_cm(); // Get distance in cm

  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" cm");

  delay(1000); // Wait for a second before taking the next reading
}
