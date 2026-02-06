#pragma once
#include <stdint.h>
#include <stdbool.h>

/**
 * @brief Internal Data Structures for the Logic Layer.
 * Decouples the Wire Protocol (Bytes) from the Execution Logic.
 */

namespace Demeter {

    // Command IDs (Must match Python definition)
    enum class CommandType : uint8_t {
        PING            = 0x01,
        ACK             = 0x02,
        NACK            = 0x03,
        ROUTE_ADD       = 0x0A,
        SET_GPIO        = 0x10,
        SET_PWM         = 0x11,
        EXEC_SEQUENCE   = 0x30,
        UNKNOWN         = 0xFF
    };

    // Internal representation of a GPIO Command
    struct SetGpioCmd {
        uint8_t pin;
        bool value;
        uint8_t flags;
    };

    // Internal representation of a PWM Command
    struct SetPwmCmd {
        uint8_t pin;
        uint16_t value;
    };

}
