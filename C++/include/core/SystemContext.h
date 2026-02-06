#pragma once

#include "core/ProtocolEngine.h"
#include "core/GpioController.h"

// System States
enum class SystemState {
    BOOT,
    IDLE,
    PROCESSING,
    ERROR
};

class SystemContext {
private:
    ProtocolEngine& _engine;
    GpioController& _executor;
    SystemState _state;

    // Internal Callback
    void handleGpioCommand(const Demeter::SetGpioCmd& cmd);

public:
    SystemContext(ProtocolEngine& engine, GpioController& executor);

    void setup();
    void loop();

    SystemState getState() const { return _state; }
};
