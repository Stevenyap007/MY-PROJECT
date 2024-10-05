#include <Wire.h>
#include <LiquidCrystal_I2C.h>
int bz = 23;   // Buzzer pin
int led = 19;  // LED pin
int rly = 5;  // Relay pin
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