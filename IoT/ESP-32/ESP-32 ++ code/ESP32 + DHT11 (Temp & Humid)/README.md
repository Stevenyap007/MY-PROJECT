# DHT11 Module with ESP32

## Getting Started

This guide will help you set up your DHT11 sensor module with the ESP32. Follow the steps below to start reading temperature and humidity data.

## 1. Wiring the DHT11 to the ESP32

Connect the DHT11 module to the ESP32 as follows:

- **VCC**: Connect to a 3.3V pin on the ESP32.
- **GND**: Connect to a GND pin on the ESP32.
- **DATA**: Connect to a digital GPIO pin on the ESP32 (e.g., GPIO 4).

## 2. Install the DHT Sensor Library

To use the DHT11 module, you'll need to install the DHT sensor library in the Arduino IDE:

1. Open the Arduino IDE.
2. Go to `Sketch > Include Library > Manage Libraries`.
3. In the Library Manager, search for **"DHT sensor library"** by Adafruit.
4. Click **Install**.

## 3. Example Code

Here’s a simple code snippet to read the temperature and humidity from the DHT11:

```cpp
#include "DHT.h"

#define DHTPIN 4      // Pin where the DHT11 is connected
#define DHTTYPE DHT11 // DHT 11

DHT dht(DHTPIN, DHTTYPE);

void setup() {
    Serial.begin(9600);
    dht.begin();
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

## 4. Upload the Code

1. Connect your ESP32 to the PC.
2. Select the correct board and port in the Arduino IDE.
3. Upload the code to the ESP32.

## 5. Open the Serial Monitor

After uploading the code:

1. Open the Serial Monitor (`Tools > Serial Monitor`).
2. Set the baud rate to **9600**.
3. You should see the temperature and humidity readings displayed every few seconds.
