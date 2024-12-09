# LDR (Light Dependent Resistor)

## Components Required
- **ESP32 WROOM-32**
- **LDR module** (or an LDR sensor with a 10kΩ resistor for voltage divider)
- **Breadboard**
- **Jumper wires** (10cm male-to-male)

## Wiring the LDR Module (AO and DO)
- **VCC** → ESP32 VIN  
- **GND** → ESP32 GND  
- **AO** → ESP32 GPIO34 (for analog readings)  
- **DO** → ESP32 GPIO23 (or any digital pin, for binary signal)

### For Analog Output (AO)
You need a pin with ADC (Analog to Digital Converter) capability to read the light intensity value. On the ESP32, not all GPIO pins support ADC, but here are the valid ADC-capable pins:

#### Recommended ADC Pins on ESP32:
- GPIO32
- GPIO33
- GPIO34
- GPIO35
- GPIO36 (also called VP)
- GPIO39 (also called VN)

**Important Note:**  
GPIO34, GPIO35, GPIO36, and GPIO39 are input-only pins (you can't use them for outputs like LEDs).  
These pins work perfectly for reading the AO signal from the LDR module.

### For Digital Output (DO)
The DO pin gives a binary (HIGH/LOW) signal, so you can connect it to any digital GPIO pin on the ESP32.

#### Recommended Digital Pins:
- GPIO23
- GPIO19
- GPIO18
- GPIO5
- GPIO4

#### Pins to Avoid:
- **GPIO0**: Used for boot mode; avoid unless you know what you're doing.  
- **GPIO2, GPIO15**: May interfere with the boot process.  
- **GPIO6–11**: Connected to the internal flash memory on most ESP32 boards—do not use.

---

## Example Code to Use Both AO and DO

```cpp
#define LDR_AO_PIN 34  // Analog output connected to GPIO34
#define LDR_DO_PIN 23  // Digital output connected to GPIO23

void setup() {
  pinMode(LDR_DO_PIN, INPUT);  // Set DO pin as input
  Serial.begin(115200);        // Start Serial communication
}

void loop() {
  // Read analog value from AO pin
  int ldrValue = analogRead(LDR_AO_PIN);
  Serial.print("Analog Value: ");
  Serial.println(ldrValue);

  // Read digital state from DO pin
  int doState = digitalRead(LDR_DO_PIN);
  Serial.print("Digital State: ");
  Serial.println(doState);

  delay(1000);  // Delay 1 second
}
```