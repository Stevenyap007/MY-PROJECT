#define SOUND_PIN_AO 34  // Analog pin connected to AO (sound level)
#define SOUND_PIN_DO 23  // Digital pin connected to DO (threshold detection)

void setup() {
  Serial.begin(115200);  // Initialize serial communication
  pinMode(SOUND_PIN_AO, INPUT);  // Set AO as input
  pinMode(SOUND_PIN_DO, INPUT);  // Set DO as input

  Serial.println("Sound Sensor Initialized (Both AO and DO).");
}

void loop() {
  // Read analog value from AO (sound level)
  int soundValue = analogRead(SOUND_PIN_AO);
  Serial.print("Sound Level (AO): ");
  Serial.println(soundValue);  // Print the analog value

  // Read digital value from DO (threshold detection)
  int soundState = digitalRead(SOUND_PIN_DO);
  if (soundState == LOW) {
    Serial.println("Sound Detected! (Above Threshold)");
  } else {
    Serial.println("No Sound Detected. (Below Threshold)");
  }

  delay(100);  // Small delay to stabilize readings
}
