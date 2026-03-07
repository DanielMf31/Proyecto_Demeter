/**
 * @file main_sensor_test.cpp
 * @brief Test standalone para lectura de DS18B20 (1-Wire) y Capacitivo v1.2 (ADC).
 *
 * Pines:
 *   - DS18B20          → GPIO 4  (requiere pull-up 4.7kΩ a 3.3V)
 *   - Capacitivo v1.2  → GPIO 34 (solo entrada, lectura analógica)
 *
 * Uso:
 *   pio run -t upload -e sensor_test && pio device monitor
 */

#include <Arduino.h>
#include "hardware/sensors/DS18B20Sensor.h"
#include "hardware/sensors/SoilMoistureSensor.h"

// ── Pines ────────────────────────────────────────────────────────────────
static constexpr uint8_t PIN_DS18B20 = 4;
static constexpr uint8_t PIN_SOIL    = 5;

// ── Calibración capacitivo (ajustar con tus valores reales) ─────────────
// airValue:   lectura ADC con el sensor al aire (seco)
// waterValue: lectura ADC con el sensor sumergido en agua
static constexpr int SOIL_AIR_VALUE   = 3000;
static constexpr int SOIL_WATER_VALUE = 1000;

// ── Intervalo de lectura ─────────────────────────────────────────────────
static constexpr unsigned long READ_INTERVAL_MS = 2000;

// ── Instancias ───────────────────────────────────────────────────────────
Demeter::Sensors::DS18B20Sensor ds18b20(PIN_DS18B20);
Demeter::Sensors::SoilMoistureSensor soilSensor(PIN_SOIL, SOIL_AIR_VALUE, SOIL_WATER_VALUE);

void setup() {
    Serial.begin(115200);
    while (!Serial) delay(10);
    delay(1000);

    Serial.println("\n========================================");
    Serial.println("  DEMETER - Sensor Test");
    Serial.println("  DS18B20 (GPIO 4) + Capacitivo (GPIO 5)");
    Serial.println("========================================\n");

    if (ds18b20.init()) {
        Serial.println("[OK] DS18B20 inicializado");
    } else {
        Serial.println("[ERROR] DS18B20 no responde. Revisa cableado y pull-up.");
    }

    if (soilSensor.init()) {
        Serial.println("[OK] Sensor capacitivo inicializado");
    } else {
        Serial.println("[ERROR] Sensor capacitivo fallo en init.");
    }

    Serial.println("\nIniciando lecturas cada 2s...\n");
}

void loop() {
    Demeter::SensorReading reading;

    // ── DS18B20 ──────────────────────────────────────────────────────────
    if (ds18b20.read(reading) && reading.isValid) {
        Serial.printf("[DS18B20]    Temp: %.2f C\n", reading.value1);
    } else {
        Serial.println("[DS18B20]    Lectura fallida (sensor desconectado?)");
    }

    // ── Capacitivo v1.2 ──────────────────────────────────────────────────
    if (soilSensor.read(reading) && reading.isValid) {
        Serial.printf("[Capacitivo] Humedad: %.0f%%  |  Raw ADC: %.0f\n",
                      reading.value1, reading.value2);
    } else {
        Serial.println("[Capacitivo] Lectura fallida");
    }

    Serial.println("----------------------------------------");
    delay(READ_INTERVAL_MS);
}
