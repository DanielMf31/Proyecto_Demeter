#include "hardware/sensors/DHTSensor.h"
#include <Arduino.h>
#include <cmath>

// Conditional Include for Hardware
#ifndef NATIVE_ENV
#include <DHT.h>
#endif

using namespace Demeter::Sensors;

DHTSensor::DHTSensor(uint8_t pin, uint8_t type, bool isMock) 
    : _pin(pin), _type(type), _isMock(isMock), _dhtInstance(nullptr) {
    _name = _isMock ? "DHT (Mock)" : "DHT (Real)";
}

DHTSensor::~DHTSensor() {
    #ifndef NATIVE_ENV
    if (_dhtInstance && !_isMock) {
        delete (DHT*)_dhtInstance;
    }
    #endif
}

bool DHTSensor::init() {
    if (_isMock) {
        return true; 
    }

    #ifndef NATIVE_ENV
    // Real Hardware Init
    DHT* dht = new DHT(_pin, _type);
    dht->begin();
    _dhtInstance = dht;
    return true;
    #else
    return false; // Cannot init real hardware in Native
    #endif
}

bool DHTSensor::read(SensorReading& outReading) {
    if (_isMock) {
        // Simulate Data
        float t = millis() / 1000.0f;
        outReading.value1 = 25.0f + 2.0f * sin(t); // Temp
        outReading.value2 = 50.0f + 5.0f * cos(t); // Hum
        outReading.isValid = true;
        return true;
    }

    #ifndef NATIVE_ENV
    if (_dhtInstance) {
        DHT* dht = (DHT*)_dhtInstance;
        float h = dht->readHumidity();
        float t = dht->readTemperature();

        if (isnan(h) || isnan(t)) {
            outReading.isValid = false;
            return false;
        }

        outReading.value1 = t;
        outReading.value2 = h;
        outReading.isValid = true;
        return true;
    }
    #endif

    return false;
}

std::string DHTSensor::getName() const {
    return _name;
}
