/**
 * @file main_node.cpp
 * @brief Firmware Entry Point for "Node" (ESP32) - Modular Sensor Prototype.
 * 
 * Implements the Demeter Protocol V2 Node logic using the new Node architecture.
 * Communicates via ESP-Now.
 */

#include <Arduino.h>
#include <WiFi.h>
#include "communications/EspNowStrategy.h"
#include "core/ProtocolEngine.h"
#include "core/Node_Sensor.h"

// Sensors
#include "hardware/sensors/DHTSensor.h"
#include "hardware/sensors/DS18B20Sensor.h"
#include "hardware/sensors/SoilMoistureSensor.h"

// ID of this Node
#define NODE_ID 2

// Configuration Flags
#define USE_MOCK_SENSORS true

// ==========================================
// Global Instances
// ==========================================

// 1. Communication Layer: ESP-Now Only
EspNowStrategy espNowStrategy;

// 2. Protocol Layer: Protocol V2 Engine
ProtocolEngine engine(&espNowStrategy);

// 3. New Modular Node Manager
Node_Sensor demeterNode(NODE_ID, &engine);

// 4. Sensors
// DHT22 on Pin 4
Demeter::Sensors::DHTSensor dhtSensor(4, 22, USE_MOCK_SENSORS); 

// DS18B20 on Pin 5
Demeter::Sensors::DS18B20Sensor tempSensor(5, USE_MOCK_SENSORS);

// Soil Moisture on Pin 34 (Analog)
Demeter::Sensors::SoilMoistureSensor soilSensor(34, 3000, 1000, USE_MOCK_SENSORS);

/**
 * @brief Standard Arduino Setup.
 */
void setup() {
    // Debug Serial (USB)
    Serial.begin(115200);
    delay(1000);
    while(!Serial) delay(10);

    Serial.println("=== DEMETER NODE V2 (Refactored Sensor) ===");
    Serial.printf("Node ID: %d\n", NODE_ID);
    Serial.printf("Mode: %s\n", USE_MOCK_SENSORS ? "MOCK" : "REAL");

    // Initialize Communication
    espNowStrategy.begin();
    
    // Register Gateway Route (Hardcoded for Prototype)
    // MAC: 9C:13:9E:A8:6F:CC
    std::array<uint8_t, 6> gatewayMac = {0x9C, 0x13, 0x9E, 0xA8, 0x6F, 0xCC};
    espNowStrategy.registerRoute(1, gatewayMac); // ID 1 = Gateway
    
    // Configure Node
    Serial.println("[Setup] Registering Sensors...");
    if (demeterNode.getSensorManager()) {
        demeterNode.getSensorManager()->addSensor(&dhtSensor);
        demeterNode.getSensorManager()->addSensor(&tempSensor);
        demeterNode.getSensorManager()->addSensor(&soilSensor);
    }

    // Configure Reporting (e.g., every 5 seconds, No Deep Sleep for now)
    demeterNode.setReportingConfig(5000, false);

    // Start Node (Initializes Engine and Sensors)
    demeterNode.begin();
    
    Serial.println("[Setup] Ready.");
}

/**
 * @brief Standard Arduino Loop.
 */
void loop() {
    // New Modular Loop
    demeterNode.update();
    
    // Legacy functionality (Serial Commands for debugging)
    if (Serial.available()) {
        char c = Serial.read();
        if (c == 'p') {
            Serial.println(">> PING Gateway");
            engine.sendPing(1);
        }
    }
}
