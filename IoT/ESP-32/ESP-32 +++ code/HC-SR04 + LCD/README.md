
# 🚀 ESP32 Ultrasonic Sensor with LCD Display — Step-by-Step Guide

## ✅ **1. Components You Need**
- **ESP32 Dev Board** — 1x  
- **HC-SR04 Ultrasonic Sensor** — 1x  
- **16x2 I2C LCD Display (0x27 address)** — 1x  
- **Jumper Wires** — as needed  
- **USB Cable** — for programming ESP32  

---

## ✅ **2. Wiring Connections**

### 🔌 **HC-SR04 to ESP32:**

| HC-SR04 Pin | ESP32 Pin  |
|-------------|------------|
| VCC         | 5V         |
| GND         | GND        |
| Trig        | GPIO 5     |
| Echo        | GPIO 18    |

### 🔌 **I2C LCD to ESP32:**

| LCD I2C Pin | ESP32 Pin  |
|-------------|------------|
| VCC         | 3.3V or 5V |
| GND         | GND        |
| SDA         | GPIO 21    |
| SCL         | GPIO 22    |

---

## ✅ **3. Install Necessary Libraries in Arduino IDE**

### 📦 **ESP32 Board Package:**
1. Go to **File > Preferences**.
2. Add this URL to **"Additional Board Manager URLs"**:
   \`\`\`
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   \`\`\`
3. Go to **Tools > Board > Board Manager**, search **ESP32**, and install it.

### 📦 **LCD I2C Library:**
1. Go to **Sketch > Include Library > Manage Libraries**.
2. Search and install \`LiquidCrystal I2C\` (by Frank de Brabander or compatible).

---

## ✅ **4. Code to Upload on ESP32**

\`\`\`cpp
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

#define echoPin 18 // Attach pin D18 to Echo of HC-SR04
#define trigPin 5  // Attach pin D5 to Trig of HC-SR04

LiquidCrystal_I2C lcd(0x27, 16, 2); // Change the address if needed

long duration; // Variable for the duration of sound wave travel
int distance;  // Variable for the distance measurement

void setup() {
  pinMode(trigPin, OUTPUT); // Sets the trigPin as an OUTPUT
  pinMode(echoPin, INPUT);  // Sets the echoPin as an INPUT

  lcd.init();                // Initialize the LCD
  // lcd.backlight();         // Uncomment if you want the backlight on
  lcd.setCursor(0, 0);
  lcd.print("Hello");
  lcd.setCursor(0, 1);
  lcd.print("World");
  delay(2000);
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("        ^_^        ");
}

void loop() {
  // Clears the trigPin condition
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  
  // Sets the trigPin HIGH (ACTIVE) for 10 microseconds
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  // Reads the echoPin, returns the sound wave travel time in microseconds
  duration = pulseIn(echoPin, HIGH);
  
  // Calculating the distance
  distance = duration * 0.034 / 2; // Speed of sound wave divided by 2 (go and back)
  
  // Clear the previous distance value
  lcd.setCursor(0, 1);
  lcd.print("Distance:     "); // Ensure the line is cleared
  
  // Print the current distance
  lcd.setCursor(9, 1);
  lcd.print(distance);
  lcd.print(" cm  "); // Add some spaces to overwrite any old value
}
\`\`\`

---

## ✅ **5. Upload and Test the System**

1. Connect ESP32 to PC via USB.
2. In Arduino IDE:
   - Go to **Tools > Board > ESP32 Dev Module**.
   - Go to **Tools > Port** and select the correct COM port.
3. Paste the code above.
4. Click **Upload**.
5. After upload:
   - The LCD will show a welcome message.
   - Then it will display **distance** measured by the ultrasonic sensor in real-time.

---

## 🎉 **Done!**
You now have a working **ESP32 ultrasonic distance measuring device with LCD display**.

---
