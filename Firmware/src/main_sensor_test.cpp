/**
 * @file main_sensor_test.cpp
 * @brief Test firmware: GPIO-powered soil sensor + WiFi ADC debug.
 *
 * Powers the capacitive sensor from a GPIO pin, inits WiFi/ESP-NOW first,
 * waits 20s for ADC to settle, then reads continuously every 2s (no deep sleep).
 *
 * Wiring:
 *   Sensor VCC  → GPIO 15 (power pin)
 *   Sensor GND  → GND
 *   Sensor AOUT → GPIO 1 (ADC)
 *   DS18B20     → GPIO 5
 *
 * Usage:
 *   pio run -e sensor_test -t upload && pio device monitor
 */

#include <Arduino.h>
#include <WiFi.h>
#include "communications/EspNowStrategy.h"
#include "core/ProtocolEngine.h"
#include "core/InternalTypes.h"
#include "hardware/sensors/DS18B20Sensor.h"
#include "hardware/sensors/SoilMoistureSensor.h"

// ── Configuration ───────────────────────────────────────────────────────
const uint8_t MY_NODE_ID  = 2;
const uint8_t GATEWAY_ID  = 1;
const uint8_t GATEWAY_MAC[] = {0x9C, 0x13, 0x9E, 0xA8, 0x6F, 0xCC};

// GPIO-powered sensor
static constexpr uint8_t SENSOR_POWER_PIN = 15;
static constexpr uint8_t SOIL_ADC_PIN     = 1;
static constexpr uint8_t TEMP_PIN         = 5;

// Soil calibration
static constexpr int SOIL_AIR_VALUE   = 650;
static constexpr int SOIL_WATER_VALUE = 300;

// Report interval
static constexpr unsigned long REPORT_INTERVAL_MS = 2000;

// ── Instances ───────────────────────────────────────────────────────────
EspNowStrategy espNow;
ProtocolEngine engine(&espNow);
Demeter::Sensors::DS18B20Sensor* tempSensor;
Demeter::Sensors::SoilMoistureSensor* soilSensor;
bool sensorOk = false;
unsigned long lastReport = 0;

void setup() {
    Serial.begin(115200);
    delay(3000);

    Serial.println("\n========================================");
    Serial.println("  DEMETER - Sensor Test (GPIO-powered)");
    Serial.printf("  Power: GPIO%d | ADC: GPIO%d | Temp: GPIO%d\n",
        SENSOR_POWER_PIN, SOIL_ADC_PIN, TEMP_PIN);
    Serial.println("========================================\n");

    // ── 1. Power on the sensor via GPIO ──────────────────────────────────
    pinMode(SENSOR_POWER_PIN, OUTPUT);
    digitalWrite(SENSOR_POWER_PIN, HIGH);
    Serial.println("[POWER] Sensor powered ON via GPIO15");

    // ── 2. Init WiFi + ESP-NOW first ─────────────────────────────────────
    WiFi.mode(WIFI_STA);
    espNow.begin();
    engine.setNodeId(MY_NODE_ID);

    std::array<uint8_t, 6> gwMac;
    std::copy(std::begin(GATEWAY_MAC), std::end(GATEWAY_MAC), gwMac.begin());
    espNow.registerRoute(GATEWAY_ID, gwMac);
    Serial.println("[RADIO] WiFi + ESP-NOW initialized\n");

    // ── 3. Wait 20s for ADC to settle with WiFi active ──────────────────
    Serial.println("[DEBUG] Waiting 20s for ADC to settle (WiFi active)...");
    pinMode(SOIL_ADC_PIN, INPUT);
    for (int i = 0; i < 20; i++) {
        int raw = analogRead(SOIL_ADC_PIN);
        Serial.printf("  [%2ds] GPIO%d raw=%d\n", i + 1, SOIL_ADC_PIN, raw);
        delay(1000);
    }

    // ── 4. Init sensors ──────────────────────────────────────────────────
    tempSensor = new Demeter::Sensors::DS18B20Sensor(TEMP_PIN);
    soilSensor = new Demeter::Sensors::SoilMoistureSensor(
        SOIL_ADC_PIN, SOIL_AIR_VALUE, SOIL_WATER_VALUE);

    bool tempOk = tempSensor->init();
    bool soilOk = soilSensor->init();
    sensorOk = tempOk && soilOk;

    Serial.printf("\n[INIT] Temp(GPIO%d): %s | Soil(GPIO%d): %s\n\n",
        TEMP_PIN, tempOk ? "OK" : "FAIL",
        SOIL_ADC_PIN, soilOk ? "OK" : "FAIL");

    Serial.println(">> Starting continuous readings every 2s...\n");
}

void loop() {
    engine.update();

    if (millis() - lastReport < REPORT_INTERVAL_MS) return;
    lastReport = millis();

    if (!sensorOk) {
        Serial.println("[SKIP] Sensors not initialized");
        return;
    }

    Demeter::SensorReading tempReading, soilReading;
    bool tempOk = tempSensor->read(tempReading) && tempReading.isValid;
    bool soilOk = soilSensor->read(soilReading) && soilReading.isValid;

    Serial.printf("[READ] Temp: %.2f C | Soil: %.0f%% | Raw ADC: %.0f\n",
        tempOk ? tempReading.value1 : -999.0f,
        soilOk ? soilReading.value1 : -1.0f,
        soilOk ? soilReading.value2 : -1.0f);

    // Build and send report
    Demeter::SensorClusterReport report;
    report.sourceId = MY_NODE_ID;

    Demeter::SensorClusterEntry entry;
    entry.plantId = 1;
    entry.temperature = tempOk ? tempReading.value1 : -999.0f;
    entry.soilMoisture = soilOk ? soilReading.value1 : -1.0f;
    report.entries.push_back(entry);

    engine.sendSensorClusterReport(GATEWAY_ID, report);
    Serial.println(">> Sent to Gateway");
}
