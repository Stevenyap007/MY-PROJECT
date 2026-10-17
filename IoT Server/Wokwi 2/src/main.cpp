#include <DHT.h>

// Define sensor and actuator pins
#define DHTPIN 15
#define DHTTYPE DHT22
#define PIR_PIN 14
#define LIGHT_PIN 13
#define AC_PIN 12

// Initialize DHT sensor
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  // Start the serial monitor log at 115200 baud rate
  Serial.begin(115200);
  dht.begin();
  
  // Set pin modes
  pinMode(PIR_PIN, INPUT);
  pinMode(LIGHT_PIN, OUTPUT);
  pinMode(AC_PIN, OUTPUT);
  
  Serial.println("System Initialized. Starting Local IoT Logging...");
  Serial.println("-------------------------------------------------");
}

void loop() {
  // Read sensor data
  float temp = dht.readTemperature();
  int motion = digitalRead(PIR_PIN);
  
  // 1. Air Conditioner Logic
  if (temp > 26.0) {
    digitalWrite(AC_PIN, HIGH);
    Serial.print("[LOG] AC: ON  | Temp: ");
  } else {
    digitalWrite(AC_PIN, LOW);
    Serial.print("[LOG] AC: OFF | Temp: ");
  }
  Serial.print(temp);
  Serial.print("°C | ");
  
  // 2. Light Logic
  if (motion == HIGH) {
    digitalWrite(LIGHT_PIN, HIGH);
    Serial.println("Light: ON  (Motion Detected)");
  } else {
    digitalWrite(LIGHT_PIN, LOW);
    Serial.println("Light: OFF (No Motion)");
  }
  
  // Poll sensors and update the log every 2 seconds
  delay(2000); 
}