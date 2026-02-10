#pragma once

#include "hardware/ISensor.h"
#include <cstdint>

namespace Demeter {
    namespace Sensors {

        /**
         * @brief Driver for DS18B20 Temperature Sensor.
         * Note: Requires DallasTemperature and OneWire libraries.
         */
        class DS18B20Sensor : public ISensor {
        private:
            uint8_t _pin;
            bool _isMock;
            std::string _name;
            
            // Pointers to library objects (void* to keep header clean for Native)
            void* _oneWire;
            void* _sensors;

        public:
            DS18B20Sensor(uint8_t pin, bool isMock = false);
            ~DS18B20Sensor();

            bool init() override;
            bool read(SensorReading& outReading) override;
            std::string getName() const override;
        };

    }
}
