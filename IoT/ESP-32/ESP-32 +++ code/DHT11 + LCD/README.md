# ESP32 with DHT11 and I2C LCD Display

## Components Needed
- **ESP32 Development Board**  
- **DHT11 Temperature and Humidity Sensor**  
- **I2C LCD (16x2) Display**  
- **Breadboard and Jumper Wires**  
- **Resistor (10kΩ)** (for DHT11 - optional but recommended)

## Hardware Connections

### DHT11 Sensor
- **VCC (Power):** Connect to 3.3V on ESP32.  
- **GND (Ground):** Connect to GND on ESP32.  
- **DATA (Signal):** Connect to GPIO 4 on ESP32.  
- **Optional:** Connect a 10kΩ resistor between **VCC** and the **DATA** pin to pull it up.

### I2C LCD Display
- **VCC (Power):** Connect to 3.3V on ESP32.  
- **GND (Ground):** Connect to GND on ESP32.  
- **SDA (Data Line):** Connect to GPIO 21 on ESP32 (default SDA pin).  
- **SCL (Clock Line):** Connect to GPIO 22 on ESP32 (default SCL pin).

---

## Code

Here’s the complete code to upload to your ESP32:

```cpp
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include "DHT.h"

#define DHTPIN 4        // DHT11 connected to GPIO 4
#define DHTTYPE DHT11   // DHT11 sensor type

// Initialize I2C LCD at address 0x27 with 16 columns and 2 rows
LiquidCrystal_I2C lcd(0x27, 16, 2);
DHT dht(DHTPIN, DHTTYPE); 

void setup() {
  Serial.begin(115200); // Start serial communication
  lcd.init();           // Initialize the LCD
  dht.begin();          // Initialize DHT11 sensor
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.backlight();
  lcd.print(F("Hello World"));
  delay(2000); // 2-second delay for stabilization
}

void loop() {
  float h = dht.readHumidity();     // Read humidity
  float t = dht.readTemperature();  // Read temperature in Celsius

  if (isnan(h) || isnan(t)) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print(F("GAGAL MEMBACA"));
    return;
  }

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Temp = ");
  lcd.print(t);
  lcd.print("'C");
  lcd.setCursor(0, 1);
  lcd.print("Humd = ");
  lcd.print(h);
  lcd.print("% ");
  delay(2000); // Delay for the next reading

  // Optional: Print readings to Serial Monitor
  // Serial.print("Temperature = ");
  // Serial.print(t);
  // Serial.print("°C | ");
  // Serial.print("Humidity = ");
  // Serial.println(h);
}
```

## Installation of Required Libraries
### DHT Sensor Library:
In Arduino IDE, go to Sketch > Include Library > Manage Libraries.
Search for DHT sensor library by Adafruit and install it.
LiquidCrystal_I2C Library:
In the Library Manager, search for LiquidCrystal I2C and install it.
If you face issues, try libraries from F Malpartida or johnrickman.

## Uploading the Code
- Connect your ESP32 to your computer via USB.
- Open Arduino IDE and select the correct board and port:
- Tools > Board: Select ESP32 Dev Module.
- Tools > Port: Select the port to which your ESP32 is connected.
- Copy the code into the IDE and click the Upload button.

## Troubleshooting Tips
### No Display on LCD:
Ensure the I2C address is correct (use an I2C scanner if necessary).
Check the LCD connections and ensure adequate power supply.
Use lcd.init(); instead of lcd.begin(); to initialize the LCD.

### DHT11 Not Reading:
Verify the connections of the DHT11 sensor.
Ensure the DATA pin is set correctly in the code.
Test the DHT11 sensor with a simple sketch to confirm it works.

## Serial Monitor:
Use Serial Monitor (set to 9600 baud) to debug readings.
Uncomment the Serial.print lines in the code for more information.