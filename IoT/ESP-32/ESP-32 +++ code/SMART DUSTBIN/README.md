# **Guide for Smart Dustbin IoT Project Using ESP32**

This project creates a **smart dustbin** that automatically opens its lid when someone approaches. It uses an **ultrasonic sensor (HC-SR04)** to measure distance, a **servo motor** to open/close the lid, an **LCD display** to show distance, an **LED** for indication, and a **buzzer** for alerts.

---

## **1. Components Needed**
1. **ESP32** - Microcontroller
2. **HC-SR04** - Ultrasonic sensor (for detecting object distance)
3. **Servo Motor** - Moves the lid
4. **LiquidCrystal I2C Display (16x2)** - Displays distance
5. **LED (optional)** - Turns on when dustbin opens
6. **Buzzer (optional)** - Beeps when someone is close
7. **Jumper wires** - For connections

---

## **2. Understanding the Code**
### **Libraries Used**
- `Wire.h`: For I2C communication with the LCD.
- `LiquidCrystal_I2C.h`: Controls the LCD.
- `ESP32Servo.h`: For controlling the servo motor.

### **Pin Assignments**
- `trigPin (5)`: Sends the signal for the ultrasonic sensor.
- `echoPin (18)`: Receives the signal back.
- `LED (19)`: Turns on when the dustbin is open.
- `BUZ (23)`: Turns on the buzzer when someone is detected.
- `Servo (pin 4)`: Moves the dustbin lid.

---

## **3. How the Code Works**
### **(A) Setup Function**
1. **Initialize Components**
   - Attach the servo motor to pin 4.
   - Set the mode of pins (`INPUT` for `echoPin`, `OUTPUT` for `trigPin`, `LED`, `BUZ`).
   - Initialize the LCD.
   - Display "Hello World" for 2 seconds.
   - Clear the LCD and show "ULTRASERVO".

### **(B) Loop Function**
1. **Measure Distance Using Ultrasonic Sensor**
   - Send a short HIGH pulse to `trigPin` (10 µs).
   - Read the time taken for the sound wave to return (`pulseIn(echoPin, HIGH)`).
   - Convert this time into **distance in cm**.

2. **Display Distance on LCD**
   - Clear previous distance and update the display.

3. **Control the Servo, LED, and Buzzer**
   - If **distance < 20 cm**, open the lid (servo at 0°), turn on LED and buzzer.
   - Else, close the lid (servo at 180°), turn off LED and buzzer.

---

## **4. Wiring Guide**
| Component       | ESP32 Pin |
|---------------|----------|
| HC-SR04 Trig  | GPIO 5   |
| HC-SR04 Echo  | GPIO 18  |
| Servo Signal  | GPIO 4   |
| LED           | GPIO 19  |
| Buzzer        | GPIO 23  |
| LCD SDA       | GPIO 21  |
| LCD SCL       | GPIO 22  |

---

## **5. Code**
```cpp
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
```
