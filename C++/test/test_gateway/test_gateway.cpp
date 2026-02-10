#include <unity.h>
#include <vector>
#include <cstring>

#include "communications/GatewayStrategy.h"
#include "../mocks/MockComms.h"

// Test Fixtures
MockComms* mockUart;
MockComms* mockEspNow;
GatewayStrategy* gateway;

void setUp(void) {
    mockUart = new MockComms();
    mockEspNow = new MockComms();
    gateway = new GatewayStrategy(mockUart, mockEspNow);
}

void tearDown(void) {
    delete gateway;
    delete mockUart;
    delete mockEspNow;
}

void test_gateway_routing_to_uart() {
    // Frame destined for ID 0 (Host)
    // [SYNC] [LEN] [FLAGS] [SRC] [DST] ...
    uint8_t frame[] = {0xFE, 5, 0x00, 0x02, 0x00, 0x0B}; // From 2 To 0

    gateway->send(frame, sizeof(frame));

    // Should be sent via UART
    TEST_ASSERT_TRUE(mockUart->sendCalled);
    TEST_ASSERT_FALSE(mockEspNow->sendCalled);
    
    // Verify Content
    TEST_ASSERT_EQUAL_INT(sizeof(frame), mockUart->lastSentData.size());
    TEST_ASSERT_EQUAL_HEX8(0x00, mockUart->lastSentData[4]); // DST
}

void test_gateway_routing_to_node() {
    // Frame destined for ID 2 (Node)
    uint8_t frame[] = {0xFE, 5, 0x00, 0x00, 0x02, 0x0A}; // From 0 To 2

    gateway->send(frame, sizeof(frame));

    // Should be sent via ESP-Now
    TEST_ASSERT_FALSE(mockUart->sendCalled);
    TEST_ASSERT_TRUE(mockEspNow->sendCalled);
    TEST_ASSERT_EQUAL_HEX8(0x02, mockEspNow->lastSentData[4]); // DST
}

void test_gateway_read_priority() {
    // Simulate data on both interfaces
    uint8_t uartData[] = {0xAA};
    uint8_t espData[] = {0xBB};

    mockUart->pushRx(std::vector<uint8_t>(uartData, uartData+1));
    mockEspNow->pushRx(std::vector<uint8_t>(espData, espData+1));

    TEST_ASSERT_TRUE(gateway->available());

    // First read should be UART (Priority)
    std::vector<uint8_t> read1 = gateway->read();
    TEST_ASSERT_EQUAL_HEX8(0xAA, read1[0]);

    // Second read should be ESP-Now
    TEST_ASSERT_TRUE(gateway->available());
    std::vector<uint8_t> read2 = gateway->read();
    TEST_ASSERT_EQUAL_HEX8(0xBB, read2[0]);

    // Empty
    TEST_ASSERT_FALSE(gateway->available());
}

int main(int argc, char **argv) {
    UNITY_BEGIN();
    RUN_TEST(test_gateway_routing_to_uart);
    RUN_TEST(test_gateway_routing_to_node);
    RUN_TEST(test_gateway_read_priority);
    UNITY_END();
    return 0;
}
