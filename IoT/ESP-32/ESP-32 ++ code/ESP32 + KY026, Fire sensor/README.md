# ESP32 Flame Sensor Setup

## Components Needed:
- **ESP32 Development Board**
- **KY-026 - Flame Sensor Module** (e.g., LM393)
- **Breadboard** (optional)
- **Jumper Wires**

## Wiring Diagram:
Here's how to wire the flame sensor to the ESP32:

| Flame Sensor Pin | ESP32 Pin (Default) | Alternative GPIO Pins |
|------------------|---------------------|------------------------|
| VCC              | 3.3V               | 3.3V                  |
| GND              | GND                | GND                   |
| DO               | GPIO 15            | GPIO 2, GPIO 4, GPIO 5, GPIO 16, GPIO 17, GPIO 18, GPIO 19, GPIO 21, GPIO 22, GPIO 23 |
| AO               | GPIO 34            | GPIO 32, GPIO 33      |

### Wiring Instructions:
1. Connect **VCC** from the flame sensor to the **3.3V** pin on the ESP32.
2. Connect **GND** from the flame sensor to a **GND** pin on the ESP32.
3. Connect **DO** (Digital Output) from the flame sensor to **GPIO 15** (or an alternative GPIO pin).
4. Connect **AO** (Analog Output) from the flame sensor to **GPIO 34** (or an alternative GPIO pin).

## Example Code:
Here’s the complete Arduino code for reading from the flame sensor:

```cpp
#define FLAME_SENSOR_DO 15  // Digital pin for flame detection (change as needed)
#define FLAME_SENSOR_AO 34  // Analog pin for flame intensity (change as needed)

void setup() {
  pinMode(FLAME_SENSOR_DO, INPUT);  // Set DO as input
  Serial.begin(115200);             // Start serial communication
}

void loop() {
  // Read from the digital output (DO)
  int flameDetected = digitalRead(FLAME_SENSOR_DO);

  // Read the analog output (AO) for flame intensity
  int flameIntensity = analogRead(FLAME_SENSOR_AO);  // Value range: 0-4095

  // Check if flame is detected based on inverted logic
  if (flameDetected == HIGH) {  // High means flame is detected
    Serial.println("Flame detected!"); // Logic adjusted
  } else {
    Serial.println("No flame detected!"); // Logic adjusted
  }

  // Print flame intensity to serial monitor
  Serial.print("Flame Intensity: ");
  Serial.println(flameIntensity);

  delay(500);  // Wait for 500ms before the next reading
}
```
## Code Explanation:
- Define Pins:
FLAME_SENSOR_DO: Digital pin used for detecting the flame.
FLAME_SENSOR_AO: Analog pin used for reading flame intensity.
- Setup Function:
Initialize the digital pin as input and start serial communication.
- Loop Function:
Continuously read the state of the digital output (DO) and analog output (AO).
Print messages based on the detected state and display the flame intensity value.

## Testing:
1. Upload the code to your ESP32 using the Arduino IDE.
2. Open the Serial Monitor (set to 115200 baud).
3. Bring a flame source close to the sensor (like a lighter or candle) and observe the output in the Serial Monitor.
4. Expected Behavior:
-- When a flame is detected, it should show "Flame detected!".
-- When no flame is present, it should show "No flame detected!".

## Troubleshooting:
Sensor Not Responding: Check wiring and ensure the sensor is powered correctly.
Incorrect Output: Confirm the logic used in the code matches the sensor's output behavior (i.e., HIGH means flame detected).