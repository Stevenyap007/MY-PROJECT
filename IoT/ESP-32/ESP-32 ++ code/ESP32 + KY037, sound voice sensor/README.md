# Components Required

- ESP32 development board  
- Sound voice sensor module (with AO and DO pins)  
- Jumper wires (male-to-male or male-to-female)  
- Breadboard (optional, for easier connections)  

---

# Pinout Overview

Here’s how the sound voice sensor connects to the ESP32:

| Sound Sensor Pin | Function                          | ESP32 Pin Options                          |
|------------------|-----------------------------------|--------------------------------------------|
| VCC              | Power Supply (+)                  | 3.3V or 5V                                  |
| GND              | Ground (-)                        | GND                                         |
| AO               | Analog Output                     | GPIO 32, 33, 34, 35, 36, 39 (ADC1 pins)     |
| DO               | Digital Output (Threshold Detection) | GPIO 4, 13, 16, 17, 18, 19, 23         |

---

# Wiring Connections

- **VCC** → ESP32 **3.3V**  
- **GND** → ESP32 **GND**  
- **AO (Analog Output)** → ESP32 **GPIO 34**  
- **DO (Digital Output)** → ESP32 **GPIO 23**  

> **Note:** If using Wi-Fi on the ESP32, prefer ADC1 pins (like GPIO 32) for analog input, since ADC2 pins can conflict with Wi-Fi operations.  

---

# Code Example: Using Both AO and DO Outputs

This code reads the analog output (AO) to monitor sound levels and the digital output (DO) to detect if the sound crosses the sensor’s threshold. If the DO value is **LOW**, it indicates the sound exceeds the threshold.

## Complete Code

```cpp
#define SOUND_PIN_AO 34  // Analog pin connected to AO (sound level)
#define SOUND_PIN_DO 23  // Digital pin connected to DO (threshold detection)

void setup() {
  Serial.begin(115200);  // Initialize serial communication
  pinMode(SOUND_PIN_AO, INPUT);  // Set AO as input
  pinMode(SOUND_PIN_DO, INPUT);  // Set DO as input

  Serial.println("Sound Sensor Initialized (Both AO and DO).");
}

void loop() {
  // Read analog value from AO (sound level)
  int soundValue = analogRead(SOUND_PIN_AO);
  Serial.print("Sound Level (AO): ");
  Serial.println(soundValue);  // Print the analog value

  // Read digital value from DO (threshold detection)
  int soundState = digitalRead(SOUND_PIN_DO);
  if (soundState == LOW) {
    Serial.println("Sound Detected! (Above Threshold)");
  } else {
    Serial.println("No Sound Detected. (Below Threshold)");
  }

  delay(100);  // Small delay to stabilize readings
}
```

---

# How the Code Works

### Analog Output (AO):
- The `analogRead()` function reads sound levels, with values ranging from **0 to 4095**.
- Higher values indicate louder sounds.

### Digital Output (DO):
- `digitalRead()` checks if the sound exceeds the preset threshold (set using the potentiometer on the sensor).
- If the sound is above the threshold, DO outputs **LOW** (active-low logic).

### Serial Monitor:
- It prints both the sound level and whether the threshold has been exceeded.

---

# Testing and Adjustments

### Upload the Code:
- Upload the code to your **ESP32** using the **Arduino IDE**.

### Open Serial Monitor:
- Set the baud rate to **115200** to view the output.
- You should see the analog sound level and whether sound is detected.

### Make Noise:
- Clap or make a sound near the sensor.
- Observe the analog readings change and the digital output switching between **HIGH** and **LOW**.

### Adjust the Potentiometer:
- Use a small screwdriver to adjust the sensor’s potentiometer.
- This changes the threshold for the **DO** pin.

---

# Troubleshooting

- **Incorrect DO readings:**
  - If DO logic seems reversed (**HIGH** for sound, **LOW** for quiet), make sure the logic in the code matches your sensor behavior.
- **AO values too low or stuck:**
  - Check the wiring to ensure proper connections.
  - Try adjusting the potentiometer to improve sensor sensitivity.
- **Wi-Fi Interference:**
  - Avoid using **ADC2 pins** (like GPIO 25, 26, 27) if the **ESP32 Wi-Fi** is enabled, as it can interfere with readings.


