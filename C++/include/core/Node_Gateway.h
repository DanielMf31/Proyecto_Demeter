#pragma once

#include "core/Node.h"
#include "core/GpioController.h"
#include "core/SensorManager.h"

class Node_Gateway : public Node {
private:
    GpioController* _executor;
    SensorManager* _sensorManager;

public:
    Node_Gateway(uint8_t id, ProtocolEngine* engine);
    ~Node_Gateway();

    void begin() override;
    void update() override;

    // Accessors for hybrid capabilities
    GpioController* getExecutor() { return _executor; }
    SensorManager* getSensorManager() { return _sensorManager; }
};
