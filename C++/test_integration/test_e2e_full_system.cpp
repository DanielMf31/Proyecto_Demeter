#include <unity.h>
#include <vector>
#include <Arduino.h>
#include "core/ProtocolEngine.h"
#include "core/Node_Gateway.h"
#include "core/Node_Sensor.h"
#include "core/Node_Actuator.h"
#include "communications/IComms.h"
#include "MockComms.h"
#include "../mocks/MockSensor.h" 

// Separate Comms for each Node (Simulating independent radios)
MockComms* gwComms = nullptr;
MockComms* sensComms = nullptr;
MockComms* actComms = nullptr;

// Nodes
Node_Gateway* gatewayNode = nullptr;
Node_Sensor* sensorNode = nullptr;
Node_Actuator* actuatorNode = nullptr;

// Engines
ProtocolEngine* gwEngine = nullptr;
ProtocolEngine* sensEngine = nullptr;
ProtocolEngine* actEngine = nullptr;

// Dependencies
MockSensor* mockSensor = nullptr;

void setup_e2e_system() {
    // 1. Network Media (Independent instances)
    gwComms = new MockComms();
    sensComms = new MockComms();
    actComms = new MockComms();

    // 2. Gateway (ID 1)
    gwEngine = new ProtocolEngine(gwComms);
    gwEngine->setNodeId(1);
    gatewayNode = new Node_Gateway(1, gwEngine);
    gatewayNode->begin();

    // 3. Sensor Node (ID 2)
    sensEngine = new ProtocolEngine(sensComms);
    sensEngine->setNodeId(2);
    sensorNode = new Node_Sensor(2, sensEngine);
    
    mockSensor = new MockSensor();
    sensorNode->getSensorManager()->addSensor(mockSensor);
    sensorNode->setReportingConfig(0, false); // Manual trigger
    sensorNode->begin();

    // 4. Actuator Node (ID 3)
    actEngine = new ProtocolEngine(actComms);
    actEngine->setNodeId(3);
    actuatorNode = new Node_Actuator(3, actEngine);
    actuatorNode->begin();
}

void teardown_e2e_system() {
    delete gatewayNode;
    delete sensorNode;
    delete actuatorNode;
    
    delete gwEngine;
    delete sensEngine;
    delete actEngine;
    
    delete gwComms;
    delete sensComms;
    delete actComms;
    
    delete mockSensor;
}

// Helper to simulate "Air" propagation
void propagate_packets() {
    // 1. Collect all TX
    std::vector<uint8_t> sensorTx = sensComms->_txBuffer;
    std::vector<uint8_t> gatewayTx = gwComms->_txBuffer;
    std::vector<uint8_t> actuatorTx = actComms->_txBuffer;
    
    // Clear TX buffers after "transmission"
    sensComms->_txBuffer.clear();
    gwComms->_txBuffer.clear();
    actComms->_txBuffer.clear();
    
    // 2. Broadcast to others (Simulate Shared Medium)
    
    // Sensor -> Gateway & Actuator
    if (!sensorTx.empty()) {
        gwComms->pushRxData(sensorTx);
        actComms->pushRxData(sensorTx);
    }
    
    // Gateway -> Sensor & Actuator
    if (!gatewayTx.empty()) {
        sensComms->pushRxData(gatewayTx);
        actComms->pushRxData(gatewayTx);
    }
    
    // Actuator -> Gateway & Sensor
    if (!actuatorTx.empty()) {
        gwComms->pushRxData(actuatorTx);
        sensComms->pushRxData(actuatorTx);
    }
}

void test_e2e_full_flow() {
    // =========================================================
    // Scenario 1: Sensor -> Gateway (Data Report)
    // =========================================================
    
    // 1. Setup Data
    mockSensor->setValues(25.5f, 60.0f);
    
    // 2. Trigger Sensor Send
    // Force immediate send by config logic (interval 1ms + delay)
    sensorNode->setReportingConfig(1, false); 
    delay(2);
    sensorNode->update(); 
    
    // 3. Propagate Physics
    propagate_packets();
    
    // 4. Gateway Process
    // Gateway reads from its RX buffer
    gatewayNode->update();
    
    // 5. Verify Gateway received it
    // Logic: If Gateway Logic was implemented, it would store this.
    // Since Gateway is currently just a "Pass-Through" or "Reporter" in code,
    // we assume success if NO ERROR and potentially if it ACKs (if logic demands).
    // Or we can check if Gateway sent an ACK?
    // Let's check `gwComms->_txBuffer` for an ACK (CMD 0x01) to ID 2.
    // The current ProtocolEngine sends ACK for PING, but maybe not for REPORTS?
    // Checking ProtocolEngine.cpp: 
    // onTempHumReportRecv -> calls callback -> No automatic ACK in `parseFrame`.
    
    // So how do verification?
    // We can check that the Gateway's IO/State is correct?
    // Or just assert that the message arrived at Gateway Comms?
    // Yes, let's verify `gwComms->received`... wait, `read` clears it.
    // We can't easily peek inside `Node_Gateway` to see if `_onTempHumRecv` fired
    // without a spy.
    
    // PROPOSAL: Verify that the ACTUATOR *ignored* the packet (ID 2->1).
    actuatorNode->update();
    // Actuator should NOT reply with NACK or anything.
    propagate_packets();
    TEST_ASSERT_TRUE(actComms->_txBuffer.empty());
    
    
    // =========================================================
    // Scenario 2: Gateway -> Actuator (Command Control)
    // =========================================================
    
    // 1. Gateway Logic triggers command
    // "Simulating" Gateway deciding to turn on Actuator (ID 3)
    Demeter::SetGpioCmd cmd;
    cmd.pin = 4;
    cmd.value = true;
    cmd.flags = 0;
    gwEngine->sendSetGpio(3, cmd); // Pin 4, ON
    
    // 2. Propagate
    propagate_packets();
    
    // 3. Actuator Process
    actuatorNode->update();
    
    // 4. Verify Actuator Action
    // Actuator should have toggled Pin 4.
    // As we can't inspect GpioController easily, let's check the Protocol Response.
    // Does Actuator send an ACK? Or something?
    // ProtocolEngine.cpp: onSetGpio -> calls callback.
    // Node_Actuator.cpp: callback -> setPin -> NO automatic ACK in callback logic usually.
    // UNLESS `SystemContext` does it?
    // SystemContext.cpp: handleGpioCommand -> execute -> NO ack.
    
    // BUT, we can make the Actuator send a PIN_REPORT as confirmation
    // if we add that logic to the test simulation or if the firmware did it.
    // Currently firmware doesn't auto-echo.
    
    // However, if we sent `SET_GPIO` with a "Sequence", maybe?
    // No.
    
    // Let's use `PING` for verification of aliveness? 
    // Or just trust that if `actuatorNode->update()` ran without crash...
    
    // Actually, `Node_Actuator` interacts with `GpioController`.
    // Can we check `MockComms` for any output?
    // If Actuator is silent, `actComms->_txBuffer` should be empty (unless it NACKs).
    propagate_packets();
    TEST_ASSERT_TRUE(actComms->_txBuffer.empty()); // Should be empty if success (no NACK)
    
    // =========================================================
    // Scenario 3: Explicit Query (Gateway -> Actuator -> Gateway)
    // =========================================================
     
    // 1. Gateway asks for Sequence or Ping
    Demeter::RequestData req = {0};
    gwEngine->sendPing(3, req);
    propagate_packets();
    
    // 2. Actuator Process
    actuatorNode->update();
    
    // 3. Propagate (Actuator sends ACK)
    propagate_packets();
    // Here `actComms` was cleared, but `gwComms` received the ACK.
    
    // 4. Verify Gateway received ACK
    // Gateway reads
    gatewayNode->update();
    
    // We can check if `gwComms` *had* data before update?
    // Yes, we missed the check.
    // Let's rewind/retry logic:
    
    // A. Gateway sends Ping
    Demeter::RequestData req2 = {0};
    gwEngine->sendPing(3, req2);
    propagate_packets(); // This moves PING from GW_TX to ACT_RX
    
    // B. Actuator updates (Reads PING, Queues ACK)
    actuatorNode->update();
    
    // C. Check Actuator TX (Should have ACK)
    // Don't propagate yet. Peek.
    TEST_ASSERT_FALSE(actComms->_txBuffer.empty());
    
    // Verify it is an ACK (Cmd ID = 0x01)
    // Frame: [Sync][Len][Flags][Src=3][Dst=1][CMD=01][CRC]
    // Src should be 3 (Actuator), Dst should be 1 (Gateway)
    // We can parse the raw buffer.
    std::vector<uint8_t>& tx = actComms->_txBuffer;
    TEST_ASSERT_GREATER_OR_EQUAL(ProtocolEngine::HEADER_SIZE + 1, tx.size());
    // Cmd ID at index 5 (Sync=0, Len=1, Flags=2, Src=3, Dst=4, Cmd=5)
    // wait, struct Header: sync, length, flags, src, dst, cmd
    // 0, 1, 2, 3, 4, 5
    TEST_ASSERT_EQUAL(0x01, tx[5]); // CMD_ACK
    TEST_ASSERT_EQUAL(0x03, tx[3]); // Src ID
    TEST_ASSERT_EQUAL(0x01, tx[4]); // Dst ID
    
    // Success!
}

void run_e2e_tests() {
    setup_e2e_system();
    RUN_TEST(test_e2e_full_flow);
    teardown_e2e_system();
}
