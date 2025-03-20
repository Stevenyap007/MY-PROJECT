#include <LiquidCrystal_I2C.h>
#define wlS 15 // Water level sensor on GPIO 15
#define bz 23  // Buzzer on GPIO 23

// LCD setup
LiquidCrystal_I2C lcd(0x27, 16, 2); 

// Variables for state management
String fNilai = "";
unsigned long previousMillis = 0;
const long interval = 100;

void setup() {
  // Initialize serial monitor
  Serial.begin(9600);

  // Set pin modes
  pinMode(wlS, INPUT);
  pinMode(bz, OUTPUT);

  // Initialize LCD
  lcd.init(); 
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Hello World");
  delay(2000);  // Pause for readability
  lcd.clear();
}

void loop() {
  // Read analog value from the water level sensor
  int val = analogRead(wlS);
  String nilai = String(val);  // Convert value to string for LCD display

  // Update the display only if the value changes or the interval passes
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    if (fNilai != nilai) {
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Level: " + nilai);
      fNilai = nilai;  // Store the last displayed value
    }
  }

  // Control buzzer based on water level
  if (val < 200) {
    digitalWrite(bz, LOW);  // Turn off the buzzer
  } else {
    digitalWrite(bz, HIGH);  // Turn on the buzzer
  }
}
