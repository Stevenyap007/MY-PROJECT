#include <WiFi.h>

// Define the network credentials (name and password for the AP)
const char* ssid = "ESP32_Hotspot";
const char* password = "12345678";  // Password must be at least 8 characters

void setup() {
  Serial.begin(115200);  // Start serial communication

  // Set ESP32 to Wi-Fi Access Point mode
  WiFi.softAP(ssid, password);
  
  // Get the IP address assigned to the ESP32 in AP mode
  IPAddress IP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(IP);  // Print the IP address to the Serial Monitor

  // Start the web server to serve a basic page
  WiFiServer server(80);
  server.begin();
  Serial.println("Server started");

  while (true) {  // Keep the server running
    WiFiClient client = server.available();  // Check if a client connects
    if (client) {
      Serial.println("Client connected");
      client.println("HTTP/1.1 200 OK");
      client.println("Content-Type: text/html");
      client.println();  // End of headers
      client.println("<!DOCTYPE HTML>");
      client.println("<html><h1>Hello from ESP32</h1></html>");
      delay(1);
      client.stop();  // Close the connection
      Serial.println("Client disconnected");
    }
  }
}

void loop() {
  // No need to use loop() in this example, all logic is in setup().
}
