/**
 * @file SoilMoistureSensor.cpp
 * @brief Implementación del sensor capacitivo de humedad de suelo.
 * 
 * ============================================================================
 * DECISIONES DE ARQUITECTURA Y DISEÑO
 * ============================================================================
 * 1. **Calibración Analógica Integrada:** Los sensores capacitivos devuelven un
 *    voltaje raw del ADC del ESP32 (0-4095). Esta clase incorpora matemáticamente
 *    los umbrales `_airValue` (seco) y `_waterValue` (mojado) para mapearlo
 *    directamente a un porcentaje amigable [0%, 100%] mediante `map`.
 * 2. **Doble Reporte (Debug vs Prod):** Aprovechando que `SensorReading` tiene 
 *    doble capacidad, se escupe en `value1` el % real y en `value2` el valor "Raw" 
 *    del ADC. Esto ayuda enormemente a calibrar el sensor vía Backend si los
 *    umblares son incorrectos.
 */

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
