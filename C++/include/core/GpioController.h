#pragma once

#include "core/InternalTypes.h"

// Hardware Abstraction for GPIO
#include <Arduino.h>

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
