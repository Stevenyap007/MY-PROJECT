# Wiring Recap
- **VCC** to 5V  
- **GND** to GND  
- **A0** to GPIO34 (Analog input for rain intensity)  
- **D0** to GPIO35 (Digital input for rain detection)  

## Digital Output (D0)
Any GPIO pin can be used for digital input, such as:  
`GPIO5`, `GPIO18`, `GPIO23`, `GPIO33`, etc.

## Analog Output (A0)
Use one of the ADC (Analog-to-Digital Converter) pins.  
The ESP32 has ADCs mapped to the following GPIOs:  
`GPIO32`, `GPIO33`, `GPIO34`, `GPIO35`, `GPIO36`, `GPIO39`

---

## Code Example

```cpp
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
```


Please consider the if else parameter with the condition from your sensor

## Explanation
Analog Value:
The analogRead(rainAnalogPin) function reads the raindrop intensity, which ranges from 0 to 4095. This gives you a precise measure of how much water is on the sensor.

## Digital Value:
The digitalRead(rainDigitalPin) function checks if rain is detected based on the threshold set on the sensor’s potentiometer. The output will be HIGH (rain detected) or LOW (no rain).