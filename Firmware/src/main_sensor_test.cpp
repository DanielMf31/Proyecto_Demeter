/**
 * @file main_sensor_test.cpp
 * @brief Test firmware: 2 plants, GPIO-powered soil sensors, WiFi + ESP-NOW.
 *
 * No deep sleep — continuous 5s readings for debugging.
 *
 * Wiring:
 *   Plant 1: DS18B20 → GPIO 4, Capacitive AOUT → GPIO 5
 *   Plant 2: DS18B20 → GPIO 6, Capacitive AOUT → GPIO 7
 *   Sensor VCC → GPIO 15 (power pin, shared)
 *   Sensor GND → GND
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

// GPIO power pin for soil sensors
static constexpr uint8_t SENSOR_POWER_PIN = 15;

// Soil calibration
static constexpr int SOIL_AIR_VALUE   = 2200;
static constexpr int SOIL_WATER_VALUE = 800;

// Report interval
static constexpr unsigned long REPORT_INTERVAL_MS = 5000;

// ── Plant definitions ──────────────────────────────────────────────────
struct PlantConfig {
    uint16_t plantId;
    uint8_t  tempPin;   // DS18B20
    uint8_t  soilPin;   // Capacitive ADC
};

static constexpr PlantConfig PLANTS[] = {
    {1, 4, 5},   // Plant 1: DS18B20 on GPIO4, Capacitive on GPIO5
    {2, 6, 7},   // Plant 2: DS18B20 on GPIO6, Capacitive on GPIO7
};
static constexpr size_t MAX_PLANTS = sizeof(PLANTS) / sizeof(PLANTS[0]);

// ── Instances ───────────────────────────────────────────────────────────
EspNowStrategy espNow;
ProtocolEngine engine(&espNow);
Demeter::Sensors::DS18B20Sensor* tempSensors[MAX_PLANTS];
Demeter::Sensors::SoilMoistureSensor* soilSensors[MAX_PLANTS];
bool plantActive[MAX_PLANTS];
unsigned long lastReport = 0;
uint8_t activePlants = 0;

void setup() {
    Serial.begin(115200);
    delay(3000);

    Serial.println("\n========================================");
    Serial.println("  DEMETER - Sensor Test (no deep sleep)");
    Serial.printf("  Power pin: GPIO%d | Plants: %d\n", SENSOR_POWER_PIN, MAX_PLANTS);
    Serial.println("========================================\n");

    // ── 1. Power on sensors via GPIO ─────────────────────────────────────
    pinMode(SENSOR_POWER_PIN, OUTPUT);
    digitalWrite(SENSOR_POWER_PIN, HIGH);
    Serial.println("[POWER] Sensors powered ON via GPIO15");

    // ── 2. Init WiFi + ESP-NOW ───────────────────────────────────────────
    WiFi.mode(WIFI_STA);
    espNow.begin();
    engine.setNodeId(MY_NODE_ID);

    std::array<uint8_t, 6> gwMac;
    std::copy(std::begin(GATEWAY_MAC), std::end(GATEWAY_MAC), gwMac.begin());
    espNow.registerRoute(GATEWAY_ID, gwMac);
    Serial.println("[RADIO] WiFi + ESP-NOW initialized\n");

    // ── 3. Wait 20s logging raw ADC each second ─────────────────────────
    Serial.println("[DEBUG] Waiting 20s for ADC to settle (WiFi active)...");
    for (size_t i = 0; i < MAX_PLANTS; i++) {
        pinMode(PLANTS[i].soilPin, INPUT);
    }
    for (int s = 0; s < 20; s++) {
        Serial.printf("  [%2ds] ", s + 1);
        for (size_t i = 0; i < MAX_PLANTS; i++) {
            int raw = analogRead(PLANTS[i].soilPin);
            Serial.printf("GPIO%d=%d  ", PLANTS[i].soilPin, raw);
        }
        Serial.println();
        delay(1000);
    }

    // ── 4. Init sensors ──────────────────────────────────────────────────
    Serial.println();
    for (size_t i = 0; i < MAX_PLANTS; i++) {
        tempSensors[i] = new Demeter::Sensors::DS18B20Sensor(PLANTS[i].tempPin);
        soilSensors[i] = new Demeter::Sensors::SoilMoistureSensor(
            PLANTS[i].soilPin, SOIL_AIR_VALUE, SOIL_WATER_VALUE);

        bool tempOk = tempSensors[i]->init();
        bool soilOk = soilSensors[i]->init();
        plantActive[i] = tempOk && soilOk;

        Serial.printf("  Plant %d (T:GPIO%d S:GPIO%d): %s\n",
            PLANTS[i].plantId, PLANTS[i].tempPin, PLANTS[i].soilPin,
            plantActive[i] ? "OK" : "SKIP (sensor missing)");

        if (plantActive[i]) activePlants++;
    }

    Serial.printf("\n%d/%d plants active. Reading every 5s...\n\n", activePlants, MAX_PLANTS);
}

void loop() {
    engine.update();

    if (millis() - lastReport < REPORT_INTERVAL_MS) return;
    lastReport = millis();

    Demeter::SensorClusterReport report;
    report.sourceId = MY_NODE_ID;

    for (size_t i = 0; i < MAX_PLANTS; i++) {
        if (!plantActive[i]) continue;

        Demeter::SensorReading tempReading, soilReading;
        bool tempOk = tempSensors[i]->read(tempReading) && tempReading.isValid;
        bool soilOk = soilSensors[i]->read(soilReading) && soilReading.isValid;

        Demeter::SensorClusterEntry entry;
        entry.plantId = PLANTS[i].plantId;
        entry.temperature = tempOk ? tempReading.value1 : -999.0f;
        entry.soilMoisture = soilOk ? soilReading.value1 : -1.0f;

        report.entries.push_back(entry);

        Serial.printf("[Plant %d] Temp: %.2f C | Soil: %.0f%% | Raw ADC: %.0f\n",
            PLANTS[i].plantId, entry.temperature, entry.soilMoisture,
            soilOk ? soilReading.value2 : -1.0f);
    }

    if (!report.entries.empty()) {
        engine.sendSensorClusterReport(GATEWAY_ID, report);
        Serial.printf(">> Sent %d entries to Gateway\n\n", (int)report.entries.size());
    }
}
