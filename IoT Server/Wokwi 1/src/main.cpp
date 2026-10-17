#include <Arduino.h>
// =====================================================================
//  Smart room node (Wokwi): ESP32 + PIR + DHT22 + 2 relays + LCD
//  - Light turns ON when motion is detected
//  - AC turns ON when room is occupied AND temperature >= threshold
//  - Both turn OFF after no motion for the occupancy timeout
//  - The hub can monitor everything and override each device over MQTT
//  - Automation runs on the ESP32 itself, so it keeps working if the hub is offline
// =====================================================================
#include <WiFi.h>
#include <PubSubClient.h>
#include <LiquidCrystal_I2C.h>
#include "DHTesp.h"

// ---------------- Settings ----------------
const char* WIFI_SSID = "Wokwi-GUEST";        // Wokwi's built-in virtual WiFi
const char* WIFI_PASS = "";
const char* BROKER    = "broker.hivemq.com";  // free public broker
const int   PORT      = 1883;
const String BASE     = "Claude-iotsim/home/livingroom";  // CHANGE "yourname" to something unique

// Pins
const int PIR_PIN         = 13;
const int DHT_PIN         = 15;
const int LIGHT_RELAY_PIN = 26;
const int AC_RELAY_PIN    = 27;

// Automation (threshold and timeout can be changed from the hub at runtime)
float tempThreshold               = 28.0;   // deg C
const float HYSTERESIS            = 1.0;    // AC turns off at threshold - 1.0 (prevents rapid on/off)
unsigned long occupancyTimeoutMs  = 30000;  // 30 s for demo; real rooms use 5-15 min

// Timing
const unsigned long DHT_READ_MS   = 2500;   // DHT22 needs >= 2 s between reads
const unsigned long TEMP_PUB_MS   = 10000;
const unsigned long STATUS_PUB_MS = 10000;
const unsigned long MQTT_RETRY_MS = 5000;
const unsigned long LCD_MS        = 500;

// ---------------- Globals ----------------
WiFiClient net;
PubSubClient mqtt(net);
DHTesp dht;
LiquidCrystal_I2C lcd(0x27, 16, 2);

enum Mode { AUTO_MODE, MANUAL_MODE };
struct Actuator { const char* name; int pin; bool on; Mode mode; };
Actuator light = { "light", LIGHT_RELAY_PIN, false, AUTO_MODE };
Actuator ac    = { "ac",    AC_RELAY_PIN,    false, AUTO_MODE };

bool motion = false;
bool everMotion = false;
unsigned long lastMotionMs = 0;
float temperature = NAN, humidity = NAN;
unsigned long lastDhtRead = 0, lastTempPub = 0, lastStatusPub = 0, lastMqttTry = 0, lastLcd = 0;

// ---------------- Helpers ----------------
String topic(const String& sub) { return BASE + "/" + sub; }
String num(float v) { return isnan(v) ? String("null") : String(v, 1); }
const char* modeStr(Mode m) { return m == AUTO_MODE ? "AUTO" : "MANUAL"; }

void pub(const String& t, const String& payload, bool retain = true) {
  Serial.printf(">> %s %s\n", t.c_str(), payload.c_str());
  if (mqtt.connected()) mqtt.publish(t.c_str(), payload.c_str(), retain);
}

bool isOccupied() {
  return motion || (everMotion && millis() - lastMotionMs < occupancyTimeoutMs);
}

void publishActuator(Actuator& a, const char* source) {
  String p = String("{\"state\":\"") + (a.on ? "ON" : "OFF") +
             "\",\"mode\":\"" + modeStr(a.mode) +
             "\",\"source\":\"" + source + "\"}";
  pub(topic(String(a.name) + "/state"), p);
}

void publishMotion() {
  pub(topic("motion"), String("{\"motion\":") + (motion ? "true" : "false") + "}");
}

void publishTemp() {
  if (isnan(temperature)) return;
  pub(topic("temp"), "{\"temperature\":" + num(temperature) + ",\"humidity\":" + num(humidity) + "}");
  lastTempPub = millis();
}

void publishConfig() {
  pub(topic("config/state"), "{\"threshold\":" + String(tempThreshold, 1) +
      ",\"timeout_s\":" + String(occupancyTimeoutMs / 1000) + "}");
}

void publishStatus() {
  String p = "{";
  p += "\"motion\":" + String(motion ? "true" : "false");
  p += ",\"occupied\":" + String(isOccupied() ? "true" : "false");
  p += ",\"temperature\":" + num(temperature);
  p += ",\"humidity\":" + num(humidity);
  p += ",\"light\":\"" + String(light.on ? "ON" : "OFF") + "\",\"light_mode\":\"" + modeStr(light.mode) + "\"";
  p += ",\"ac\":\"" + String(ac.on ? "ON" : "OFF") + "\",\"ac_mode\":\"" + modeStr(ac.mode) + "\"";
  p += ",\"threshold\":" + String(tempThreshold, 1);
  p += ",\"timeout_s\":" + String(occupancyTimeoutMs / 1000);
  p += ",\"rssi\":" + String(WiFi.RSSI());
  p += ",\"uptime_s\":" + String(millis() / 1000);
  p += "}";
  pub(topic("status"), p, false);
  lastStatusPub = millis();
}

// ---------------- Actuators & automation ----------------
void setActuator(Actuator& a, bool on, const char* source) {
  if (a.on == on) return;
  a.on = on;
  digitalWrite(a.pin, on ? HIGH : LOW);   // relay clicks, lamp LED follows
  publishActuator(a, source);
}

void runAutomation() {
  bool occ = isOccupied();
  if (light.mode == AUTO_MODE) setActuator(light, occ, "auto");
  if (ac.mode == AUTO_MODE && !isnan(temperature)) {
    if (occ && temperature >= tempThreshold)                     setActuator(ac, true,  "auto");
    else if (!occ || temperature <= tempThreshold - HYSTERESIS)  setActuator(ac, false, "auto");
  }
}

// Commands from the hub: "ON" / "OFF" = manual override, "AUTO" = back to automation
void handleCommand(Actuator& a, const String& cmd) {
  if (cmd == "ON" || cmd == "OFF") {
    a.mode = MANUAL_MODE;
    bool want = (cmd == "ON");
    if (a.on == want) publishActuator(a, "manual");
    else setActuator(a, want, "manual");
  } else if (cmd == "AUTO") {
    a.mode = AUTO_MODE;
    publishActuator(a, "auto");
    runAutomation();
  }
}

void onMessage(char* t, byte* payload, unsigned int len) {
  String msg;
  for (unsigned int i = 0; i < len; i++) msg += (char)payload[i];
  msg.trim();
  String cmd = msg; cmd.toUpperCase();
  String tp(t);
  Serial.printf("<< %s %s\n", t, msg.c_str());

  if (tp == topic("light/set"))      handleCommand(light, cmd);
  else if (tp == topic("ac/set"))    handleCommand(ac, cmd);
  else if (tp == topic("config/threshold")) {
    float v = msg.toFloat();
    if (v >= 16 && v <= 40) { tempThreshold = v; publishConfig(); runAutomation(); }
  } else if (tp == topic("config/timeout")) {
    long s = msg.toInt();
    if (s >= 5 && s <= 3600) { occupancyTimeoutMs = s * 1000UL; publishConfig(); }
  }
}

// ---------------- Connectivity ----------------
void connectWiFi() {
  lcd.clear(); lcd.print("Connecting WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) { delay(250); Serial.print("."); }
  Serial.println(" WiFi connected");
}

void ensureMqtt() {
  if (mqtt.connected()) return;
  if (lastMqttTry != 0 && millis() - lastMqttTry < MQTT_RETRY_MS) return;
  lastMqttTry = millis();

  String id = "room-node-" + String((uint32_t)esp_random(), HEX);
  String avail = topic("availability");
  // Last Will: broker publishes "offline" automatically if this device disappears
  if (mqtt.connect(id.c_str(), avail.c_str(), 1, true, "offline")) {
    Serial.println("MQTT connected");
    pub(avail, "online");
    mqtt.subscribe(topic("light/set").c_str(), 1);
    mqtt.subscribe(topic("ac/set").c_str(), 1);
    mqtt.subscribe(topic("config/threshold").c_str(), 1);
    mqtt.subscribe(topic("config/timeout").c_str(), 1);
    publishActuator(light, "boot");
    publishActuator(ac, "boot");
    publishMotion();
    publishConfig();
  } else {
    Serial.printf("MQTT failed (rc=%d), retrying\n", mqtt.state());
  }
}

// ---------------- LCD ----------------
void printLine(int row, const char* s) {
  lcd.setCursor(0, row);
  lcd.print(s);
  for (int i = strlen(s); i < 16; i++) lcd.print(' ');
}

void updateLcd() {
  char l1[17], l2[17];
  if (isnan(temperature)) snprintf(l1, sizeof(l1), "T--.- H-- TH%4.1f", tempThreshold);
  else snprintf(l1, sizeof(l1), "T%4.1f H%2.0f TH%4.1f", temperature, humidity, tempThreshold);
  // M = occupied, * = device is in manual override
  snprintf(l2, sizeof(l2), "%c L:%-3s%c AC:%-3s%c",
           isOccupied() ? 'M' : '-',
           light.on ? "ON" : "OFF", light.mode == MANUAL_MODE ? '*' : ' ',
           ac.on ? "ON" : "OFF",    ac.mode == MANUAL_MODE ? '*' : ' ');
  printLine(0, l1);
  printLine(1, l2);
  lastLcd = millis();
}

// ---------------- Main ----------------
void setup() {
  Serial.begin(115200);
  pinMode(PIR_PIN, INPUT);
  pinMode(LIGHT_RELAY_PIN, OUTPUT);
  pinMode(AC_RELAY_PIN, OUTPUT);
  digitalWrite(LIGHT_RELAY_PIN, LOW);
  digitalWrite(AC_RELAY_PIN, LOW);

  lcd.init();
  lcd.backlight();
  dht.setup(DHT_PIN, DHTesp::DHT22);

  connectWiFi();
  mqtt.setServer(BROKER, PORT);
  mqtt.setBufferSize(512);
  mqtt.setCallback(onMessage);
  ensureMqtt();
  updateLcd();
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) WiFi.reconnect();
  ensureMqtt();
  mqtt.loop();

  // Motion
  bool m = digitalRead(PIR_PIN) == HIGH;
  if (m) { lastMotionMs = millis(); everMotion = true; }
  if (m != motion) { motion = m; publishMotion(); }

  // Temperature & humidity
  if (millis() - lastDhtRead > DHT_READ_MS) {
    lastDhtRead = millis();
    TempAndHumidity d = dht.getTempAndHumidity();
    if (dht.getStatus() == 0) { temperature = d.temperature; humidity = d.humidity; }
  }
  if (millis() - lastTempPub > TEMP_PUB_MS) publishTemp();

  runAutomation();

  if (millis() - lastStatusPub > STATUS_PUB_MS) publishStatus();
  if (millis() - lastLcd > LCD_MS) updateLcd();
  delay(20);
}
