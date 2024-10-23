#include <WiFi.h>  // ESP32 uses WiFi.h, not ESP8266WiFi.h

const char* ssid = "YOUR_WIFI_SSID";   // Replace with your WiFi SSID
const char* password = "YOUR_WIFI_PASSWORD"; // Replace with your WiFi Password

int ledPin = 2;  // Built-in LED pin (usually GPIO2 on ESP32)
WiFiServer server(80);     // Start a server on port 80

void setup() {
  Serial.begin(115200);
  delay(10);

  // Set LED pin as output and turn it off
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);

  // Connect to WiFi
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println();
  Serial.println("WiFi connected");
  
  // Start the server
  server.begin();
  Serial.println("Server started");

  // Print the IP address
  Serial.print("Use this URL to connect: ");
  Serial.print("http://");
  Serial.print(WiFi.localIP());
  Serial.println("/");
}

void loop() {
  // Check if a client has connected
  WiFiClient client = server.available();
  if (!client) {
    return;
  }

  // Wait until the client sends some data
  Serial.println("New client connected");
  while (!client.available()) {
    delay(1);
  }

  // Read the request
  String request = client.readStringUntil('\r');
  Serial.println(request);
  client.flush();

  // Handle the request
  int value = LOW;
  if (request.indexOf("/LED=ON") != -1) {
    digitalWrite(ledPin, HIGH);
    value = HIGH;
  }
  if (request.indexOf("/LED=OFF") != -1) {
    digitalWrite(ledPin, LOW);
    value = LOW;
  }

  // Prepare the response
  client.println("HTTP/1.1 200 OK");
  client.println("Content-Type: text/html");
  client.println();  // Important, do not forget this line
  client.println("<!DOCTYPE HTML>");
  client.println("<html>");
  
  // LED status display
  client.print("LED is now: ");
  if (value == HIGH) {
    client.print("ON");
  } else {
    client.print("OFF");
  }
  
  // Buttons to control LED
  client.println("<br><br>");
  client.println("<a href=\"/LED=ON\"><button>Turn ON LED</button></a>");
  client.println("<a href=\"/LED=OFF\"><button>Turn OFF LED</button></a><br/>");
  client.println("</html>");
  
  delay(1);
  Serial.println("Client disconnected");
}
