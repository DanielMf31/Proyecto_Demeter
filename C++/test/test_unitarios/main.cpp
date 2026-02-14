#include <unity.h>
#include <Arduino.h>
#include "core/ProtocolEngine.h"
#include "core/GpioController.h"
#include "core/SystemManager.h"
#include "test_runners.h"
#include "MockComms.h"

// Global Definitions
MockComms* mockComms = nullptr;
ProtocolEngine* engine = nullptr;
GpioController* gpio = nullptr;
SystemManager* sys = nullptr;

void setUp(void) {
    // Common Setup
    mockComms = new MockComms();
    engine = new ProtocolEngine(mockComms);
    engine->setNodeId(1); 
    mockComms->reset();

    gpio = new GpioController();
    std::vector<uint8_t> safePins = {4, 5, 6};
    gpio->setPins(safePins);
    
    // SystemManager Setup
    sys = new SystemManager(engine);
    
    // Configure Context (ID=1) to match Test Expectations
    sys->getContext().setIdentity(1, Demeter::NodeRole::GATEWAY);
    
    sys->enableExecutor(gpio);
    sys->setup();
}

void tearDown(void) {
    if (sys) { delete sys; sys = nullptr; }
    if (engine) { delete engine; engine = nullptr; }
    if (mockComms) { delete mockComms; mockComms = nullptr; }
    if (gpio) { delete gpio; gpio = nullptr; }
}

int main(int argc, char **argv) {
    UNITY_BEGIN();
    
    Serial.println("Running Protocol Tests...");
    run_protocol_tests();

    Serial.println("Running GPIO Controller Tests...");
    run_gpio_controller_tests();

    Serial.println("Running System Manager Tests...");
    run_system_manager_tests();
    
    // Serial.println("Running Node Architecture Tests...");
    // run_node_architecture_tests();

    UNITY_END();
    return 0;
}
