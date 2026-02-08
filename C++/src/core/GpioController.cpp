#include "core/GpioController.h"

#ifndef ARDUINO
    // Mock Implementation for Native Environment
    #include <iostream>
    #include <map>
    
    static std::map<uint8_t, uint8_t> _mockPinStates;

    void pinMode(uint8_t pin, uint8_t mode) { 
        // Mock: Do nothing or log
    }
    
    void digitalWrite(uint8_t pin, uint8_t val) {
        _mockPinStates[pin] = val;
        // std::cout << "[GPIO] PIN " << (int)pin << " -> " << (int)val << std::endl;
    }

    uint8_t getMockPinState(uint8_t pin) {
        return _mockPinStates[pin];
    }
#endif

void GpioController::init() {
    // Initialize default pins for MVP (4, 5, 6, 7) context
    // Hardcoded for now as per PRD requirements
    const uint8_t pins[] = {4, 5, 6, 7};
    for (uint8_t pin : pins) {
        pinMode(pin, OUTPUT);
        digitalWrite(pin, LOW); // Start OFF
    }
}

void GpioController::execute(const Demeter::SetGpioCmd& cmd) {
    // 1. Safety Checks (MVP Scope: Only 4-7 allowed)
    if (cmd.pin < 4 || cmd.pin > 7) return;

    // 2. Actuate
    digitalWrite(cmd.pin, cmd.value ? HIGH : LOW);
    
    // Optional: Log action (if Serial is available/mocked)
    // Serial.printf("GPIO %d -> %s\n", cmd.pin, cmd.value ? "ON" : "OFF");
}
