#include <unity.h>
#include <vector>
#include <map>
#include <queue>
#include <Arduino.h>
#include "core/ProtocolEngine.h"
#include "core/Node_Gateway.h"
#include "core/Node_Sensor.h"
#include "core/Node_Actuator.h"
#include "../mocks/VirtualStrategy.h"
#include "../mocks/MockSensor.h" 

// Static Definitions for VirtualStrategy
std::map<uint8_t, std::queue<std::vector<uint8_t>>> VirtualStrategy::_mailbox;
std::map<uint8_t, VirtualStrategy*> VirtualStrategy::_instances;

// Components
VirtualStrategy* gwComms = nullptr;
VirtualStrategy* sensComms = nullptr;
VirtualStrategy* actComms = nullptr;

Node_Gateway* gatewayNode = nullptr;
Node_Sensor* sensorNode = nullptr;
Node_Actuator* actuatorNode = nullptr;

ProtocolEngine* gwEngine = nullptr;
ProtocolEngine* sensEngine = nullptr;
ProtocolEngine* actEngine = nullptr;

MockSensor* mockSensor = nullptr;

void setup_e2e_system() {
    VirtualStrategy::resetBus();

    // 1. Gateway (ID 1)
    gwComms = new VirtualStrategy(1);
    gwEngine = new ProtocolEngine(gwComms);
    gwEngine->setNodeId(1);
    gatewayNode = new Node_Gateway(1, gwEngine);
    gatewayNode->begin();

    // 2. Sensor (ID 2)
    sensComms = new VirtualStrategy(2);
    sensEngine = new ProtocolEngine(sensComms);
    sensEngine->setNodeId(2);
    sensorNode = new Node_Sensor(2, sensEngine);
    
    // Config logic
    mockSensor = new MockSensor();
    // Assuming Node_Sensor handles SensorManager internally, we inject if possible or assume default.
    // Node_Sensor constructor creates new SensorManager. We need to access it.
    if (sensorNode->getSensorManager()) {
        sensorNode->getSensorManager()->addSensor(mockSensor);
    }
    
    // Disable random mock data for predictable testing unless we want it
    // But verify MOCK_DATA_ENABLED interaction?
    // Let's use real mock sensor readings for verification.
    sensorNode->setReportingConfig(0, false); // Manual trigger
    sensorNode->begin();

    // 3. Actuator (ID 3)
    actComms = new VirtualStrategy(3);
    actEngine = new ProtocolEngine(actComms);
    actEngine->setNodeId(3);
    actuatorNode = new Node_Actuator(3, actEngine);
    actuatorNode->begin();
}

void teardown_e2e_system() {
    delete gatewayNode;
    delete sensorNode;
    delete actuatorNode;
    // Engines deleted by Nodes usually? No, passed by ptr.
    // SystemManager deletes them? No.
    // We should delete them.
    delete gwEngine;
    delete sensEngine;
    delete actEngine;
    
    delete gwComms;
    delete sensComms;
    delete actComms;
    
    // mockSensor is deleted by SensorManager inside Node_Sensor? 
    // SensorManager takes ownership? 
    // Usually "addSensor" just stores pointer.
    // We should delete it if SensorManager doesn't.
    // Let's assume we own it for safety or check implementation.
    // Implementation: SensorManager doesn't seem to delete sensors in destructor.
    delete mockSensor;
}

void test_virtual_handshake() {
    // Sensor Init Handshake to Gateway
    // 1. Trigger Handshake
    Demeter::AckData ctx = {0, (uint8_t)Demeter::SessionContext::SENSOR_REPORT};
    sensorNode->getSystemManager()->initiateHandshake(1, ctx);
    
    // 2. Loop to propagate messages
    // SystemManager::update uses millis() for timeout/retry.
    // VirtualBus is instant.
    
    // Cycle 1: Sensor Sends SYN
    sensorNode->update(); 
    
    // Gateway Recv SYN -> Sends SYN-ACK
    gatewayNode->update();
    
    // Sensor Recv SYN-ACK -> Sends ACK -> State RUNNING
    sensorNode->update();
    
    // Gateway Recv ACK -> State RUNNING
    gatewayNode->update();
    
    // VERIFY
    TEST_ASSERT_EQUAL(Demeter::SystemState::RUNNING, sensorNode->getSystemManager()->getState());
    TEST_ASSERT_EQUAL(Demeter::SystemState::RUNNING, gatewayNode->getSystemManager()->getState());
}

void test_virtual_data_flow() {
    // Sensor sets value
    mockSensor->setValues(25.5f, 60.0f);
    
    // Sensor Collect & Publish
    sensorNode->getSystemManager()->collectAndPublishSensorData(1);
    
    // Propagate: Gateway reads
    gatewayNode->update();
    
    // Verify?
    // Gateway logs to serial? 
    // We can add a listener to Gateway to intercept
    bool received = false;
    gatewayNode->getSystemManager()->addSensorDataListener([&](const Demeter::TempHumReport& r){
        received = true;
        TEST_ASSERT_EQUAL(2, r.sourceId);
        TEST_ASSERT_EQUAL_FLOAT(25.5f, r.temperature);
        TEST_ASSERT_EQUAL_FLOAT(60.0f, r.humidity);
    });
    
    // Re-process to trigger listener (Wait, listener triggers on update() -> handle... -> listener)
    // We already called update(). But we adding listener AFTER update? No good.
    // Add listener first testing logic?
    // We need to re-send.
    
    // Send again
    mockSensor->setValues(30.0f, 70.0f);
    sensorNode->getSystemManager()->collectAndPublishSensorData(1);
    
    // Gateway update should trigger
    gatewayNode->update();
    
    TEST_ASSERT_TRUE(received);
}

void test_virtual_command_flow() {
    // Gateway sends Command to Actuator
    Demeter::SetGpioCmd cmd;
    cmd.pin = 4;
    cmd.value = true;
    
    bool executed = false;
    actuatorNode->addGpioListener([&](const Demeter::SetGpioCmd& c){
        executed = true;
        TEST_ASSERT_EQUAL(4, c.pin);
        TEST_ASSERT_TRUE(c.value);
    });
    
    gatewayNode->getSystemManager()->sendCommand(3, cmd);
    
    // Actuator Updates
    actuatorNode->update();
    
    TEST_ASSERT_TRUE(executed);
}

void run_e2e_tests() {
    setup_e2e_system();
    RUN_TEST(test_virtual_handshake);
    RUN_TEST(test_virtual_data_flow);
    RUN_TEST(test_virtual_command_flow);
    teardown_e2e_system();
}
