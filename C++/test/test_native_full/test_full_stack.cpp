#include <unity.h>
#include <vector>
#include <iostream>
#include "communications/IComms.h"
#include "core/ProtocolEngine.h"
#include "core/GpioController.h"

// 1. Mock Strategy for Injection
class MockStrategy : public IComms {
public:
    std::vector<uint8_t> _rxBuffer;
    
    void begin() override {}
    void send(const uint8_t* data, size_t length) override {}
    bool available() override { return !_rxBuffer.empty(); }
    
    std::vector<uint8_t> read() override {
        std::vector<uint8_t> ret = _rxBuffer;
        _rxBuffer.clear(); // Consume
        return ret;
    }
    
    // Test Helper
    void injectFrame(const std::vector<uint8_t>& frame) {
        _rxBuffer = frame;
    }
};

// 2. Global instances
MockStrategy* mockRadio;
ProtocolEngine* engine;
GpioController* gpio;
Demeter::SetGpioCmd lastCmd;
bool cmdReceived = false;

void setUp(void) {
    mockRadio = new MockStrategy();
    engine = new ProtocolEngine(mockRadio);
    gpio = new GpioController();
    cmdReceived = false;

    // Link Engine to Controller via Lambda
    engine->onSetGpio([](const Demeter::SetGpioCmd& cmd) {
        lastCmd = cmd;
        cmdReceived = true;
        gpio->execute(cmd); // Actually run controller logic
    });
    
    engine->setNodeId(0x0A); // Match DST in test frame
}

void tearDown(void) {
    delete mockRadio;
    delete engine;
    delete gpio;
}

void test_full_flow_set_gpio(void) {
    // Construct Valid Frame: SYNC(FE) LEN(3) FLAGS(1) SRC(0) DST(10) CMD(10) [04 01 00] CRC
    // CRC = Sum(01 00 10 10 04 01 00) % 256
    //       1 + 16 + 16 + 4 + 1 = 38 (0x26)
    // Msg Body: 01 00 10 10 04 01 00
    
    // Header(6) + Payload(3) + CRC(1) = 10 bytes
    // Frame: FE 03 01 00 0A 10 04 01 00 [CRC]
    
    // Manual CRC Calc:
    // Header Data: 03 01 00 0A 10
    // Payload: 04 01 00
    // Sum: 3+1+0+10+16 + 4+1+0 = 35 (0x23)
    
    std::vector<uint8_t> frame = {
        0xFE,       // Sync
        0x03,       // Len
        0x01, 0x00, 0x0A, 0x10, // Flags, Src, Dst, Cmd(SET_GPIO)
        0x04, 0x01, 0x00,       // Pin 4, High, Flags
        0x23        // CRC (Calculated manually: 35)
    };

    mockRadio->injectFrame(frame);
    engine->update(); // Should read mock, parse, and trigger callback

    TEST_ASSERT_TRUE_MESSAGE(cmdReceived, "Callback should be triggered");
    TEST_ASSERT_EQUAL(4, lastCmd.pin);
    TEST_ASSERT_TRUE(lastCmd.value);
}

void test_crc_failure_drops_frame(void) {
    std::vector<uint8_t> frame = {
        0xFE, 0x03, 0x01, 0x00, 0x0A, 0x10, 
        0x04, 0x01, 0x00, 
        0x99 // BAD CRC
    };

    mockRadio->injectFrame(frame);
    engine->update();

    TEST_ASSERT_FALSE_MESSAGE(cmdReceived, "Bad CRC should NOT trigger callback");
}

int main(int argc, char **argv) {
    UNITY_BEGIN();
    RUN_TEST(test_full_flow_set_gpio);
    RUN_TEST(test_crc_failure_drops_frame);
    UNITY_END();
    return 0;
}
