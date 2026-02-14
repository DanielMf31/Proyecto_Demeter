#include <unity.h>
#include "core/GpioController.h"
#include "core/PinConfig.h"
#include <Arduino.h> // Mocked
#include "test_runners.h"

// External references (Defined in test_main.cpp)
extern GpioController* gpio;

void test_rejects_protected_pins(void) {
    // Try to configure UART pins (1, 3, 16, 17) and one safe pin (4)
    std::vector<uint8_t> mingledConfig = {1, 3, 16, 17, 4}; 
    
    gpio->setPins(mingledConfig);
    gpio->init();

    // Verify:
    // 1. Safe Pin (4) should work.
    Demeter::SetGpioCmd cmdSafe = {4, true, 0};
    gpio->execute(cmdSafe);
    TEST_ASSERT_EQUAL(HIGH, digitalRead(4));

    // 2. Protected Pin (1) should NOT work (remain in default/previous state)
    // First, ensure Pin 1 is "Low" or unknown in Mock.
    digitalWrite(1, LOW); 
    
    Demeter::SetGpioCmd cmdBad = {1, true, 0}; 
    gpio->execute(cmdBad);
    
    // Should still be LOW because GpioController refused to touch it
    TEST_ASSERT_EQUAL(LOW, digitalRead(1));
}

void test_accepts_safe_pins(void) {
    std::vector<uint8_t> safeConfig = {4, 5};
    gpio->setPins(safeConfig);
    gpio->init();
    
    // Command for Pin 4 (Safe) -> High
    Demeter::SetGpioCmd cmd = {4, true, 0};
    gpio->execute(cmd);
    TEST_ASSERT_EQUAL(HIGH, digitalRead(4));
    
    // Command for Pin 4 -> Low
    cmd.value = false;
    gpio->execute(cmd);
    TEST_ASSERT_EQUAL(LOW, digitalRead(4));
}

void test_rejects_unmanaged_pins(void) {
    // Pin 12 is Safe in hardware, but NOT in our config list
    std::vector<uint8_t> config = {4};
    gpio->setPins(config);
    gpio->init();
    
    // Ensure Pin 12 is LOW
    digitalWrite(12, LOW);
    
    // Execute on Pin 12
    Demeter::SetGpioCmd cmd = {12, true, 0}; // Try to set HIGH
    gpio->execute(cmd);
    
    // Should stay LOW because it wasn't in setPins()
    TEST_ASSERT_EQUAL(LOW, digitalRead(12));
}


void run_gpio_controller_tests() {
    RUN_TEST(test_rejects_protected_pins);
    RUN_TEST(test_accepts_safe_pins);
    RUN_TEST(test_rejects_unmanaged_pins);
}
