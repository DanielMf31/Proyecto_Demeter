#pragma once

#include "IComms.h"

// If running natively (Unit Tests), we Mock Arduino.h
// If running on ESP32 (PlatformIO env:esp32), we use real Arduino.h
#ifdef ARDUINO
    #include <Arduino.h>
#else
    #include <iostream>
    #include <string>
    // Native Mock for HardwareSerial type
    class HardwareSerial {
    public:
        void begin(unsigned long baud) {}
        size_t write(const uint8_t *buffer, size_t size) { return size; }
        int available() { return 0; }
        int read() { return -1; }
    };
    // Mock Serial for instantiation
    extern HardwareSerial Serial; 
#endif

class UartStrategy : public IComms {
private:
    HardwareSerial* _serial;
    uint32_t _baudRate;

public:
    /**
     * @brief Construct a new Uart Strategy object
     * 
     * @param serial Pointer to HardwareSerial (e.g. &Serial)
     * @param baudRate Baud rate (e.g. 115200)
     */
    UartStrategy(HardwareSerial* serial, uint32_t baudRate);

    void begin() override;
    void send(const uint8_t* data, size_t length) override;
    bool available() override;
    std::vector<uint8_t> read() override;
};
