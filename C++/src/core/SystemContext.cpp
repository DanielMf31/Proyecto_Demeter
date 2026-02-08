#include "core/SystemContext.h"
#ifdef ARDUINO
#include <Arduino.h>
#endif

// Helper for Lambda
SystemContext::SystemContext(ProtocolEngine& engine, GpioController& executor) 
    : _engine(engine), _executor(executor), _state(SystemState::BOOT), _execMode(ExecutionMode::IMMEDIATE) {}

void SystemContext::setup() {
    _state = SystemState::IDLE;
    _executor.init();

    // Register Callback
    _engine.onSetGpio([this](const Demeter::SetGpioCmd& cmd) {
        this->handleGpioCommand(cmd);
    });
}

void SystemContext::loop() {
    if (_state == SystemState::ERROR) {
        return;
    }

    _engine.update();
}

void SystemContext::handleGpioCommand(const Demeter::SetGpioCmd& cmd) {
    if (_state == SystemState::ERROR) return;

    if (_execMode == ExecutionMode::IMMEDIATE) {
        _state = SystemState::PROCESSING;
        _executor.execute(cmd);
        _state = SystemState::IDLE;
    } else {
        // Queue Mode
        _commandQueue.push_back(cmd);
        // Maybe blink an LED to indicate reception?
    }
}

void SystemContext::setExecutionMode(ExecutionMode mode) {
    _execMode = mode;
    if (mode == ExecutionMode::IMMEDIATE) {
        // If switching back to immediate, maybe clear queue or execute?
        // Let's clear to avoid surprises.
        _commandQueue.clear();
    }
}

void SystemContext::executeQueue() {
    if (_commandQueue.empty()) return;

    _state = SystemState::PROCESSING;
    for (const auto& cmd : _commandQueue) {
        _executor.execute(cmd);
        // Small delay between batched commands?
        // Keeping it fast for now.
    }
    _commandQueue.clear();
    _state = SystemState::IDLE;
}

void SystemContext::clearQueue() {
    _commandQueue.clear();
}
