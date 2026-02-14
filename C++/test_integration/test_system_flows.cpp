#include <unity.h>
#include "core/SystemContext.h"
#include "communications/EspNowStrategy.h"
#include "core/GpioController.h"
#include <Arduino.h>

void test_remote_gpio_execution() {
    // 1. Setup Network (Shared Medium)
    EspNowStrategy espGw;
    EspNowStrategy espNode;
    
    // 2. Setup Gateway (Controller)
    ProtocolEngine gateway(&espGw);
    gateway.setNodeId(1);
    
    // 3. Setup Node 2 (System Under Test)
    ProtocolEngine nodeEngine(&espNode);
    nodeEngine.setNodeId(2);
    
    // SystemContext wraps the Node's Engine
    SystemContext nodeSystem(&nodeEngine);
    
    // Hardware (Mocked)
    GpioController nodeGpio;
    std::vector<uint8_t> safePins = {4};
    nodeGpio.setPins(safePins);
    nodeSystem.enableExecutor(&nodeGpio);
    
    nodeSystem.setup(); // Hooks callbacks
    
    // Ensure Pin 4 starts LOW
    digitalWrite(4, LOW);
    
    // 4. Action: Gateway sends SET_GPIO to Node 2
    // Pin 4, High
    // Pin 4, High
    Demeter::SetGpioCmd cmd;
    cmd.pin = 4;
    cmd.value = true;
    cmd.flags = 0;
    gateway.sendSetGpio(2, cmd);
    
    // 5. Simulation Step
    gateway.update(); // Puts message on "air" (EspNowStrategy shared state)
    
    // Node loop processes incoming message
    nodeSystem.loop(); 
    
    // 6. Verification
    // SystemContext should have received message via Engine -> triggered callback -> Executed on GPIO
    TEST_ASSERT_EQUAL(HIGH, digitalRead(4));
}

void test_remote_sequence_execution() {
    // 1. Setup
    EspNowStrategy espGw;
    EspNowStrategy espNode;
    
    ProtocolEngine gateway(&espGw);
    gateway.setNodeId(1);
    
    ProtocolEngine nodeEngine(&espNode);
    nodeEngine.setNodeId(2);
    
    SystemContext nodeSystem(&nodeEngine);
    GpioController nodeGpio;
    nodeGpio.setPins({5});
    nodeSystem.enableExecutor(&nodeGpio);
    nodeSystem.setup();
    
    // Mock Time
    setMockMillis(2000);
    digitalWrite(5, LOW);
    
    // 2. Define Sequence
    // Step 1: Pin 5 HIGH, Delay 100ms
    Demeter::SequenceStep step1 = {5, true, 100};
    std::vector<Demeter::SequenceStep> steps = {step1};
    
    // 3. Action
    Demeter::ExecSequenceCmd seqCmd;
    seqCmd.steps = steps;
    gateway.sendExecSequence(2, seqCmd);
    
    // 4. Simulation
    gateway.update(); // Send
    nodeSystem.loop(); // Receive & Start Sequence
    
    // Immediate Effect (Step 1 start)
    TEST_ASSERT_EQUAL(HIGH, digitalRead(5));
    
    // Wait for end? 
    // Logic just asserted start. That validates the "Flow" (Gateway -> SystemContext -> Sequencer).
    // Detailed sequencer timing is covered in Unit Tests.
}

void run_system_flows() {
    RUN_TEST(test_remote_gpio_execution);
    RUN_TEST(test_remote_sequence_execution);
}
