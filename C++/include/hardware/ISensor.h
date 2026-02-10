#pragma once

#include <string>
#include <vector>
#include <cstdint>

/**
 * @file ISensor.h
 * @brief Interface for Modular Sensors.
 */

namespace Demeter {

    /**
     * @brief Generic Data Structure for Sensor Readings.
     * Union/Variant approach could be used, but for simplicity in embedded C++11/14,
     * we use a struct with optional fields or a specific payload type.
     * For Demeter V2, we usually report Temp/Hum.
     */
    struct SensorReading {
        float value1; // e.g. Temperature
        float value2; // e.g. Humidity
        bool isValid;
    };

    /**
     * @class ISensor
     * @brief Abstract Base Class for all Sensors.
     */
    class ISensor {
    public:
        virtual ~ISensor() = default;

        /**
         * @brief Initialize the sensor hardware.
         * @return true if initialization was successful.
         */
        virtual bool init() = 0;

        /**
         * @brief Read data from the sensor.
         * @param outReading Reference to store the reading.
         * @return true if a new valid reading was obtained.
         */
        virtual bool read(SensorReading& outReading) = 0;

        /**
         * @brief Get the Name of the sensor driver.
         */
        virtual std::string getName() const = 0;
    };

}
