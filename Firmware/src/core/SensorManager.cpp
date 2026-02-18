#include "core/SensorManager.h"
#include <Arduino.h>

SensorManager::SensorManager() {}

void SensorManager::addSensor(Demeter::ISensor* sensor) {
    if (sensor) {
        _sensors.push_back(sensor);
    }
}

void SensorManager::begin() {
    for (auto* sensor : _sensors) {
        bool ok = sensor->init();
        Serial.printf("[SensorManager] Sensor '%s' Init: %s\n", 
            sensor->getName().c_str(), 
            ok ? "OK" : "FAIL");
    }
}

std::vector<Demeter::SensorReading> SensorManager::readAll() {
    std::vector<Demeter::SensorReading> readings;
    for (auto* sensor : _sensors) {
        Demeter::SensorReading data;
        if (sensor->read(data) && data.isValid) {
            readings.push_back(data);
        }
    }
    return readings;
}

const std::vector<Demeter::ISensor*>& SensorManager::getSensors() const {
    return _sensors;
}
