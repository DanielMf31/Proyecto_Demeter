#pragma once

#include "hardware/ISensor.h"
#include <cstdint>

// Forward Declaration for Adafruit DHT (avoid including full header here if possible, 
// but usually needed for member object. For simplicity, we use pointer or conditional)
// #include <DHT.h> 

namespace Demeter {
    namespace Sensors {

        /**
         * @brief Implementation of a DHT Sensor (V2).
         * Supports MOCK mode for testing and REAL mode for hardware.
         */
        class DHTSensor : public ISensor {
        private:
            uint8_t _pin;
            uint8_t _type; // DHT11, DHT22
            bool _isMock;
            std::string _name;
            
            // void* to avoid hardware dependency in header if running native? 
            // Better to wrap or use Pimpl, but for embedded we usually keep it simple.
            // We'll use a void pointer cast for the real object to compile on Native.
            void* _dhtInstance; 

        public:
            /**
             * @param pin GPIO Pin
             * @param type DHT Type (11 or 22)
             * @param isMock If true, generates random data.
             */
            DHTSensor(uint8_t pin, uint8_t type, bool isMock = false);
            ~DHTSensor();

            bool init() override;
            bool read(SensorReading& outReading) override;
            std::string getName() const override;
        };

    }
}
