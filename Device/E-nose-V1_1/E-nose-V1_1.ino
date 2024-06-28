#include <DHT.h>
#include <FS.h>
#include <SPIFFS.h>
#include <ArduinoJson.h>
#include "src/Relay.h"

// Pin definitions for the ESP32
#define DHTPIN 14           // Digital pin connected to the DHT sensor
#define DHTTYPE DHT11       // DHT 22 (AM2302), AM2321

// Initialize DHT sensor.
DHT dht(DHTPIN, DHTTYPE);

// Gas sensor pins
const int gasPins[] = {12, 15, 13, 4, 34, 32, 25};

// Relay instances
Relay relaySolenoid1(33);  // Auto turn off enabled
Relay relaySolenoid2(5);   // Auto turn off enabled
Relay relayPump(26);       // Auto turn off disabled

// Variables to store sensor readings
int gasValues[7];
float temperature;
float humidity;

// Timing variables
unsigned long previousMillis = 0;
const long interval = 1000;  // Interval at which to read sensors (milliseconds)
const unsigned long connectionTimeout = 5000; // Timeout for connection in milliseconds
unsigned long lastReceivedTime = 0;  // Last time data was received

// Connection flag
bool connected = false;
unsigned long itemNumber = 0; // Data item number

// Variables for alternating relay control
bool alternateRelays = false;
unsigned long relay1ToggleInterval = 0;
unsigned long relay2ToggleInterval = 0;
unsigned long nextToggleTime = 0;
bool relay1Active = true; // Track which relay is currently active
unsigned long cycleCount = 0; // Count the number of completed cycles
unsigned long totalCycles = 0; // Total number of cycles to run

// Operation status
enum OperationStatus {
  IDLE,
  RUNNING,
  COMPLETED,
  MANUAL_STOP
};
OperationStatus operationStatus = IDLE;

void loadSettings() {
  if (!SPIFFS.begin(true)) {
    Serial.println("DEBUG: An Error has occurred while mounting SPIFFS");
    return;
  }

  File file = SPIFFS.open("/config.json", "r");
  if (!file) {
    Serial.println("DEBUG: Failed to open config file, creating default config");
    saveSettings(); // Create default config file if it doesn't exist
    return;
  }

  size_t size = file.size();
  if (size > 1024) {
    Serial.println("DEBUG: Config file size is too large");
    return;
  }

  std::unique_ptr<char[]> buf(new char[size]);
  file.readBytes(buf.get(), size);
  file.close();

  StaticJsonDocument<1024> doc;
  DeserializationError error = deserializeJson(doc, buf.get());
  if (error) {
    Serial.println("DEBUG: Failed to parse config file, loading default settings");
    // Load default settings
    relaySolenoid1.setTurnOnDuration(5);
    relaySolenoid2.setTurnOnDuration(5);
    totalCycles = 10; // Default number of cycles
    saveSettings();
    return;
  }

  relaySolenoid1.setTurnOnDuration(doc["relaySolenoid1"]["duration"].as<unsigned long>());
  relaySolenoid2.setTurnOnDuration(doc["relaySolenoid2"]["duration"].as<unsigned long>());
  totalCycles = doc["cycle"].as<unsigned long>();
}

void saveSettings() {
  StaticJsonDocument<1024> doc;
  doc["relaySolenoid1"]["duration"] = relaySolenoid1.getTurnOnDuration();
  doc["relaySolenoid2"]["duration"] = relaySolenoid2.getTurnOnDuration();
  doc["cycle"] = totalCycles;

  File file = SPIFFS.open("/config.json", "w");
  if (!file) {
    if (connected) {
      Serial.println("DEBUG: Failed to open config file for writing");
    }
    return;
  }

  serializeJson(doc, file);
  file.close();
}

void sendSettings() {
  StaticJsonDocument<1024> doc;
  doc["relaySolenoid1"]["duration"] = relaySolenoid1.getTurnOnDuration();
  doc["relaySolenoid2"]["duration"] = relaySolenoid2.getTurnOnDuration();
  doc["cycle"] = totalCycles;

  String settings;
  serializeJson(doc, settings);
  Serial.println(settings);
  Serial.println("DEBUG: Settings sent");
}

void setup() {
  Serial.begin(115200);

  // Initialize gas sensor pins
  for (int i = 0; i < 7; i++) {
    pinMode(gasPins[i], INPUT);
  }

  // Initialize DHT sensor
  dht.begin();

  // Load settings from config file
  loadSettings();

  Serial.println("ESP32_DEVICE_IDENTIFIER");
}

void loop() {
  unsigned long currentMillis = millis();

  // Check if there is any data available on the serial port
  if (Serial.available() > 0) {
    char command = Serial.read();
    if (command == 'C') {
      connected = true;
      relayPump.turnOn();  // Turn on the relayPump when connected
      relaySolenoid1.turnOn();
      relaySolenoid2.turnOff();  // Ensure relaySolenoid2 is off
      lastReceivedTime = currentMillis; // Reset the last received time
      operationStatus = IDLE;
      Serial.println("DEBUG: Connected");
    } else if (command == 'K') {
      lastReceivedTime = currentMillis; // Reset the last received time for keep-alive message
    } else if (command == 'I') {
      Serial.println("ESP32_DEVICE_IDENTIFIER");
    } else if (command == 'L') {
      sendSettings();
    } else if (command == 'R') {
      itemNumber = 0; // Reset item number
    } else if (command == 'S') {
      // Handle incoming settings JSON
      String json = Serial.readString();
      StaticJsonDocument<1024> doc;
      DeserializationError error = deserializeJson(doc, json);
      if (error) {
        Serial.println("DEBUG: Failed to parse settings JSON");
      } else {
        relaySolenoid1.setTurnOnDuration(doc["relaySolenoid1"]["duration"].as<unsigned long>());
        relaySolenoid2.setTurnOnDuration(doc["relaySolenoid2"]["duration"].as<unsigned long>());
        totalCycles = doc["cycle"].as<unsigned long>();
        saveSettings(); // Save settings to config file
      }
    } else if (command == 'A') { // New command to start alternating relays
      alternateRelays = true;
      relay1ToggleInterval = relaySolenoid1.getTurnOnDuration() * 1000; // Convert seconds to milliseconds
      relay2ToggleInterval = relaySolenoid2.getTurnOnDuration() * 1000; // Convert seconds to milliseconds
      nextToggleTime = currentMillis + relay1ToggleInterval; // Initial toggle time
      relaySolenoid1.turnOn();
      relaySolenoid2.turnOff();
      relay1Active = true;
      cycleCount = 0;
      operationStatus = RUNNING;
      Serial.println("DEBUG: Alternating relays started");
    } else if (command == 'B') { // New command to stop alternating relays
      alternateRelays = false;
      relaySolenoid1.turnOn();
      relaySolenoid2.turnOff();
      operationStatus = MANUAL_STOP;
      Serial.println("DEBUG: Alternating relays stopped");
    }
  }

  // Check for connection timeout
  if (connected && (currentMillis - lastReceivedTime > connectionTimeout)) {
    connected = false;
    relayPump.turnOff();  // Turn off the relayPump if no communication within the timeout
    relaySolenoid1.turnOff();
    relaySolenoid2.turnOff();
    operationStatus = IDLE;
    Serial.println("DEBUG: Connection timed out");
  }

  // Only send data if connected
  if (connected) {
    if (currentMillis - previousMillis >= interval) {
      // Save the last time you read the sensors
      previousMillis = currentMillis;

      // Read gas sensor values
      for (int i = 0; i < 7; i++) {
        gasValues[i] = analogRead(gasPins[i]);
      }

      // Read temperature and humidity
      temperature = dht.readTemperature();
      humidity = dht.readHumidity();

      // Create JSON formatted string
      String jsonData = "{";
      jsonData += "\"itemNumber\":" + String(itemNumber++) + ",";
      jsonData += "\"gasValues\":[" + String(gasValues[0]) + "," + String(gasValues[1]) + "," + String(gasValues[2]) + "," + String(gasValues[3]) + "," + String(gasValues[4]) + "," + String(gasValues[5]) + "," + String(gasValues[6]) + "],";
      jsonData += "\"temperature\":" + String(temperature) + ",";
      jsonData += "\"humidity\":" + String(humidity) + ",";
      jsonData += "\"operationStatus\":" + String(operationStatus);
      jsonData += "}";

      // Print JSON data to Serial Monitor
      Serial.println(jsonData);
    }

    // Update relays
    relaySolenoid1.update(currentMillis);
    relaySolenoid2.update(currentMillis);
    relayPump.update(currentMillis);

    // Handle alternating relays
    if (alternateRelays) {
      if (currentMillis >= nextToggleTime) {
        if (relay1Active) {
          relaySolenoid1.turnOff();
          relaySolenoid2.turnOn();
          nextToggleTime = currentMillis + relay2ToggleInterval;
        } else {
          relaySolenoid1.turnOn();
          relaySolenoid2.turnOff();
          nextToggleTime = currentMillis + relay1ToggleInterval;
          cycleCount++;  // Increment cycle count after each complete cycle
          if (cycleCount >= totalCycles) {
            alternateRelays = false; // Stop alternating if cycle limit is reached
            relaySolenoid1.turnOn();
            relaySolenoid2.turnOff();
            operationStatus = COMPLETED;
            Serial.println("DEBUG: Alternating relays completed all cycles");
          }
        }
        relay1Active = !relay1Active; // Toggle the active relay
      }
    }
  } else {
    // Ensure the relayPump and relays are turned off if the connection is lost
    relayPump.turnOff();
    relaySolenoid1.turnOff();
    relaySolenoid2.turnOff();
  }
}
