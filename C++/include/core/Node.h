#pragma once

#include <vector>
#include <memory>
#include "core/ProtocolEngine.h"
#include "hardware/ISensor.h"

/**
 * @file Node.h
 * @brief Logic for a Modular Node.
 */

class Node {
protected:
    uint8_t _nodeId;
    ProtocolEngine* _engine;
    std::vector<Demeter::ISensor*> _sensors; // Pointers to sensors (managed externally or here)
    
    // Config
    bool _isSensorNode; // If true, enters deep sleep after reporting
    uint32_t _reportIntervalMs;
    unsigned long _lastReportTime;

public:
    /**
     * @brief Construct a new Node object.
     * @param id The Protocol ID of this node.
     * @param engine Pointer to the Protocol Engine.
     */
    Node(uint8_t id, ProtocolEngine* engine);

    /**
     * @brief Register a sensor to the node.
     * @param sensor Pointer to the sensor instance.
     */
    void registerSensor(Demeter::ISensor* sensor);

    /**
     * @brief Initialize Node and all registered sensors.
     */
    void begin();

    /**
     * @brief Update Loop.
     * Handles data collection and transmission.
     */
    void update();

    /**
     * @brief Configure reporting behavior.
     * @param intervalMs Time between data reports (0 = On Demand Only).
     * @param deepSleep Enable Deep Sleep between reports?
     */
    void setReportingConfig(uint32_t intervalMs, bool deepSleep);

private:
    void collectAndSend();
};
