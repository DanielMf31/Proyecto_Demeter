#pragma once

#include "core/Node.h"
#include "core/GpioController.h"

/**
 * @file Node_Actuator.h
 * @brief Concrete Node implementation for Actuators.
 */

class Node_Actuator : public Node {
private:
    GpioController* _executor;

public:
    Node_Actuator(uint8_t id, ProtocolEngine* engine);
    ~Node_Actuator();

    void begin() override;
    
    // Allow access to executor for setup
    GpioController* getExecutor() { return _executor; }
};
