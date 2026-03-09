/**
 * @file main_sensor_cluster.cpp
 * @brief Deep-sleep sensor cluster: wakes every 60 s, reads DS18B20 +
 *        capacitive sensors, sends SENSOR_CLUSTER_REPORT via ESP-NOW
 *        to the gateway (Node 1), then returns to deep sleep.
 *
 * Pin assignment (alternating soil/temp per plant):
 *   Plant 1: Capacitive → GPIO 4, DS18B20 → GPIO 5
 *   Plant 2: Capacitive → GPIO 6, DS18B20 → GPIO 7
 *
 * The number of active plants is auto-detected: if a DS18B20 fails init,
 * that plant pair is skipped. This allows testing with 1-2 sensors.
 *
 * Deep-sleep behaviour:
 *   - On wake (or first boot) setup() runs the full cycle: init → read → send → sleep.
 *   - loop() is a fallback that triggers sleep in case setup() didn't reach it.
 *
 * Usage:
 *   pio run -e sensor_cluster -t upload && pio device monitor
 */

#include <Arduino.h>
#include <WiFi.h>
#include <esp_sleep.h>
#include "communications/EspNowStrategy.h"
#include "core/ProtocolEngine.h"
#include "core/InternalTypes.h"
#include "hardware/sensors/DS18B20Sensor.h"
#include "hardware/sensors/SoilMoistureSensor.h"

// ── Configuration ───────────────────────────────────────────────────────
const uint8_t MY_NODE_ID = 2;
const uint8_t GATEWAY_ID = 1;

// Gateway MAC (from `pio device list`: SER=9C:13:9E:A8:6F:CC on /dev/ttyACM0)
const uint8_t GATEWAY_MAC[] = {0x9C, 0x13, 0x9E, 0xA8, 0x6F, 0xCC};

// Deep-sleep duration in seconds
static constexpr uint64_t SLEEP_DURATION_S = 60;
static constexpr uint64_t SLEEP_DURATION_US = SLEEP_DURATION_S * 1000000ULL;

// ── Soil calibration (adjust for your sensors) ─────────────────────────
static constexpr int SOIL_AIR_VALUE   = 650;
static constexpr int SOIL_WATER_VALUE = 300;

// ── Plant definitions ──────────────────────────────────────────────────
struct PlantConfig {
    uint16_t plantId;
    uint8_t  tempPin;
    uint8_t  soilPin;
};

static constexpr PlantConfig PLANTS[] = {
    {1, 5, 4},   // Plant 1: DS18B20 on GPIO5, Capacitive on GPIO4
    {2, 7, 6},   // Plant 2: DS18B20 on GPIO7, Capacitive on GPIO6
};
static constexpr size_t MAX_PLANTS = sizeof(PLANTS) / sizeof(PLANTS[0]);

// ── Helper: wakeup reason string ────────────────────────────────────────
static const char* wakeupReason() {
    switch (esp_sleep_get_wakeup_cause()) {
        case ESP_SLEEP_WAKEUP_TIMER: return "TIMER";
        case ESP_SLEEP_WAKEUP_EXT0:  return "EXT0";
        case ESP_SLEEP_WAKEUP_EXT1:  return "EXT1";
        default:                     return "POWER_ON / RESET";
    }
}

void setup() {
    Serial.begin(115200);
    delay(2000); // wait for USB CDC

    Serial.println("\n========================================");
    Serial.println("  DEMETER - Sensor Cluster Node");
    Serial.printf("  Node ID: %d | Plants: %d\n", MY_NODE_ID, MAX_PLANTS);
    Serial.printf("  WAKE UP reason: %s\n", wakeupReason());
    Serial.println("========================================\n");

    // ── Init ESP-NOW ────────────────────────────────────────────────────
    WiFi.mode(WIFI_STA);
    EspNowStrategy espNow;
    ProtocolEngine engine(&espNow);
    espNow.begin();
    engine.setNodeId(MY_NODE_ID);

    std::array<uint8_t, 6> gwMac;
    std::copy(std::begin(GATEWAY_MAC), std::end(GATEWAY_MAC), gwMac.begin());
    espNow.registerRoute(GATEWAY_ID, gwMac);

    // ── Init sensors per plant ──────────────────────────────────────────
    Demeter::Sensors::DS18B20Sensor* tempSensors[MAX_PLANTS];
    Demeter::Sensors::SoilMoistureSensor* soilSensors[MAX_PLANTS];
    bool plantActive[MAX_PLANTS];

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

    Serial.printf("\n%d/%d plants active.\n\n", activePlants, MAX_PLANTS);

    // ── Read sensors + build report ─────────────────────────────────────
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

    // ── Send report ─────────────────────────────────────────────────────
    if (!report.entries.empty()) {
        engine.sendSensorClusterReport(GATEWAY_ID, report);
        Serial.printf(">> Sent SENSOR_CLUSTER_REPORT (%d entries) to Gateway\n",
            (int)report.entries.size());
    } else {
        Serial.println(">> No active sensors, skipping report.");
    }

    // ── Cleanup heap-allocated sensors ──────────────────────────────────
    for (size_t i = 0; i < MAX_PLANTS; i++) {
        delete tempSensors[i];
        delete soilSensors[i];
    }

    // ── Enter deep sleep ────────────────────────────────────────────────
    delay(500); // let ESP-NOW finish transmitting
    Serial.println(">> 5s window before deep sleep (flash new code now if needed)...");
    delay(5000);
    Serial.printf(">> Entering deep sleep for %llu s...\n\n", SLEEP_DURATION_S);
    Serial.flush();
    esp_deep_sleep(SLEEP_DURATION_US);
}

void loop() {
    // Fallback: should never reach here; deep sleep resets into setup().
    delay(1000);
}
