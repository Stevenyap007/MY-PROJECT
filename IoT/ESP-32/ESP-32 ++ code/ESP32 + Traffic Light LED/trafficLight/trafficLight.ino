// Define pin numbers for the LEDs
const int redLed = 23;
const int yellowLed = 22;
const int greenLed = 21;

void setup() {
  // Initialize serial communication
  Serial.begin(115200);

  // Set LED pins as output
  pinMode(redLed, OUTPUT);
  pinMode(yellowLed, OUTPUT);
  pinMode(greenLed, OUTPUT);
}

void loop() {
  // Red light on
  digitalWrite(redLed, HIGH);
  digitalWrite(yellowLed, LOW);
  digitalWrite(greenLed, LOW);
  Serial.println("Red Light ON");
  delay(5000); // Red light duration (5 seconds)

  // Yellow light on
  digitalWrite(redLed, LOW);
  digitalWrite(yellowLed, HIGH);
  digitalWrite(greenLed, LOW);
  Serial.println("Yellow Light ON");
  delay(2000); // Yellow light duration (2 seconds)

  // Green light on
  digitalWrite(redLed, LOW);
  digitalWrite(yellowLed, LOW);
  digitalWrite(greenLed, HIGH);
  Serial.println("Green Light ON");
  delay(5000); // Green light duration (5 seconds)

  // Yellow light on again before red
  digitalWrite(redLed, LOW);
  digitalWrite(yellowLed, HIGH);
  digitalWrite(greenLed, LOW);
  Serial.println("Yellow Light ON");
  delay(2000); // Yellow light duration (2 seconds)
}
