#include "core/Node_Gateway.h"
#include <Arduino.h>

Node_Gateway::Node_Gateway(uint8_t id, ProtocolEngine* engine) 
    : _nodeId(id), _engine(engine), _systemManager(nullptr) {
    
    // Create Components
    _executor = new GpioController();
    _sensorManager = new SensorManager();

    // Dependency Injection into SystemManager
    if (_engine) {
        _systemManager = new SystemManager(_engine);
        _systemManager->enableExecutor(_executor);
        _systemManager->enableSensorManager(_sensorManager);
    }
}

Node_Gateway::~Node_Gateway() {
    delete _executor;
    delete _sensorManager;
    if (_systemManager) {
        delete _systemManager;
    }
}

void Node_Gateway::begin() {
    if (!_systemManager) return;

    // 1. Initialize Context
    auto& ctx = _systemManager->getContext();
    ctx.setIdentity(_nodeId, Demeter::NodeRole::GATEWAY);

    // 2. Initialize Hardware Config
    if (auto* executor = _systemManager->getExecutor()) {
        // Manage pins for the 4 web buttons
        executor->setPins({4, 5, 6, 7}); 
    }

    // 3. Initialize System Logic
    _systemManager->setup(); // Initialize Context Logic & Callbacks
}

void Node_Gateway::update() {
    // Updates SystemManager and Engine
    if (_systemManager) {
        _systemManager->update();
    } else if (_engine) {
        _engine->update();
    }

    // Additional Gateway logic if needed
}
