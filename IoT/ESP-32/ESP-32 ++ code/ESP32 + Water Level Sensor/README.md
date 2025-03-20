# Components Required
- **ESP32 (WROOM-32)**
- **Water Level Sensor**
- **Breadboard (optional)**
- **Jumper Wires (Female-to-Female)**
- **USB Cable for ESP32**

## Wiring Diagram

| Sensor Pin | ESP32 Pin |
|------------|------------|
| **+ (VCC)** | 3.3V or VIN |
| **- (GND)** | GND |
| **S (Signal)** | GPIO 32 or any analog pin |

> ⚠️ **Note:**  
> - If you power the sensor with VIN (5V), use a voltage divider on the signal pin to step down the output to 3.3V for safety.  
> - Without a voltage divider, using 3.3V power is safer for direct connections.

### Recommended Alternative Pins for Analog Input (ADC1)
- **GPIO 32**
- **GPIO 33**
- **GPIO 34** (input-only)
- **GPIO 35** (input-only)
- **GPIO 36** (also called **VP**)
- **GPIO 39** (also called **VN**)

## Upload the Code to ESP32
1. Connect the ESP32 to your computer via USB.
2. Press the **Upload** button in the Arduino IDE.
3. If the upload fails, press and hold the **BOOT** button on the ESP32 while uploading.

## Testing the Setup
1. Open the **Serial Monitor** (**Tools → Serial Monitor**) and set the baud rate to **115200**.
2. Immerse the sensor in water at different levels and observe the readings in the Serial Monitor.

## Troubleshooting
### **Incorrect or No Values**
- Check the connections.
- Ensure the ESP32 pin you selected supports analog input.

### **Inconsistent Values**
- Try using **GPIO 32** or **GPIO 33** instead of **GPIO 15**.
- Power the sensor using **3.3V** for better stability.

### **Upload Issues**
- Press and hold the **BOOT** button during upload.
- Check that the correct port is selected.
