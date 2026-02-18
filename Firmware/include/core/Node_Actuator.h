#pragma once

#include "core/INode.h"
#include "core/ProtocolEngine.h"
#include "core/SystemManager.h"
#include "core/GpioController.h"

/**
 * @file Node_Actuator.h
 * @brief Concrete Node implementation for Actuators.
 */

class Node_Actuator : public INode {
private:
    uint8_t _nodeId;
    ProtocolEngine* _engine;
    SystemManager* _systemManager;
    GpioController* _executor;

public:
    Node_Actuator(uint8_t id, ProtocolEngine* engine, GpioController* executor = nullptr);
    ~Node_Actuator();

    void begin() override;
    void update() override;
    
    // Facade Methods
    void addGpioListener(Demeter::GpioCallback cb);
    
    // Allow access to executor for setup
    GpioController* getExecutor() { return _executor; }
    SystemManager* getSystemManager() { return _systemManager; }
};
