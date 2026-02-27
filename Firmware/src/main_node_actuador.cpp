/**
 * @file main_node_actuador.cpp
 * @brief Firmware de Entrada Principal (Entry Point) para un Nodo tipo Actuador.
 * 
 * Funcionalidades:
 * - Comunicación reactiva asíncrona mediante ESP-NOW con la red mesh (hacia el Gateway).
 * - Control de Relay de Motor local acoplado al GpioController.
 */

#include <Arduino.h>
#include "core/ProtocolEngine.h"
#include "communications/EspNowStrategy.h"
#include "core/GpioController.h"
#include "core/Node_Actuator.h"

// =============================================================================
// CONFIGURATION
// =============================================================================
// IF NODE_ID is not defined in platformio.ini, default to 3
#ifndef NODE_ID
#define NODE_ID 3
#endif

const uint8_t GATEWAY_ID = 1;

// MAC Address of Gateway (Must match the one in main_gateway.cpp)
// MAC from Gateway Log: 9C:13:9E:A8:6F:CC
const uint8_t GATEWAY_MAC[] = {0x9C, 0x13, 0x9E, 0xA8, 0x6F, 0xCC}; 

// Hardware Pins
const uint8_t PIN_MOTOR_RELAY = 4;

// Modes for local control (simplification)
enum ActuatorMode {
    MODE_IDLE = 0,
    MODE_ACTIVE = 1
};
int currentMode = MODE_IDLE; 

// =============================================================================
// INSTANCES
// =============================================================================
EspNowStrategy espNowStrategy;
ProtocolEngine engine(&espNowStrategy);
Node_Actuator node(NODE_ID, &engine);

void setup() {
    Serial.begin(115200);
    delay(2000);

    Serial.printf("=== ACTUATOR NODE (ID: %d) ===\n", NODE_ID);
    Serial.println("Commands:");
    Serial.println("  'i': IDLE (Ignore Commands)");
    Serial.println("  'a': ACTIVE (Execute Commands)");

    // Initialize Comms
    espNowStrategy.begin();
    std::array<uint8_t, 6> gatewayMac;
    memcpy(gatewayMac.data(), GATEWAY_MAC, 6);
    espNowStrategy.registerRoute(GATEWAY_ID, gatewayMac);
    espNowStrategy.registerRoute(0, gatewayMac); // Node 0 is Server (via Gateway)

    // Initialize Node
    if (node.getExecutor()) {
        std::vector<uint8_t> pins = {PIN_MOTOR_RELAY};
        node.getExecutor()->setPins(pins);
    }
    node.begin();

    // Callback for Command Execution
    node.addGpioListener([&](const Demeter::SetGpioCmd& cmd) {
        if (currentMode == MODE_IDLE) {
            Serial.println(">> [IGNORED] Command received but mode is IDLE.");
            return;
        }

        Serial.println("========================================");
        Serial.println(">> [ACTUATOR] COMMAND RECEIVED!");
        Serial.printf(">> Target Pin: %d | Value: %s\n", cmd.pin, cmd.value ? "HIGH" : "LOW");
        Serial.println("========================================");

        // Execute via SystemManager (which calls Executor)
        node.getSystemManager()->injectCommand(cmd); 
        
        // Send Feedback to Server (0)
        Demeter::PinReport report;
        report.sourceId = NODE_ID;
        report.pin = cmd.pin;
        report.state = cmd.value;
        node.getSystemManager()->sendPinStatus(0, report); // Target 0 
        
        Serial.println(">> [ACTUATOR] Feedback sent to Gateway.");
    });

    Serial.println("[Setup] Ready.");
}

void loop() {
    node.update();

    if (Serial.available()) {
        char c = Serial.read();
        if (c == 'r') {
            Serial.println(">> [CMD] Resetting Node...");
            delay(100);
            ESP.restart();
        } else if (c == 'i') {
            currentMode = MODE_IDLE;
            Serial.println(">> MODE: IDLE");
        } else if (c == 'a') {
            currentMode = MODE_ACTIVE;
            Serial.println(">> MODE: ACTIVE (Waiting for commands)");
        } else if (c == 'h') {
            Serial.println(">> [CMD] Initiating Handshake with Gateway (ID 1)...");
            if (node.getSystemManager()) {
                node.getSystemManager()->initiateHandshake(GATEWAY_ID);
            }
        }
    }
}
