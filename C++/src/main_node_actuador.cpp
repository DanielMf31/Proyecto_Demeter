/**
 * @file main_node_actuador.cpp
 * @brief Firmware for Actuator Node (Window Motor Control).
 * Features:
 * - IDLE/ACTIVE Modes
 * - ESP-NOW Communication with Gateway
 * - RGB LED Feedback (FastLED on Pin 48)
 * - Motor Relay Control (Pin 4)
 */

#include <Arduino.h>
#include "core/ProtocolEngine.h"
#include "communications/EspNowStrategy.h"
#include "core/GpioController.h"
#include "core/Node_Actuator.h"

// =============================================================================
// CONFIGURATION
// =============================================================================
const uint8_t MY_NODE_ID = 3; // ACTUATOR NODE ID
const uint8_t GATEWAY_ID = 1;

// MAC Address of Gateway (Must match the one in main_gateway.cpp)
const uint8_t GATEWAY_MAC[] = {0x9C, 0x13, 0x9E, 0xAC, 0x01, 0xC4}; 

// Hardware Pins
const std::vector<uint8_t> CONTROLLED_PINS = {2, 4, 15}; // Example Pins

// =============================================================================
// INSTANCES
// =============================================================================
EspNowStrategy espNowStrategy;
ProtocolEngine engine(&espNowStrategy);
};
int currentMode = MODE_IDLE; 

void setup() {
    Serial.begin(115200);
    delay(2000);

    Serial.println("=== ACTUATOR NODE (ID: 3) ===");
    Serial.println("Using FastLED");
    Serial.println("Commands:");
    Serial.println("  'i': IDLE (Ignore Commands)");
    Serial.println("  'a': ACTIVE (Execute Commands)");

    // Initialize RGB LED
    FastLED.addLeds<LED_TYPE, RGB_LED_PIN, COLOR_ORDER>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);
    FastLED.setBrightness(20);
    leds[0] = CRGB::Black; // OFF
    FastLED.show();

    // Initialize Comms
    espNowStrategy.begin();
    std::array<uint8_t, 6> gatewayMac = {0x9C, 0x13, 0x9E, 0xA8, 0x6F, 0xCC}; // UPDATE MAC IF NEEDED
    espNowStrategy.registerRoute(GATEWAY_ID, gatewayMac);

    // Initialize Node
    node.getExecutor()->setPins({PIN_MOTOR_RELAY});
    node.begin();

    // Callback for Command Execution (Observer 1: Visual Feedback)
    node.addGpioListener([&](const Demeter::SetGpioCmd& cmd) {
        // ALWAYS Blink to show reception, even if IDLE
        leds[0] = CRGB::Blue;
        FastLED.show();
        delay(50);
        leds[0] = CRGB::Black;
        FastLED.show();
        
        if (currentMode == MODE_IDLE) {
            Serial.println(">> [IGNORED] Command received but mode is IDLE.");
            return;
        }

        Serial.println("========================================");
        Serial.println(">> [ACTUATOR] COMMAND RECEIVED!");
        Serial.printf(">> Target Pin: %d | Value: %s\n", cmd.pin, cmd.value ? "HIGH" : "LOW");
        Serial.println("========================================");

        // Visual Feedback: Green (High) / Red (Low)
        if (cmd.value) {
            leds[0] = CRGB::Green;
        } else {
            leds[0] = CRGB::Red;
        }
        FastLED.show();

        node.getSystemManager()->injectCommand(cmd); // Execute hardware
        
        // Send Feedback to Gateway
        node.getSystemManager()->sendPinStatus(GATEWAY_ID, cmd.pin, cmd.value); 
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
            leds[0] = CRGB::Black;
            FastLED.show();
        } else if (c == 'a') {
            currentMode = MODE_ACTIVE;
            Serial.println(">> MODE: ACTIVE (Waiting for commands)");
            leds[0] = CRGB::MediumBlue; // Dim Blue active
            FastLED.show();
        } else if (c == 'h') {
            Serial.println(">> [CMD] Initiating Handshake with Gateway (ID 1)...");
            if (node.getSystemManager()) {
                node.getSystemManager()->initiateHandshake(GATEWAY_ID);
            }
        }
    }
}
