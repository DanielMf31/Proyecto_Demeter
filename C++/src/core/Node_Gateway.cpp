#include "core/Node_Gateway.h"

Node_Gateway::Node_Gateway(uint8_t id, ProtocolEngine* engine) 
    : Node(id, engine) {
    _executor = new GpioController();
    _sensorManager = new SensorManager();
}

Node_Gateway::~Node_Gateway() {
    delete _executor;
    delete _sensorManager;
}

void Node_Gateway::begin() {
    // 1. Initialize Hardware Config (Before Context Setup)
    if (_executor) {
        // Default pin configuration for Gateway (if any)
        // For now, we can leave it empty or map specific pins
        // Example: Gateway might have a status LED on Pin 4
        _executor->setPins({4}); 
    }

    // 2. Initialize System Context with Hybrid Capabilities
    if (_systemContext) {
        _systemContext->enableExecutor(_executor);
        _systemContext->enableSensorManager(_sensorManager);
        _systemContext->setup(); // Initialize Context Logic (Calls executor->init and sensorManager->begin)
    }

    // 3. Initialize Communication (Engine)
    // Note: ProtocolEngine::begin() is not explicit, but initialization happens via constructor dependencies
    // However, if there are specific start-up sequences, do them here.
}

void Node_Gateway::update() {
    Node::update(); // Updates SystemContext and Engine

    // Additional Gateway logic if needed
    // e.g., Periodic status checks or local sensor reading
}
