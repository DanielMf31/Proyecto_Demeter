#pragma once

#include "core/InternalTypes.h"
#include "core/PinConfig.h"
#include <vector>

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
private:
    std::vector<uint8_t> _managedPins;

public:
    /**
     * @brief Configure the list of managed pins.
     * @param pins List of GPIO numbers.
     */
    void setPins(const std::vector<uint8_t>& pins);

    /**
     * @brief Initialize configured GPIO pins.
     * Sets managed pins as OUTPUT and initializes them to LOW.
     */
    void init();

    /**
     * @brief Execute a State Change Command.
     * @param cmd Command containing target PIN and Logic Level.
     */
    void execute(const Demeter::SetGpioCmd& cmd);
};
