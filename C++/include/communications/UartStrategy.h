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

/**
 * @brief UART Communication Implementation.
 * 
 * Concrete implementation of IComms for Serial Communication (UART).
 * Supports both HardwareSerial (ESP32) and Mock Serial (Native Tests).
 */
class UartStrategy : public IComms {
private:
    HardwareSerial* _serial; ///< Pointer to the underlying Serial interface.
    uint32_t _baudRate;      ///< Communication speed (bps).

public:
    /**
     * @brief Construct a new Uart Strategy object.
     * 
     * @param serial Pointer to HardwareSerial instance (e.g. &Serial).
     * @param baudRate Baud rate for communication (e.g. 115200).
     * @param rxPin RX Pin number (optional, -1 to use default).
     * @param txPin TX Pin number (optional, -1 to use default).
     */
    UartStrategy(HardwareSerial* serial, uint32_t baudRate, int8_t rxPin = -1, int8_t txPin = -1);

    /**
     * @brief Initialize the UART Interface.
     * Configures the Serial port with the parameters provided in constructor.
     */
    void begin() override;

    /**
     * @brief Send raw bytes via UART.
     * @param data Pointer to the buffer.
     * @param length Number of bytes to write.
     */
    void send(const uint8_t* data, size_t length) override;

    /**
     * @brief Check if data is available in the RX buffer.
     * @return true if > 0 bytes are available.
     */
    bool available() override;

    /**
     * @brief Read all available bytes from UART.
     * @return std::vector<uint8_t> containing received data.
     */
    std::vector<uint8_t> read() override;

private:
    int8_t _rxPin; ///< Configured RX Pin.
    int8_t _txPin; ///< Configured TX Pin.
};
