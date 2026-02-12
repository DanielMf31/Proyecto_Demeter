#include "core/Node_Actuator.h"
#include <Arduino.h>

Node_Actuator::Node_Actuator(uint8_t id, ProtocolEngine* engine) 
    : Node(id, engine), _executor(new GpioController()) {
    // Enable Executor in SystemContext
    if (_systemContext && _executor) {
        _systemContext->enableExecutor(_executor);
    }
}

Node_Actuator::~Node_Actuator() {
    if (_executor) {
        delete _executor;
    }
}

void Node_Actuator::begin() {
    // Call Base Begin (inits SystemContext and Engine ID)
    Node::begin();
    
    Serial.println("[Node_Actuator] Initialized.");
}
