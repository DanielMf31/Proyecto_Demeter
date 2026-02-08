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

/**
 * @brief Main logic class for the Firmware.
 *
 * Implements a centralized workflow controller that bridges:
 * - Protocol Engine (Input/Output)
 * - GPIO Controller (Hardware Action)
 * - State Machine (State Management)
 */
class SystemContext {
private:
    ProtocolEngine& _engine;
    GpioController& _executor;
    SystemState _state;
    ExecutionMode _execMode;

    // Command Queue for Interactive Mode
    std::vector<Demeter::SetGpioCmd> _commandQueue;

    // Sequencer State
    std::vector<Demeter::SequenceStep> _activeSequence;
    size_t _sequenceStepIndex;
    unsigned long _lastStepTime;
    bool _isSequencerActive;

    // Internal Callback
    void handleGpioCommand(const Demeter::SetGpioCmd& cmd);

public:
    /**
     * @brief Construct a new System Context.
     * @param engine Reference to Protocol Engine.
     * @param executor Reference to GPIO Controller.
     */
    SystemContext(ProtocolEngine& engine, GpioController& executor);

    /**
     * @brief Initialize the system components.
     * Sets up callbacks and initializes hardware.
     */
    void setup();

    /**
     * @brief Main System Loop.
     * Should be called in `loop()`. Handles protocol updates.
     */
    void loop();

    /**
     * @brief Configure the execution mode (Immediate vs Queued).
     * @param mode Desired mode.
     */
    void setExecutionMode(ExecutionMode mode);

    /**
     * @brief Trigger execution of all queued commands.
     * Used in INTERACTIVE_QUEUE mode.
     */
    void executeQueue();

    /**
     * @brief Clear pending commands in the queue.
     */
    void clearQueue();
    
    // Public Handler for Protocol
    /**
     * @brief Handle EXEC_SEQUENCE command.
     * Loads the sequence into the active buffer and starts execution.
     * @param cmd Command containing the list of steps.
     */
    void handleExecSequence(const Demeter::ExecSequenceCmd& cmd);
    
    // Manual Command Injection
    /**
     * @brief Inject a command manually (bypass parsing).
     * Useful from `main_receptor.cpp` Serial Menu.
     */
    void injectCommand(const Demeter::SetGpioCmd& cmd);

    SystemState getState() const { return _state; }
    size_t getQueueSize() const { return _commandQueue.size(); }
};
