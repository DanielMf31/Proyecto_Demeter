#include "core/GpioController.h"

/**
 * @file GpioController.cpp
 * @brief GPIO Hardware Abstraction Implementation.
 */

void GpioController::setPins(const std::vector<uint8_t>& pins) {
    _managedPins = pins;
}

void GpioController::init() {
    if (_managedPins.empty()) {
        // Fallback or just do nothing
        return;
    }

    for (uint8_t pin : _managedPins) {
        pinMode(pin, OUTPUT);
        digitalWrite(pin, LOW); // Start OFF
    }
}

void GpioController::execute(const Demeter::SetGpioCmd& cmd) {
    // 1. Validation
    bool isValid = false;
    for (uint8_t pin : _managedPins) {
        if (pin == cmd.pin) {
            isValid = true;
            break;
        }
    }

    if (!isValid) return;

    // 2. Actuate
    digitalWrite(cmd.pin, cmd.value ? HIGH : LOW);
}
