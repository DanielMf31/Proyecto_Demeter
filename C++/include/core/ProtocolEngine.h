#pragma once

#include "communications/IComms.h"
#include "core/InternalTypes.h"
#include <functional>

/**
 * @brief Binary Protocol Parser (V2).
 * Handles Serialization/Deserialization and CRC Validation.
 */
class ProtocolEngine {
public:
    // Callback types for event handling
    using GpioCallback = std::function<void(const Demeter::SetGpioCmd&)>;

private:
    IComms* _strategy;
    GpioCallback _onGpioCommand;

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
     * @brief Construct a new Protocol Engine
     * @param strategy Pointer to the Communication Strategy (UART, LoRa...)
     */
    ProtocolEngine(IComms* strategy);

    /**
     * @brief Process incoming data from the strategy.
     * Should be called in the main loop.
     */
    void update();

    /**
     * @brief Register callback for SET_GPIO commands.
     */
    void onSetGpio(GpioCallback cb);
    
    // Helpers for testing
    void parseFrame(const std::vector<uint8_t>& frame);
};
