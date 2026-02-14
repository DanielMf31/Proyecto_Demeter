#pragma once
#include <stdint.h>
#include <stdbool.h>
#include <vector>
#include <array>
#include <functional>

/**
 * @brief Internal Data Structures for the Logic Layer.
 * Decouples the Wire Protocol (Bytes) from the Execution Logic.
 */

namespace Demeter {

    // System States (Moved from SystemManager.h)
    enum class SystemState {
        BOOT,
        HANDSHAKE_SEND_SYN,
        HANDSHAKE_WAIT_SYN_ACK,
        HANDSHAKE_SEND_ACK,
        IDLE,
        RUNNING,
        ERROR
    };

    // Node Roles
    enum class NodeRole {
        SENSOR,
        ACTUATOR,
        GATEWAY,
        HYBRID
    };

    /**
     * @brief Command IDs for the Demeter Protocol V2.
     * @note Must match the Python definition in `schemas_protocol.py`.
     */
    enum class CommandType : uint8_t {
        PING            = 0x01, ///< Keep-alive check. Expects ACK.
        ACK             = 0x02, ///< Acknowledge successful command receipt.
        NACK            = 0x03, ///< Negative Acknowledge (Error).
        SYN             = 0x04, ///< Synchronize (Handshake 1/3).
        SYN_ACK         = 0x05, ///< Synchronize-Acknowledge (Handshake 2/3).
        ROUTE_ADD       = 0x0A, ///< Register a new route in the routing table.
        TEMP_HUM_REPORT = 0x0B, ///< Report Sensor Data (Temp/Hum). Replaces DATA_REPORT.
        PIN_REPORT      = 0x0C, ///< Report GPIO Pin State change.
        SYSTEM_REPORT   = 0x0D, ///< Report System State (Mode, Battery).
        SET_GPIO        = 0x10, ///< Set Digital Output state.
        SET_PWM         = 0x11, ///< Set PWM Duty Cycle.
        EXEC_SEQUENCE   = 0x30, ///< Execute a complex sequence of actions.
        GET_SENSORS     = 0x20, ///< Request Sensor Data.
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

    /**
     * @brief System Status Report.
     */
    struct SystemReport {
        uint8_t sourceId;
        uint8_t mode;
        uint16_t batteryMv;
    };

    /**
     * @brief Temp/Hum Sensor Report.
     */
    struct TempHumReport {
        uint8_t sourceId;
        float temperature;
        float humidity;
    };

    /**
     * @brief Pin Status Report.
     */
    struct PinReport {
        uint8_t sourceId;
        uint8_t pin;
        bool state;
    };

    /**
     * @brief Acknowledgement Data.
     */
    struct AckData {
        uint8_t sourceId;
        uint8_t context;
    };

    /**
     * @brief Command to add a static route (Mesh/Graph).
     */
    struct RouteAddCmd {
        uint8_t nodeId;
        std::array<uint8_t, 6> mac;
    };

    /**
     * @brief Generic NACK Data.
     */
    struct NackData {
        uint8_t sourceId;
        uint8_t errorCode; // Optional context
    };

    /**
     * @brief Generic Request Data (Ping, GetSensors).
     */
    struct RequestData {
        uint8_t sourceId;
    };

    // Callback Types (Standardized)
    using GpioCallback = std::function<void(const SetGpioCmd&)>;
    using PwmCallback = std::function<void(const SetPwmCmd&)>;
    using SequenceCallback = std::function<void(const ExecSequenceCmd&)>;
    using AckCallback = std::function<void(const AckData&)>;
    using PingCallback = std::function<void(const RequestData&)>;
    using TempHumReportCallback = std::function<void(const TempHumReport&)>;
    using PinReportCallback = std::function<void(const PinReport&)>;
    using SystemReportCallback = std::function<void(const SystemReport&)>;
    using GetSensorsCallback = std::function<void(const RequestData&)>;
    using RouteAddCallback = std::function<void(const RouteAddCmd&)>;
    using NackCallback = std::function<void(const NackData&)>;

    // Session Context for Handshake (ACK Payload)
    enum class SessionContext : uint8_t {
        GENERAL = 0x00,
        SENSOR_REPORT = 0x01,
        COMMAND = 0x02,
        CRITICAL_ALERT = 0x03
    };

}
