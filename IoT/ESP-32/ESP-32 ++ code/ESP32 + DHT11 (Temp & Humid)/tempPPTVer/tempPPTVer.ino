#include "DHT.h"

#define DHTPIN 4      // Pin where the DHT11 is connected
#define DHTTYPE DHT11 // DHT 11

DHT dht(DHTPIN, DHTTYPE);

void setup() {
    Serial.begin(9600);
    Serial.println();
    Serial.println("Status\tHumidity (%)\tTemperature (C)\t(F)");
    dht.begin(); // Initialize the DHT sensor
}

void loop() {
    delay(2000); // Wait a few seconds between measurements

    float humidity = dht.readHumidity(); // Get humidity value
    float temperature = dht.readTemperature(); // Get temperature value
    float temperatureF = (temperature * 9.0 / 5.0) + 32;

    // Check if any reads failed and exit early (to try again).
    if (isnan(humidity) || isnan(temperature)) {
        Serial.println("Failed to read from DHT sensor!");
        return;
    }

    // Print the results to the Serial Monitor
    Serial.print("OK\t");
    Serial.print(humidity, 1); // Print humidity
    Serial.print("\t\t");
    Serial.print(temperature, 1); // Print temperature
    Serial.print("\t\t");
    Serial.println(temperatureF, 1);
}
