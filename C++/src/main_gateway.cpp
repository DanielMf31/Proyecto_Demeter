/**
 * @file main_receptor.cpp
 * @brief Firmware Entry Point for "Receptor" (ESP32).
 * 
 * Implements the Demeter Protocol V2 Receptor logic.
 * Initializes the Dependency Injection container (SystemContext)
 * and managing the main Arduino Loop.
 */

#include <Arduino.h>
#include <WiFi.h>
#include "communications/UartStrategy.h"
#include "communications/EspNowStrategy.h"
#include "communications/GatewayStrategy.h"
#include "core/ProtocolEngine.h"
#include "core/Node_Gateway.h"

// Define Hardware Serial for ESP32
// RX=16, TX=17 (Adjust per hardware revision)
#define RXD2 16
#define TXD2 17

// ==========================================
// Global Instances (Dependency Injection)
// ==========================================

// 1. Communication Layers
// 1.1 UART (Host Connection)
UartStrategy uartStrategy(&Serial2, 115200, RXD2, TXD2);

// 1.2 ESP-Now (Node Network)
EspNowStrategy espNowStrategy;

// 1.3 Composite Gateway Strategy
GatewayStrategy gatewayStrategy(&uartStrategy, &espNowStrategy);

// 2. Protocol Layer: Protocol V2 Engine
// Uses the Composite Strategy
ProtocolEngine engine(&gatewayStrategy);

// 3. Application Layer: Node Gateway (Hybrid)
// ID 1 for Gateway
Node_Gateway gateway(1, &engine);

/**
 * @brief Standard Arduino Setup.
 * Initializes Debug Serial, System Context, and Communication.
 */
void setup() {
    // Debug Serial (USB)
    Serial.begin(115200);
    
    // Feedback LED (GPIO 4) is now managed by GpioController in Node_Gateway,
    // but we can still access it manually if needed, or rely on commands.
    // Ensure Pin 4 is Output (managed by Node_Gateway::begin -> GpioController::init)

    delay(1000);
    while(!Serial) delay(10);

    Serial.println("=== DEMETER GATEWAY V2 (Hybrid Node) ===");
    Serial.println(" [I] Mode: IMMEDIATE");
    Serial.println(" [R] Mode: QUEUED");
    Serial.println("==========================================");

    // Initialize Communications
    gatewayStrategy.begin();

    // Initialize Node (SystemContext, GpioController, SensorManager)
    gateway.begin();
    
    // Feedback Logic: Toggle GPIO 4 (Index 0 for user "1") on ACK
    engine.onAckRecv([](uint8_t srcId) {
        static bool state = false;
        state = !state;
        // We can use the gateway's GpioController if we want
        // gateway.getExecutor()->execute(...)
        // Or direct write for debug feedback
        digitalWrite(4, state ? HIGH : LOW);
        Serial.printf(">> ACK Received from Node %d. Toggled GPIO 4 to %s\n", srcId, state ? "ON" : "OFF");
    });

    // Forward Data Reports to UART (Target 0)
    engine.onTempHumReportRecv([&](uint8_t srcId, float temp, float hum) {
        Serial.printf(">> DATA REPORT from Node %d: %.2f C, %.2f %%\n", srcId, temp, hum);
        // Proxy to Host (ID 0)
        engine.sendTempHumReport(0, temp, hum); 
    });
    
    // DEBUG: HARDCODE NODE 2 MAC (From devices.json: 9C:13:9E:AC:50:C4)
    std::array<uint8_t, 6> node2Mac = {0x9C, 0x13, 0x9E, 0xAC, 0x50, 0xC4};
    espNowStrategy.registerRoute(2, node2Mac);
    Serial.println("DEBUG: Hardcoded Route for Node 2 added.");
}

/**
 * @brief Standard Arduino Loop.
 * 1. Updates System Context (Polls UART).
 * 2. Checks Debug Serial for Manual Commands.
 */
void loop() {
    // 1. System Loop (Protocol Engine Update via Node)
    gateway.update();

    // 2. User Interactive Menu (Serial USB / Debug)
    if (Serial.available()) {
        char c = toupper(Serial.read());
        // Simple state tracking for toggling in manual mode
        static bool pinStates[8] = {false}; 

        switch (c) {
            case 'H': {
                Serial.println(">> TX -> PING Host (ID 0)");
                engine.sendPing(0);
                break;
            }
            case 'P': {
                Serial.println(">> TX -> PING Node 2 (Manual)");
                engine.sendPing(2);
                break;
            }
            case 'I':
                gateway.getSystemContext()->setExecutionMode(ExecutionMode::IMMEDIATE);
                Serial.println(">> MODE: IMMEDIATE");
                break;
            case 'R':
                gateway.getSystemContext()->setExecutionMode(ExecutionMode::INTERACTIVE_QUEUE);
                Serial.println(">> MODE: QUEUE (Buffering...)");
                break;
            case 'M':
                Serial.print(">> Gateway MAC: ");
                Serial.println(WiFi.macAddress());
                break;
            case 'E':
                Serial.println(">> EXECUTING QUEUE...");
                gateway.getSystemContext()->executeQueue();
                break;
            case 'C':
                gateway.getSystemContext()->clearQueue();
                Serial.println(">> QUEUE CLEARED");
                break;
            
            case 'D': {
                Serial.println(">> TX -> TEMP HUM REPORT (Manual Mock)");
                engine.sendTempHumReport(0, 24.5f, 55.0f);
                break;
            }

            case '1':
            case '2':
            case '3':
            case '4': {
                uint8_t pin = (c - '0') + 3; // '1'->4, '2'->5, '3'->6, '4'->7
                pinStates[pin] = !pinStates[pin]; 
                
                Demeter::SetGpioCmd cmd;
                cmd.pin = pin;
                cmd.value = pinStates[pin];
                cmd.flags = 0;

                Serial.printf(">> MANUAL: PIN %d -> %s\n", pin, cmd.value ? "ON" : "OFF");
                gateway.getSystemContext()->injectCommand(cmd); 
                break;
            }

            case '\n':
            case '\r':
                break;
            default:
                Serial.print("Unknown Command: ");
                Serial.println(c);
                break;
        }
    }
}
