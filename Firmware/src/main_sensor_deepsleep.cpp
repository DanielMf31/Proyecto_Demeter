/**
 * @file main_sensor_deepsleep.cpp
 * @brief Deep-sleep sensor cluster: powers sensors via GPIO, waits 20s for
 *        ADC to settle, reads + sends, then sleeps 2s.
 *
 * Wiring:
 *   Plant 1: DS18B20 → GPIO 4, Capacitive AOUT → GPIO 5
 *   Plant 2: DS18B20 → GPIO 6, Capacitive AOUT → GPIO 7
 *   Sensor VCC → GPIO 15 (power pin, shared)
 *   Sensor GND → GND
 *
 * Usage:
 *   pio run -e sensor_deepsleep -t upload && pio device monitor
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
const uint8_t MY_NODE_ID  = 2;
const uint8_t GATEWAY_ID  = 1;
const uint8_t GATEWAY_MAC[] = {0x9C, 0x13, 0x9E, 0xA8, 0x6F, 0xCC};

// GPIO power pin for soil sensors
static constexpr uint8_t SENSOR_POWER_PIN = 15;

// Deep-sleep duration
static constexpr uint64_t SLEEP_DURATION_S  = 2;
static constexpr uint64_t SLEEP_DURATION_US = SLEEP_DURATION_S * 1000000ULL;

// Soil calibration
static constexpr int SOIL_AIR_VALUE   = 2200;
static constexpr int SOIL_WATER_VALUE = 800;

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

// ── Helper ──────────────────────────────────────────────────────────────
static const char* wakeupReason() {
    switch (esp_sleep_get_wakeup_cause()) {
        case ESP_SLEEP_WAKEUP_TIMER: return "TIMER";
        default:                     return "POWER_ON / RESET";
    }
}

void setup() {
    Serial.begin(115200);
    delay(3000);

    Serial.println("\n========================================");
    Serial.println("  DEMETER - Sensor Deep Sleep Test");
    Serial.printf("  Power: GPIO%d | Sleep: %llus\n", SENSOR_POWER_PIN, SLEEP_DURATION_S);
    Serial.printf("  WAKE UP reason: %s\n", wakeupReason());
    Serial.println("========================================\n");

    // ── 1. Power on sensors via GPIO ─────────────────────────────────────
    pinMode(SENSOR_POWER_PIN, OUTPUT);
    digitalWrite(SENSOR_POWER_PIN, HIGH);
    Serial.println("[POWER] Sensors powered ON via GPIO15");

    // ── 2. Init WiFi + ESP-NOW ───────────────────────────────────────────
    WiFi.mode(WIFI_STA);
    EspNowStrategy espNow;
    ProtocolEngine engine(&espNow);
    espNow.begin();
    engine.setNodeId(MY_NODE_ID);

    std::array<uint8_t, 6> gwMac;
    std::copy(std::begin(GATEWAY_MAC), std::end(GATEWAY_MAC), gwMac.begin());
    espNow.registerRoute(GATEWAY_ID, gwMac);
    Serial.println("[RADIO] WiFi + ESP-NOW initialized\n");

    // ── 3. Wait 20s for ADC to settle, logging raw each second ───────────
    Serial.println("[DEBUG] Waiting 20s for ADC to settle...");
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

    // ── 4. Init sensors + read ───────────────────────────────────────────
    Demeter::SensorClusterReport report;
    report.sourceId = MY_NODE_ID;
    uint8_t activePlants = 0;

    Serial.println();
    for (size_t i = 0; i < MAX_PLANTS; i++) {
        auto* temp = new Demeter::Sensors::DS18B20Sensor(PLANTS[i].tempPin);
        auto* soil = new Demeter::Sensors::SoilMoistureSensor(
            PLANTS[i].soilPin, SOIL_AIR_VALUE, SOIL_WATER_VALUE);

        bool tempOk = temp->init();
        bool soilOk = soil->init();

        if (tempOk && soilOk) {
            activePlants++;

            Demeter::SensorReading tempReading, soilReading;
            bool tOk = temp->read(tempReading) && tempReading.isValid;
            bool sOk = soil->read(soilReading) && soilReading.isValid;

            Demeter::SensorClusterEntry entry;
            entry.plantId = PLANTS[i].plantId;
            entry.temperature = tOk ? tempReading.value1 : -999.0f;
            entry.soilMoisture = sOk ? soilReading.value1 : -1.0f;
            report.entries.push_back(entry);

            Serial.printf("[Plant %d] Temp: %.2f C | Soil: %.0f%% | Raw ADC: %.0f\n",
                PLANTS[i].plantId, entry.temperature, entry.soilMoisture,
                sOk ? soilReading.value2 : -1.0f);
        } else {
            Serial.printf("[Plant %d] SKIP (T:%s S:%s)\n",
                PLANTS[i].plantId, tempOk ? "OK" : "FAIL", soilOk ? "OK" : "FAIL");
        }

        delete temp;
        delete soil;
    }

    // ── 5. Send report ───────────────────────────────────────────────────
    if (!report.entries.empty()) {
        engine.sendSensorClusterReport(GATEWAY_ID, report);
        Serial.printf("\n>> Sent %d entries to Gateway\n", (int)report.entries.size());
    } else {
        Serial.println("\n>> No active sensors, skipping report.");
    }

    // ── 6. Power off sensors + deep sleep ────────────────────────────────
    digitalWrite(SENSOR_POWER_PIN, LOW);
    delay(500); // let ESP-NOW finish
    Serial.printf(">> Entering deep sleep for %llus...\n\n", SLEEP_DURATION_S);
    Serial.flush();
    esp_deep_sleep(SLEEP_DURATION_US);
}

void loop() {
    delay(1000);
}
