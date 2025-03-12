#include <ESP32Servo.h>  // Use the ESP32Servo library

Servo myServo;  // Create a servo object

int servoPin = 18;  // GPIO pin for the servo signal
int angle = 0;      // Store the servo angle

void setup() {
  myServo.attach(servoPin);  // Attach servo to GPIO 18
  Serial.begin(115200);      // Start serial communication
}

void loop() {
  // Sweep from 0° to 180°
  for (angle = 0; angle <= 180; angle += 1) {
    myServo.write(angle);  // Set servo to angle
    delay(15);  // Wait 15ms for smooth movement
  }

  // Sweep back from 180° to 0°
  for (angle = 180; angle >= 0; angle -= 1) {
    myServo.write(angle);  // Set servo to angle
    delay(15);  // Wait 15ms for smooth movement
  }
}
