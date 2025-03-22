#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define OLED_ADDRESS 0x3C   // I2C address of the OLED

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

void setup() {
    Serial.begin(115200);
    display.begin(OLED_ADDRESS, OLED_ADDRESS); // Use OLED_ADDRESS directly
    display.clearDisplay();
    display.setTextColor(SSD1306_WHITE);
}

void loop() {
    // Clear the display
    display.clearDisplay();

    // Simulate audio levels with random values
    for (int i = 0; i < SCREEN_WIDTH; i += 10) {
        int audioLevel = random(0, SCREEN_HEIGHT);  // Generate a random audio level

        // Draw a vertical bar for each random level
        display.fillRect(i, SCREEN_HEIGHT - audioLevel, 8, audioLevel, SSD1306_WHITE);
    }
    
    // Optionally, display a label
    display.setCursor(0, 0);
    display.print("Simulated Audio Visualization");
    
    // Update the display
    display.display();
    delay(200);  // Small delay for readability
}
