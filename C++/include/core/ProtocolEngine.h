#pragma once

#include "communications/IComms.h"
#include "core/InternalTypes.h"
#include <functional>

/**
 * @brief Binary Protocol Parser (V2).
 * Handles Serialization/Deserialization and CRC Validation.
 */
/**
 * @class ProtocolEngine
 * @brief Handles the Demeter Binary Protocol (V2).
 * 
 * Responsible for:
 * 1. Deserializing incoming byte streams into frames.
 * 2. Validating frames (Sync Byte, Length, CRC).
 * 3. Dispatching valid commands to registered callbacks.
 * 4. Generating and serializing response frames (ACK/NACK).
 * 
 * @note This class is platform-agnostic. It relies on IComms interface.
 */
class ProtocolEngine {
public:
    // Callback types for event handling
    using GpioCallback = std::function<void(const Demeter::SetGpioCmd&)>;
    using PwmCallback = std::function<void(const Demeter::SetPwmCmd&)>;
    using SequenceCallback = std::function<void(const Demeter::ExecSequenceCmd&)>;
    using AckCallback = std::function<void(uint8_t srcId)>;
    using PingCallback = std::function<void(uint8_t srcId)>;
    using TempHumReportCallback = std::function<void(uint8_t srcId, float temp, float hum)>;
    using PinReportCallback = std::function<void(uint8_t srcId, uint8_t pin, bool state)>;
    using SystemReportCallback = std::function<void(uint8_t srcId, uint8_t mode, uint16_t batteryMv)>;
    using GetSensorsCallback = std::function<void(uint8_t srcId)>;

private:
    IComms* _strategy;
    GpioCallback _onGpioCommand;
    PwmCallback _onPwmCommand;
    SequenceCallback _onSequenceCommand;
    AckCallback _onAckRecv;
    PingCallback _onPingRecv;
    TempHumReportCallback _onTempHumReportRecv;
    PinReportCallback _onPinReportRecv;
    SystemReportCallback _onSystemReportRecv;
    GetSensorsCallback _onGetSensorsRecv;
    
    // ...

public:
    // ...

    /**
     * @brief Send Sensor Data Report (Temp/Hum)
     * Replaces sendDataReport.
     * @param targetId Destination Device ID.
     * @param temp Temperature in Celsius.
     * @param hum Humidity in %.
     */
    void sendTempHumReport(uint8_t targetId, float temp, float hum);

    /**
     * @brief Send GPIO State Report (Feedback).
     * @param targetId Destination Device ID.
     * @param pin GPIO Number.
     * @param state Current State (true=HIGH).
     */
    void sendPinReport(uint8_t targetId, uint8_t pin, bool state);

    /**
     * @brief Send System Status Report.
     * @param targetId Destination Device ID.
     * @param mode System Mode (0=Active, 1=LightSleep, 2=DeepSleep).
     * @param batteryMv Battery Voltage in millivolts.
     */
    void sendSystemReport(uint8_t targetId, uint8_t mode, uint16_t batteryMv);

    // ...

    /**
     * @brief Register callback for TempHumReport reception.
     * @param cb Function to call when a Temp/Hum Report is received.
     */
    void onTempHumReportRecv(TempHumReportCallback cb);

    /**
     * @brief Register callback for PinReport reception.
     * @param cb Function to call when a Pin Report is received.
     */
    void onPinReportRecv(PinReportCallback cb);

    /**
     * @brief Register callback for SystemReport reception.
     * @param cb Function to call when a System Report is received.
     */
    void onSystemReportRecv(SystemReportCallback cb);

    /**
     * @brief Register callback for GET_SENSORS reception.
     * @param cb Function to call when a GET_SENSORS command is received.
     */
    void onGetSensorsRecv(GetSensorsCallback cb);

private:
    /**
     * @brief Send an ACK (Acknowledge) frame.
     * @param targetId The device ID to send the ACK to.
     */
    void sendAck(uint8_t targetId);

    /**
     * @brief Send a NACK (Negative Acknowledge) frame.
     * @param targetId The device ID to send the NACK to.
     */
    void sendNack(uint8_t targetId);

    /**
     * @brief Construct and send a generic frame.
     * 
     * Handles the creation of the header, calculation of CRC, and transmission
     * via the strategy.
     * 
     * @param cmdId Command ID (e.g., PING, ACK).
     * @param targetId Destination Device ID.
     * @param payload Vector containing the command payload.
     */
    void sendFrame(uint8_t cmdId, uint8_t targetId, const std::vector<uint8_t>& payload);

    // Helpers for testing
    /**
     * @brief Parses a single frame buffer.
     * Exposed for Unit Testing purposes.
     * @param frame byte vector containing the full frame (header + payload + crc).
     */
    void parseFrame(const std::vector<uint8_t>& frame);
};
