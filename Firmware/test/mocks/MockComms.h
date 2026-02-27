#pragma once

#include "communications/IComms.h"
#include <vector>
#include <array>
#include <cstdint>
#include <cstring>

class MockComms : public IComms {
public:
    std::vector<uint8_t> _rxBuffer;
    std::vector<uint8_t> _txBuffer;
    
    // For verifying routed packets
    struct RoutedPacket {
        std::vector<uint8_t> data;
    };
    std::vector<RoutedPacket> _routedPackets;

    // For verifying route registration
    struct RouteEntry {
        uint8_t nodeId;
        std::array<uint8_t, 6> mac;
    };
    std::vector<RouteEntry> _registeredRoutes;

    void begin() override {}
    
    void send(const uint8_t* data, size_t length) override {
        // Capture outgoing data
        _txBuffer.insert(_txBuffer.end(), data, data + length);
    }
    
    bool available() override { return !_rxBuffer.empty(); }
    
    std::vector<uint8_t> read() override {
        std::vector<uint8_t> temp = _rxBuffer;
        _rxBuffer.clear();
        return temp;
    }

    void registerRoute(uint8_t nodeId, const std::array<uint8_t, 6>& mac) override {
        _registeredRoutes.push_back({nodeId, mac});
    }

    // Helper to push data to "Rx" (Simulate incoming data)
    void pushRxData(const std::vector<uint8_t>& data) {
        _rxBuffer.insert(_rxBuffer.end(), data.begin(), data.end());
    }
    
    // Clear all history
    void reset() {
        _rxBuffer.clear();
        _txBuffer.clear();
        _registeredRoutes.clear();
        _routedPackets.clear(); 
    }
};
