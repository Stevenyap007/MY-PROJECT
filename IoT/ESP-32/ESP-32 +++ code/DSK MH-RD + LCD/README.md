# Raindrop Sensor with ESP32 and LCD I2C 1602

## 1. Devices and Materials Needed:
- **ESP32** (with USB cable)
- **DSK MH-RD** (Raindrop sensor module)
- **LCD I2C 1602** (16x2 LCD with I2C interface)
- **Power Supply MB102** (Optional for breadboard power)
- **Jumper Wires** (Male-to-female and male-to-male, preferably 10CM)
- **Breadboard** (400-point for easy wiring)

## 2. Wiring Setup:
Here’s how to connect the devices to your ESP32:

### DSK MH-RD to ESP32:
- GND (RD) → GND (ESP32)
- VCC (RD) → 5V (ESP32)
- DO (RD) → GPIO 21 (ESP32)

### LCD I2C 1602 to ESP32:
- GND (LCD) → GND (ESP32)
- VCC (LCD) → 3.3V (ESP32) or 5V (since many I2C LCDs can work with either voltage)
- SDA (LCD) → GPIO 21 (ESP32)
- SCL (LCD) → GPIO 22 (ESP32)

> **Note:** Both the DSK MH-RD and LCD use the same I2C pins (SDA and SCL), so they are connected in parallel.

## 3. Code to Set Up and Display Time:
This code will initialize the RTC and LCD, set the current time (if necessary), and display the current date and time on the LCD.

```cpp
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

int bz = 23;   // Buzzer pin
int led = 19;  // LED pin
int rly = 5;   // Relay pin
int sensor_DO = 4;

LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  Serial.begin(9600);
  lcd.init();
  lcd.backlight(); 
  pinMode(sensor_DO, INPUT);
  pinMode(bz, OUTPUT);
  pinMode(led, OUTPUT);
  pinMode(rly, OUTPUT);
  
  lcd.setCursor(0, 0);
  lcd.print(" MONSTERCHIP");
  lcd.setCursor(0, 1);
  lcd.print(" INDONESIA");
  delay(2000);
  
  lcd.setCursor(0, 0);
  lcd.print("RAINDROPS SENSOR");
}

void loop() {
  int val = digitalRead(sensor_DO);
  Serial.print("Digital Output: ");
  Serial.println(val);
  
  if (val == 1) {
    digitalWrite(bz, LOW);
    digitalWrite(led, LOW);
    digitalWrite(rly, HIGH);
    lcd.setCursor(0, 1);
    lcd.print(" Status: Dry ");
  } else {
    digitalWrite(bz, HIGH);
    digitalWrite(led, HIGH);
    digitalWrite(rly, LOW);
    lcd.setCursor(0, 1);
    lcd.print(" Status: Wet ");
  }
}
```

please consider the if else parameter with the condition from your sensor