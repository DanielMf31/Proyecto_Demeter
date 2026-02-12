/**
 * @file main_node_actuador_ventana.cpp
 * @brief Firmware for Actuator Node (Window Motor Control).
 * 
 * Implements Protocol V2 to control a relay based on SET_GPIO commands.
 * Uses new Modular Architecture (Node_Actuator).
 */

#include <Arduino.h>
#include <WiFi.h>
#include "communications/EspNowStrategy.h"
#include "core/ProtocolEngine.h"
#include "core/Node_Actuator.h"

// ==========================================
// Configuration
// ==========================================
#define NODE_ID 3                 // Unique ID for Actuator
#define GATEWAY_ID 1

// Pin Definitions
#define PIN_MOTOR_RELAY 2         // GPIO 2

// ==========================================
// Global Instances
// ==========================================
EspNowStrategy espNowStrategy;
ProtocolEngine engine(&espNowStrategy);
Node_Actuator node(NODE_ID, &engine);

// ==========================================
// Main
// ==========================================

void setup() {
    Serial.begin(115200);
    delay(1000);
    while(!Serial) delay(10);

    Serial.println("=== DEMETER ACTUATOR NODE V2 (Refactored) ===");
    Serial.printf("Node ID: %d\n", NODE_ID);
    
    // Comms Init
    espNowStrategy.begin();
    
    // Register Gateway
    // MAC: 9C:13:9E:A8:6F:CC (Gateway)
    std::array<uint8_t, 6> gatewayMac = {0x9C, 0x13, 0x9E, 0xA8, 0x6F, 0xCC};
    espNowStrategy.registerRoute(GATEWAY_ID, gatewayMac);

    // Configure Actuator Pins
    node.getExecutor()->setPins({PIN_MOTOR_RELAY});

    // Start Node (Inits SystemContext, Executor, Engine)
    node.begin();

    Serial.println("[Setup] Ready. Waiting for commands...");
}

void loop() {
    node.update();
}
