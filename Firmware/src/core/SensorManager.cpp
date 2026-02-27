#include "core/SensorManager.h"
#include <Arduino.h>

/**
 * @file SensorManager.cpp
 * @brief Gestor abstracto de recolección de métricas.
 * 
 * ============================================================================
 * DECISIONES DE ARQUITECTURA Y DISEÑO
 * ============================================================================
 * ¿Por qué esta clase no incluye "#include <DHT.h>"?
 * 1. **Polimorfismo e Inversión de Dependencias (D de SOLID):**
 *    Esta clase gestiona un array de punteros genéricos `ISensor*`.
 *    A la hora de recolectar métricas es "ciega"; no le importa si está iterando
 *    sobre un DHT22 (1 cable), un BME280 (I2C) o un anemómetro analógico.
 *    Solo sabe que todo sensor obedece al contrato `->read()` y devuelve un
 *    Struct genérico `SensorReading`. 
 *    Esto hace que agregar nuevos sensores en el futuro no requiera modificar
 *    ni una sola línea del core lógico, solo crear la clase en `/hardware/sensors`.
 */

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

/**
 * @brief Orquesta el barrido completo de todos los sensores hardware incrustados.
 * 
 * Retorna un Vector (Lista dinámica) con todas las magnitudes válidas extraídas.
 * Si un sensor falla al leer (ej. cable suelto), simplemente no insertará  
 * el punto de datos en el vector y continuará sin bloquear el sistema.
 */
std::vector<Demeter::SensorReading> SensorManager::readAll() {
    std::vector<Demeter::SensorReading> readings;
    for (auto* sensor : _sensors) {
        Demeter::SensorReading data;
        // Invocación polimórfica (Late Binding) del sensor concreto.
        if (sensor->read(data) && data.isValid) {
            readings.push_back(data);
        }
    }
    return readings;
}

const std::vector<Demeter::ISensor*>& SensorManager::getSensors() const {
    return _sensors;
}
