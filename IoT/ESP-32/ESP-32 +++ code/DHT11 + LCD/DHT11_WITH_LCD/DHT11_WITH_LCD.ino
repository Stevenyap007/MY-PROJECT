#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include "DHT.h"

#define DHTPIN 4        // Pin DHT11 dihubungkan ke pin GPIO 4
#define DHTTYPE DHT11   // Tipe sensor DHT

// Set alamat I2C serta jenis LCD
LiquidCrystal_I2C lcd(0x27, 16, 2); // Alamat I2C adalah 0x27
DHT dht(DHTPIN, DHTTYPE);           // Menginisialisasi DHT sensor

void setup() {
  Serial.begin(115200); // Start serial communication
  lcd.init();         // Inisialisasi LCD
  dht.begin();        // Inisialisasi DHT11 sensor
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.backlight();
  lcd.print(F("Hello World"));
  delay(2000);        // Jeda 2 detik untuk stabilisasi
}

void loop() {
  float h = dht.readHumidity();     // Baca kelembaban dalam RH (%)
  float t = dht.readTemperature();  // Baca suhu dalam Celcius (default)

  // Cek pembacaan dan komunikasi dengan DHT11
  if (isnan(h) || isnan(t)) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print(F("GAGAL MEMBACA"));
    return; // Cek semua pembacaan
  }

  // Tampilkan suhu dan kelembaban
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Temp = ");
  lcd.print(t); // Tampilkan suhu dalam Celcius
  lcd.print("'C");
  lcd.setCursor(0, 1);
  lcd.print("Humd = "); // Tampilkan kelembaban udara
  lcd.print(h);
  lcd.print("% ");
  delay(2000); // Delay untuk pembacaan berikutnya

  // Optional: Print to Serial Monitor for debugging
  // Serial.print("Temperature = ");
  // Serial.print(t);
  // Serial.print("°C | ");
  // Serial.print("Humidity = ");
  // Serial.print(h);
  // Serial.println("% ");
}
