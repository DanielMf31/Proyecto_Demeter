#pragma once

#include "core/ProtocolEngine.h"
#include "core/GpioController.h"
#include "core/InternalTypes.h"
#include <vector>

// System States
enum class SystemState {
    BOOT,
    IDLE,
    PROCESSING,
    ERROR
};

// Execution Mode
enum class ExecutionMode {
    IMMEDIATE, // Execute as soon as received (Default)
    INTERACTIVE_QUEUE // Queue commands, execute on trigger
};

class SystemContext {
private:
    ProtocolEngine& _engine;
    GpioController& _executor;
    SystemState _state;
    ExecutionMode _execMode;

    // Command Queue for Interactive Mode
    std::vector<Demeter::SetGpioCmd> _commandQueue;

    // Internal Callback
    void handleGpioCommand(const Demeter::SetGpioCmd& cmd);

public:
    SystemContext(ProtocolEngine& engine, GpioController& executor);

    void setup();
    void loop();

    void setExecutionMode(ExecutionMode mode);
    void executeQueue(); // Trigger execution of queued commands
    void clearQueue();
    
    // Manual Command Injection
    void injectCommand(const Demeter::SetGpioCmd& cmd);

    SystemState getState() const { return _state; }
    size_t getQueueSize() const { return _commandQueue.size(); }
};
