#pragma once

#include <stdint.h>

/**
 * @file INode.h
 * @brief Interface for all Nodes (Sensor, Actuator, Gateway).
 * forces explicit implementation of logic in subclasses.
 */
class INode {
public:
    virtual ~INode() = default;

    /**
     * @brief Initialize the Node and its specific dependencies.
     */
    virtual void begin() = 0;

    /**
     * @brief Main Update Loop.
     * Should be called in the Arduino loop().
     */
    virtual void update() = 0;
};
