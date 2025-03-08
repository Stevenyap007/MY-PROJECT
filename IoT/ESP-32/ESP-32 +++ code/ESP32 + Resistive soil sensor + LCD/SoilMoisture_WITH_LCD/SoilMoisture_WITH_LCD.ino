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
