#pragma once
#include <stdint.h>
#include "InternalTypes.h"
#include <vector>

namespace Demeter {

    /**
     * @brief Centralized System Context.
     * Manages Identity, State, and Configuration for the Node.
     */
    class SystemContext {
    private:
        // --- Identity ---
        uint8_t _nodeId;
        uint8_t _gatewayId;
        NodeRole _role;
        
        // --- State ---
        SystemState _currentState; 
        uint16_t _batteryMv;
        uint32_t _uptimeSeconds;
        uint8_t _lastErrorCode;

        // --- Configuration ---
        bool _deepSleepEnabled;
        uint32_t _reportIntervalMs;
        std::vector<uint8_t> _activePins;

    public:
        SystemContext();

        // Getters & Setters
        void setIdentity(uint8_t id, NodeRole role, uint8_t gatewayId = 1);
        uint8_t nodeId() const { return _nodeId; }
        uint8_t gatewayId() const { return _gatewayId; }
        NodeRole role() const { return _role; }

        // State Management
        void setState(SystemState state);
        SystemState getState() const { return _currentState; }
        
        void updateBattery(uint16_t mv);
        uint16_t getBattery() const { return _batteryMv; }

        // Config
        void setConfig(uint32_t intervalMs, bool deepSleep);
        bool isDeepSleepEnabled() const { return _deepSleepEnabled; }
        uint32_t getReportInterval() const { return _reportIntervalMs; }
    };
}
