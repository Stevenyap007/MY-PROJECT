# Connecting and Using the HC-SR04 Ultrasonic Sensor with ESP32

## Components Needed
- ESP32 development board
- HC-SR04 ultrasonic sensor
- Jumper wires (10CM male-to-male)
- Power Supply MB102 (Optional for breadboard power)
- Breadboard (optional)

## Pin Connections

| HC-SR04 Pin | ESP32 Pin |
|-------------|-----------|
| VCC         | 5V        |
| GND         | GND       |
| Trig        | GPIO 18   |
| Echo        | GPIO 5    |

## Code Example

```cpp
#define echoPin 18 // attach pin D2 Arduino to pin Echo of HC-SR04
#define trigPin 5 //attach pin D3 Arduino to pin Trig of HC-SR04

// defines variables
long duration; // variable for the duration of sound wave travel
int distance;  // variable for the distance measurement

void setup() {
  pinMode(trigPin, OUTPUT);  // Sets the trigPin as an OUTPUT
  pinMode(echoPin, INPUT);   // Sets the echoPin as an INPUT
  Serial.begin(9600);        // Serial Communication starts with 9600 baudrate speed
  Serial.println("Ultrasonic Sensor HC-SR04 Test"); // print text to Serial Monitor
  Serial.println("with Arduino UNO R3");
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
  
  // Displays the distance on the Serial Monitor
  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" cm");
}
```

## How It Works
The HC-SR04 sensor sends an ultrasonic pulse from the Trig pin and listens for an echo on the Echo pin. The time it takes for the echo to return is converted into a distance measurement.
