# Step-by-Step Guide: Using HC-SR04 Ultrasonic Sensor with ESP32

## Components Needed:
- ESP32 development board
- HC-SR04 ultrasonic sensor
- Jumper wires (10CM male-to-male)
- Breadboard (optional)

## Pin Connections:

| HC-SR04 Pin | ESP32 Pin |
|-------------|-----------|
| VCC         | 5V        |
| GND         | GND       |
| Trig        | GPIO 15   |
| Echo        | GPIO 4    |

**Note:** You can choose any GPIO pins for Trig and Echo, but the code example below assumes GPIO 15 and GPIO 4.

Alternative GPIO Pins:
Trig Pin: GPIO 5, 12, 14, 18, 19
Echo Pin: GPIO 16, 17, 21, 22

## Code Example:

We will use the `NewPing` library for handling the sensor.

### Step 1: Install the Library

In Arduino IDE:
1. Go to **Sketch > Include Library > Manage Libraries**.
2. Search for **NewPing**.
3. Install the NewPing library.

### Step 2: Upload the Code

```cpp
#include <NewPing.h>

#define TRIG_PIN 15  // GPIO pin connected to Trig
#define ECHO_PIN 4   // GPIO pin connected to Echo
#define MAX_DISTANCE 400 // Maximum distance in cm for the sensor

NewPing sonar(TRIG_PIN, ECHO_PIN, MAX_DISTANCE);

void setup() {
  Serial.begin(115200); // Initialize serial communication at 115200 baud rate
}

void loop() {
  delay(50); // Delay between sensor readings
  unsigned int distance = sonar.ping_cm(); // Get distance in cm

  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" cm");

  delay(1000); // Wait for a second before taking the next reading
}
```

### How It Works

The HC-SR04 ultrasonic sensor measures distance by emitting an ultrasonic pulse from its **Trig** pin and detecting the echo on its **Echo** pin. The time elapsed between sending and receiving the pulse is directly proportional to the distance of the object from the sensor. In this setup, the **NewPing** library is utilized to handle the timing and calculation, providing the distance measurement in centimeters.

- **TRIG_PIN (GPIO 15):** Connected to the sensor's Trig pin; responsible for sending the ultrasonic burst.
- **ECHO_PIN (GPIO 4):** Connected to the sensor's Echo pin; receives the echo after it bounces back from the object.
- **MAX_DISTANCE:** Defines the maximum distance (in centimeters) that the sensor can measure, e.g., 400 cm.

### Testing

After uploading the code to your ESP32:

1. Open the **Serial Monitor** in the Arduino IDE by pressing `Ctrl+Shift+M` (or `Cmd+Shift+M` on Mac).
2. Set the baud rate to **115200** to match the serial communication speed defined in the code.
3. Observe the output; the measured distance in centimeters will be displayed, updating every second.

This continuous measurement allows you to monitor real-time distance readings from the sensor.

If you have any further questions or need additional assistance, feel free to ask!

