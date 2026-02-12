#include "core/Node_Sensor.h"
#include <Arduino.h>

Node_Sensor::Node_Sensor(uint8_t id, ProtocolEngine* engine) 
    : Node(id, engine), _sensorManager(new SensorManager()), 
      _reportIntervalMs(0), _lastReportTime(0), _deepSleepEnabled(false) {
    
    // Enable SensorManager in SystemContext
    if (_systemContext && _sensorManager) {
        _systemContext->enableSensorManager(_sensorManager);
    }
}

Node_Sensor::~Node_Sensor() {
    if (_sensorManager) {
        delete _sensorManager;
    }
}

void Node_Sensor::begin() {
    Node::begin();

    // Register Callback for Manual Read
    if (_engine) {
        _engine->onGetSensorsRecv([this](uint8_t srcId) {
            Serial.printf("[Node_Sensor] Manual Read Request from %d\n", srcId);
            this->collectAndSend();
        });
    }

    Serial.println("[Node_Sensor] Initialized.");
}

void Node_Sensor::update() {
    Node::update();

    if (_reportIntervalMs > 0) {
        if (millis() - _lastReportTime >= _reportIntervalMs) {
            collectAndSend();
            _lastReportTime = millis();

            if (_deepSleepEnabled) {
                Serial.println("[Node_Sensor] Going to Sleep...");
                Serial.flush();
                // esp_deep_sleep(_reportIntervalMs * 1000);
            }
        }
    }
}

void Node_Sensor::collectAndSend() {
    if (!_sensorManager || !_engine) return;

    // Use SensorManager to get readings
    auto readings = _sensorManager->readAll();
    
    // Send readings
    // For V2 MVP: We take the first sensor that gives valid data.
    // Or iterate? Protocol supports multiple reports?
    // ProtocolEngine has sendTempHumReport.
    
    for (const auto& data : readings) {
       // Determine Target (Gateway = 1)
       // We assume data.value1 is Temp, value2 is Hum for now as per ISensor conventions in this project
       _engine->sendTempHumReport(1, data.value1, data.value2);
       
       Serial.printf("[Node_Sensor] Reporting: %.2f / %.2f\n", data.value1, data.value2);
    }
}

void Node_Sensor::setReportingConfig(uint32_t intervalMs, bool deepSleep) {
    _reportIntervalMs = intervalMs;
    _deepSleepEnabled = deepSleep;
}
