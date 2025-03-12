#include <LiquidCrystal_I2C.h>
#include <Wire.h>

const int soundpin = 2;  // Sound sensor input pin
const int bzpin = 5;      // Buzzer pin
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
