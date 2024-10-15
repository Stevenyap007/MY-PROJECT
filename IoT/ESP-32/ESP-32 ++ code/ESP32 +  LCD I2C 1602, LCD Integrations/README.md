# Components Needed
- **ESP32 board**  
- **LCD I2C 1602**  
- **4-pin Jumper wires (10CM Female-to-Female)**  
- **Breadboard (optional)**  
- **Power source for ESP32 (via USB)**  

---

# Wiring

Connect the LCD I2C module to the ESP32 using the following pins:

| LCD I2C Pin | ESP32 Pin |
|-------------|-----------|
| VCC         | 3.3V      |
| GND         | GND       |
| SDA         | GPIO 21   |
| SCL         | GPIO 22   |

### Other Potential GPIO Alternatives:
- **GPIO 16 (SCL)** and **GPIO 17 (SDA)**: Versatile and available for I2C communication.  
- **GPIO 4 (SDA)** and **GPIO 5 (SCL)**: Common choices for various ESP32 projects.  
- **GPIO 25 (SDA)** and **GPIO 26 (SCL)**: Less common but still valid for I2C.  
- **GPIO 32 (SDA)** and **GPIO 33 (SCL)**: Useful if other default GPIOs are occupied.  

---

# Install Required Libraries

### Wire Library:
- Already included with the Arduino IDE, so no need to install it.

### LiquidCrystal I2C Library:
1. Open the **Arduino IDE**.  
2. Go to **Sketch > Include Library > Manage Libraries**.  
3. In the Library Manager, search for **"LiquidCrystal I2C"**.  
4. Install the library by **Frank de Brabander** (a common choice for LCDs with I2C).

---

# Code Example

Here is a simple code to test the LCD display:

```cpp
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Initialize the LCD with the I2C address 0x27 for a 16x2 display
LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  // Start serial communication for debugging
  Serial.begin(115200);
  
  // Initialize the LCD
  Serial.println("Initializing LCD...");
  lcd.init();  // Set up the LCD's number of columns and rows
  Serial.println("LCD Initialized");

  // Turn on the backlight
  Serial.println("Turning on backlight...");
  lcd.backlight();
  Serial.println("Backlight On");

  // Print messages on the LCD
  Serial.println("Printing to the LCD...");
  lcd.setCursor(0, 0);  // Set cursor to first row, first column
  lcd.print("Hello, World!");  // Print message on the first row
  Serial.println("First row printed: 'Hello, World!'");

  lcd.setCursor(0, 1);  // Set cursor to second row, first column
  lcd.print("ESP32 Test");  // Print message on the second row
  Serial.println("Second row printed: 'ESP32 Test'");
}

void loop() {
  // Nothing to do here
}
```


# Explanation
lcd.init();: Sets up the LCD's number of columns and rows (16x2).
lcd.backlight();: Turns on the LCD backlight.
lcd.setCursor(x, y);: Sets the cursor to a specific position on the LCD (x: column, y: row).
lcd.print("text");: Prints text on the LCD.


# Uploading the Code
Open the Arduino IDE.
Select your ESP32 board (Tools > Board > ESP32 Dev Module).
Select the correct COM port (Tools > Port).
Upload the code by clicking the Upload button.