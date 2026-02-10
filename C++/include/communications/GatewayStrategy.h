#pragma once

#include "communications/IComms.h"
#include <vector>

/**
 * @class GatewayStrategy
 * @brief Composite Communication Strategy for the Gateway.
 * Manages both UART (Host connection) and ESP-Now (Node network).
 * Routes packets based on Destination ID.
 */
class GatewayStrategy : public IComms {
public:
    // Inject Abstract Interfaces for Testability
    GatewayStrategy(IComms* uart, IComms* espNow);

    void begin() override;
    void registerRoute(uint8_t id, const std::array<uint8_t, 6>& mac) override;
    void send(const uint8_t* data, size_t length) override;
    bool available() override;
    std::vector<uint8_t> read() override;

private:
    IComms* _uart;
    IComms* _espNow;
};
