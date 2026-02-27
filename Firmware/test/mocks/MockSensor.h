#pragma once

#include "hardware/ISensor.h"

class MockSensor : public Demeter::ISensor {
private:
    float _temp;
    float _hum;
    bool _initialized;

public:
    MockSensor() : _temp(25.0f), _hum(50.0f), _initialized(false) {}

    bool init() override {
        _initialized = true;
        return true;
    }

    bool read(Demeter::SensorReading& out) override {
        if (!_initialized) return false;
        out.value1 = _temp;
        out.value2 = _hum;
        out.isValid = true;
        return true;
    }

    std::string getName() const override {
        return "MockSensor";
    }

    // Helper to set values for testing
    void setValues(float t, float h) {
        _temp = t;
        _hum = h;
    }
};
