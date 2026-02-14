#include "core/Node_Sensor.h"
#include <Arduino.h>

Node_Sensor::Node_Sensor(uint8_t id, ProtocolEngine* engine) 
    : _nodeId(id), _engine(engine), _systemManager(nullptr),
      _sensorManager(new SensorManager()), 
      _reportIntervalMs(0), _lastReportTime(0), _deepSleepEnabled(false) {
    
    // Dependency Injection into SystemManager
    if (_engine) {
        _systemManager = new SystemManager(_engine);
        // Enable SensorManager in SystemManager
        if (_sensorManager) {
            _systemManager->enableSensorManager(_sensorManager);
        }
    }
}

Node_Sensor::~Node_Sensor() {
    if (_sensorManager) {
        delete _sensorManager;
    }
    if (_systemManager) {
        delete _systemManager;
    }
}

void Node_Sensor::begin() {
    if (!_systemManager) return;

    // 1. Initialize Context
    auto& ctx = _systemManager->getContext();
    ctx.setIdentity(_nodeId, Demeter::NodeRole::SENSOR);
    ctx.setConfig(_reportIntervalMs, _deepSleepEnabled);

    // 2. Initialize SystemManager (Handles callbacks like GetSensors automatically)
    _systemManager->setup();

    Serial.println("[Node_Sensor] Initialized.");
}

void Node_Sensor::update() {
    // 1. Update System Manager (which updates Engine)
    if (_systemManager) {
        _systemManager->update();
    } else {
        return; // specific error handling or fallback?
    }

    // 2. Logic based on System State
    Demeter::SystemState state = _systemManager->getState();

    switch (state) {
        case Demeter::SystemState::BOOT:
        case Demeter::SystemState::IDLE:
        case Demeter::SystemState::ERROR:
            // Try to connect to Gateway (ID 1)
            // Throttle connection attempts? SystemManager handles handshake timeout individually, 
            // but we shouldn't spam initiateHandshake every loop if it's already "IDLE" after a failure.
            // For now, simple logic: If IDLE, try to connect.
            // But we need a "Retry Interval" here or inside SystemManager.
            // SystemManager::initiateHandshake checks if already in progress, but if it failed and went back to IDLE...
            // Let's rely on a simple periodic check here to avoid spamming.
            static unsigned long lastConnectAttempt = 0;
            if (millis() - lastConnectAttempt > 5000) {
                 Serial.println("[Node_Sensor] State is IDLE/BOOT. Initiating Handshake with Gateway (1)...");
                 Demeter::AckData context = {0, (uint8_t)Demeter::SessionContext::SENSOR_REPORT};
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
            // 3. Connected! Periodic Reporting Logic
            if (_reportIntervalMs > 0) {
                if (millis() - _lastReportTime >= _reportIntervalMs) {
                    // DELEGATE TO SYSTEM MANAGER
                    _systemManager->collectAndPublishSensorData(1); // Target Gateway (1)
                    _lastReportTime = millis();

                    if (_deepSleepEnabled) {
                        Serial.println("[Node_Sensor] Going to Sleep...");
                        Serial.flush();
                        // esp_deep_sleep(_reportIntervalMs * 1000);
                    }
                }
            }
            break;
    }
}

void Node_Sensor::collectAndSend() {
    // Deprecated. Use _systemManager->collectAndPublishSensorData(1) directly
    if (_systemManager) _systemManager->collectAndPublishSensorData(1);
}

void Node_Sensor::setReportingConfig(uint32_t intervalMs, bool deepSleep) {
    _reportIntervalMs = intervalMs;
    _deepSleepEnabled = deepSleep;
}
