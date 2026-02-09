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

private:
    IComms* _strategy;
    GpioCallback _onGpioCommand;
    PwmCallback _onPwmCommand;
    SequenceCallback _onSequenceCommand;
    AckCallback _onAckRecv;
    
    uint8_t _myId = 1; // Default to Gateway ID

    // Frame Constants
    static const uint8_t SYNC_BYTE = 0xFE;
    static const uint8_t HEADER_SIZE = 6; // Sync, Len, Flags, Src, Dst, Cmd

    #pragma pack(push, 1)
    struct Header {
        uint8_t sync;
        uint8_t length;     // Payload Length
        uint8_t flags;
        uint8_t src_id;
        uint8_t dst_id;
        uint8_t cmd_id;
    };
    #pragma pack(pop)

    uint8_t calculateCRC(const uint8_t* data, size_t len);

public:
    /**
     * @brief Construct a new Protocol Engine.
     * @param strategy Pointer to the Communication Strategy (UART, LoRa...).
     */
    ProtocolEngine(IComms* strategy);

    /**
     * @brief Configure the local Node ID.
     * @param id The ID of this device (Default: 1).
     */
    void setNodeId(uint8_t id);

    /**
     * @brief Process incoming data from the strategy.
     * 
     * Reads available bytes from the transport layer, parses potential frames,
     * and triggers callbacks if a valid frame is found.
     * Should be called frequently in the main loop.
     */
    void update();

    /**
     * @brief Register callback for SET_GPIO commands.
     * @param cb Function to call when a valid GPIO command is received.
     */
    void onSetGpio(GpioCallback cb);

    /**
     * @brief Register callback for SET_PWM commands.
     * @param cb Function to call when a valid PWM command is received.
     */
    void onSetPwm(PwmCallback cb);

    /**
     * @brief Register callback for EXEC_SEQUENCE commands.
     * @param cb Function to call when a valid Sequence command is received.
     */
    void onExecSequence(SequenceCallback cb);

    /**
     * @brief Register callback for ACK reception.
     * @param cb Function to call when an ACK is received.
     */
    void onAckRecv(AckCallback cb);

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
