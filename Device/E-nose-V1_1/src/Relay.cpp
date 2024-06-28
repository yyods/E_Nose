// Relay.cpp

#include "Relay.h"
#include <Arduino.h>

Relay::Relay(int pin, bool autoTurnOffEnabled)
    : relayPin(pin), manualControl(false), manualOverrideTime(0), turnOnDuration(0), autoTurnOff(autoTurnOffEnabled) {
    pinMode(relayPin, OUTPUT);
    digitalWrite(relayPin, HIGH); // Ensure the relay is off at startup
}

void Relay::update(unsigned long currentMillis) {
    // Handle manual override
    if (manualControl && (currentMillis - manualOverrideTime > manualOverrideDuration)) {
        manualControl = false; // Reset manual control after 5 minutes
    }

    // Check for turn off condition based on duration
    if (autoTurnOff && manualControl && (currentMillis - turnOnTime > turnOnDuration)) {
        turnOff();
        manualControl = false;
    }
}

void Relay::turnOn() {
    manualControl = true;
    manualOverrideTime = millis(); // Record the time of manual override
    turnOnTime = millis();
    digitalWrite(relayPin, LOW);
}

void Relay::turnOff() {
    manualControl = true;
    manualOverrideTime = millis(); // Record the time of manual override
    digitalWrite(relayPin, HIGH);
}

bool Relay::isOn() const {
    return digitalRead(relayPin) == LOW; // Adjust based on relay type
}

void Relay::setTurnOnDuration(unsigned long durationInSeconds) {
    turnOnDuration = durationInSeconds * 1000; // Convert seconds to milliseconds
}

unsigned long Relay::getTurnOnDuration() const {
    return turnOnDuration / 1000; // Convert milliseconds to seconds
}
