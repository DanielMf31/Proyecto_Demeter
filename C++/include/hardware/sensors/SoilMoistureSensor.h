#pragma once

#include "hardware/ISensor.h"
#include <cstdint>

namespace Demeter {
    namespace Sensors {

        /**
         * @brief Driver for Analog Capacitive Soil Moisture Sensor (v1.2).
         */
        class SoilMoistureSensor : public ISensor {
        private:
            uint8_t _pin;
            bool _isMock;
            std::string _name;
            
            // Calibration values
            int _airValue;   // ADC value in air (0% humidity)
            int _waterValue; // ADC value in water (100% humidity)

        public:
            SoilMoistureSensor(uint8_t pin, int airVal = 3000, int waterVal = 1000, bool isMock = false);

            bool init() override;
            bool read(SensorReading& outReading) override;
            std::string getName() const override;
        };

    }
}
