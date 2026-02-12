#include <unity.h>
#include <vector>
#include <cstring>
#include "core/ProtocolEngine.h"
#include "communications/IComms.h"
#include <Arduino.h> // Mock - Include LAST to avoid macro conflicts

// Mock Strategy
class MockComms : public IComms {
public:
    std::vector<uint8_t> _rxBuffer;
    std::vector<uint8_t> _txBuffer;
    
    void begin() override {}
    void send(const uint8_t* data, size_t length) override {
        _txBuffer.insert(_txBuffer.end(), data, data + length);
    }
    bool available() override { return !_rxBuffer.empty(); }
    
    std::vector<uint8_t> read() override {
        std::vector<uint8_t> temp = _rxBuffer;
        _rxBuffer.clear();
        return temp;
    }

    // Helper to push data to "Rx"
    void pushData(const std::vector<uint8_t>& data) {
        _rxBuffer.insert(_rxBuffer.end(), data.begin(), data.end());
    }
};

MockComms* mockComms;
ProtocolEngine* engine;

void setUp(void) {
    mockComms = new MockComms();
    engine = new ProtocolEngine(mockComms);
}

void tearDown(void) {
    delete engine;
    delete mockComms;
}

void test_parse_gpio_command(void) {
    bool callbackCalled = false;
    Demeter::SetGpioCmd receivedCmd;

    engine->onSetGpio([&](const Demeter::SetGpioCmd& cmd) {
        callbackCalled = true;
        receivedCmd = cmd;
    });

    // Frame: Sync(FE) Len(03) Flags(00) Src(0A) Dst(01) Cmd(10) [04 01 00] CRC(??)
    // Payload: Pin 4, Val 1, Flags 0
    // CRC: 03+00+0A+01+10 + 04+01+00 = 35 (0x23)
    // CRC Calculation:
    // Header (Excl Sync): 03+00+0A+01+10 = 1E (30)
    // Payload: 04+01+00 = 05
    // Total: 35 (0x23)
    // Wait... CRC is MOD 256 sum of ALL bytes starting from LEN?
    // Let's check ProtocolEngine implementation.
    // implementation: for (size_t i = 0; i < len; i++) sum += data[i];
    // frame.data() points to start of frame (SYNC). 
    // ProtocolEngine::parseFrame:
    // uint8_t calcCRC = calculateCRC(dataStart, dataLen);
    // dataStart is &frame[1] (LEN). dataLen is (HeaderSize-1) + PayloadSize.
    // HeaderSize is 6. So Header bytes [LEN, FLAGS, SRC, DST, CMD].
    // Payload bytes ...
    
    // Correct CRC construction for test:
    // LEN=03, FLAGS=00, SRC=0A, DST=01, CMD=10 -> Sum=1E
    // Pay=04, 01, 00 -> Sum=05
    // Total=23 (0x23)
    // This matches. 
    // Why did it fail? 
    // Maybe `engine` needs `setNodeId(1)` to accept frames for DST=1?
    // ProtocolEngine ctor doesn't set ID. Default might be 0? 
    // Let's set ID.
    engine->setNodeId(1);
    
    std::vector<uint8_t> frame = {0xFE, 0x03, 0x00, 0x0A, 0x01, 0x10, 0x04, 0x01, 0x00, 0x23};
    
    mockComms->pushData(frame);
    engine->update();

    TEST_ASSERT_TRUE(callbackCalled);
    // TEST_ASSERT_EQUAL(HIGH, digitalRead(4)); // REMOVED: ProtocolEngine does not write to GPIO directly.
    TEST_ASSERT_EQUAL(HIGH, receivedCmd.value);
}

void test_parse_pwm_command(void) {
    bool callbackCalled = false;
    Demeter::SetPwmCmd receivedCmd;

    engine->onSetPwm([&](const Demeter::SetPwmCmd& cmd) {
        callbackCalled = true;
        receivedCmd = cmd;
    });

    // Frame: Sync(FE) Len(03) ... Cmd(11) [05 E8 03] CRC(??)
    // Payload: Pin 5, Value 1000 (0x03E8) -> Low: E8, High: 03
    // Header Sum (excluding Sync): 03+00+0A+01+11 = 1F (31)
    // Payload Sum: 05 + E8 + 03 = F0 (240)
    // Total Sum: 31 + 240 = 271 -> CRC = 271 % 256 = 15 (0x0F)
    std::vector<uint8_t> frame = {0xFE, 0x03, 0x00, 0x0A, 0x01, 0x11, 0x05, 0xE8, 0x03, 0x0F};
    
    mockComms->pushData(frame);
    engine->update();

    TEST_ASSERT_TRUE(callbackCalled);
    TEST_ASSERT_EQUAL(5, receivedCmd.pin);
    TEST_ASSERT_EQUAL(1000, receivedCmd.value);
}

void test_bad_crc_ignored(void) {
    bool callbackCalled = false;
    engine->onSetGpio([&](const Demeter::SetGpioCmd& cmd) { callbackCalled = true; });

    // Same GPIO frame but BAD CRC (0xFF instead of 0x13)
    std::vector<uint8_t> frame = {0xFE, 0x03, 0x00, 0x0A, 0x01, 0x10, 0x04, 0x01, 0x00, 0xFF};
    
    mockComms->pushData(frame);
    engine->update();

    TEST_ASSERT_FALSE(callbackCalled);
}

void test_ping_triggers_ack(void) {
    // Frame: Sync(FE) Len(00) Flags(00) Src(0A) Dst(01) Cmd(01 PING) ... CRC
    // CRC: 00+00+0A+01+01 = 0C (12)
    std::vector<uint8_t> frame = {0xFE, 0x00, 0x00, 0x0A, 0x01, 0x01, 0x0C};
    
    mockComms->pushData(frame);
    mockComms->_txBuffer.clear(); // Clear before update
    engine->update();

    // Verify ACK sent
    // ACK Frame: [FE][00][00][01][0A][02 ACK][CRC]
    // CRC: 00+00+01+0A+02 = 0D (13)
    
    // ProtocolEngine::sendFrame adds +1 for null terminator or vector sizing? 
    // Frame size: 7 bytes.
    // If using vector, size is exact.
    TEST_ASSERT_EQUAL(7, mockComms->_txBuffer.size());
    if (mockComms->_txBuffer.size() >= 7) {
        TEST_ASSERT_EQUAL(0xFE, mockComms->_txBuffer[0]); // Sync
        TEST_ASSERT_EQUAL(0x02, mockComms->_txBuffer[5]); // CMD ACK
        TEST_ASSERT_EQUAL(0x0A, mockComms->_txBuffer[4]); // DST (Source of PING)
        TEST_ASSERT_EQUAL(0x0D, mockComms->_txBuffer[6]); // CRC
    }
}

int main(int argc, char **argv) {
    UNITY_BEGIN();
    RUN_TEST(test_parse_gpio_command);
    RUN_TEST(test_parse_pwm_command);
    RUN_TEST(test_bad_crc_ignored);
    RUN_TEST(test_ping_triggers_ack);
    UNITY_END();
    return 0;
}
