#include "hardware/sensors/DS18B20Sensor.h"
#include <Arduino.h>

// Conditional Includes
#ifndef NATIVE_ENV
#include <OneWire.h>
#include <DallasTemperature.h>
#endif

using namespace Demeter::Sensors;

DS18B20Sensor::DS18B20Sensor(uint8_t pin, bool isMock) 
    : _pin(pin), _isMock(isMock), _oneWire(nullptr), _sensors(nullptr) {
    _name = _isMock ? "DS18B20 (Mock)" : "DS18B20 (Real)";
}

DS18B20Sensor::~DS18B20Sensor() {
    #ifndef NATIVE_ENV
    if (_sensors && !_isMock) {
        delete (DallasTemperature*)_sensors;
    }
    if (_oneWire && !_isMock) {
        delete (OneWire*)_oneWire;
    }
    #endif
}

bool DS18B20Sensor::init() {
    if (_isMock) return true;

    #ifndef NATIVE_ENV
    OneWire* oneWire = new OneWire(_pin);
    DallasTemperature* sensors = new DallasTemperature(oneWire);
    sensors->begin();
    
    _oneWire = oneWire;
    _sensors = sensors;
    return true;
    #else
    return false;
    #endif
}

bool DS18B20Sensor::read(SensorReading& outReading) {
    if (_isMock) {
        // Mock Data: 18C - 22C
        outReading.value1 = 20.0f + ((rand() % 400) / 100.0f) - 2.0f; 
        outReading.value2 = 0.0f; // No humidity
        outReading.isValid = true;
        return true;
    }

    #ifndef NATIVE_ENV
    if (_sensors) {
        DallasTemperature* dt = (DallasTemperature*)_sensors;
        dt->requestTemperatures(); 
        // Note: requestTemperatures is blocking by default. 
        // For Async/Non-blocking, we would need a state machine here (Request -> Wait -> Read).
        // For MVP, blocking (~750ms) is acceptable if report interval is low.
        
        float tempC = dt->getTempCByIndex(0);
        if (tempC == DEVICE_DISCONNECTED_C) {
            outReading.isValid = false;
            return false;
        }

        outReading.value1 = tempC;
        outReading.value2 = 0.0f;
        outReading.isValid = true;
        return true;
    }
    #endif

    return false;
}

std::string DS18B20Sensor::getName() const {
    return _name;
}
