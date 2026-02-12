#pragma once

#include "communications/IComms.h"
#include "core/InternalTypes.h"
#include <functional>
#include <vector>
#include <cstdint>
#include <cstddef>

/**
 * @brief Binary Protocol Parser (V2).
 * Handles Serialization/Deserialization and CRC Validation.
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
    uint8_t _myId; // Node ID

    // Callbacks
    GpioCallback _onGpioCommand;
    PwmCallback _onPwmCommand;
    SequenceCallback _onSequenceCommand;
    AckCallback _onAckRecv;
    PingCallback _onPingRecv;
    TempHumReportCallback _onTempHumReportRecv;
    PinReportCallback _onPinReportRecv;
    SystemReportCallback _onSystemReportRecv;
    GetSensorsCallback _onGetSensorsRecv;

    // Protocol Constants
    static const uint8_t SYNC_BYTE = 0xFE;

    // Header Structure (Packed)
    struct Header {
        uint8_t sync;
        uint8_t length;     // Payload Length
        uint8_t flags;
        uint8_t src_id;
        uint8_t dst_id;
        uint8_t cmd_id;
    } __attribute__((packed));

    static const size_t HEADER_SIZE = sizeof(Header);

    /**
     * @brief Calculates a simple Modular Sum CRC (Mod 256).
     * @param data Pointer to data buffer.
     * @param len Length of data in bytes.
     * @return uint8_t Calculated CRC.
     */
    uint8_t calculateCRC(const uint8_t* data, size_t len);

public:
    ProtocolEngine(IComms* strategy);

    // Callback Setters
    void onSetGpio(GpioCallback cb);
    void onSetPwm(PwmCallback cb);
    void onExecSequence(SequenceCallback cb);
    void onAckRecv(AckCallback cb);
    void onPingRecv(PingCallback cb);
    void onTempHumReportRecv(TempHumReportCallback cb);
    void onPinReportRecv(PinReportCallback cb);
    void onSystemReportRecv(SystemReportCallback cb);
    void onGetSensorsRecv(GetSensorsCallback cb);

    /**
     * @brief Update Loop.
     * Reads from strategy, parses frames, and dispatches callbacks.
     */
    void update();

    /**
     * @brief Set the Node ID.
     * @param id The ID to use as Source.
     */
    void setNodeId(uint8_t id);

    /**
     * @brief Send Sensor Data Report (Temp/Hum)
     * Replaces sendDataReport.
     */
    void sendTempHumReport(uint8_t targetId, float temp, float hum);

    /**
     * @brief Send GPIO State Report (Feedback).
     */
    void sendPinReport(uint8_t targetId, uint8_t pin, bool state);

    /**
     * @brief Send System Status Report.
     */
    void sendSystemReport(uint8_t targetId, uint8_t mode, uint16_t batteryMv);
    
    /**
     * @brief Send PING.
     */
    void sendPing(uint8_t targetId);

private:
    /**
     * @brief Send Frame Helpers.
     */
    void sendAck(uint8_t targetId);
    void sendNack(uint8_t targetId);
    void sendFrame(uint8_t cmdId, uint8_t targetId, const std::vector<uint8_t>& payload);

    /**
     * @brief Parses a single frame buffer.
     */
    void parseFrame(const std::vector<uint8_t>& frame);
};
