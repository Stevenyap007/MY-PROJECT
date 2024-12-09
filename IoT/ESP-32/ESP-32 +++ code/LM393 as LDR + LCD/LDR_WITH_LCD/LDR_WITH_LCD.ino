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
