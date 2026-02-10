#include "hardware/sensors/SoilMoistureSensor.h"
#include <Arduino.h>
#include <algorithm>

using namespace Demeter::Sensors;

SoilMoistureSensor::SoilMoistureSensor(uint8_t pin, int airVal, int waterVal, bool isMock) 
    : _pin(pin), _airValue(airVal), _waterValue(waterVal), _isMock(isMock) {
    _name = _isMock ? "Soil Moisture (Mock)" : "Soil Moisture (Real)";
}

bool SoilMoistureSensor::init() {
    if (!_isMock) {
        pinMode(_pin, INPUT);
    }
    return true;
}

bool SoilMoistureSensor::read(SensorReading& outReading) {
    if (_isMock) {
        // Mock Data: 0 - 100%
        outReading.value1 = (float)(rand() % 101); // % Moisture
        outReading.value2 = 0.0f;
        outReading.isValid = true;
        return true;
    }

    #ifndef NATIVE_ENV
    int raw = analogRead(_pin);
    
    // Map raw to 0-100%
    // Note: Capacitive sensors usually give High value for Dry (Air) and Low for Wet (Water).
    // So we map from [Air, Water] to [0, 100].
    
    long mapVal = map(raw, _airValue, _waterValue, 0, 100);
    
    // Constrain to 0-100
    mapVal = std::max(0L, std::min(100L, mapVal));

    outReading.value1 = (float)mapVal;
    outReading.value2 = (float)raw; // Return Raw value as secondary for debug/calibration
    outReading.isValid = true;
    return true;
    #else
    return false;
    #endif
}

std::string SoilMoistureSensor::getName() const {
    return _name;
}
