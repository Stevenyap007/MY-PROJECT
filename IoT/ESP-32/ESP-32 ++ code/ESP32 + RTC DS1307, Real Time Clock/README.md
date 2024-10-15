# Circuit Setup

## RTC DS1307 Connections:
- **VCC** → 3.3V (or 5V)  
- **GND** → GND  
- **SDA** → GPIO 21 (ESP32 I2C SDA)  
- **SCL** → GPIO 22 (ESP32 I2C SCL)  
- **Optional:** Add a CR2032 battery to the RTC module for backup.

### SDA (Data Line) - Possible Pins:
- GPIO 21 (Default SDA)  
- GPIO 13  
- GPIO 4  
- GPIO 15  
- GPIO 25  
- GPIO 26  

### SCL (Clock Line) - Possible Pins:
- GPIO 22 (Default SCL)  
- GPIO 14  
- GPIO 16  
- GPIO 5  
- GPIO 17  
- GPIO 18  

---

# Arduino Code

Below is a code example using the **Wire** library and the **RTClib** to read real-time data.

### Install Libraries:
1. Go to **Tools > Manage Libraries**.  
2. Search and install **RTClib by Adafruit**.

```cpp
#include <Wire.h>
#include "RTClib.h"

// Create RTC object
RTC_DS1307 rtc;

void setup() {
  Serial.begin(115200);  // Initialize serial communication
  Wire.begin(21, 22);    // Initialize I2C on ESP32 pins

  if (!rtc.begin()) {
    Serial.println("Couldn't find RTC");
    while (1);  // Halt the program if RTC isn't found
  }

  if (!rtc.isrunning()) {
    Serial.println("RTC is not running, setting the time!");
    // Set the time (YYYY, MM, DD, HH, MM, SS)
    rtc.adjust(DateTime(2024, 10, 14, 12, 0, 0));  // Replace with your current date and time
  }
}

void loop() {
  DateTime now = rtc.now();  // Get the current time

  // Print time and date to Serial Monitor
  Serial.print(now.year(), DEC);
  Serial.print('/');
  Serial.print(now.month(), DEC);
  Serial.print('/');
  Serial.print(now.day(), DEC);
  Serial.print(" ");
  Serial.print(now.hour(), DEC);
  Serial.print(':');
  Serial.print(now.minute(), DEC);
  Serial.print(':');
  Serial.print(now.second(), DEC);
  Serial.println();

  delay(1000);  // Update every second
}
```

# Explanation
## Setup Phase:
Initializes the RTC and sets the I2C communication pins.
If the RTC isn't running, the code sets the initial time (you can modify it to your current time).

## Loop Phase:
Every second, the program fetches and prints the current time and date via the Serial Monitor.

# How to Run
Open the Arduino IDE.
Connect the ESP32 to your computer.
Select the correct board and port from the Tools menu.
Upload the code.
Open the Serial Monitor to see the real-time data.