#include "core/Node.h"
#include <Arduino.h>

Node::Node(uint8_t id, ProtocolEngine* engine) 
    : _nodeId(id), _engine(engine), _isSensorNode(false), 
      _reportIntervalMs(0), _lastReportTime(0) {}

void Node::registerSensor(Demeter::ISensor* sensor) {
    _sensors.push_back(sensor);
}

void Node::begin() {
    // 1. Initialize Engine ID
    if (_engine) {
        _engine->setNodeId(_nodeId);
    }

    // 2. Initialize Sensors
    for (auto* sensor : _sensors) {
        bool ok = sensor->init();
        Serial.printf("[Node] Sensor '%s' Init: %s\n", 
            sensor->getName().c_str(), 
            ok ? "OK" : "FAIL");
    }

    // 3. Register Callbacks on Engine (e.g. On-Demand reading)
    if (_engine) {
        _engine->onGetSensorsRecv([this](uint8_t srcId) {
            Serial.printf("[Node] Manual Read Request from %d\n", srcId);
            this->collectAndSend();
        });
    }
}

void Node::update() {
    // 1. Update Engine (Process Incoming)
    if (_engine) {
        _engine->update();
    }

    // 2. Periodic Reporting
    if (_reportIntervalMs > 0) {
        if (millis() - _lastReportTime >= _reportIntervalMs) {
            collectAndSend();
            _lastReportTime = millis();
            
            // 3. Deep Sleep Handling (Simplified for now)
            if (_isSensorNode) {
                Serial.println("[Node] Going to Sleep...");
                Serial.flush();
                // esp_deep_sleep(_reportIntervalMs * 1000); 
                // Note: Real deep sleep requires reinits. Use Light Sleep or delay for prototype.
            }
        }
    }
}

void Node::collectAndSend() {
    // Iterate sensors and send data
    // Protocol V2 supports CMD_DATA_REPORT with 2 values (Temp/Hum).
    // If we have multiple sensors, we might need multiple packets or a combined one.
    // For V2 MVP: We take the first sensor that gives valid data.
    
    for (auto* sensor : _sensors) {
        Demeter::SensorReading data;
        if (sensor->read(data) && data.isValid) {
            Serial.printf("[Node] Reading from %s: %.2f / %.2f\n", 
                sensor->getName().c_str(), data.value1, data.value2);
            
            // Determine Target (Gateway = 1 or Host = 0?)
            // Usually valid to send to Gateway (1).
            if (_engine) {
                _engine->sendTempHumReport(1, data.value1, data.value2);
            }
        }
    }
}

void Node::setReportingConfig(uint32_t intervalMs, bool deepSleep) {
    _reportIntervalMs = intervalMs;
    _isSensorNode = deepSleep;
}
