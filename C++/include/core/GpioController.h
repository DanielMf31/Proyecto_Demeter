#pragma once

#include "core/InternalTypes.h"

// Hardware Abstraction for GPIO
#ifdef ARDUINO
    #include <Arduino.h>
#else
    // Mock for Native Test
    #include <stdint.h>
    void pinMode(uint8_t pin, uint8_t mode);
    void digitalWrite(uint8_t pin, uint8_t val);
    #define OUTPUT 1
    #define HIGH 1
    #define LOW 0
#endif

class GpioController {
public:
    void init();
    void execute(const Demeter::SetGpioCmd& cmd);
};
