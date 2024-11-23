# ESP32 Flame Sensor Project

## 1. Components Needed
- ESP32 Development Board
- Flame Sensor
- Buzzer
- I2C LCD (e.g., 16x2)
- Breadboard and Jumper Wires
- Power Supply (e.g., USB or battery)

## 2. Wiring Setup
Connect the components as follows:

- **Flame Sensor**:
  - VCC → 3.3V on ESP32
  - GND → GND on ESP32
  - OUT → GPIO 2 on ESP32

- **Buzzer**:
  - Positive (longer leg) → GPIO 5 on ESP32
  - Negative (shorter leg) → GND on ESP32

- **I2C LCD**:
  - VCC → 5V (or 3.3V, depending on your LCD) on ESP32
  - GND → GND on ESP32
  - SDA → GPIO 21 on ESP32 (default I2C SDA)
  - SCL → GPIO 22 on ESP32 (default I2C SCL)

## 3. Install Libraries
Make sure to install the following libraries in the Arduino IDE:
- **Wire**: Usually pre-installed.
- **LiquidCrystal I2C**: You can install it through the Library Manager by searching for "LiquidCrystal I2C."

## 4. Sample Code
Here’s the full code you can use, following the modifications discussed:

```cpp
#define ldr 15
#define buz 5
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

String fNilai2, nilai = "";
int fNilai;
unsigned long previousMillis = 0;
const long interval = 200;
LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  Serial.begin(9600);
  pinMode(ldr, INPUT);
  pinMode(buz, OUTPUT);
  Serial.println("Ready\n");

  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("HELLO");
  delay(2000);
}

void loop() {
  int light = analogRead(ldr);

  if (light < 400) {
    digitalWrite(buz, LOW);
    nilai = "Terang";
    lcd.setCursor(6, 1);
    lcd.print("Terang    ");
  } else {
    digitalWrite(buz, HIGH);
    nilai = "Redup";
    lcd.setCursor(6, 1);
    lcd.print("Redup     ");
  }

  if (fNilai2 != nilai) {
    Serial.println(nilai);
    fNilai2 = nilai;
  }

  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    if (fNilai != light) {
      lcd.setCursor(0, 0);
      lcd.print("Light Sensor    ");
      fNilai = light;
    }
    lcd.setCursor(0, 1);
    lcd.print(light);
  }
}
```

## 5. Upload Code
1. Connect your ESP32 to your computer via USB.
2. Open the Arduino IDE.
3. Select the correct board and port from the Tools menu.
4. Copy the code above into a new sketch.
5. Click the Upload button.

## 6. Testing the Setup
- After uploading, open the Serial Monitor (set to 9600 baud rate).
- Observe the messages indicating whether flame is detected or not.
- The LCD should display "FLAME SENSOR" initially and update with detection results.

## 7. Troubleshooting
- LCD Not Displaying:
-- Check the I2C connections.
-- Verify the I2C address (use an I2C scanner if necessary).
-- Make sure the LCD has power.
- Flame Sensor Not Responding:
-- Ensure it is wired correctly.
-- Test the flame sensor with a lighter (carefully) to see if it detects flame.
- Buzzer Not Activating:
-- Check the buzzer connections.
-- Ensure GPIO pin for the buzzer is correct and functioning.

## 8. Tips for Future Projects
- Always double-check your wiring before powering up.
- Use a breadboard for temporary setups.
- For better readability, consider implementing a function to clear or update the LCD display.
- Experiment with different sensors or modules to expand your project.
