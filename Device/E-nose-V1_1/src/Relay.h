// Relay.h

#ifndef RELAY_H
#define RELAY_H

class Relay {
private:
    int relayPin;
    bool manualControl;
    unsigned long manualOverrideTime;
    const unsigned long manualOverrideDuration = 300000; // 5 minutes in milliseconds
    unsigned long turnOnTime; // Time when the relay was turned on
    unsigned long turnOnDuration; // Duration to keep the relay on
    bool autoTurnOff; // Enable or disable auto turn off feature

public:
    Relay(int pin, bool autoTurnOffEnabled = false);
    void update(unsigned long currentMillis);
    void turnOn();
    void turnOff();
    bool isOn() const;
    void setTurnOnDuration(unsigned long durationInSeconds);
    unsigned long getTurnOnDuration() const;
};

#endif // RELAY_H
