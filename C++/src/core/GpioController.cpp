#include "core/GpioController.h"

/**
 * @file GpioController.cpp
 * @brief GPIO Hardware Abstraction Implementation.
 */



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
