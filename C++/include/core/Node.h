#pragma once

#include "core/ProtocolEngine.h"
#include "core/SystemContext.h"

/**
 * @file Node.h
 * @brief Abstract Base Node.
 */

class Node {
protected:
    uint8_t _nodeId;
    ProtocolEngine* _engine;
    SystemContext* _systemContext;

public:
    /**
     * @brief Construct a new Node object.
     * @param id The Protocol ID of this node.
     * @param engine Pointer to the Protocol Engine.
     */
    Node(uint8_t id, ProtocolEngine* engine);
    
    virtual ~Node();

    /**
     * @brief Initialize Node and SystemContext.
     * Subclasses must override to configure their specific modules.
     */
    virtual void begin();

    /**
     * @brief Update Loop.
     * Should be called in the main loop.
     */
    virtual void update();
    
    SystemContext* getSystemContext() { return _systemContext; }
};
