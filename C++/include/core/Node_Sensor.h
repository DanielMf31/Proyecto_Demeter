#pragma once

#include "core/INode.h"
#include "core/ProtocolEngine.h"
#include "core/SystemManager.h"
#include "core/SensorManager.h"

/**
 * @file Node_Sensor.h
 * @brief Concrete Node implementation for Sensors.
 * Manages SensorManager, ProtocolEngine, and SystemManager explicitly.
 */

class Node_Sensor : public INode {
private:
    uint8_t _nodeId;
    ProtocolEngine* _engine;
    SystemManager* _systemManager;
    SensorManager* _sensorManager;
    
    // Reporting Config
    uint32_t _reportIntervalMs;
    unsigned long _lastReportTime;
    bool _deepSleepEnabled;

    void collectAndSend();

public:
    Node_Sensor(uint8_t id, ProtocolEngine* engine);
    ~Node_Sensor();

    void begin() override;
    void update() override;

    /**
     * @brief Configure reporting behavior.
     * @param intervalMs Time between data reports (0 = On Demand Only).
     * @param deepSleep Enable Deep Sleep between reports?
     */
    void setReportingConfig(uint32_t intervalMs, bool deepSleep);

    SensorManager* getSensorManager() { return _sensorManager; }
    SystemManager* getSystemManager() { return _systemManager; }
};
