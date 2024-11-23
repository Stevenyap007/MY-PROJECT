#include <Wire.h>
#include <LiquidCrystal_I2C.h>

int Flame = 2;  // Pin for flame sensor
int Buz = 5;    // Pin for buzzer
LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  Serial.begin(9600);
  pinMode(Flame, INPUT);
  pinMode(Buz, OUTPUT);
  
  lcd.init();             // Use init() instead of begin()
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print(" Hello ");
  lcd.setCursor(0, 1);
  lcd.print(" World ");
  delay(2000);
  lcd.setCursor(0, 0);
  lcd.print(" FLAME SENSOR ");
}

void loop() {
  if (digitalRead(Flame) == HIGH) {  // Adjust based on your sensor's logic
    digitalWrite(Buz, HIGH);
    Serial.println("Flame Detected");
    lcd.setCursor(0, 1);
    lcd.print(" Flame Detected ");
  } else {
    digitalWrite(Buz, LOW);
    Serial.println("Flame Not Detected");
    lcd.setCursor(0, 1);
    lcd.print(" Not Detected    "); // Ensure enough spaces to clear old text
  }
}
