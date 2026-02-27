#pragma once

#include "core/ProtocolEngine.h"
#include "core/GpioController.h"
#include "core/SensorManager.h"
#include "communications/IComms.h"
#include <vector>
#include <map>

// --- Mock Comms Strategy ---
class MockComms : public IComms {
public:
    std::vector<uint8_t> lastSentPacket;
    bool availableFlag = false;
    
    void begin() override {}
    void registerRoute(uint8_t id, const std::array<uint8_t, 6>& mac) override {}
    
    std::vector<uint8_t> rxBuffer;

    void send(const uint8_t* data, size_t length) override {
        lastSentPacket.assign(data, data + length);
    }
    
    bool available() override { return !rxBuffer.empty(); }
    
    std::vector<uint8_t> read() override {
        if (rxBuffer.empty()) return {};
        std::vector<uint8_t> temp = rxBuffer;
        rxBuffer.clear(); // One-shot read for simplicity
        return temp;
    }

    void inject(const std::vector<uint8_t>& data) {
        rxBuffer = data;
    }

    bool addPeer(const uint8_t* mac) override { return true; } // Stub
};

// --- Mock Protocol Engine ---
// We can use the REAL ProtocolEngine with a MockComms, OR extend/mock it.
// Since we want to test the Node logic (Layer 3), we should ideally trust ProtocolEngine (Layer 2) works
// if we tested it separately. However, injecting data into Node often requires triggering Engine Callbacks.
// A helper wrapper to trigger callbacks is useful.

class ProtocolEngineWrapper : public ProtocolEngine {
public:
    ProtocolEngineWrapper(IComms* strategy) : ProtocolEngine(strategy) {}

    // Public triggers for protected callbacks (if we had access, but we assume we trigger via receive)
    // Actually, Engine callbacks are register-only. To trigger them, we must simulate packet reception
    // OR just use the Engine's `onSetGpio` setters to inspect what the Node registered.
    
    // Better approach for Node testing: 
    // The Node registers callbacks on the Engine. We want to verify it registered them.
    // And when we trigger the callback, the Node does something.
    
    // To trigger the callback: We can inject a valid packet into MockComms and call engine.update().
};

// --- Mock GPIO Controller ---
class MockGpioController : public GpioController {
public:
    std::map<uint8_t, bool> pinStates;

    bool digitalWrite(uint8_t pin, uint8_t val) override {
        pinStates[pin] = (val > 0);
        return true;
    }

    uint8_t digitalRead(uint8_t pin) override {
        return pinStates[pin] ? 1 : 0;
    }
    
    // Helper
    bool getPinState(uint8_t pin) {
        return pinStates[pin];
    }
};

// --- Mock Sensor Manager ---
class MockSensorManager : public SensorManager {
public:
    float mockTemp = 25.0;
    float mockHum = 60.0;

    void readAll() override {
        // No-op
    }

    String getJson() override {
        return "{\"temp\": 25.0, \"hum\": 60.0}";
    }
    
    // Override explicit getters if they exist in base, 
    // typically SensorManager just manages list. 
    // If Node calls specific sensors, we might need deeper mocks.
    // Assuming Node uses SensorManager abstractions.
};
