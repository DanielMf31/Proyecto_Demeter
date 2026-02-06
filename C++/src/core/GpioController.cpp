#include "core/GpioController.h"

#ifndef ARDUINO
    // Mock Implementation for Native Environment
    #include <iostream>
    void pinMode(uint8_t pin, uint8_t mode) { 
        // Mock: Do nothing or log
    }
    void digitalWrite(uint8_t pin, uint8_t val) {
        // Mock: Logic verified in tests via spies if needed
        // std::cout << "Native GPIO " << (int)pin << " set to " << (int)val << std::endl;
    }
#endif

void GpioController::init() {
    // Initialize default pins if necessary
}

void GpioController::execute(const Demeter::SetGpioCmd& cmd) {
    // 1. Safety Checks (Example: Don't allow pin 0 or 1 if UART is used)
    if (cmd.pin == 0 || cmd.pin == 1) return;

    // 2. Configure Pin (Lazy init could go here, for now assume configured or do it now)
    pinMode(cmd.pin, OUTPUT);

    // 3. Actuate
    digitalWrite(cmd.pin, cmd.value ? HIGH : LOW);
}
