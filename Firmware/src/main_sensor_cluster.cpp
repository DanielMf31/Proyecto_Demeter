/**
 * @file main_sensor_cluster.cpp
 * @brief Test firmware: reads DS18B20 + capacitive sensors, packs into
 *        SENSOR_CLUSTER_REPORT and sends via ESP-NOW to gateway (Node 1).
 *
 * Pin assignment (alternating temp/soil per plant):
 *   Plant 1: DS18B20 → GPIO 4, Capacitive → GPIO 5
 *   Plant 2: DS18B20 → GPIO 6, Capacitive → GPIO 7
 *
 * The number of active plants is auto-detected: if a DS18B20 fails init,
 * that plant pair is skipped. This allows testing with 1-2 sensors.
 *
 * Usage:
 *   pio run -e sensor_cluster -t upload && pio device monitor
 */

#include <Arduino.h>
#include <WiFi.h>
#include "communications/EspNowStrategy.h"
#include "core/ProtocolEngine.h"
#include "core/InternalTypes.h"
#include "hardware/sensors/DS18B20Sensor.h"
#include "hardware/sensors/SoilMoistureSensor.h"

// ── Configuration ───────────────────────────────────────────────────────
const uint8_t MY_NODE_ID = 2;
const uint8_t GATEWAY_ID = 1;

// Gateway MAC — REPLACE WITH YOUR GATEWAY'S REAL MAC
const uint8_t GATEWAY_MAC[] = {0x20, 0x6E, 0xF1, 0x85, 0x58, 0xD0};

// Report interval
static constexpr unsigned long REPORT_INTERVAL_MS = 5000;

// ── Soil calibration (adjust for your sensors) ─────────────────────────
static constexpr int SOIL_AIR_VALUE   = 3000;
static constexpr int SOIL_WATER_VALUE = 1000;

// ── Plant definitions ──────────────────────────────────────────────────
struct PlantConfig {
    uint16_t plantId;
    uint8_t  tempPin;
    uint8_t  soilPin;
};

static constexpr PlantConfig PLANTS[] = {
    {1, 4, 5},   // Plant 1: DS18B20 on GPIO4, Capacitive on GPIO5
    {2, 6, 7},   // Plant 2: DS18B20 on GPIO6, Capacitive on GPIO7
};
static constexpr size_t MAX_PLANTS = sizeof(PLANTS) / sizeof(PLANTS[0]);

// ── Sensor instances ──────────────────────────────────────────────────
Demeter::Sensors::DS18B20Sensor* tempSensors[MAX_PLANTS];
Demeter::Sensors::SoilMoistureSensor* soilSensors[MAX_PLANTS];
bool plantActive[MAX_PLANTS];

// ── Communication ─────────────────────────────────────────────────────
EspNowStrategy espNow;
ProtocolEngine engine(&espNow);

unsigned long lastReport = 0;

void setup() {
    Serial.begin(115200);
    delay(2000);

    Serial.println("\n========================================");
    Serial.println("  DEMETER - Sensor Cluster Node");
    Serial.printf("  Node ID: %d | Plants: %d\n", MY_NODE_ID, MAX_PLANTS);
    Serial.println("========================================\n");

    // Init ESP-NOW
    WiFi.mode(WIFI_STA);
    espNow.begin();
    engine.setNodeId(MY_NODE_ID);

    // Register gateway route
    std::array<uint8_t, 6> gwMac;
    std::copy(std::begin(GATEWAY_MAC), std::end(GATEWAY_MAC), gwMac.begin());
    espNow.registerRoute(GATEWAY_ID, gwMac);

    // Init sensors per plant
    uint8_t activePlants = 0;
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

    Serial.printf("\n%d/%d plants active. Reporting every %lus.\n\n",
        activePlants, MAX_PLANTS, REPORT_INTERVAL_MS / 1000);
}

void loop() {
    engine.update();

    if (millis() - lastReport < REPORT_INTERVAL_MS) return;
    lastReport = millis();

    // Build cluster report with only active plants
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

        Serial.printf("[Plant %d] Temp: %.2f C | Soil: %.0f%%\n",
            PLANTS[i].plantId, entry.temperature, entry.soilMoisture);
    }

    if (!report.entries.empty()) {
        engine.sendSensorClusterReport(GATEWAY_ID, report);
        Serial.printf(">> Sent SENSOR_CLUSTER_REPORT (%d entries) to Gateway\n\n",
            (int)report.entries.size());
    } else {
        Serial.println(">> No active sensors, skipping report.\n");
    }
}
