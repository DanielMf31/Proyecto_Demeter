#pragma once

#include "communications/IComms.h"
#include <esp_now.h>
#include <map>
#include <array>
#include <vector>

/**
 * @class EspNowStrategy
 * @brief Implementation of IComms for ESP-Now.
 * Handles peer registration and sending/receiving data via ESP-Now.
 */
class EspNowStrategy : public IComms {
public:
    EspNowStrategy();
    virtual ~EspNowStrategy();

    // IComms Interface
    void begin() override;
    void send(const uint8_t* data, size_t length) override;
    bool available() override;
    std::vector<uint8_t> read() override;
    void registerRoute(uint8_t id, const std::array<uint8_t, 6>& mac) override;

    // ESP-Now Callbacks (Static wrappers)
    static void onDataSent(const uint8_t *mac_addr, esp_now_send_status_t status);
    static void onDataRecv(const uint8_t * mac, const uint8_t *incomingData, int len);

private:
    static std::map<uint8_t, std::array<uint8_t, 6>> _routeTable;
    static std::vector<uint8_t> _rxBuffer;
    static bool _rxAvailable;
    
    // Helper to add peer to ESP-Now stack
    bool addPeer(const uint8_t* mac);
};
