#include <WiFi.h>               // For ESP32 Wi-Fi functionality
#include <DHT.h>                // DHT sensor library

// Replace with your network credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Set DHT sensor type and GPIO pin
#define DHTPIN 4       // Pin where the data line of DHT sensor is connected
#define DHTTYPE DHT11  // Change to DHT22 if you're using that sensor
DHT dht(DHTPIN, DHTTYPE);

// Create web server object on port 80
WiFiServer server(80);

// Variables to store temperature and humidity readings
float temperature;
float humidity;

void setup() {
  Serial.begin(115200);           // Start serial communication
  dht.begin();                    // Initialize the DHT sensor

  // Connect to Wi-Fi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }

  // Print the ESP32 IP address
  Serial.println("WiFi connected!");
  Serial.print("ESP32 IP Address: ");
  Serial.println(WiFi.localIP());

  // Start the web server
  server.begin();
}

void loop() {
  // Check if a client has connected
  WiFiClient client = server.available();
  
  if (client) {
    Serial.println("New Client.");
    String currentLine = "";
    
    // Loop while the client is connected
    while (client.connected()) {
      if (client.available()) {
        char c = client.read();
        Serial.write(c);

        // If the byte is a newline character, check the request
        if (c == '\n') {
          // Check if the client request is a GET request for "/"
          if (currentLine.length() == 0) {
            // Read the temperature and humidity from the DHT sensor
            temperature = dht.readTemperature();   // Read temperature in Celsius
            humidity = dht.readHumidity();         // Read humidity

            // Check if readings are valid
            if (isnan(temperature) || isnan(humidity)) {
              Serial.println("Failed to read from DHT sensor!");
            }

            // Respond with HTML content
            client.println("HTTP/1.1 200 OK");
            client.println("Content-type:text/html");
            client.println("Connection: close");
            client.println();
            
            // HTML content with auto-refresh (6 seconds)
            client.println("<html>");
            client.println("<head><meta http-equiv='refresh' content='6'></head>");
            client.println("<body><h1>ESP32 Web Server</h1>");
            client.println("<p>Temperature: " + String(temperature) + " °C</p>");
            client.println("<p>Humidity: " + String(humidity) + " %</p>");
            client.println("</body></html>");
            
            client.println();
            break;
          }
          currentLine = "";
        } else if (c != '\r') {
          // Add character to the currentLine
          currentLine += c;
        }
      }
    }
    // Close the connection
    client.stop();
    Serial.println("Client disconnected.");
  }
}
