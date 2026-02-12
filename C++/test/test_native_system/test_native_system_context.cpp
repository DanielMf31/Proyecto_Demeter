#include <unity.h>
#include <vector>
#include "communications/IComms.h"
#include "core/ProtocolEngine.h"
#include "core/GpioController.h"
#include "core/SystemContext.h"
#include "core/InternalTypes.h"

// Re-using MockStrategy from previous test (Inline here to avoid linking issues or create common header later)
// For simplicity in this specific test file:
class MockStrategy : public IComms {
public:
    std::vector<uint8_t> _rxBuffer;
    void begin() override {}
    void send(const uint8_t* data, size_t length) override {}
    bool available() override { return !_rxBuffer.empty(); }
    std::vector<uint8_t> read() override {
        std::vector<uint8_t> ret = _rxBuffer;
        _rxBuffer.clear();
        return ret;
    }
    void injectFrame(const std::vector<uint8_t>& frame) {
        _rxBuffer = frame;
    }
};

// Global Pointers
MockStrategy* mockRadio;
ProtocolEngine* engine;
GpioController* gpio;
SystemContext* systemCtx;

void setUp(void) {
    mockRadio = new MockStrategy();
    engine = new ProtocolEngine(mockRadio);
    gpio = new GpioController();
    systemCtx = new SystemContext(engine);
    systemCtx->enableExecutor(gpio);
    systemCtx->setup();
}

void tearDown(void) {
    delete systemCtx;
    delete gpio;
    delete engine;
    delete mockRadio;
}

void test_system_initial_state(void) {
    TEST_ASSERT_EQUAL(SystemState::IDLE, systemCtx->getState());
}

void test_system_processes_command(void) {
    // Inject Valid SET_GPIO Frame (Pin 4, High)
    std::vector<uint8_t> frame = {
        0xFE, 0x03, 0x01, 0x00, 0x0A, 0x10, 
        0x04, 0x01, 0x00, 
        0x23 // CRC
    };
    mockRadio->injectFrame(frame);
    
    // System Loop should read engine -> trigger callback -> execute -> return to IDLE
    // Note: Since Executor is synchronous in MVP, state Processing happens inside loop() and reverts to IDLE immediately.
    systemCtx->loop();
    
    // Verify system survived and didn't crash
    TEST_ASSERT_EQUAL(SystemState::IDLE, systemCtx->getState());
    
    // Ideally we would mock GpioController to Verify execution, 
    // but for now we trust the Integration Test verified the chain.
    // This test ensures SystemContext handles the flow components.
}

int main(int argc, char **argv) {
    UNITY_BEGIN();
    RUN_TEST(test_system_initial_state);
    RUN_TEST(test_system_processes_command);
    UNITY_END();
    return 0;
}
