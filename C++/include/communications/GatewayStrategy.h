#pragma once

#include "communications/IComms.h"
#include "communications/UartStrategy.h"
#include "communications/EspNowStrategy.h"
#include <vector>

/**
 * @class GatewayStrategy
 * @brief Composite Communication Strategy for the Gateway.
 * Manages both UART (Host connection) and ESP-Now (Node network).
 * Routes packets based on Destination ID.
 */
class GatewayStrategy : public IComms {
public:
    GatewayStrategy(UartStrategy* uart, EspNowStrategy* espNow) 
        : _uart(uart), _espNow(espNow) {}

    void begin() override {
        _uart->begin();
        _espNow->begin();
    }

    void registerRoute(uint8_t id, const std::array<uint8_t, 6>& mac) override {
        // Routes are for ESP-Now nodes
        _espNow->registerRoute(id, mac);
    }

    void send(const uint8_t* data, size_t length) override {
        if (length < 6) return;

        // Extract Destination ID (Index 4)
        uint8_t dstId = data[4];

        if (dstId == 0) {
            // ID 0 is reserved for Host -> Send via UART
            _uart->send(data, length);
        } else {
            // All other valid IDs (except self=1) are likely ESP-Now nodes
            // EspNowStrategy handles lookup and sending.
            // If unknown, it drops it. 
            // Note: EspNowStrategy.send() performs the route lookup.
            _espNow->send(data, length);
        }
    }

    bool available() override {
        return _uart->available() || _espNow->available();
    }

    std::vector<uint8_t> read() override {
        // Priority to UART (Command from Host)
        if (_uart->available()) {
            return _uart->read();
        }
        // Then ESP-Now (Response from Node)
        if (_espNow->available()) {
            return _espNow->read();
        }
        return {};
    }

private:
    UartStrategy* _uart;
    EspNowStrategy* _espNow;
};
