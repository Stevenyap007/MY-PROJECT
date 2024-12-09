# ESP32 Light Monitoring Project with LDR, Buzzer, and LCD

## 1. Components Required
- **ESP32 Development Board**
- **LDR (Light Dependent Resistor)**
- **Buzzer** (Active buzzer with two pins)
- **LCD 1602 with I2C Module**
- **Breadboard** (optional)
- **10CM Jumper Wires** (male-to-male / male-to-female)
- **Power Supply MB102** or **micro-USB cable** for powering the ESP32

---

## 2. Circuit Connections

### LDR Sensor Connection:
- One pin of the LDR → VIN (VCC).
- The other pin of the LDR → ESP32 GPIO 15 (analog pin).
- 10kΩ resistor between LDR and GND to form a voltage divider.

### Buzzer Connection:
- Positive pin of the buzzer → ESP32 GPIO 5.
- Negative pin of the buzzer → GND.

### LCD I2C Connection:
- VCC → VIN on the ESP32.
- GND → GND on the ESP32.
- SDA → GPIO 21.
- SCL → GPIO 22.

### Powering the ESP32:
- Use an MB102 Power Supply connected to the breadboard rails.
- Alternatively, power the ESP32 via micro-USB from a laptop or power bank.

---

## 3. Complete Code

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

## 4. Code Walkthrough
Setup Phase:
- Initializes the LCD and buzzer.
- Displays the message "HELLO" for 2 seconds during startup.
Main Loop:
- Reads LDR values using analogRead() to measure light intensity.
- If the light level is below 400:
-- The buzzer stays off.
-- "Terang" is displayed on the LCD.
-If the light level is above 400:
-- The buzzer turns on.
-- "Redup" is displayed on the LCD.
Serial Monitor Output:
- Prints the status change ("Terang" or "Redup") only when the light condition changes, reducing redundant output.
LCD Update Interval:
- The LCD refreshes every 200 ms using a non-blocking millis() check to ensure smooth operation.

## 5. Testing the Setup
1. Power On:
- Connect your ESP32 to the power source (via MB102 or USB).
2. Monitor Output:
- Open the Serial Monitor in Arduino IDE (9600 baud rate).
3. Bright Environment:
- Place the LDR in a bright environment and verify:
- The buzzer stays off.
- The LCD displays "Terang" and the light value.
4. Simulate Darkness:
- Cover the LDR to simulate darkness and verify:
- The buzzer turns on.
- The LCD displays "Redup" and the light value.

## 6. Troubleshooting Tips
LCD Not Displaying Anything:
- Check the I2C address of your LCD (use an I2C scanner if needed).
- Ensure SDA and SCL are connected to the correct pins (GPIO 21 and 22).
Buzzer Not Working:
- Ensure the buzzer's positive leg is connected to GPIO 5.
- Test the buzzer by connecting it directly to VIN and GND.
Wrong LDR Values:
- Double-check the voltage divider wiring (LDR + 10kΩ resistor).
- Ensure you are using GPIO 15 for the analog input.
ESP32 Not Uploading Code:
- Hold the BOOT button while uploading the code to your ESP32, if needed.

## 7. Final Thoughts
This project demonstrates how to use an LDR sensor with ESP32 to monitor light intensity and trigger a buzzer and LCD display. It’s a simple but practical example of IoT automation, which can be expanded for real-world use cases like:

- Security systems: Alert when it gets dark in certain areas.
- Home automation: Automate room lights and alarms based on light levels.
- Garden monitoring: Detect light levels for plant care automation.