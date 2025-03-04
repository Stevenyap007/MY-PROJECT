#define RELAY_PIN 5  // Pin connected to the relay module
#define LED_PIN 23   // Pin connected to the LED

void setup() {
  pinMode(RELAY_PIN, OUTPUT);  // Set relay pin as an output
  pinMode(LED_PIN, OUTPUT);     // Set LED pin as an output
  digitalWrite(RELAY_PIN, LOW);  // Initialize relay as off (LOW)
  digitalWrite(LED_PIN, LOW);     // Initialize LED as off (LOW)
}

void loop() {
  digitalWrite(RELAY_PIN, HIGH);  // Turn relay on
  digitalWrite(LED_PIN, HIGH);     // Turn LED on
  delay(2000);                     // Wait for 2 seconds
  digitalWrite(RELAY_PIN, LOW);   // Turn relay off
  digitalWrite(LED_PIN, LOW);      // Turn LED off
  delay(2000);                     // Wait for 2 seconds
}
