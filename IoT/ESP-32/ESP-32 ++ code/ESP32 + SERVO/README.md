# What You'll Need

- **ESP32 board** (WROOM-32, Devkit, etc.)  
- **Servo Motor** (e.g., SG90 or MG90S)  
- **3 Jumper Wires** (10CM male-to-male / female-to-male)  
- **Arduino IDE** (with ESP32 board support installed)  

---

# Step 1: Install the ESP32Servo Library

1. Open **Arduino IDE**.  
2. Go to **Tools > Manage Libraries**.  
3. In the search bar, type **ESP32Servo**.  
4. Find **ESP32Servo** by Kevin Harrington and click **Install**.  

---

# Step 2: Wiring Your ESP32 and Servo Motor

The servo motor has three pins:

| Servo Pin     | ESP32 Pin        |
|---------------|------------------|
| Brown (GND)  | GND              |
| Red (VCC)    | 5V               |
| Orange (Signal)| GPIO 18        |

### Recommended PWM-Capable GPIO Pins for Servo Control:
- GPIO 5  
- GPIO 12  
- GPIO 13  
- GPIO 14  
- GPIO 15  
- **GPIO 18** (used in the example code)  
- GPIO 19  
- GPIO 21  
- GPIO 22  
- GPIO 23  
- GPIO 25  
- GPIO 26  
- GPIO 27  

#### ⚠️ Note on GPIO Pin Limitations:
- Avoid using **GPIO 0, 2, or 4** if you plan to reflash the ESP32 often.  
- **GPIO 34 to 39** are input-only and **cannot** be used for PWM or servo signals.  
- **GPIO 15**: Check your board documentation; some boards may require a pull-down resistor at boot.  

---

# Step 3: Arduino Code for ESP32 with Servo

Use the following code to test the servo:

```cpp
#include <ESP32Servo.h>  // Include the ESP32Servo library

Servo myServo;  // Create a Servo object

int servoPin = 18;  // GPIO pin connected to the servo signal wire
int angle = 0;      // Variable to store the current angle

void setup() {
  myServo.attach(servoPin);  // Attach the servo to GPIO 18
  Serial.begin(115200);  // Start serial communication
}

void loop() {
  // Sweep from 0° to 180°
  for (angle = 0; angle <= 180; angle++) {
    myServo.write(angle);  // Move servo to the current angle
    delay(15);  // Wait for the servo to reach the position
  }

  // Sweep back from 180° to 0°
  for (angle = 180; angle >= 0; angle--) {
    myServo.write(angle);  // Move servo to the current angle
    delay(15);  // Wait for the servo to reach the position
  }
}
```

---

# Step 4: Upload the Code to ESP32

1. Select the correct board:  
   Go to **Tools > Board > Select ESP32 Dev Module**.  
2. Select the correct port:  
   Go to **Tools > Port** and select the port where your ESP32 is connected.  
3. Click the **Upload** button and wait until the code uploads successfully.  

---

# Step 5: Test Your Setup

1. Open the **Serial Monitor** in Arduino IDE (set baud rate to **115200**).  
2. If everything is connected properly, the servo motor will sweep smoothly from **0° to 180°** and back.  

---

# Troubleshooting Tips

### Servo not moving?
- Double-check the wiring, especially the **GND** and **signal** pin connections.  
- Ensure **VCC** is connected to the **5V** pin on the ESP32.  

### Servo jittering or behaving strangely?
- Some GPIO pins may not support PWM well. Try using other pins like **GPIO 23, 19, or 5**.  
- If the ESP32's **5V** pin can't provide enough power, use an **external 5V power source** and connect the **GND** of the ESP32 and the power source together.  

---

# Conclusion

You have successfully connected your **ESP32** to a **servo motor** and controlled it using the **ESP32Servo library**.  
This guide ensures that your hardware setup and code are correct and provides solutions to common issues.
