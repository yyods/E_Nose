#include <DHT.h>

// Pin definitions for the ESP32
#define DHTPIN 14           // Digital pin connected to the DHT sensor
#define DHTTYPE DHT11       // DHT 22 (AM2302), AM2321

// Initialize DHT sensor.
DHT dht(DHTPIN, DHTTYPE);

// Gas sensor pins
const int gasPins[] = {12, 15, 13, 4, 34, 32, 25};

// Relay pins
const int relaySolenoid1 = 33;
const int relaySolenoid2 = 5;
const int relayPump = 26;   // Corrected from 25 to 26 to avoid conflict

// Variables to store sensor readings
int gasValues[7];
float temperature;
float humidity;

void setup() {
  Serial.begin(115200);

  // Print a unique identifier to the Serial Monitor
  Serial.println("ESP32_DEVICE_IDENTIFIER");

  // Initialize gas sensor pins
  for (int i = 0; i < 7; i++) {
    pinMode(gasPins[i], INPUT);
  }

  // Initialize relay pins
  pinMode(relaySolenoid1, OUTPUT);
  pinMode(relaySolenoid2, OUTPUT);
  pinMode(relayPump, OUTPUT);

  // Initialize DHT sensor
  dht.begin();

  // Initialize relay states
  digitalWrite(relaySolenoid1, HIGH);
  digitalWrite(relaySolenoid2, HIGH);
  digitalWrite(relayPump, HIGH);
}

void loop() {
  // Read gas sensor values
  for (int i = 0; i < 7; i++) {
    gasValues[i] = analogRead(gasPins[i]);
  }

  // Read temperature and humidity
  temperature = dht.readTemperature();
  humidity = dht.readHumidity();

  // Print sensor values to Serial Monitor
  Serial.print("Gas Sensor Values: ");
  for (int i = 0; i < 7; i++) {
    Serial.print(gasValues[i]);
    Serial.print(" ");
  }
  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.print(" *C ");
  Serial.print("Humidity: ");
  Serial.print(humidity);
  Serial.println(" %");

  // Check for commands from Serial Monitor
  if (Serial.available() > 0) {
    char command = Serial.read();

    switch (command) {
      case 'a':
        digitalWrite(relaySolenoid1, HIGH);  // Turn on Solenoid Valve 1
        break;
      case 'A':
        digitalWrite(relaySolenoid1, LOW);   // Turn off Solenoid Valve 1
        break;
      case 'p':
        digitalWrite(relaySolenoid2, HIGH);  // Turn on Solenoid Valve 2
        break;
      case 'P':
        digitalWrite(relaySolenoid2, LOW);   // Turn off Solenoid Valve 2
        break;
      case 'b':
        digitalWrite(relayPump, HIGH);       // Turn on Pump
        break;
      case 'B':
        digitalWrite(relayPump, LOW);        // Turn off Pump
        break;
      default:
        Serial.println("Unknown command");
        break;
    }
  }

  // Wait 1 second before next loop
  delay(1000);
}
