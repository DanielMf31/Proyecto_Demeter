/**
 * @file main_node_sensor.cpp
 * @brief Firmware de Entrada Principal (Entry Point) para un Nodo tipo Sensor.
 * 
 * Muestra el instanciamiento de un "Node_Sensor" con ESP-NOW y un gestor de sensores.
 * Habilita el envío automático de reportes (Reporting Config) o por demanda (Comandos).
 */
#include <Arduino.h>
#include <WiFi.h>
#include "communications/EspNowStrategy.h"
#include "core/ProtocolEngine.h"
#include "core/Node_Sensor.h"
#include "hardware/sensors/DHTSensor.h"
#include "hardware/sensors/DS18B20Sensor.h"
#include "hardware/sensors/SoilMoistureSensor.h"

// Si NODE_ID no está compilado bajo build_flags, forzamos 2.
#ifndef NODE_ID
#define NODE_ID 2
#endif

#define USE_MOCK_SENSORS true

EspNowStrategy espNowStrategy;
ProtocolEngine engine(&espNowStrategy);
Node_Sensor demeterNode(NODE_ID, &engine);

Demeter::Sensors::DHTSensor dhtSensor(4, 22, USE_MOCK_SENSORS);

void setup() {
    Serial.begin(115200);
    delay(1000);
    Serial.println("=== DEMETER SENSOR NODE V2 ===");
    Serial.printf("Node ID: %d\n", NODE_ID);

    // 1. Init Communications
    espNowStrategy.begin();

    // REGISTER GATEWAY MAC (Required for initiating communication)
    // MAC from Gateway Log: 9C:13:9E:A8:6F:CC
    std::array<uint8_t, 6> gatewayMac = {0x9C, 0x13, 0x9E, 0xA8, 0x6F, 0xCC}; 
    espNowStrategy.registerRoute(1, gatewayMac); // Node 1 is Gateway
    espNowStrategy.registerRoute(0, gatewayMac); // Node 0 is Server (via Gateway)
    
    // 2. Register Sensors
    if (demeterNode.getSensorManager()) {
        demeterNode.getSensorManager()->addSensor(&dhtSensor);
    }

    // 3. Configure Node (Default: Active Reporting every 5s)
    demeterNode.setReportingConfig(5000, false); 
    
    // 4. Start Node
    demeterNode.begin();
    
    Serial.println("[Setup] Ready. Waiting for Handshake or 'a' command.");
}

void loop() {
    // 1. Always Update (Listen & Internal State Machine)
    demeterNode.update();

    // 2. User Control
    if (Serial.available()) {
        char c = Serial.read();
        if (c == 'r') {
            Serial.println(">> [CMD] Resetting Node...");
            delay(100);
            ESP.restart();
        } else if (c == 'a') {
            // Activate Reporting every 5 seconds
            demeterNode.setReportingConfig(5000, false);
            Serial.println(">> [CMD] MODE: ACTIVE (Sending every 5s)");
            
            // Should also ensure SystemState allows sending? 
            // If in IDLE state, Node_Sensor logic might need Handshake first.
            // But let's assume we want to force start or just set config.
            // If we are IDLE, Node_Sensor checks state. 
            // If we want to force "Running", we might need to trick SystemManager or just rely on Handshake.
            // For testing, let's initiate handshake too just in case.
             if (demeterNode.getSystemManager()) {
                demeterNode.getSystemManager()->initiateHandshake(1);
            }
        } else if (c == 'i') {
            // Idle
            demeterNode.setReportingConfig(0, false);
            Serial.println(">> [CMD] MODE: IDLE (Listening)");
        } else if (c == 'h') {
            Serial.println(">> [CMD] Initiating Handshake with Gateway (ID 1)...");
            if (demeterNode.getSystemManager()) {
                demeterNode.getSystemManager()->initiateHandshake(1);
            }
        }
    }
}
