#include <unity.h>
#include <Arduino.h>

// Forward declarations of runner functions
void run_integration_tests(); // From test_integration.cpp (renaming main)
void run_system_flows();      // From test_system_flows.cpp (new)
void run_e2e_tests();         // From test_e2e_full_system.cpp

int main(int argc, char **argv) {
    UNITY_BEGIN();
    
    // Original Protocol Integration Tests
    run_integration_tests();
    
    // New System Level Flows
    run_system_flows();

    // E2E Full System Test
    run_e2e_tests();

    UNITY_END();
    return 0;
}
