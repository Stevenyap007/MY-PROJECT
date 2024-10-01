// Define PIR sensor pin
int pirPin = 14; // Connect PIR sensor OUT to GPIO 14
int pirState = LOW;  // By default, no motion detected

void setup() {
  // Initialize serial communication
  Serial.begin(115200);
  
  // Set PIR sensor pin as input
  pinMode(pirPin, INPUT);
  
  // Start serial monitor
  Serial.println("PIR Sensor is starting...");
}

void loop() {
  // Read the PIR sensor input
  int sensorValue = digitalRead(pirPin);
  
  if (sensorValue == HIGH) {  // Motion detected
    if (pirState == LOW) {
      Serial.println("Motion detected!");
      pirState = HIGH;
    }
  } else {
    if (pirState == HIGH) {
      Serial.println("Motion ended.");
      pirState = LOW;
    }
  }
  delay(1000);  // Delay to debounce the sensor
}

