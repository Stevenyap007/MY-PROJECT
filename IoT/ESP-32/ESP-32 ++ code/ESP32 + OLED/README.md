# **ESP32 + OLED Display Guide**

## **1. Components Required**
- **ESP32 Development Board**
- **0.96" OLED Display (SSD1306, 128x64)**
- **Jumper wires**
- **USB Cable**

---

## **2. Wiring Diagram**
### **Connect the OLED to ESP32 using I2C**
| OLED (SSD1306) | ESP32 |
|---------------|------|
| VCC | 3.3V |
| GND | GND |
| SDA | GPIO 21 |
| SCL | GPIO 22 |

---

## **3. Install Required Libraries**
Before uploading the code, ensure you have the necessary libraries installed in the **Arduino IDE**.

### **Steps to Install Libraries**
1. Open **Arduino IDE**.
2. Go to **Sketch** → **Include Library** → **Manage Libraries**.
3. Search for **Adafruit SSD1306** and install it.
4. Search for **Adafruit GFX Library** and install it.

---

## **4. Arduino Code for ESP32 + OLED**
This is the code you provided, which initializes the OLED and displays a simple message.

```cpp
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
```

---
## **5. Uploading the Code**
1. Connect your **ESP32** to your computer using a USB cable.
2. Open **Arduino IDE** and select the correct board:
   - **Tools** → **Board** → **ESP32 Dev Module**
   - **Tools** → **Port** → Select the correct COM port
3. Click the **Upload** button.

---

## **6. Explanation of the Code**
- The **Adafruit_SSD1306** library is used to control the OLED.
- The display is initialized using `display.begin(SSD1306_SWITCHCAPVCC, 0x3C)`, where `0x3C` is the I2C address.
- `display.setTextSize(1);` sets the font size.
- `display.setTextColor(SSD1306_WHITE);` sets the text color.
- `display.setCursor(0, 0);` positions the text at the top-left corner.
- `display.println(F("Hello, ESP32!"));` prints text on the screen.
- `display.display();` refreshes the OLED to show the text.

---

## **7. Troubleshooting Tips**
- **Nothing appears on the screen?**
  - Double-check the **I2C connections** (SDA → GPIO 21, SCL → GPIO 22).
  - Ensure your **OLED is powered (VCC to 3.3V, GND to GND)**.
  - Try running an **I2C scanner** to check if the OLED address is `0x3C`.

- **Text is not clear?**
  - Increase the text size using `display.setTextSize(2);`
  - Adjust the **contrast** by modifying the font color.

---

This guide should get you started with using an ESP32 and an **OLED display**! Let me know if you need further modifications or explanations. 🚀
