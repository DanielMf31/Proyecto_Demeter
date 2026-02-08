#pragma once

#include "core/InternalTypes.h"

// Hardware Abstraction for GPIO
#ifdef ARDUINO
    #include <Arduino.h>
#else
    // Mock for Native Test
    // Mock for Native Test
    #include <stdint.h>
    void pinMode(uint8_t pin, uint8_t mode);
    void digitalWrite(uint8_t pin, uint8_t val);
    uint8_t getMockPinState(uint8_t pin); // Helper for tests
    #define OUTPUT 1
    #define HIGH 1
    #define LOW 0
#endif

/**
 * @class GpioController
 * @brief Hardware Abstraction Layer (HAL) for GPIO Control.
 * 
 * Manages the physical pins of the ESP32.
 * Decouples logic from hardware specifics (Arduino API).
 */
class GpioController {
public:
    /**
     * @brief Initialize GPIO pins.
     * Sets PINS 4-7 as OUTPUT and initializes them to LOW.
     */
    void init();

    /**
     * @brief Execute a State Change Command.
     * @param cmd Command containing target PIN and Logic Level.
     * @note Only affects Pins 4-7 (Safe-guard for MVP).
     */
    void execute(const Demeter::SetGpioCmd& cmd);
};
