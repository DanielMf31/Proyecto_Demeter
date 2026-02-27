#include <unity.h>
#include "core/SystemManager.h"
#include "MockComms.h"
#include "test_runners.h"

// External references (Defined in main.cpp)
extern SystemManager* sys;
extern MockComms* mockComms;
extern ProtocolEngine* engine;

// =============================================================================
// TEST GROUP: Senders (Verifying SystemManager calls ProtocolEngine correctly)
// =============================================================================

void test_sys_send_sensor_data(void) {
    mockComms->reset();
    
    Demeter::TempHumReport report = {0, 25.5f, 60.0f};
    sys->sendSensorData(10, report);
    
    TEST_ASSERT_GREATER_THAN(0, mockComms->_txBuffer.size());
    // Expect 0x0B (TEMP_HUM_REPORT)
    TEST_ASSERT_EQUAL((uint8_t)Demeter::CommandType::TEMP_HUM_REPORT, mockComms->_txBuffer[5]); 
}

void test_sys_send_pin_status(void) {
    mockComms->reset();
    
    Demeter::PinReport report = {0, 5, true};
    sys->sendPinStatus(10, report);
    
    TEST_ASSERT_GREATER_THAN(0, mockComms->_txBuffer.size());
    // Expect 0x0C (PIN_REPORT)
    TEST_ASSERT_EQUAL((uint8_t)Demeter::CommandType::PIN_REPORT, mockComms->_txBuffer[5]); 
}

void test_sys_send_command(void) {
    mockComms->reset();
    
    Demeter::SetGpioCmd cmd = {2, true, 0};
    sys->sendCommand(10, cmd);
    
    TEST_ASSERT_GREATER_THAN(0, mockComms->_txBuffer.size());
    // Expect 0x10 (SET_GPIO)
    TEST_ASSERT_EQUAL((uint8_t)Demeter::CommandType::SET_GPIO, mockComms->_txBuffer[5]); 
}

void test_sys_initiate_handshake(void) {
    mockComms->reset();
    
    // Init Handshake with Node 10, Context=1 (BOOT)
    Demeter::AckData ctx = {0, 1}; 
    sys->initiateHandshake(10, ctx);
    
    // Should send SYN (0x04)
    TEST_ASSERT_GREATER_THAN(0, mockComms->_txBuffer.size());
    TEST_ASSERT_EQUAL((uint8_t)Demeter::CommandType::SYN, mockComms->_txBuffer[5]); 
    
    // Paylaod should contain Context (1)
}

// =============================================================================
// RUNNER
// =============================================================================

void run_system_manager_tests() {
    RUN_TEST(test_sys_send_sensor_data);
    RUN_TEST(test_sys_send_pin_status);
    RUN_TEST(test_sys_send_command);
    RUN_TEST(test_sys_initiate_handshake);
}
