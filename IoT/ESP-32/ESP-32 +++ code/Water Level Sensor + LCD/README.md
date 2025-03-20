# Water Level Monitoring System with ESP32

## 1. Components Required
- **ESP32 WROOM-32**  
- **Water Level Sensor**  
- **16x2 I2C LCD Display**  
- **Buzzer**  
- **Jumper Wires (Male to Male / Male to Female)**  
- **Breadboard**  

## 2. Wiring Diagram

### ESP32 Wiring

| Component            | Pin on Component | Pin on ESP32 |
|----------------------|-----------------|-------------|
| **Water Level Sensor** | VCC             | 5V          |
|                      | GND             | GND         |
|                      | Analog Output   | GPIO 15     |
| **LCD I2C Display**  | VCC             | 5V          |
|                      | GND             | GND         |
|                      | SDA             | GPIO 21     |
|                      | SCL             | GPIO 22     |
| **Buzzer**          | VCC (+)         | GPIO 23     |
|                      | GND (-)         | GND         |

### Note:
- **I2C Pins**: Make sure to connect the SDA and SCL pins correctly (**GPIO 21** and **GPIO 22** are default I2C pins for the ESP32).  
- **Water Level Sensor**: The resistive sensor outputs analog values to **GPIO 15**.  
- Use **10CM jumper wires** for cleaner connections.  

---

## 3. Code for ESP32 with Water Level Sensor, LCD, and Buzzer

```cpp
#include <LiquidCrystal_I2C.h>

#define wlS 15  // Water level sensor on GPIO 15
#define bz 23   // Buzzer on GPIO 23

// LCD setup
LiquidCrystal_I2C lcd(0x27, 16, 2); 

// Variables for state management
String fNilai = "";
unsigned long previousMillis = 0;
const long interval = 100;

void setup() {
  // Initialize serial monitor
  Serial.begin(9600);

  // Set pin modes
  pinMode(wlS, INPUT);
  pinMode(bz, OUTPUT);

  // Initialize LCD
  lcd.init(); 
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Hello World");
  delay(2000);  // Pause for readability
  lcd.clear();
}

void loop() {
  // Read analog value from the water level sensor
  int val = analogRead(wlS);
  String nilai = String(val);  // Convert value to string for LCD display

  // Update the display only if the value changes or the interval passes
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    if (fNilai != nilai) {
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Level: " + nilai);
      fNilai = nilai;  // Store the last displayed value
    }
  }

  // Control buzzer based on water level
  if (val < 200) {
    digitalWrite(bz, LOW);  // Turn off the buzzer
  } else {
    digitalWrite(bz, HIGH);  // Turn on the buzzer
  }
}
```

## 4. Uploading the Code to ESP32
1. Connect the **ESP32** to your computer using a **USB cable**.  
2. In the **Arduino IDE**, go to **Tools > Board** and select **ESP32 Dev Module**.  
3. Choose the correct **Port** under **Tools > Port**.  
4. Click **Upload** to flash the code to your ESP32.  

---

## 5. How the Code Works

### **Reading Sensor Data**
- The function `analogRead(wlS)` reads the **water level sensor’s analog output**.  
- The value ranges between **0 (dry)** and **4095 (full)** since the ESP32 has a **12-bit ADC**.  

### **Displaying Data on LCD**
- The **LCD** will display the **water level value** whenever it changes.  
- If the value remains the same, the display will **not update**.  

### **Buzzer Control**
- If the **sensor value** is **below 200**, the **buzzer turns off**.  
- Otherwise, the **buzzer remains on**.  

### **Serial Monitor Output**
- The **water level value** is also **printed to the serial monitor** for debugging.  
