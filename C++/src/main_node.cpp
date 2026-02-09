/**
 * @file main_node.cpp
 * @brief Firmware Entry Point for "Node" (ESP32).
 * 
 * Implements the Demeter Protocol V2 Node logic.
 * Communicates via ESP-Now.
 */

#include <Arduino.h>
#include <WiFi.h>  // Required for macAddress()
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
    
    // Feedback: Blink RGB Green on PING
    engine.onPingRecv([](uint8_t srcId) {
        #ifdef RGB_BUILTIN
        // Green Blink
        neopixelWrite(RGB_BUILTIN, 0, 50, 0); 
        delay(100);
        neopixelWrite(RGB_BUILTIN, 0, 0, 0);
        #endif
        Serial.printf(">> PING from %d\n", srcId);
    });

    // Handle GET_SENSORS Request (On Demand)
    engine.onGetSensorsRecv([](uint8_t srcId) {
        Serial.printf(">> GET_SENSORS from %d. Sending Data Report...\n", srcId);
        
        // Mock Data Generation
        float mockTemp = 20.0f + (rand() % 100) / 10.0f;
        float mockHum = 40.0f + (rand() % 200) / 10.0f;

        // Send Response to Requestor
        engine.sendDataReport(srcId, mockTemp, mockHum);
        
        #ifdef RGB_BUILTIN
        // Blue Blink for Data
        neopixelWrite(RGB_BUILTIN, 0, 0, 50); 
        delay(100);
        neopixelWrite(RGB_BUILTIN, 0, 0, 0);
        #endif
    });

    // Initialize System Logic
    systemCtx.setup();
    
    // Initialize Communication
    espNowStrategy.begin();
    
    // HARDCODED GATEWAY MAC (From devices.json: 9C:13:9E:A8:6F:CC)
    std::array<uint8_t, 6> gatewayMac = {0x9C, 0x13, 0x9E, 0xA8, 0x6F, 0xCC};
    espNowStrategy.registerRoute(1, gatewayMac); // ID 1 = Gateway
    
    // TURN OFF RGB LED (ESP32-S3 DevKitC-1)
    #ifdef RGB_BUILTIN
    neopixelWrite(RGB_BUILTIN, 0, 0, 0);
    #endif
}

/**
 * @brief Standard Arduino Loop.
 */
void loop() {
    // 1. System Loop (Protocol Engine Update)
    systemCtx.loop();
    
    // 2. Serial Command Check (For MAC)
    if (Serial.available()) {
        char c = Serial.read();
        if (c == 'm' || c == 'M') {
            Serial.print("MAC Address: ");
            Serial.println(WiFi.macAddress());
        }
        else if (c == 'p' || c == 'P') {
            Serial.println(">> TX -> PING Gateway (Manual)");
            engine.sendPing(1); // Gateway ID = 1
        }
    }

    // Periodic Data Sending Disabled (On-Demand Mode)
}
