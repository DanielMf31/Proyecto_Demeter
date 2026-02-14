#include "core/Node_Actuator.h"
#include <Arduino.h>

Node_Actuator::Node_Actuator(uint8_t id, ProtocolEngine* engine, GpioController* executor) 
    : _nodeId(id), _engine(engine), _systemManager(nullptr), 
      _executor(executor ? executor : new GpioController()) {
    
    if (_engine) {
        _systemManager = new SystemManager(_engine);
        // Enable Executor in SystemManager
        if (_executor) {
            _systemManager->enableExecutor(_executor);
        }
    }
}

Node_Actuator::~Node_Actuator() {
    if (_executor) {
        delete _executor;
    }
    if (_systemManager) {
        delete _systemManager;
    }
}

void Node_Actuator::begin() {
    if (!_systemManager) return;

    // 1. Initialize Context
    auto& ctx = _systemManager->getContext();
    ctx.setIdentity(_nodeId, Demeter::NodeRole::ACTUATOR);

    // 2. Initialize SystemManager
    _systemManager->setup();
    
    Serial.println("[Node_Actuator] Initialized.");
}

void Node_Actuator::update() {
    // 1. Update System Manager
    if (_systemManager) {
        _systemManager->update();
    } else {
        return;
    }

    // 2. Logic based on System State
    Demeter::SystemState state = _systemManager->getState();

    switch (state) {
        case Demeter::SystemState::BOOT:
        case Demeter::SystemState::IDLE:
        case Demeter::SystemState::ERROR:
            // Try to connect to Gateway (ID 1)
            static unsigned long lastConnectAttempt = 0;
            if (millis() - lastConnectAttempt > 5000) {
                 Serial.println("[Node_Actuator] State is IDLE/BOOT. Initiating Handshake with Gateway (1)...");
                 // Actuators usually listen, so GENERAL context is fine, or maybe we define a specific one later.
                 Demeter::AckData context = {0, (uint8_t)Demeter::SessionContext::GENERAL};
                 _systemManager->initiateHandshake(1, context);
                 lastConnectAttempt = millis();
            }
            break;

        case Demeter::SystemState::HANDSHAKE_SEND_SYN:
        case Demeter::SystemState::HANDSHAKE_WAIT_SYN_ACK:
        case Demeter::SystemState::HANDSHAKE_SEND_ACK:
            // Waiting for connection...
            break;

        case Demeter::SystemState::RUNNING:
            // Actuator is passive: waits for commands via callbacks.
            // We could implement a periodic "Heartbeat" here if needed.
            break;
    }
}

void Node_Actuator::addGpioListener(Demeter::GpioCallback cb) {
    if (_systemManager) {
        _systemManager->addGpioListener(cb);
    }
}
