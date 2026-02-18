#include "core/GpioController.h"

/**
 * @file GpioController.cpp
 * @brief GPIO Hardware Abstraction Implementation.
 */

void GpioController::setPins(const std::vector<uint8_t>& pins) {
    _managedPins.clear();
    for(uint8_t pin : pins) {
        // Enforce BSP Protection
        if(isPinProtected(pin)) {
            // Log warning in debug mode? 
            // For now, Silent Rejection as per plan.
            continue;
        }
        _managedPins.push_back(pin);
    }
}

void GpioController::init() {
    if (_managedPins.empty()) {
        return;
    }

    for (uint8_t pin : _managedPins) {
        // Double check just in case, though setPins handles it.
        if(!isPinProtected(pin)) {
             pinMode(pin, OUTPUT);
             digitalWrite(pin, LOW); // Start OFF
        }
    }
}

void GpioController::execute(const Demeter::SetGpioCmd& cmd) {
    // 1. Validation: Is this pin managed by us?
    bool isManaged = false;
    for (uint8_t pin : _managedPins) {
        if (pin == cmd.pin) {
            isManaged = true;
            break;
        }
    }

    if (!isManaged) return; // Silent Fail: We don't control this pin.

    // 2. Redundant Safety Check (Defense in Depth)
    if(isPinProtected(cmd.pin)) return;

    // 3. Actuate
    digitalWrite(cmd.pin, cmd.value ? HIGH : LOW);
}
