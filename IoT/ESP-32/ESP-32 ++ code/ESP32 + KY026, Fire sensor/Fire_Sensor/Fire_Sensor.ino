#define FLAME_SENSOR_DO 15  // Digital pin for flame detection
#define FLAME_SENSOR_AO 34  // Analog pin for flame intensity

void setup() {
  pinMode(FLAME_SENSOR_DO, INPUT);  // Set DO as input
  Serial.begin(115200);             // Start serial communication
}

void loop() {
  // Read from the digital output (DO)
  int flameDetected = digitalRead(FLAME_SENSOR_DO);

  // Read the analog output (AO) for flame intensity
  int flameIntensity = analogRead(FLAME_SENSOR_AO);  // Value range: 0-4095

  // Check if flame is detected based on inverted logic
  if (flameDetected == HIGH) {  // High means flame is detected
    Serial.println("Flame detected!"); // Logic adjusted
  } else {
    Serial.println("No flame detected!"); // Logic adjusted
  }

  // Print flame intensity to serial monitor
  Serial.print("Flame Intensity: ");
  Serial.println(flameIntensity);

  delay(500);  // Wait for 500ms before the next reading
}
