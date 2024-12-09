#define LDR_AO_PIN 34  // Analog output connected to GPIO34
#define LDR_DO_PIN 23  // Digital output connected to GPIO23    

void setup() {
  pinMode(LDR_DO_PIN, INPUT);  // Set DO pin as input

  Serial.begin(115200);        // Start Serial communication
}

void loop() {
  // Read analog value from AO pin
  int ldrValue = analogRead(LDR_AO_PIN);
  Serial.print("Analog Value: ");
  Serial.println(ldrValue);

  // Read digital state from DO pin
  int doState = digitalRead(LDR_DO_PIN);
  Serial.print("Digital State: ");
  Serial.println(doState);

  delay(1000);  // Delay 1 second
}
