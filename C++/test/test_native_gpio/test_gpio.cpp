#include <unity.h>
#include "core/GpioController.h"

GpioController* controller;

void setUp(void) {
    controller = new GpioController();
    // Clear mock state (optional, if we exposed a clear method, 
    // but creating a new controller doesn't clear the static map.
    // We should rely on setting known states or adding a clearMock helper.
    // For MVP, just specific tests.
}

void tearDown(void) {
    delete controller;
}

void test_init_sets_pins_low(void) {
    controller->init();
    TEST_ASSERT_EQUAL(0, digitalRead(4));
    TEST_ASSERT_EQUAL(0, digitalRead(5));
    TEST_ASSERT_EQUAL(0, digitalRead(6));
    TEST_ASSERT_EQUAL(0, digitalRead(7));
}

void test_execute_valid_pin_on(void) {
    Demeter::SetGpioCmd cmd;
    cmd.pin = 4;
    cmd.value = true;
    cmd.flags = 0;

    controller->execute(cmd);
    TEST_ASSERT_EQUAL(1, digitalRead(4));
}

void test_execute_valid_pin_off(void) {
    // First set ON
    Demeter::SetGpioCmd cmdOn;
    cmdOn.pin = 5;
    cmdOn.value = true;
    controller->execute(cmdOn);
    TEST_ASSERT_EQUAL(1, digitalRead(5));

    // Then set OFF
    Demeter::SetGpioCmd cmdOff;
    cmdOff.pin = 5;
    cmdOff.value = false;
    controller->execute(cmdOff);
    TEST_ASSERT_EQUAL(0, digitalRead(5));
}

void test_ignore_invalid_pins(void) {
    Demeter::SetGpioCmd cmd;
    cmd.pin = 2; // Invalid (Range is 4-7)
    cmd.value = true;

    // Ensure it's 0 before
    // (Note: std::map defaults to 0 if not found, but we want to ensure write didn't happen)
    // Actually our mock writes to map. If we check size or if key exists...
    // But getMockPinState returns value.
    // Best way: Pre-set to 0, execute, check 0.
    
    controller->execute(cmd);
    TEST_ASSERT_EQUAL(0, digitalRead(2));
}

int main(int argc, char **argv) {
    UNITY_BEGIN();
    RUN_TEST(test_init_sets_pins_low);
    RUN_TEST(test_execute_valid_pin_on);
    RUN_TEST(test_execute_valid_pin_off);
    RUN_TEST(test_ignore_invalid_pins);
    UNITY_END();
    return 0;
}
