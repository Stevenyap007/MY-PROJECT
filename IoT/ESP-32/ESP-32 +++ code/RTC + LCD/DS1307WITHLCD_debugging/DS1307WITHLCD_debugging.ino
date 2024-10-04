#include <LiquidCrystal_I2C.h>
#include <Wire.h>
#include "RTClib.h"

RTC_DS1307 rtc;
LiquidCrystal_I2C lcd(0x27, 16, 2);  // I2C address for the LCD

char namaHari[7][12] = {"Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"};

void setup() {
  // Start Serial for debugging
  Serial.begin(115200);
  Serial.println("Starting...");

  // Initialize the LCD
  Serial.println("Initializing LCD...");
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print(" MONSTERCHIP");
  lcd.setCursor(0, 1);
  lcd.print(" INDONESIA");
  delay(2000);
  lcd.clear();
  Serial.println("LCD initialized successfully.");

  // Initialize the RTC
  Serial.println("Initializing RTC...");
  if (!rtc.begin()) {
    Serial.println("Couldn't find RTC. Check wiring.");
    lcd.setCursor(0, 0);
    lcd.print("RTC not found");
    while (1);  // Stop the program here if RTC is not found
  }

  // Check if RTC is running
  if (!rtc.isrunning()) {
    Serial.println("RTC is NOT running! Setting time.");
    lcd.setCursor(0, 0);
    lcd.print("RTC not running");

    // Uncomment the following line if you want to set the RTC to the time when the sketch is compiled.
    // rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
  }

  Serial.println("RTC initialized successfully.");
}

void loop() {
  // Get current time from the RTC
  DateTime now = rtc.now();
  Serial.print("Current time: ");
  Serial.print(now.hour());
  Serial.print(":");
  Serial.print(now.minute());
  Serial.print(":");
  Serial.println(now.second());

  // Display the day and date on the LCD
  lcd.setCursor(0, 0);
  lcd.print(namaHari[now.dayOfTheWeek()]);
  lcd.print(", ");
  lcd.print(now.day(), DEC);
  lcd.print("/");
  lcd.print(now.month(), DEC);
  lcd.print("/");
  lcd.print(now.year(), DEC);

  // Display the time on the LCD
  lcd.setCursor(0, 1);
  lcd.print("Time: ");
  lcd.print(now.hour(), DEC);
  lcd.print(":");
  lcd.print(now.minute(), DEC);
  lcd.print(":");
  lcd.print(now.second(), DEC);

  delay(1000);  // Update every second
}
