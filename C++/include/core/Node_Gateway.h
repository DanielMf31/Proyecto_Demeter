#pragma once

#include "core/INode.h"
#include "core/ProtocolEngine.h"
#include "core/SystemManager.h"
#include "core/GpioController.h"
#include "core/SensorManager.h"

class Node_Gateway : public INode {
private:
    uint8_t _nodeId;
    ProtocolEngine* _engine;
    SystemManager* _systemManager;
    GpioController* _executor;
    SensorManager* _sensorManager;

public:
    Node_Gateway(uint8_t id, ProtocolEngine* engine);
    ~Node_Gateway();

    void begin() override;
    void update() override;

    // Accessors for hybrid capabilities
    GpioController* getExecutor() { return _executor; }
    SensorManager* getSensorManager() { return _sensorManager; }
    SystemManager* getSystemManager() { return _systemManager; }
};
