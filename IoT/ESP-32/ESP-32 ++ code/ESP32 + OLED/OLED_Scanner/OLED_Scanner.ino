#include <Wire.h>

void setup() {
    Serial.begin(115200);
    Wire.begin();
    Serial.println("\nI2C Scanner");
}

void loop() {
    byte error, address;
    int nDevices = 0;

    Serial.println("Scanning...");

    for (address = 1; address < 127; address++) {
        // The I2C protocol uses a 7-bit address
        Wire.beginTransmission(address);
        error = Wire.endTransmission();

        if (error == 0) {
            Serial.print("I2C device found at address 0x");
            if (address < 16) {
                Serial.print("0");
            }
            Serial.print(address, HEX);
            Serial.println("  !");
            nDevices++;
            delay(500);  // Wait for half a second for stability
        }
        else if (error == 4) {
            Serial.print("Unknown error at address 0x");
            if (address < 16) {
                Serial.print("0");
            }
            Serial.println(address, HEX);
        }
    }
    if (nDevices == 0) {
        Serial.println("No I2C devices found\n");
    }
    else {
        Serial.println("done\n");
    }

    delay(5000);  // Wait 5 seconds before the next scan
}
