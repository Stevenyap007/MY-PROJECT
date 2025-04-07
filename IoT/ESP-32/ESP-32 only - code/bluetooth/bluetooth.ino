#include "BluetoothSerial.h"  // Include Bluetooth library

BluetoothSerial BT;  // Create a BluetoothSerial object

void setup() {
  Serial.begin(115200);  // Start serial communication with PC
  BT.begin("ESP32_Bluetooth");  // Set Bluetooth device name
  Serial.println("Bluetooth Started. Waiting for connection...");
}

void loop() {
  // Check if data is available from Bluetooth
  if (BT.available()) {
    String incoming = BT.readString();  // Read the data
    Serial.print("Received: ");
    Serial.println(incoming);  // Print received data to Serial Monitor

    // Send a response back via Bluetooth
    BT.print("You sent: ");
    BT.println(incoming);
  }
}
