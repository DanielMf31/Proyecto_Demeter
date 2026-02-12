#include "core/SystemContext.h"
#include <Arduino.h>

/**
 * @file SystemContext.cpp
 * @brief Workflow Orchestrator Implementation.
 */

SystemContext::SystemContext(ProtocolEngine* engine) 
    : _engine(engine), _executor(nullptr), _sensorManager(nullptr), 
      _state(SystemState::BOOT), _execMode(ExecutionMode::IMMEDIATE),
      _sequenceStepIndex(0), _lastStepTime(0), _isSequencerActive(false) {}

void SystemContext::enableExecutor(GpioController* executor) {
    _executor = executor;
}

void SystemContext::enableSensorManager(SensorManager* manager) {
    _sensorManager = manager;
}

void SystemContext::setup() {
    _state = SystemState::IDLE;
    
    if (_executor) {
        _executor->init();
    }
    
    if (_sensorManager) {
        _sensorManager->begin();
    }

    if (_engine) {
        // Register Callback
        // Captures 'this' to allow calling member function from lambda
        _engine->onSetGpio([this](const Demeter::SetGpioCmd& cmd) {
            this->handleGpioCommand(cmd);
        });

        _engine->onExecSequence([this](const Demeter::ExecSequenceCmd& cmd) {
            this->handleExecSequence(cmd);
        });
    }
}

void SystemContext::loop() {
    if (_state == SystemState::ERROR) {
        return;
    }

    if (_engine) {
        _engine->update();
    }

    // Sequencer Logic
    if (_isSequencerActive && !_activeSequence.empty() && _executor) {
        if (_sequenceStepIndex < _activeSequence.size()) {
            // Check if delay has passed
            unsigned long currentTime = millis();
            if (currentTime - _lastStepTime >= _activeSequence[_sequenceStepIndex].delayMs) {
                // Time to move to next step
                _sequenceStepIndex++;
                
                if (_sequenceStepIndex < _activeSequence.size()) {
                    // Execute Next Step
                    const auto& step = _activeSequence[_sequenceStepIndex];
                    
                    Demeter::SetGpioCmd gpioCmd;
                    gpioCmd.pin = step.pin;
                    gpioCmd.value = step.value;
                    gpioCmd.flags = 0; // Immediate
                    
                    _executor->execute(gpioCmd);
                    _lastStepTime = currentTime;
                } else {
                    // Sequence Finished
                    _isSequencerActive = false;
                }
            }
        } else {
             _isSequencerActive = false;
        }
    }
}

/**
 * @brief Internal handler for GPIO commands.
 * Decides whether to execute immediately or queue based on _execMode.
 */
void SystemContext::handleGpioCommand(const Demeter::SetGpioCmd& cmd) {
    if (_state == SystemState::ERROR) return;
    if (!_executor) return; // Ignore if no executor enabled

    if (_execMode == ExecutionMode::IMMEDIATE) {
        _state = SystemState::PROCESSING;
        _executor->execute(cmd);
        _state = SystemState::IDLE;
    } else {
        // Queue Mode
        _commandQueue.push_back(cmd);
    }
}

void SystemContext::setExecutionMode(ExecutionMode mode) {
    _execMode = mode;
    if (mode == ExecutionMode::IMMEDIATE) {
        // If switching back to immediate, clear queue to avoid surprises.
        _commandQueue.clear();
    }
}

void SystemContext::executeQueue() {
    if (_commandQueue.empty()) return;
    if (!_executor) return;

    _state = SystemState::PROCESSING;
    for (const auto& cmd : _commandQueue) {
        _executor->execute(cmd);
        // Potential delay could be added here if needed
    }
    _commandQueue.clear();
    _state = SystemState::IDLE;
}

void SystemContext::clearQueue() {
    _commandQueue.clear();
}

void SystemContext::injectCommand(const Demeter::SetGpioCmd& cmd) {
    handleGpioCommand(cmd);
}

void SystemContext::handleExecSequence(const Demeter::ExecSequenceCmd& cmd) {
    if (_state == SystemState::ERROR) return;
    if (!_executor) return;

    // Load new sequence
    _activeSequence = cmd.steps;
    
    if (_activeSequence.empty()) {
        _isSequencerActive = false;
        return;
    }

    // Start immediately
    _isSequencerActive = true;
    _sequenceStepIndex = 0;
    
    // Execute First Step Immediately
    const auto& step = _activeSequence[0];
    Demeter::SetGpioCmd gpioCmd;
    gpioCmd.pin = step.pin;
    gpioCmd.value = step.value;
    gpioCmd.flags = 0;
    
    _executor->execute(gpioCmd);
    _lastStepTime = millis();
}
