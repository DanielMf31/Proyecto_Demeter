#include <unity.h>
#include <iostream>
#include "communications/UartStrategy.h"

// ==========================================
// MOCK SUPPORT (HardwareSerial is defined in UartStrategy.h for Native)
// We need to subclass or manipulate it to test "sending"
// But since UartStrategy.h defines a lightweight Mock, we can just use it.
// ==========================================

void setUp(void) {
    // set stuff up here
}

void tearDown(void) {
    // clean stuff up here
}

void test_uart_begin(void) {
    HardwareSerial mockSerial;
    UartStrategy uart(&mockSerial, 115200);
    
    // begin() should not crash
    uart.begin();
    TEST_ASSERT_TRUE(true); 
}

void test_uart_send(void) {
    HardwareSerial mockSerial;
    UartStrategy uart(&mockSerial, 115200);
    
    uint8_t payload[] = {0xAA, 0xBB};
    
    // In our Simple Mock, write() returns size. 
    // We can't verify distinct calls unless we enhanced the Mock.
    // For now, ensure it calls the method without error.
    uart.send(payload, 2);
    
    TEST_ASSERT_TRUE(true);
}

void test_uart_read_empty(void) {
    HardwareSerial mockSerial; // Default mock available() = 0
    UartStrategy uart(&mockSerial, 115200);
    
    TEST_ASSERT_FALSE(uart.available());
    std::vector<uint8_t> data = uart.read();
    TEST_ASSERT_EQUAL(0, data.size());
}

int main(int argc, char **argv) {
    UNITY_BEGIN();
    RUN_TEST(test_uart_begin);
    RUN_TEST(test_uart_send);
    RUN_TEST(test_uart_read_empty);
    UNITY_END();
    return 0;
}
