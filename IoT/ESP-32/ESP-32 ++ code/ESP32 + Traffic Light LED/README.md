# **ESP32 Traffic Light LED System Guide**

## **Introduction**
This project simulates a basic traffic light system using an ESP32 and three LEDs (Red, Yellow, and Green). The ESP32 controls the lights in a sequence to mimic real-world traffic signals.

## **Components Required**
- **ESP32 Development Board**
- **3 x LEDs** (Red, Yellow, Green)
- **3 x 220Ω Resistors** (Optional but recommended)
- **Breadboard**
- **Jumper Wires**
- **Power Source (USB Cable)**

---

## **Wiring Diagram**
| LED Color  | ESP32 Pin | Resistor (Optional) |  
|------------|----------|---------------------|  
| Red        | GPIO 23  | 220Ω                |  
| Yellow     | GPIO 22  | 220Ω                |  
| Green      | GPIO 21  | 220Ω                |  

### **Connections:**
1. **Red LED:**
   - Connect the **anode (+)** of the red LED to **GPIO 23** (via 220Ω resistor).
   - Connect the **cathode (-)** to **GND**.

2. **Yellow LED:**
   - Connect the **anode (+)** of the yellow LED to **GPIO 22** (via 220Ω resistor).
   - Connect the **cathode (-)** to **GND**.

3. **Green LED:**
   - Connect the **anode (+)** of the green LED to **GPIO 21** (via 220Ω resistor).
   - Connect the **cathode (-)** to **GND**.

---

## **Code Implementation**
Here’s the Arduino code that controls the LED sequence:

```cpp
// Define pin numbers for the LEDs
const int redLed = 23;
const int yellowLed = 22;
const int greenLed = 21;

void setup() {
  Serial.begin(115200); // Start serial monitor

  // Set LED pins as outputs
  pinMode(redLed, OUTPUT);
  pinMode(yellowLed, OUTPUT);
  pinMode(greenLed, OUTPUT);
}

void loop() {
  // Red light on
  digitalWrite(redLed, HIGH);
  digitalWrite(yellowLed, LOW);
  digitalWrite(greenLed, LOW);
  Serial.println("Red Light ON");
  delay(5000); // Wait 5 seconds

  // Yellow light on
  digitalWrite(redLed, LOW);
  digitalWrite(yellowLed, HIGH);
  digitalWrite(greenLed, LOW);
  Serial.println("Yellow Light ON");
  delay(2000); // Wait 2 seconds

  // Green light on
  digitalWrite(redLed, LOW);
  digitalWrite(yellowLed, LOW);
  digitalWrite(greenLed, HIGH);
  Serial.println("Green Light ON");
  delay(5000); // Wait 5 seconds

  // Yellow light before red
  digitalWrite(redLed, LOW);
  digitalWrite(yellowLed, HIGH);
  digitalWrite(greenLed, LOW);
  Serial.println("Yellow Light ON");
  delay(2000); // Wait 2 seconds
}
```

---

## **Step-by-Step Walkthrough**

### **Step 1: Setup Your Hardware**
- Connect the LEDs and resistors as described in the wiring section.

### **Step 2: Install Arduino IDE & ESP32 Board Support**
1. Download and install the **Arduino IDE**.
2. Add **ESP32 Board Support** by going to:
   - **File** → **Preferences** → Paste the following into "Additional Board Manager URLs":
     ```
     https://dl.espressif.com/dl/package_esp32_index.json
     ```
   - Then go to **Tools** → **Board** → **Boards Manager** and install "ESP32 by Espressif Systems".

### **Step 3: Upload the Code**
1. Open **Arduino IDE**.
2. Copy and paste the above code into a new sketch.
3. Select **Board** → **ESP32 Dev Module**.
4. Select the correct **COM Port**.
5. Click **Upload**.

### **Step 4: Open Serial Monitor**
- Open the **Serial Monitor** (`Tools` → `Serial Monitor`).
- Set the baud rate to **115200** to view the traffic light status.

---

## **How It Works**
1. **Red Light ON** for 5 seconds → Cars must stop.
2. **Yellow Light ON** for 2 seconds → Prepare to go.
3. **Green Light ON** for 5 seconds → Cars can move.
4. **Yellow Light ON** for 2 seconds → Prepare to stop.
5. **Loop repeats indefinitely.**

---

