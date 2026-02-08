#pragma once
#include <stdint.h>
#include <stdbool.h>
#include <vector>

/**
 * @brief Internal Data Structures for the Logic Layer.
 * Decouples the Wire Protocol (Bytes) from the Execution Logic.
 */

namespace Demeter {

    /**
     * @brief Command IDs for the Demeter Protocol V2.
     * @note Must match the Python definition in `schemas_protocol.py`.
     */
    enum class CommandType : uint8_t {
        PING            = 0x01, ///< Keep-alive check. Expects ACK.
        ACK             = 0x02, ///< Acknowledge successful command receipt.
        NACK            = 0x03, ///< Negative Acknowledge (Error).
        ROUTE_ADD       = 0x0A, ///< Register a new route in the routing table.
        SET_GPIO        = 0x10, ///< Set Digital Output state.
        SET_PWM         = 0x11, ///< Set PWM Duty Cycle.
        EXEC_SEQUENCE   = 0x30, ///< Execute a complex sequence of actions.
        UNKNOWN         = 0xFF  ///< Fallback for invalid commands.
    };

    /**
     * @brief Internal representation of a SET_GPIO command.
     * Used to decouple the byte-stream from the logic handler.
     */
    struct SetGpioCmd {
        uint8_t pin;    ///< Target GPIO Pin Number.
        bool value;     ///< Desired State (true=HIGH, false=LOW).
        uint8_t flags;  ///< Optional flags (e.g. force, duration).
    };

    /**
     * @brief Internal representation of a SET_PWM command.
     */
    struct SetPwmCmd {
        uint8_t pin;    ///< Target GPIO Pin Number.
        uint16_t value; ///< Duty Cycle (0-65535 or 0-100 depending on resolution).
    };

    /**
     * @brief Step for the Sequencer.
     */
    struct SequenceStep {
        uint8_t pin;      ///< GPIO Pin.
        bool value;       ///< State.
        uint32_t delayMs; ///< Duration to hold this state (ms).
    };

    /**
     * @brief Command to execute a sequence of steps.
     */
    struct ExecSequenceCmd {
        std::vector<SequenceStep> steps;
    };

}
