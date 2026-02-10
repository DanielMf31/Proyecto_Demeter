#pragma once

#include "communications/IComms.h"
#include <vector>
#include <cstring>
#include <iostream>

class MockComms : public IComms {
public:
    std::vector<uint8_t> lastSentData;
    bool sendCalled = false;

    // Simulate RX
    std::vector<uint8_t> rxBuffer;

    void begin() override {}
    
    void send(const uint8_t* data, size_t length) override {
        sendCalled = true;
        lastSentData.clear();
        lastSentData.insert(lastSentData.end(), data, data + length);
    }

    void registerRoute(uint8_t id, const std::array<uint8_t, 6>& mac) override {}
    
    bool available() override { 
        return !rxBuffer.empty(); 
    }

    std::vector<uint8_t> read() override { 
        if (rxBuffer.empty()) return {};
        std::vector<uint8_t> ret = rxBuffer;
        rxBuffer.clear(); // Consume
        return ret;
    }

    // Helper for Tests
    void pushRx(const std::vector<uint8_t>& data) {
        rxBuffer.insert(rxBuffer.end(), data.begin(), data.end());
    }
};
