#include <WiFi.h>

// Replace with your network credentials
const char* ssid = "YourWifiName";
const char* password = "YourWiFiPass";

void setup() {
  // Start the Serial communication to see the log in the Serial Monitor
  Serial.begin(115200);

  // Connecting to Wi-Fi
  Serial.println("Connecting to Wi-Fi...");
  WiFi.begin(ssid, password);

  // Wait until the ESP32 is connected to Wi-Fi
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting...");
  }

  // When connected, print the local IP address
  Serial.println("Connected to Wi-Fi!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // Your loop code can go here
}
