#include "DHT.h"

#define DHTPIN 4      // Pin where the DHT11 is connected (change this if you used a different GPIO)
#define DHTTYPE DHT11 // DHT 11

DHT dht(DHTPIN, DHTTYPE);

void setup() {
    Serial.begin(9600); // Start the Serial communication
    dht.begin();        // Initialize the DHT11 sensor
}

void loop() {
    // Wait a few seconds between measurements
    delay(2000);
    
    // Read temperature as Celsius
    float t = dht.readTemperature();
    // Read humidity
    float h = dht.readHumidity();
    
    // Check if any reads failed and exit early (to try again).
    if (isnan(t) || isnan(h)) {
        Serial.println("Failed to read from DHT sensor!");
        return;
    }
    
    // Print the results to the Serial Monitor
    Serial.print("Temperature: ");
    Serial.print(t);
    Serial.print(" °C, Humidity: ");
    Serial.print(h);
    Serial.println(" %");
}
