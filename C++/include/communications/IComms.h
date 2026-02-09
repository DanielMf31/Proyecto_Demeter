#pragma once

/**
 * @file IComms.h
 * @brief Abstract Interface for Communication Strategies.
 * @author Proyecto Demeter Team
 * @date 2026-02-08
 */

#include <stdint.h>
#include <stddef.h>
#include <vector>
#include <array>

/**
 * @brief Abstract Interface for Communication Layer.
 * Implements the Strategy Pattern strictly.
 * 
 * Implementations: UartStrategy, EspNowStrategy, LoraStrategy.
 */
class IComms {
public:
    virtual ~IComms() {}

    /**
     * @brief Initialize the hardware interface (e.g. Serial.begin).
     */
    virtual void begin() = 0;

    /**
     * @brief Send raw bytes over the medium.
     * @param data Pointer to byte buffer.
     * @param length Number of bytes to send.
     */
    virtual void send(const uint8_t* data, size_t length) = 0;

    /**
     * @brief Check if bytes are available to read.
     * @return true if at least one byte is in buffer.
     */
    virtual bool available() = 0;

    /**
     * @brief Read all available bytes from the buffer.
     * Note: In a real constrained embedded system, passing vectors 
     * by value might be expensive, but for ESP32 and this architectural
     * pattern (where payload < 256 bytes), it's acceptable for cleanliness.
     * 
     * Alternative: read(uint8_t* buffer, size_t maxLen)
     * For now, following the design document's std::vector approach.
     */
    virtual std::vector<uint8_t> read() = 0;

    /**
     * @brief Register a route for a remote node (ESP-Now).
     * @param id Node ID (Protocol Level).
     * @param mac MAC Address (6 bytes).
     * Default implementation does nothing (for UART/LoRa).
     */
    virtual void registerRoute(uint8_t id, const std::array<uint8_t, 6>& mac) {
        (void)id; (void)mac;
    }
};
