#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// Define the dimensions of the OLED display
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

// Create an SSD1306 object
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

void setup() {
  // Initialize the display
  display.begin(SSD1306_SWITCHCAPVCC, 0x3C); // Initialize with I2C address 0x3C, Change address if necessary
  display.clearDisplay();
  
  // Display static text
  display.setTextSize(1);      
  display.setTextColor(SSD1306_WHITE);  
  display.setCursor(0, 0);     
  display.println(F("Hello, ESP32!"));
  
  // Show the display
  display.display();
}

void loop() {
  // You can add more code here to update the display dynamically
}
