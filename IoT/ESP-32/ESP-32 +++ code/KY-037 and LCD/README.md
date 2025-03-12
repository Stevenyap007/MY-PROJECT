# Step 1: Components Required

- ESP32 (WROOM-32 or similar)  
- Sound Sensor Module (KY-037)  
- Jumper Wires (Male-to-Male)  
- Breadboard (optional)  
- Buzzer (optional)  
- LCD I2C 1602 Display (optional)  

---

# Step 2: Wiring Connections

Use the **AO** pin to get the analog value from the sensor. Here’s the pin connection:

| Sound Sensor | ESP32                     |
|--------------|---------------------------|
| AO (Analog Out) | GPIO 2 (Analog-capable pin) |
| GND          | GND                       |
| VCC          | 3.3V                      |
| Buzzer +     | GPIO 5                    |
| Buzzer -     | GND                       |

---

# Step 3: Code to Use AO Pin

Here’s the full code to read analog values from the sound sensor and trigger a buzzer based on the sound level.

## Complete Code

```cpp
#include <LiquidCrystal_I2C.h>
#include <Wire.h>

const int soundpin = 2;  // Sound sensor input pin
const int bzpin = 5;    // Buzzer pin
const int threshold = 400; // Threshold value for sound sensor

LiquidCrystal_I2C lcd(0x27, 16, 2); // LCD I2C address, 16 columns, 2 rows

void setup() {
  Serial.begin(9600);
  pinMode(soundpin, INPUT);
  pinMode(bzpin, OUTPUT);

  lcd.init();  // Initialize LCD
  lcd.backlight();  // Turn on the backlight

  // Display welcome message
  lcd.setCursor(0, 0);
  lcd.print("Hello");
  lcd.setCursor(0, 1);
  lcd.print("World");
  delay(2000);
  lcd.clear();
}

void loop() {
  int soundsens = analogRead(soundpin);  // Read data from sound sensor

  lcd.setCursor(0, 0);
  lcd.print("SoundVoiceSensor");
  lcd.setCursor(0, 1);
  lcd.print("Sensor = ");

  if (soundsens >= threshold) {
    digitalWrite(bzpin, HIGH);  // Activate buzzer
    lcd.setCursor(9, 1);
    lcd.print(" ON ");
    delay(2000);
  } else {
    Serial.println("SoundVoice = OFF");
    digitalWrite(bzpin, LOW);  // Deactivate buzzer
    lcd.setCursor(9, 1);
    lcd.print(" OFF");
  }
}
```

---

# Step 4: Explanation of the Code

### ✅ Pin Configuration:
- The **AO** pin from the sound sensor is connected to **GPIO 2** on the ESP32, which is read using `analogRead()`.

### ✅ LCD Display Setup:
- The **LCD** displays the sound intensity value in real-time.

### ✅ Threshold Logic:
- If the sound value from `analogRead()` exceeds the threshold (**400**), the **buzzer turns ON**. Otherwise, it stays OFF.

### ✅ Serial Monitor Output:
- The sound intensity values are printed to the **Serial Monitor** to help with debugging and calibration.

---

# Step 5: Testing and Calibration

### ⚙️ Upload the Code:
- Use the **Arduino IDE** to upload the code to the **ESP32**.

### ⚙️ Open Serial Monitor:
- Go to **Tools → Serial Monitor** in the Arduino IDE.
- Set the baud rate to **9600** to see real-time sound values.

### ⚙️ Calibrate the Potentiometer:
- If the sensor is not sensitive enough, adjust the **potentiometer** on the sound sensor until it detects sound changes effectively.

### ⚙️ Adjust Threshold:
- If the buzzer activates too often or not at all, tweak the **threshold** value in the code (e.g., try **300** or **500**).

---

# Step 6: Troubleshooting Tips

### ❗ No readings on the serial monitor?
- Ensure the sound sensor’s **AO pin** is connected to an **analog-capable GPIO pin** on the ESP32 (e.g., **GPIO 34**).

### ❗ Buzzer not working?
- Make sure the **buzzer** is connected properly.
- Check that the correct **GPIO pin** is defined in the code.

### ❗ Unresponsive LCD?
- Double-check the **I2C address**.
- If **0x27** doesn’t work, try scanning I2C devices to confirm the correct address.

---
