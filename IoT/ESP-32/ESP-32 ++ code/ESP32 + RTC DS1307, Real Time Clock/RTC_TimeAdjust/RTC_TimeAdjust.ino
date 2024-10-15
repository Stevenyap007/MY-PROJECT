#include <Wire.h>
#include "RTClib.h"

RTC_DS1307 rtc;

void setup() {
  Serial.begin(115200);
  Wire.begin();

  if (!rtc.begin()) {
    Serial.println("Couldn't find RTC");
    while (1);
  }

  //MANUAL METHOD
  // Adjust the RTC to the correct time (YYYY, MM, DD, HH, MM, SS)
  rtc.adjust(DateTime(2024, 10, 14, 17, 14, 0));  // Set to 14th Oct 2024, 15:30:00

  //AUTO METHOD
  // rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));


  Serial.println("RTC time adjusted.");
}

void loop() {
  DateTime now = rtc.now();

  Serial.print(now.year()); Serial.print('/');
  Serial.print(now.month()); Serial.print('/');
  Serial.print(now.day()); Serial.print(" ");
  Serial.print(now.hour()); Serial.print(':');
  Serial.print(now.minute()); Serial.print(':');
  Serial.println(now.second());

  delay(1000);
}
