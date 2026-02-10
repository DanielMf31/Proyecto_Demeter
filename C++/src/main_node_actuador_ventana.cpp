/**
 * @file main_node_actuador_ventana.cpp
 * @brief Firmware for Actuator Node (Window Motor Control).
 * 
 * Implements Protocol V2 to control a relay based on SET_GPIO commands.
 * Reports status (Motor State + Battery) back to Gateway.
 */

#include <Arduino.h>
#include <WiFi.h>
#include "communications/EspNowStrategy.h"
#include "core/ProtocolEngine.h"

// ==========================================
// Configuration
// ==========================================
#define NODE_ID 3                 // Unique ID for Actuator
#define GATEWAY_ID 1

// Pin Definitions
#define PIN_MOTOR_RELAY 2         // GPIO 2 (Onboard LED usually, good for visual test)
#define PIN_BATTERY_ADC 35        // ADC1_CH7 

// Simulation/Constants
#define BATTERY_MAX_VOLTAGE 12.6
#define BATTERY_MIN_VOLTAGE 10.5

// ==========================================
// Global Instances
// ==========================================
EspNowStrategy espNowStrategy;
ProtocolEngine engine(&espNowStrategy);

// State
bool motorState = false;

// ==========================================
// Helper Functions
// ==========================================

float readBatteryVoltage() {
    uint16_t raw = analogRead(PIN_BATTERY_ADC);
    // Simple divider logic: 3.3V ADC. Divider Ratio assumed 4:1 (13.2V max)
    // voltage = raw * (3.3 / 4095.0) * 4.0;
    // For prototype without real divider, we just return a simulated value based on raw noise
    return 12.0 + (raw % 100) / 100.0; 
}

void reportStatus() {
    float voltage = readBatteryVoltage();
    bool stateVal = motorState;
    
    Serial.printf("[Actuator] Reporting: Motor=%s, Bat=%.2fV\n", stateVal ? "ON" : "OFF", voltage);
    
    // Send PIN_REPORT (Cmd 0x0C) for Motor State
    engine.sendPinReport(GATEWAY_ID, PIN_MOTOR_RELAY, stateVal);

    // Send SYSTEM_REPORT (Cmd 0x0D) for Battery/Mode
    // Mode 0 = Active
    uint16_t battMv = (uint16_t)(voltage * 1000); 
    engine.sendSystemReport(GATEWAY_ID, 0, battMv);
}

// ==========================================
// Callbacks
// ==========================================

void onSetGpioCommand(Demeter::SetGpioCmd cmd) {
    Serial.printf("[Actuator] CMD SET_GPIO Pin=%d Val=%d\n", cmd.pin, cmd.value);
    
    // We only control our specific PIN
    if (cmd.pin == PIN_MOTOR_RELAY) {
        motorState = cmd.value;
        digitalWrite(PIN_MOTOR_RELAY, motorState ? HIGH : LOW);
        
        // Immediate Feedback
        reportStatus();
    } else {
        Serial.println("[Actuator] Ignored (Wrong Pin)");
    }
}

void onPingRecv(uint8_t srcId) {
    Serial.printf("[Actuator] Ping from %d\n", srcId);
    // Engine automatically sends ACK. 
    // We can also send a report to say "I'm alive and here is my status"
    // reportStatus(); // Optional
}

// ==========================================
// Main
// ==========================================

void setup() {
    Serial.begin(115200);
    delay(1000);
    while(!Serial) delay(10);

    Serial.println("=== DEMETER ACTUATOR NODE V2 (Window Control) ===");
    Serial.printf("Node ID: %d\n", NODE_ID);

    // Hardware Init
    pinMode(PIN_MOTOR_RELAY, OUTPUT);
    digitalWrite(PIN_MOTOR_RELAY, LOW);
    
    // Comms Init
    espNowStrategy.begin();
    engine.setNodeId(NODE_ID);
    
    // Register Gateway
    // MAC: 9C:13:9E:A8:6F:CC (Gateway)
    std::array<uint8_t, 6> gatewayMac = {0x9C, 0x13, 0x9E, 0xA8, 0x6F, 0xCC};
    espNowStrategy.registerRoute(GATEWAY_ID, gatewayMac);

    // Register Callbacks
    engine.onSetGpio(onSetGpioCommand);
    engine.onPingRecv(onPingRecv);

    Serial.println("[Setup] Ready. Waiting for commands...");
}

void loop() {
    engine.update();
    
    // Simple Light Sleep logic could go here
    // For now, standard active loop
}
