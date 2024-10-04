# 1. Devices and Materials Needed:
- ESP32 (with USB cable)
- RTC DS1307 (Real-Time Clock module)
- LCD I2C 1602 (16x2 LCD with I2C interface)
- Power Supply MB102 (Optional for breadboard power)
- Jumper Wires (Male-to-female and male-to-male, preferably 10CM)
- Breadboard (400-point for easy wiring)

# 2. Wiring Setup:
Here’s how to connect the devices to your ESP32:

### RTC DS1307 to ESP32:
- GND (RTC) → GND (ESP32)
- VCC (RTC) → 3.3V (ESP32)
- SDA (RTC) → GPIO 21 (ESP32)
- SCL (RTC) → GPIO 22 (ESP32)

### LCD I2C 1602 to ESP32:
- GND (LCD) → GND (ESP32)
- VCC (LCD) → 3.3V (ESP32) or 5V (since many I2C LCDs can work with either voltage)
- SDA (LCD) → GPIO 21 (ESP32)
- SCL (LCD) → GPIO 22 (ESP32)

**Note:** Both the RTC and LCD use the same I2C pins (SDA and SCL), so they are connected in parallel.

# 3. Libraries Required:
You need to install the following libraries:

### RTClib for the RTC:
In Arduino IDE, go to **Sketch → Include Library → Manage Libraries** and search for "RTClib" by Adafruit.

### LiquidCrystal I2C for the LCD:
Search for "LiquidCrystal I2C" in the same Library Manager window.

# 4. Code to Set Up and Display Time:
This code will initialize the RTC and LCD, set the current time (if necessary), and display the current date and time on the LCD.

```cpp
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include "RTClib.h"

// Initialize RTC and LCD
RTC_DS1307 rtc;
LiquidCrystal_I2C lcd(0x27, 16, 2);  // Set LCD I2C address and size

char namaHari[7][12] = {"Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"};

void setup() {
  // Initialize Serial for debugging
  Serial.begin(9600);
  Serial.println("Starting...");

  // Initialize LCD
  lcd.init();  // Use init() for LCD with I2C
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print(" MONSTERCHIP");
  lcd.setCursor(0, 1);
  lcd.print(" INDONESIA");
  delay(2000);  // Wait for 2 seconds to display the message
  lcd.clear();

  // Initialize RTC
  if (!rtc.begin()) {
    Serial.println("Couldn't find RTC. Check wiring.");
    lcd.setCursor(0, 0);
    lcd.print("RTC not found");
    while (1);  // Stop if RTC is not found
  }

  if (!rtc.isrunning()) {
    Serial.println("RTC is NOT running! Setting the time...");
    // Set the time here only if the RTC is not running
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
    
    // Uncomment the following line to manually set time (adjust values as needed)
    // rtc.adjust(DateTime(2024, 10, 02, 20, 30, 0)); // Year, Month, Day, Hour, Minute, Second
  }

  Serial.println("RTC initialized.");
}

void loop() {
  // Get current time from RTC
  DateTime now = rtc.now();

  // Display the current day and date on the LCD
  lcd.setCursor(0, 0);
  lcd.print(namaHari[now.dayOfTheWeek()]);
  lcd.print(", ");
  lcd.print(now.day(), DEC);
  lcd.print("/");
  lcd.print(now.month(), DEC);
  lcd.print("/");
  lcd.print(now.year(), DEC);

  // Display the current time on the LCD
  lcd.setCursor(0, 1);
  lcd.print("Time: ");
  lcd.print(now.hour(), DEC);
  lcd.print(":");
  lcd.print(now.minute(), DEC);
  lcd.print(":");
  lcd.print(now.second(), DEC);

  // Output the time to the Serial Monitor
  Serial.print("Current time: ");
  Serial.print(now.hour());
  Serial.print(":");
  Serial.print(now.minute());
  Serial.print(":");
  Serial.println(now.second());

  delay(1000);  // Update the time every second
}

```
# 5. Key Points to Keep in Mind:
Power Supply: Both the RTC DS1307 and the LCD can be powered by 3.3V or 5V from the ESP32. Make sure that your power connections are stable.
Backup Battery for RTC: Ensure that the DS1307 module has a functioning CR2032 backup battery installed so that it keeps track of the time even when the main power is disconnected.
I2C Address: Make sure that the I2C address of the LCD (0x27 in this case) matches your specific module. If the I2C address is different, you can scan it using an I2C scanner sketch.

# 6. Troubleshooting:
If the LCD is not displaying anything:
Double-check your wiring, especially the SDA and SCL pins.
Make sure the lcd.init() is used instead of lcd.begin().
Check the I2C address using an I2C scanner tool to verify it's correct (0x27 for most I2C LCDs).

# 7. Conclusion:
With these steps, your ESP32 should now be able to display the current date and time on the LCD I2C 1602 by using the RTC DS1307. You can adjust the time manually or let the RTC sync automatically to the compilation time.
Feel free to experiment further or ask if you need additional details!
