#include "core/Node.h"
#include <Arduino.h>

Node::Node(uint8_t id, ProtocolEngine* engine) 
    : _nodeId(id), _engine(engine), _systemContext(nullptr) {
    if (_engine) {
        _systemContext = new SystemContext(_engine);
    }
}

Node::~Node() {
    if (_systemContext) {
        delete _systemContext;
    }
}

void Node::begin() {
    // 1. Initialize Engine ID
    if (_engine) {
        _engine->setNodeId(_nodeId);
    }

    // 2. Initialize SystemContext
    if (_systemContext) {
        _systemContext->setup();
    }
}

void Node::update() {
    // 1. Update Engine (via SystemContext or directly)
    // SystemContext::loop() calls engine->update()
    if (_systemContext) {
        _systemContext->loop();
    } else if (_engine) {
        _engine->update();
    }
}
