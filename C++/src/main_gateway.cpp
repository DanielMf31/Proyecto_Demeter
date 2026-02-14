#include <Arduino.h>
#include <WiFi.h>
#include "communications/UartStrategy.h"
#include "communications/EspNowStrategy.h"
#include "communications/GatewayStrategy.h"
#include "core/ProtocolEngine.h"
#include "core/Node_Gateway.h"

// =============================================================================
// CONFIGURATION
// =============================================================================
const uint8_t MY_NODE_ID = 1;

// MAC Addresses of Known Nodes
// REPLACE THESE WITH REAL MACs FROM YOUR HARDWARE
const uint8_t SENSOR_MAC[] = {0x20, 0x6E, 0xF1, 0x85, 0x58, 0xD0}; // Node 2 (User Provided)
const uint8_t ACTUATOR_MAC[] = {0x9C, 0x13, 0x9E, 0xAC, 0x50, 0xC4}; // Node 3 (User Provided)

#define RXD2 16
#define TXD2 17

// =============================================================================
// INSTANCES
// =============================================================================
UartStrategy uartStrategy(&Serial2, 115200, RXD2, TXD2);
EspNowStrategy espNowStrategy;
GatewayStrategy gatewayStrategy(&uartStrategy, &espNowStrategy);
ProtocolEngine engine(&gatewayStrategy);
Node_Gateway gateway(MY_NODE_ID, &engine);

// =============================================================================
// SERIAL COMMAND PARSER
// =============================================================================
// Format: "CMD:SET_GPIO:<NODE_ID>:<PIN>:<VALUE>"
// Example: "CMD:SET_GPIO:3:2:1" -> Node 3, Pin 2, HIGH

void processSerialCommand(String cmd) {
    cmd.trim();
    if (cmd.startsWith("CMD:SET_GPIO:")) {
        // Parse params
        int firstColon = cmd.indexOf(':', 13);
        int secondColon = cmd.indexOf(':', firstColon + 1);
        
        if (firstColon == -1 || secondColon == -1) {
            Serial.println(">> [ERROR] Invalid Format. Use: CMD:SET_GPIO:<ID>:<PIN>:<VAL>");
            return;
        }

        String idStr = cmd.substring(13, firstColon);
        String pinStr = cmd.substring(firstColon + 1, secondColon);
        String valStr = cmd.substring(secondColon + 1);

        uint8_t targetId = idStr.toInt();
        uint8_t pin = pinStr.toInt();
        uint8_t val = valStr.toInt();

        Serial.printf(">> [CMD] Sending SET_GPIO to Node %d: Pin %d -> %d\n", targetId, pin, val);

        Demeter::SetGpioCmd gpioCmd;
        gpioCmd.pin = pin;
        gpioCmd.value = (val > 0);
        gpioCmd.flags = 0;

        gateway.getSystemManager()->sendCommand(targetId, gpioCmd);
    } else if (cmd.startsWith("CMD:HANDSHAKE:")) {
        // Format: CMD:HANDSHAKE:<NODE_ID>
        int firstColon = cmd.indexOf(':', 13);
        if (firstColon != -1) {
             String idStr = cmd.substring(14); // 13 is 'CMD:HANDSHAKE' len is 13? No. "CMD:HANDSHAKE" is 13. : is 14th?
             // "CMD:HANDSHAKE:" length is 14. 
             idStr = cmd.substring(14);
             uint8_t targetId = idStr.toInt();
             Serial.printf(">> [CMD] Initiating Handshake with Node %d\n", targetId);
             gateway.getSystemManager()->initiateHandshake(targetId);
        }
    } else if (cmd == "INFO") {
        Serial.println(">> [INFO] Gateway Running. Modes: Serial Loopback + ESP-NOW.");
    } else if (cmd == "r" || cmd == "RESET") {
        Serial.println(">> [CMD] Resetting System...");
        delay(100);
        ESP.restart();
    } else {
        Serial.println(">> [ERROR] Unknown Command.");
    }
}

void setup() {
    Serial.begin(115200);
    delay(1000);
    while(!Serial) delay(10); // Wait for USB

    Serial.println("=== DEMETER GATEWAY V2 (Direct Control) ===");
    Serial.println("Type commands in console:");
    Serial.println("  CMD:SET_GPIO:<ID>:<PIN>:<VAL>  (e.g., CMD:SET_GPIO:3:2:1)");
    Serial.println("  INFO                           (System Status)");

    // 1. Init Strategies
    gatewayStrategy.begin();

    // 2. Register Routes (Update with Real MACs for testing)
    std::array<uint8_t, 6> sensorMac;
    std::copy(std::begin(SENSOR_MAC), std::end(SENSOR_MAC), sensorMac.begin());
    espNowStrategy.registerRoute(2, sensorMac);

    std::array<uint8_t, 6> actuatorMac;
    std::copy(std::begin(ACTUATOR_MAC), std::end(ACTUATOR_MAC), actuatorMac.begin());
    espNowStrategy.registerRoute(3, actuatorMac);

    // 3. Start Gateway
    gateway.begin();

    // 4. Configure Callbacks
    
    // Ack Listener
    gateway.getSystemManager()->addAckListener([](const Demeter::AckData& data) {
         // Serial.printf(">> [ACK] Node %d confirmed (Ctx: 0x%02X)\n", data.sourceId, data.context);
    });

    // Sensor Data Listener (Always Active)
    gateway.getSystemManager()->addSensorDataListener([](const Demeter::TempHumReport& report) {
        // Serial.printf(">> [DATA] Node %d: %.2f C, %.2f %%\n", report.sourceId, report.temperature, report.humidity);
        // Forward to UART/Host?
        // gateway.getSystemManager()->sendSensorData(0, report); 
    });

    // Pin Status Listener
    gateway.getSystemManager()->addPinReportListener([](const Demeter::PinReport& report) {
        // Serial.printf(">> [STATUS] Node %d Pin %d is %s\n", report.sourceId, report.pin, report.state ? "ON" : "OFF");
    });
    
    Serial.println("[Setup] Ready.");
}

void loop() {
    // 1. Core Update
    gateway.update();

    // 2. Serial Command Input
    if (Serial.available()) {
        String line = Serial.readStringUntil('\n');
        processSerialCommand(line);
    }
}
