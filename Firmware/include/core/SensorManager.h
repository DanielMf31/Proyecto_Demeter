#pragma once

#include "hardware/ISensor.h"
#include <vector>
#include <memory>

/**
 * @file SensorManager.h
 * @brief Manages a collection of sensors.
 */
class SensorManager {
private:
    std::vector<Demeter::ISensor*> _sensors;

public:
    SensorManager();

    /**
     * @brief Add a sensor to the manager.
     * @param sensor Pointer to the sensor instance.
     */
    void addSensor(Demeter::ISensor* sensor);

    /**
     * @brief Initialize all registered sensors.
     */
    void begin();

    /**
     * @brief Read all sensors.
     * @return A vector of valid readings.
     */
    std::vector<Demeter::SensorReading> readAll();

    /**
     * @brief Get the list of sensors.
     */
    const std::vector<Demeter::ISensor*>& getSensors() const;
};
