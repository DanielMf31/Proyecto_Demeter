#include <Arduino.h>
#include <WiFi.h>
#include "communications/EspNowStrategy.h"
#include "core/ProtocolEngine.h"
#include "core/Node_Sensor.h"
#include "hardware/sensors/DHTSensor.h"
#include "hardware/sensors/DS18B20Sensor.h"
#include "hardware/sensors/SoilMoistureSensor.h"

// If NODE_ID is not defined via build flags, default to 2
#ifndef NODE_ID
#define NODE_ID 2
#endif

#define USE_MOCK_SENSORS true

EspNowStrategy espNowStrategy;
ProtocolEngine engine(&espNowStrategy);
Node_Sensor demeterNode(NODE_ID, &engine);

// Sensors
Demeter::Sensors::DHTSensor dhtSensor(4, 22, USE_MOCK_SENSORS); 
Node_Sensor node(MY_NODE_ID, &engine);

void setup() {
    Serial.begin(115200);
    delay(1000);
    Serial.println("=== DEMETER SENSOR NODE V2 ===");
    Serial.printf("Node ID: %d\n", MY_NODE_ID);

    // 1. Init Communications
    espNowStrategy.begin();
    demeterNode.setReportingConfig(0, false); 
    
    Serial.println("[Setup] Ready.");
}

void loop() {
    // 1. Always Update (Listen)
    demeterNode.update();

    // 2. Active Mode: Send Report every 5s
    if (currentMode == MODE_ACTIVE_SENDING) {
        if (millis() - lastSendTime >= 5000) {
            lastSendTime = millis();
            Serial.println(">> [AUTO] Sending Sensor Report");
            
            // Mock Data for Reliability Testing
            // (Or read real sensors if connected)
            demeterNode.getSystemManager()->sendSensorData(1, 23.5, 60.2); 
        }
    }

    // 3. User Control
    if (Serial.available()) {
        char c = Serial.read();
        if (c == 'r') {
            Serial.println(">> [CMD] Resetting Node...");
            delay(100);
            ESP.restart();
        } else if (c == 'a') {
            currentMode = MODE_ACTIVE_SENDING;
            Serial.println(">> MODE: ACTIVE (Sending every 5s)");
        } else if (c == 'i') {
            currentMode = MODE_IDLE;
            Serial.println(">> MODE: IDLE (Listening)");
        } else if (c == 'h') {
            Serial.println(">> [CMD] Initiating Handshake with Gateway (ID 1)...");
            if (demeterNode.getSystemManager()) {
                demeterNode.getSystemManager()->initiateHandshake(1);
            }
        }
