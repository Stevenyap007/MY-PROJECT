const int analogPin = 34;  // GPIO pin for AO (analog output)
const int digitalPin = 2;  // GPIO pin for DO (digital output)
int analogValue = 0;
int digitalValue = 0;

void setup() {
  Serial.begin(115200);  // Start serial communication
  pinMode(digitalPin, INPUT);  // Set DO pin as input
  Serial.println("Send 'stop' to stop sending data, 'start' to resume.");
}

void loop() {
  // Read the analog value (detailed moisture level)
  analogValue = analogRead(analogPin);
  Serial.print("Soil Moisture Level (Analog): ");
  Serial.println(analogValue);
  int moisturePercent = map(analogValue, 0, 4095, 100, 0);  // Map to percentage (0-100)
  Serial.print("Soil Moisture Percentage: ");
  Serial.print(moisturePercent);
  Serial.println("%");
  float moisturePercentFormula = 100 - (analogValue * 100.0 / 4095);
  Serial.print("Soil Moisture Formula Percentage: ");
  Serial.print(moisturePercentFormula);
  Serial.println("%");


  // Read the digital value (threshold check)
  digitalValue = digitalRead(digitalPin);
  Serial.print("Soil Moisture Status (Digital): ");
  if (digitalValue == HIGH) {
    Serial.println("Dry");  // Indicates soil is dry
  } else {
    Serial.println("Wet");  // Indicates soil is wet
  }

  Serial.println();
  delay(1000);  // Delay for readability
}
