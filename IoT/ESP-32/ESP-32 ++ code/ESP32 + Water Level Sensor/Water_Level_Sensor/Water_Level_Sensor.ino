#define WATER_SENSOR_PIN 36  // Use GPIO 36 for analog input

void setup() {
  Serial.begin(115200);  // Start serial communication
  pinMode(WATER_SENSOR_PIN, INPUT);  // Set pin as input
}

void loop() {
  int waterLevel = analogRead(WATER_SENSOR_PIN); // Read the sensor value
  float percentage = map(waterLevel, 0, 4095, 0, 100); // Convert to percentage
  Serial.print("Water Level Value: ");
  Serial.println(waterLevel);// Print the value
   
  Serial.print("Water Level: ");
  Serial.print(percentage);
  Serial.println("%");
    
  delay(1000);  // Wait for 1 second
}
