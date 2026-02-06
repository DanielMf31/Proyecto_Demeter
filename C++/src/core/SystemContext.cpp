#include "core/SystemContext.h"

// Helper for Lambda
// We need to capture 'this' to call member functions from callback
SystemContext::SystemContext(ProtocolEngine& engine, GpioController& executor) 
    : _engine(engine), _executor(executor), _state(SystemState::BOOT) {}

void SystemContext::setup() {
    _state = SystemState::IDLE;
    _executor.init();

    // Register Callback
    // Lambda captures 'this' to call private method
    _engine.onSetGpio([this](const Demeter::SetGpioCmd& cmd) {
        this->handleGpioCommand(cmd);
    });
}

void SystemContext::loop() {
    // 1. Process Logic based on State
    if (_state == SystemState::ERROR) {
        // Blink red led?
        return;
    }

    // 2. Update Engine (Read Uart)
    _engine.update();
}

void SystemContext::handleGpioCommand(const Demeter::SetGpioCmd& cmd) {
    if (_state == SystemState::ERROR) return;

    _state = SystemState::PROCESSING;
    
    // Delegate to Executor
    _executor.execute(cmd);
    
    _state = SystemState::IDLE;
}
