#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <ESP32Servo.h> // Use the ESP32 compatible Servo library

#define echoPin 18 // attach pin D2 Arduino to pin Echo of HC-SR04
#define trigPin 5  // attach pin D3 Arduino to pin Trig of HC-SR04
#define LED 19
#define BUZ 23

Servo servoku; // Declare the servo object
LiquidCrystal_I2C lcd(0x27, 16, 2); // I2C address and dimensions

long duration; // Duration of the sound wave travel
int distance; // Distance measurement

void setup() {
  servoku.attach(4); // Attach the servo to pin 4
  pinMode(trigPin, OUTPUT); // Set the trigPin as an OUTPUT
  pinMode(echoPin, INPUT); // Set the echoPin as an INPUT
  pinMode(LED, OUTPUT); // Set the LED as an OUTPUT
  pinMode(BUZ, OUTPUT); // Set the BUZ as an OUTPUT
  
  lcd.init(); // Initialize the LCD
  lcd.setCursor(0, 0);
  lcd.print(" Hello");
  lcd.setCursor(0, 1);
  lcd.print(" World");
  delay(2000);
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(" ULTRASERVO");
}

void loop() {
  // Clear the trigPin condition
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  
  // Set the trigPin HIGH (ACTIVE) for 10 microseconds
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  // Read the echoPin, return the sound wave travel time in microseconds
  duration = pulseIn(echoPin, HIGH);
  
  // Calculate the distance
  distance = duration * 0.034 / 2; // Speed of sound wave divided by 2 (go and back)
  
  lcd.setCursor(0, 1);
  lcd.print("Distance: ");
  lcd.setCursor(9, 1);
  lcd.print("     "); // Clear previous distance
  lcd.setCursor(9, 1);
  lcd.print(distance);
  lcd.print(" cm ");
  
  if (distance < 20) {
    servoku.write(0); // Move servo to 0 degrees
    digitalWrite(LED, HIGH); // Turn on LED
    digitalWrite(BUZ, HIGH); // Turn on buzzer
    delay(500);
  } else {
    servoku.write(180); // Move servo to 180 degrees
    digitalWrite(LED, LOW); // Turn off LED
    digitalWrite(BUZ, LOW); // Turn off buzzer
  }
}
