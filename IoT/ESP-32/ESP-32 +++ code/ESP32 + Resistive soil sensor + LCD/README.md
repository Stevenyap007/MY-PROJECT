## Components Required
- **ESP32 (WROOM-32)**
- **Soil Moisture Sensor** (resistive type)
- **Buzzer** (3.3V compatible)
- **LCD I2C 1602 display** (address 0x27)
- **Breadboard** (optional)
- **Jumper Wires** (male-to-male)

## Wiring Guide
### Use these pin connections:

| Component               | Pin        | ESP32 Pin |
|-------------------------|-----------|-----------|
| **Soil Moisture Sensor** | VCC       | 3.3V      |
|                         | GND       | GND       |
|                         | Signal    | GPIO 4    |
| **Buzzer**             | + (Positive) | GPIO 5 |
|                         | - (Negative) | GND    |
| **LCD I2C**             | VCC       | 3.3V      |
|                         | GND       | GND       |
|                         | SDA       | GPIO 21   |
|                         | SCL       | GPIO 22   |

**Note:** Ensure your ESP32 is powered via USB or a reliable power source (5V).

## Installing Required Libraries
1. Open **Arduino IDE**.
2. Go to `Sketch > Include Library > Manage Libraries`.
3. Search for **"LiquidCrystal I2C"** and install a library that matches the ESP32 environment (e.g., by Frank de Brabander).
4. Make sure the I2C address for your LCD is **0x27**. If you’re unsure, use an **I2C scanner** to confirm it.

## Full Code
```cpp
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

const int SoilSensor = 4;
const int Bz = 23;  // Buzzer pin

LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  lcd.init();  // Initialize LCD
  lcd.backlight();

  pinMode(SoilSensor, INPUT);
  pinMode(Bz, OUTPUT);

  lcd.setCursor(0, 0);
  lcd.print(" Hello");
  lcd.setCursor(0, 1);
  lcd.print(" World");
  delay(2000);

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(" SOIL SENSOR");
}

void loop() {
  if (digitalRead(SoilSensor) == HIGH) {
    lcd.setCursor(0, 1);
    lcd.print(" Kondisi Kering ");
    digitalWrite(Bz, LOW);  // Turn off buzzer
  } else {
    lcd.setCursor(0, 1);
    lcd.print(" Kondisi Lembab ");
    digitalWrite(Bz, HIGH);  // Turn on buzzer
  }
}
```

## Explanation of the Code
### **Library Import:**
- `Wire.h` is used for I2C communication.
- `LiquidCrystal_I2C.h` is used to control the LCD.

### **Pin Setup:**
- **Soil Moisture Sensor:** GPIO 4
- **Buzzer:** GPIO 23
- **LCD I2C:** SDA (GPIO 21) / SCL (GPIO 22)

### **Setup Section:**
1. Initialize the **LCD** and enable the **backlight**.
2. Display a **welcome message** for **2 seconds**, then clear the screen.
3. Set the display to show **“SOIL SENSOR.”**

### **Loop Section:**
- If the soil is **dry (HIGH)**:
  - LCD displays **"Kondisi Kering"**.
  - Buzzer remains **OFF**.
- If the soil is **moist (LOW)**:
  - LCD displays **"Kondisi Lembab"**.
  - Buzzer **turns ON**.

## Testing and Troubleshooting
### **Step 1: Upload the Code**
1. Connect your **ESP32** to your **computer via USB**.
2. Open **Arduino IDE** and select the correct board and port:
   - `Tools > Board > ESP32 Dev Module`
   - `Tools > Port > Your ESP32's Port`
3. Click **Upload (⭮)** to upload the code to your ESP32.

### **Step 2: Monitor Behavior**
- **When the soil is dry**, the LCD should display **“Kondisi Kering”**, and the buzzer will remain **OFF**.
- **When the soil is moist**, the LCD should display **“Kondisi Lembab”**, and the buzzer will **turn ON**.

### **Step 3: Troubleshooting**
- **LCD not displaying properly?**
  - Check if the **I2C address** is correct (`0x27`).
  - Ensure **SDA (GPIO 21) and SCL (GPIO 22)** connections are correct.
- **Buzzer not working?**
  - Make sure the **positive leg** is connected to **GPIO 23** and the **negative leg** to **GND**.
- **Soil sensor showing incorrect readings?**
  - Check the connections, especially if the sensor’s **signal wire** is connected to **GPIO 4**.

## Final Result
After **uploading the code** and setting everything up, your ESP32 project will:
- **Detect soil moisture levels** using the sensor.
- **Display the status** on the LCD (**"Kondisi Kering" or "Kondisi Lembab"**).
- **Activate the buzzer** when the soil is **moist**.
