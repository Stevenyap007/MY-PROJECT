#include <Wire.h>
#include <LiquidCrystal_I2C.h>

#define echoPin 18 // Attach pin D18 to Echo of HC-SR04
#define trigPin 5  // Attach pin D5 to Trig of HC-SR04

LiquidCrystal_I2C lcd(0x27, 16, 2); // Change the address if needed

long duration; // Variable for the duration of sound wave travel
int distance;  // Variable for the distance measurement

void setup() {
  pinMode(trigPin, OUTPUT); // Sets the trigPin as an OUTPUT
  pinMode(echoPin, INPUT);  // Sets the echoPin as an INPUT

  lcd.init();                // Initialize the LCD
  // lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Hello");
  lcd.setCursor(0, 1);
  lcd.print("World");
  delay(2000);
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("        ^_^        ");
}

void loop() {
  // Clears the trigPin condition
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  
  // Sets the trigPin HIGH (ACTIVE) for 10 microseconds
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  // Reads the echoPin, returns the sound wave travel time in microseconds
  duration = pulseIn(echoPin, HIGH);
  
  // Calculating the distance
  distance = duration * 0.034 / 2; // Speed of sound wave divided by 2 (go and back)
  
  // Clear the previous distance value
  lcd.setCursor(0, 1);
  lcd.print("Distance:     "); // Ensure the line is cleared
  
  // Print the current distance
  lcd.setCursor(9, 1);
  lcd.print(distance);
  lcd.print(" cm  "); // Add some spaces to overwrite any old value
}
