/**
 * @file main_receptor.cpp
 * @brief Firmware Entry Point for "Receptor" (ESP32).
 * 
 * Implements the Demeter Protocol V2 Receptor logic.
 * Initializes the Dependency Injection container (SystemContext)
 * and managing the main Arduino Loop.
 */

#include <Arduino.h>
#include "communications/UartStrategy.h"
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

// 1. Communication Layer: UART (Serial2)
// Uses pins 16 (RX) and 17 (TX) at 115200 baud.
UartStrategy uartStrategy(&Serial2, 115200, RXD2, TXD2);

// 2. Protocol Layer: Protocol V2 Engine
// Decoupled from transport via IComms interface.
ProtocolEngine engine(&uartStrategy);

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
    delay(1000);
    while(!Serial) delay(10);

    Serial.println("=== DEMETER RECEPTOR V2 (MVP GPIO) ===");
    Serial.println(" [1-4] Toggle PIN 4-7");
    Serial.println(" [I] Mode: IMMEDIATE (Default)");
    Serial.println(" [R] Mode: QUEUED (Interactive)");
    Serial.println(" [E] Execute Queue");
    Serial.println(" [C] Clear Queue");
    Serial.println("======================================");

    // Initialize System Logic
    systemCtx.setup();
    
    // Initialize Communication (Starts Serial2)
    uartStrategy.begin();
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
            case 'I':
                systemCtx.setExecutionMode(ExecutionMode::IMMEDIATE);
                Serial.println(">> MODE: IMMEDIATE");
                break;
            case 'R':
                systemCtx.setExecutionMode(ExecutionMode::INTERACTIVE_QUEUE);
                Serial.println(">> MODE: QUEUE (Buffering...)");
                break;
            case 'E':
                Serial.println(">> EXECUTING QUEUE...");
                systemCtx.executeQueue();
                break;
            case 'C':
                systemCtx.clearQueue();
                Serial.println(">> QUEUE CLEARED");
                break;
            
            // Manual GPIO Control Shortcuts
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