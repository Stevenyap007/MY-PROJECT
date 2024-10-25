#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Initialize the LCD with the I2C address 0x27 for a 16x2 display
LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  // Start serial communication for debugging
  Serial.begin(115200);
  
  // Initialize the LCD
  Serial.println("Initializing LCD...");
  // lcd.begin(16, 2);
  lcd.init();  // Set up the LCD's number of columns and rows
  Serial.println("LCD Initialized");

  // Turn on the backlight
  Serial.println("Turning on backlight...");
  lcd.backlight();
  Serial.println("Backlight On");

  // Print messages on the LCD
  Serial.println("Printing to the LCD...");
  lcd.setCursor(0, 0);  // Set cursor to first row, first column
  lcd.print("Hello, World!");  // Print message on the first row
  Serial.println("First row printed: 'Hello, World!'");

  lcd.setCursor(0, 1);  // Set cursor to second row, first column
  lcd.print("ESP32 Test");  // Print message on the second row
  Serial.println("Second row printed: 'ESP32 Test'");
}

void loop() {
  // Nothing to do here
}
