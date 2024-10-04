# Wiring the PIR Sensor to ESP32

The PIR sensor typically has 3 pins:
- **VCC**: Power (Connect to 5V on ESP32)
- **GND**: Ground (Connect to GND on ESP32)
- **OUT**: Output signal (Connect to any GPIO pin on ESP32)

For example, you can connect the OUT pin to GPIO 14.

## Wiring Example:
- PIR VCC → 5V (ESP32)
- PIR GND → GND (ESP32)
- PIR OUT → GPIO 14 (ESP32)

## Recommended GPIO Pins:
- **GPIO 13**: Safe and commonly used for digital inputs.
- **GPIO 14**: Works well for digital input/output, as shown in the previous code.
- **GPIO 27**: Another good option for general input, often used in sensors.
- **GPIO 32**: Reliable for digital input, not connected to internal flash.
- **GPIO 33**: Similar to GPIO 32, good for sensor input.

## Code:

```cpp
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
```

## Explanation:
- The digitalRead(pirPin) function reads the signal from the PIR sensor.
- When motion is detected, the sensor sends a HIGH signal (prints "Motion detected!").
- When motion stops, it sends a LOW signal (prints "Motion ended.").

## Upload to ESP32:
1. Make sure your ESP32 is connected to your computer.
2. Select the correct board (ESP32 Dev Module) and port in the Arduino IDE.
3. Upload the code.
4. Open the Serial Monitor (baud rate set to 115200) to see the motion detection messages.