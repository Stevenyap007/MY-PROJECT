# Components Required

- **ESP32 board** (WROOM-32 or similar)  
- **1-Channel Relay Module**  
- **LED** (any color)  
- **Breadboard** (optional for easier connections)  
- **Jumper Wires** (Male-to-Female recommended)  

---

# Code Example

Here’s the Arduino code to control the relay and the LED:

```cpp
#define RELAY_PIN 5  // Pin connected to the relay module
#define LED_PIN 23   // Pin connected to the LED

void setup() {
  pinMode(RELAY_PIN, OUTPUT);  // Set relay pin as an output
  pinMode(LED_PIN, OUTPUT);     // Set LED pin as an output
  digitalWrite(RELAY_PIN, LOW);  // Initialize relay as off (LOW)
  digitalWrite(LED_PIN, LOW);     // Initialize LED as off (LOW)
}

void loop() {
  digitalWrite(RELAY_PIN, HIGH);  // Turn relay on
  digitalWrite(LED_PIN, HIGH);     // Turn LED on
  delay(2000);                     // Wait for 2 seconds
  digitalWrite(RELAY_PIN, LOW);   // Turn relay off
  digitalWrite(LED_PIN, LOW);      // Turn LED off
  delay(2000);                     // Wait for 2 seconds
}
```

# How to Upload the Code
1. Open the Arduino IDE on your computer.
2. Select your ESP32 board from Tools > Board.
3. Connect your ESP32 to the computer using a USB cable.
4. Select the correct COM port from Tools > Port.
5. Copy and paste the provided code into a new sketch.
6. Click on the Upload button (right arrow) to compile and upload the code to the ESP32.

# Testing the Setup
- After uploading, the ESP32 should power on.
- The LED will blink on and off every 2 seconds, indicating that the relay is being activated.
- If an external load is connected, it should also turn on and off in sync with the LED.