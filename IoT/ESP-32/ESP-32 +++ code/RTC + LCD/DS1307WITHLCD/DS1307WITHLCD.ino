#include <LiquidCrystal_I2C.h>
#include <Wire.h>
#include "RTClib.h"
RTC_DS1307 rtc;
LiquidCrystal_I2C lcd(0x27, 16, 2);

char namaHari[7][12] = {"Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"};

void setup () {
  // while (!Serial); // for Leonardo/Micro/Zero
  Serial.begin(9600);
  // lcd.begin(16, 2);
  lcd.init(); 
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print(" MONSTERCHIP");
  lcd.setCursor(0, 1);
  lcd.print(" INDONESIA");
  delay(2000);
  lcd.clear();
  if (! rtc.begin()) {
  Serial.println("Couldn't find RTC");
  while (1);
  }
  if (! rtc.isrunning()) {
  Serial.println("RTC is NOT running!");
  }
}
void loop () {
  DateTime now = rtc.now();
  lcd.setCursor(0, 0);
  lcd.print(namaHari[now.dayOfTheWeek()]);
  lcd.print(", ");
  lcd.print(now.day(), DEC);
  lcd.print("/");
  lcd.print(now.month(), DEC);
  lcd.print("/");
  lcd.print(now.year(), DEC);
  lcd.setCursor(0, 1);
  lcd.print("Time: ");
  lcd.print(now.hour(), DEC);
  lcd.print(":");
  lcd.print(now.minute(), DEC);
  lcd.print(":");
  lcd.print(now.second(), DEC);
  lcd.print(" ");
}