// Define the touch pin (T3 = GPIO15)
#define TOUCH_PIN 15  

// Threshold value: adjust based on your environment
int touchThreshold = 30;  

void setup() {
  Serial.begin(115200);  // Start serial communication
  delay(1000);  // Wait for setup stabilization
  Serial.println("ESP32 Touch Sensor Test");
}

void loop() {
  // Read touch value from the touch pin
  int touchValue = touchRead(TOUCH_PIN);  
  Serial.print("Touch Value: ");
  Serial.println(touchValue);  

  // Check if the value is below the threshold (i.e., touched)
  if (touchValue < touchThreshold) {
    Serial.println("Touched!");
  }

  delay(500);  // Delay to avoid flooding the Serial Monitor
}



// alternative pin
// Touch Pins: T0 - T9  
// T0 = GPIO4  
// T1 = GPIO0  
// T2 = GPIO2  
// T3 = GPIO15  
// T4 = GPIO13  
// T5 = GPIO12  
// T6 = GPIO14  
// T7 = GPIO27  
// T8 = GPIO33  
// T9 = GPIO32  
