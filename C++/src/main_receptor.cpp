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
#include "core/GpioController.h"
#include "core/SystemContext.h"

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

// 3. Hardware Layer: GPIO Controller
// Manages physical pin states.
GpioController gpioController;

// 4. System Layer: Context Orchestrator
// Binds Engine and Controller, manages State & Queue.
SystemContext systemCtx(engine, gpioController);

/**
 * @brief Standard Arduino Setup.
 * Initializes Debug Serial, System Context, and Communication.
 */
void setup() {
    // Debug Serial (USB)
    Serial.begin(115200);
    
    // Feedback LED (GPIO 4)
    pinMode(4, OUTPUT);
    digitalWrite(4, LOW);

    delay(1000);
    while(!Serial) delay(10);

    Serial.println("=== DEMETER GATEWAY V2 (ESP-Now + UART) ===");
    Serial.println(" [I] Mode: IMMEDIATE");
    Serial.println(" [R] Mode: QUEUED");
    Serial.println("==========================================");

    // Initialize System Logic
    systemCtx.setup();
    
    // Feedback Logic: Toggle GPIO 4 (Index 0 for user "1") on ACK
    // Note: User said "encience gpio 4" when receiving ACK from Ping.
    // If it's already on, turn off.
    engine.onAckRecv([](uint8_t srcId) {
        // Toggle GPIO 4 (Mapped to ID 4 in GpioController, or Index 0?)
        // GpioController uses 0-3 for pins 4-7.
        static bool state = false;
        state = !state;
        // On ESP32-S3 DevKit, Pin 4 might be used for something else or correct.
        // Assuming Pin 4 is valid.
        digitalWrite(4, state ? HIGH : LOW);
        Serial.printf(">> ACK Received from Node %d. Toggled GPIO 4 to %s\n", srcId, state ? "ON" : "OFF");
    });

    // Forward Data Reports to UART (Target 0)
    // When Gateway (ID 1) receives DataReport, it needs to send it to Host (ID 0).
    // The ProtocolEngine::sendDataReport sends to a target.
    // If we call engine.sendDataReport(0, ...), it will construct a NEW frame and send it.
    // Strategy for ID 0 is UART.
    engine.onDataReportRecv([&](uint8_t srcId, float temp, float hum) {
        Serial.printf(">> DATA REPORT from Node %d: %.2f C, %.2f %%\n", srcId, temp, hum);
        // Forward as a new packet from Gateway (or preserve source?)
        // V2 Protocol Header has Source ID. 
        // If we use sendDataReport, Source will be Gateway (1).
        // This effectively "proxies" the data. The Host will see "From Node 1: Temp X".
        // But we want "From Node 2".
        // To preserve Source ID, we would need to manually construct frame or add "Forwarding" capability.
        // OR: We simply tell ProtocolEngine to "spoof" source? No.
        // OR: The Node should have sent it to ID 0 (Host) initially!
        // If Node sends to ID 0, Gateway forwards it at Rule 5.
        
        // However, user setup currently sends to Target 1.
        // So we will proxy it. 
        // The host will see it coming from Gateway (1).
        // BUT the payload contains the data. 
        // Does the Host care about the Source ID for logging? 
        // Yes, likely.
        
        // Workaround: We Re-Send it to ID 0.
        // If we want Host to know it's from Node 2, we might need to modify payload or header.
        // For now, let's just send it to ID 0.
        engine.sendDataReport(0, temp, hum); 
    });
    
    // Initialize Composite Communication (Starts UART + ESP-Now)
    gatewayStrategy.begin();
    
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
    // 1. System Loop (Protocol Engine Update)
    systemCtx.loop();

    // 2. User Interactive Menu (Serial USB / Debug)
    if (Serial.available()) {
        char c = toupper(Serial.read());
        // Simple state tracking for toggling in manual mode
        static bool pinStates[8] = {false}; 

        switch (c) {
            case 'H': {
                // Manual PING to Host (ID 0)
                Serial.println(">> TX -> PING Host (ID 0)");
                engine.sendPing(0);
                break;
            }
            case 'P': {
                // Manual PING to Node 2
                Serial.println(">> TX -> PING Node 2 (Manual)");
                std::vector<uint8_t> empty;
                // We use engine's internal sendFrame via headers if possible, 
                // but sendFrame is private. 
                // We can't call sendFrame directly. 
                // Alternative: Inject a "Ping" command? No, ProtocolEngine handles sending.
                // We need a public method in ProtocolEngine to send Ping.
                // OR we just use the Strategy directly to send a raw frame?
                // Let's expose sendPing in ProtocolEngine or make sendFrame protected/public.
                // For now, I'll modify ProtocolEngine.h to make sendFrame public OR add sendPing.
                // Using a lambda or creating a temporary command?
                // Actually, ProtocolEngine should have a sendPing method.
                // I will add `sendPing(uint8_t target)` to ProtocolEngine.
                engine.sendPing(2);
                break;
            }
            case 'I':
                systemCtx.setExecutionMode(ExecutionMode::IMMEDIATE);
                Serial.println(">> MODE: IMMEDIATE");
                break;
            case 'R':
                systemCtx.setExecutionMode(ExecutionMode::INTERACTIVE_QUEUE);
                Serial.println(">> MODE: QUEUE (Buffering...)");
                break;
            case 'M':
                Serial.print(">> Gateway MAC: ");
                Serial.println(WiFi.macAddress());
                break;
            case 'E':
                Serial.println(">> EXECUTING QUEUE...");
                systemCtx.executeQueue();
                break;
            case 'C':
                systemCtx.clearQueue();
                Serial.println(">> QUEUE CLEARED");
                break;
            
            case 'D': {
                // Manual Data Report to Host (ID 0)
                Serial.println(">> TX -> DATA REPORT (Manual Mock)");
                // Send Mock Temp: 24.5C, Hum: 55.0%
                engine.sendDataReport(0, 24.5f, 55.0f);
                break;
            }

            case '1':
            case '2':
            case '3':
            case '4': {
                uint8_t pin = (c - '0') + 3; // '1'->4, '2'->5, '3'->6, '4'->7
                pinStates[pin] = !pinStates[pin]; // Toggle Local State
                
                Demeter::SetGpioCmd cmd;
                cmd.pin = pin;
                cmd.value = pinStates[pin];
                cmd.flags = 0;

                Serial.printf(">> MANUAL: PIN %d -> %s\n", pin, cmd.value ? "ON" : "OFF");
                systemCtx.injectCommand(cmd); // Inject into Protocol Logic
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