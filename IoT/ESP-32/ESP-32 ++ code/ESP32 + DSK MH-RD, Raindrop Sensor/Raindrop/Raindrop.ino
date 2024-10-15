int rainAnalogPin = 34;  // A0 pin connected to GPIO34
int rainDigitalPin = 35;  // D0 pin connected to GPIO35

void setup() {
  Serial.begin(115200);  // Start serial communication
  pinMode(rainDigitalPin, INPUT);  // Set D0 as input
}

void loop() {
  // Reading the rain intensity from the analog pin
  int rainIntensity = analogRead(rainAnalogPin);  // Range 0-4095 for ESP32
  // Reading the rain detection status from the digital pin
  int rainDetected = digitalRead(rainDigitalPin);

  // Print rain intensity
  Serial.print("Raindrop Sensor Analog Value (Intensity): ");
  Serial.println(rainIntensity);

  // Print rain detection status
  if (rainDetected == LOW) {
    Serial.print(rainDetected);
    Serial.println("Rain detected (Digital Output: LOW)");
  } else {
    Serial.print(rainDetected);
    Serial.println("No rain (Digital Output: HIGH)");
  }

  // Wait for half a second before the next reading
  delay(500);
}
