#pragma once

#include <array>
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
    // Callback types are now in InternalTypes.h (Demeter namespace)

private:
    IComms* _strategy;
    uint8_t _myId; // Node ID

    // Callbacks
    Demeter::GpioCallback _onGpioCommand;
    Demeter::PwmCallback _onPwmCommand;
    Demeter::SequenceCallback _onSequenceCommand;
    Demeter::AckCallback _onAckRecv;
    Demeter::PingCallback _onPingRecv;
    Demeter::TempHumReportCallback _onTempHumReportRecv;
    Demeter::PinReportCallback    _onPinReport;
    Demeter::SystemReportCallback _onSystemReport;
    Demeter::GetSensorsCallback   _onGetSensors;
    Demeter::RouteAddCallback     _onRouteAdd;
    Demeter::NackCallback         _onNack;
    Demeter::AckCallback _onSynRecv;
    Demeter::AckCallback _onSynAckRecv;

public:
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

private:

    /**
     * @brief Calculates a simple Modular Sum CRC (Mod 256).
     * @param data Pointer to data buffer.
     * @param len Length of data in bytes.
     * @return uint8_t Calculated CRC.
     */
    uint8_t calculateCRC(const uint8_t* data, size_t len);

public:
    // =============================================================
    // SECTION: 1. Setup & Configuration (Parsing Logic)
    // =============================================================
    ProtocolEngine(IComms* strategy);

    /**
     * @brief Set the Node ID.
     * @param id The ID to use as Source within the protocol.
     */
    void setNodeId(uint8_t id);

    /**
     * @brief Update Loop (The "Heart" of the Parsing Stage).
     * Reads from strategy, parses frames, and dispatches callbacks.
     * Should be called frequently in loop().
     */
    void update();

    // Callback Setters
    void onSetGpio(Demeter::GpioCallback cb);
    void onSetPwm(Demeter::PwmCallback cb);
    void onExecSequence(Demeter::SequenceCallback cb);
    void onAckRecv(Demeter::AckCallback cb);
    void onPingRecv(Demeter::PingCallback cb);
    void onTempHumReportRecv(Demeter::TempHumReportCallback cb);
    void onPinReportRecv(Demeter::PinReportCallback cb);
    void onSystemReportRecv(Demeter::SystemReportCallback cb);
    void onGetSensorsRecv(Demeter::GetSensorsCallback cb);
    void onRouteAddRecv(Demeter::RouteAddCallback cb);
    void onNackRecv(Demeter::NackCallback cb);
    void onSynRecv(Demeter::AckCallback cb);
    void onSynAckRecv(Demeter::AckCallback cb);

    // --- Configuration ---
    /**
     * @brief Register a static route in the underlying comms strategy.
     * @param id The Node ID.
     * @param mac The MAC Address (6 bytes).
     */
    void registerRoute(uint8_t id, const std::array<uint8_t, 6>& mac);

    // =============================================================
    // SECTION: 2. High-Level Command Senders (Application Layer)
    // =============================================================
    // These methods construct specific commands and call sendFrame()

    /**
     * @brief Send Sensor Data Report (Temp/Hum).
     */
    void sendTempHumReport(uint8_t targetId, const Demeter::TempHumReport& report);

    /**
     * @brief Send GPIO State Report (Feedback).
     */
    void sendPinReport(uint8_t targetId, const Demeter::PinReport& report);

    /**
     * @brief Send System Status Report (Mode, Battery).
     */
    void sendSystemReport(uint8_t targetId, const Demeter::SystemReport& report);
    
    /**
     * @brief Send PING command to check connectivity.
     */
    void sendPing(uint8_t targetId, const Demeter::RequestData& data);
    
    /**
     * @brief Send SYN (Handshake 1/3) compatible with UART/ESP-Now.
     */
    void sendSyn(uint8_t targetId, const Demeter::AckData& data);

    /**
     * @brief Send SYN-ACK (Handshake 2/3).
     */
    void sendSynAck(uint8_t targetId, const Demeter::AckData& data);

    /**
     * @brief Send GPIO Control Command to set a pin state.
     */
    void sendSetGpio(uint8_t targetId, const Demeter::SetGpioCmd& cmd);

    /**
     * @brief Request Sensor Data from a node.
     */
    void sendGetSensors(uint8_t targetId, const Demeter::RequestData& data);

    /**
     * @brief Send Execution Sequence.
     */
    void sendExecSequence(uint8_t targetId, const Demeter::ExecSequenceCmd& cmd);

    // =============================================================
    // SECTION: 3. Low-Level Send Logic (Transport Layer)
    // =============================================================
    // These methods handle the raw frame construction, CRC, and transmission.

    /**
     * @brief Send ACK (Acknowledge) response, optionally with Context.
     */
    /**
     * @brief Send ACK (Acknowledge) response, optionally with Context.
     */
    void sendAck(uint8_t targetId, const Demeter::AckData& data);

private:
    /**
     * @brief Send NACK (Negative Acknowledge) response.
     */
    void sendNack(uint8_t targetId);

    /**
     * @brief Core method to build and send a frame via IComms.
     * Wraps payload with Header, Sync Byte, and CRC.
     */
    void sendFrame(uint8_t cmdId, uint8_t targetId, const std::vector<uint8_t>& payload);

    /**
     * @brief Internal parsing logic for a received frame buffer.
     * Validates CRC and Header before dispatching to callbacks.
     */
    void parseFrame(const std::vector<uint8_t>& frame);
};
