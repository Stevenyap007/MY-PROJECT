# Download link
   ```
   https://drive.google.com/file/d/1AzYYWvQLamMcQZ2QmIk7ehWy7Nr10ml5/view?usp=drivesdk
   https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers
   https://www.arduino.cc/en/software
   ```


# ESP32 Setup and Basic Blink Example

## 1. Install ESP32 in Arduino IDE
1. Open Arduino IDE.
2. Go to **File > Preferences**.
3. In the **Additional Boards Manager URLs**, add the following URL:
   
   ```
   https://dl.espressif.com/dl/package_esp32_index.json
   ```

4. Click **OK**.
5. Next, go to **Tools > Board > Boards Manager**.
6. Search for **ESP32** and install the package.

## 2. Select the ESP32 Board
1. Go to **Tools > Board**, and choose **ESP32 Dev Module** (or the specific ESP32 model you're using).

## 3. Connect NodeMCU ESP32 to Computer
1. Use a USB cable to connect the ESP32 to your computer.
2. Check the port in **Tools > Port**, and select the correct one.

## 4. Basic Code Example
Here’s a simple code to test the ESP32 with an LED blink example:

```cpp
void setup() {
  pinMode(2, OUTPUT); // Pin 2 is the built-in LED on most ESP32 boards
}

void loop() {
  digitalWrite(2, HIGH);  // Turn the LED on
  delay(1000);            // Wait for a second
  digitalWrite(2, LOW);   // Turn the LED off
  delay(1000);            // Wait for a second
}
```

Upload the sketch by clicking on the **Upload** button.

## 5. Monitor Serial Output
1. Open the **Serial Monitor** (Ctrl+Shift+M), and set the baud rate to **115200** to see any serial outputs from the ESP32.
