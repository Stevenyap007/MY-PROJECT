# Barang yang Digunakan
- **ESP32**  
- **Cable Female to Female** (6 pcs)  
- **Sensor Kelembaban Tanah** (Tipe Resistive, bukan Capacitive)  
  - **MH-Sensor-series** (Moisture Hygrometer, untuk menentukan level kelembaban pada tanah)

## Pinout Sensor Kelembaban Tanah:
- **AO (Analog Output):** Memberikan sinyal analog berdasarkan level kelembaban tanah.
- **DO (Digital Output):** Memberikan sinyal digital HIGH atau LOW saat kelembaban melewati batas yang diatur (disesuaikan dengan potensiometer di sensor).  

### Wiring:
- **VCC** → Hubungkan ke 3.3V atau 5V pada ESP32 (sesuai toleransi tegangan sensor).  
- **GND** → Hubungkan ke GND pada ESP32.  
- **AO (Analog Output)** → Hubungkan ke pin input analog pada ESP32 (misalnya, GPIO 34).  
- **DO (Digital Output)** → Hubungkan ke pin digital pada ESP32 (misalnya, GPIO 2).

---

## Penjelasan GPIO:
1. **Analog Output (AO):**  
   - Pin GPIO 34 hingga GPIO 39:  
     Ini adalah pin input-only dan cocok untuk membaca nilai analog di ESP32. Umumnya, GPIO 34 sering digunakan untuk AO.  
     - **Contoh:** 
       - `GPIO 34` membaca nilai analog langsung dan tidak memiliki fungsi lain.

2. **Digital Output (DO):**  
   - Pin GPIO yang dapat digunakan:  
     GPIO 0, 2, 4, 5, 12, 14, 15, 16, 17, 18, 19, 21, 22, 23.  
     Anda dapat memilih salah satu dari pin tersebut untuk DO.

---

## Contoh Kode
```cpp
const int analogPin = 34;  // GPIO pin untuk AO (analog output)
const int digitalPin = 2;  // GPIO pin untuk DO (digital output)
int analogValue = 0;
int digitalValue = 0;

void setup() {
  Serial.begin(115200);  // Mulai komunikasi serial
  pinMode(digitalPin, INPUT);  // Atur pin DO sebagai input
}

void loop() {
  // Baca nilai analog (level kelembaban detail)
  analogValue = analogRead(analogPin);
  Serial.print("Soil Moisture Level (Analog): ");
  Serial.println(analogValue);

  // Konversi ke persentase (0-100)
  int moisturePercent = map(analogValue, 0, 4095, 100, 0);
  Serial.print("Soil Moisture Percentage: ");
  Serial.print(moisturePercent);
  Serial.println("%");

  // Formula alternatif untuk persentase kelembaban
  float moisturePercentFormula = 100 - (analogValue * 100.0 / 4095);
  Serial.print("Soil Moisture Formula Percentage: ");
  Serial.print(moisturePercentFormula);
  Serial.println("%");

  // Baca nilai digital (cek ambang batas)
  digitalValue = digitalRead(digitalPin);
  Serial.print("Soil Moisture Status (Digital): ");
  if (digitalValue == HIGH) {
    Serial.println("Dry");  // Menunjukkan tanah kering
  } else {
    Serial.println("Wet");  // Menunjukkan tanah basah
  }

  delay(1000);  // Delay untuk keterbacaan
}
```

##Penjelasan Tambahan
GPIO 34: Cocok untuk membaca sinyal analog dari sensor.
GPIO 2: Bisa digunakan untuk membaca sinyal digital, menunjukkan status kering atau basah.
Map Function: Mengkonversi rentang nilai ADC (0-4095) ke persentase (0-100%).