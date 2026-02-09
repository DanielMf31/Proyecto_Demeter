/**
 * @file main_node.cpp
 * @brief Firmware Entry Point for "Node" (ESP32).
 * 
 * Implements the Demeter Protocol V2 Node logic.
 * Communicates via ESP-Now.
 */

#include <Arduino.h>
#include "communications/EspNowStrategy.h"
#include "core/ProtocolEngine.h"
#include "core/GpioController.h"
#include "core/SystemContext.h"

// ID of this Node (Ideally read from NVS or Switches)
#define NODE_ID 2

// ==========================================
// Global Instances
// ==========================================

// 1. Communication Layer: ESP-Now Only
EspNowStrategy espNowStrategy;

// 2. Protocol Layer: Protocol V2 Engine
ProtocolEngine engine(&espNowStrategy);

// 3. Hardware Layer: GPIO Controller
GpioController gpioController;

// 4. System Layer: Context Orchestrator
SystemContext systemCtx(engine, gpioController);

/**
 * @brief Standard Arduino Setup.
 */
void setup() {
    // Debug Serial (USB)
    Serial.begin(115200);
    delay(1000);
    while(!Serial) delay(10);

    Serial.println("=== DEMETER NODE V2 (ESP-Now) ===");
    Serial.printf("Node ID: %d\n", NODE_ID);
    Serial.println("Waiting for Gateway PING/Route...");

    // Configure Protocol Engine
    engine.setNodeId(NODE_ID);

    // Initialize System Logic
    systemCtx.setup();
    
    // Initialize Communication
    espNowStrategy.begin();
}

/**
 * @brief Standard Arduino Loop.
 */
void loop() {
    // 1. System Loop (Protocol Engine Update)
    systemCtx.loop();
    
    // Optional: Sleep or low power mode could go here
}
