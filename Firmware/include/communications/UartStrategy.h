#pragma once

#include "communications/IComms.h"
#include <vector>

// If running natively (Unit Tests), we Mock Arduino.h
// If running on ESP32 (PlatformIO env:esp32), we use real Arduino.h
#ifdef NATIVE_ENV
#include <Arduino.h> // Mock
#else
#include <Arduino.h>
#endif

/**
 * @class UartStrategy
 * @brief Implementación Concreta de Comunicación Serie (UART).
 * 
 * Puentea la interfaz `IComms` a la clase nativa `HardwareSerial` del framework Arduino.
 * Soporta Mocking si se des-comenta el macro NATIVE_ENV para tests en Linux.
 * 
 * @par Ejemplo de uso:
 * @code
 * // Instanciar sobre UART2 en ESP32
 * UartStrategy uart2(&Serial2, 115200, 16, 17);
 * uart2.begin();
 * 
 * if (uart2.available()) {
 *     auto frame = uart2.read();
 * }
 * @endcode
 */
class UartStrategy : public IComms {
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
    virtual ~UartStrategy();

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
     * @brief Comprueba si el Buffer FIFO del HW tiene bytes.
     * @return true si `_serial->available() > 0`.
     */
    bool available() override;

    /**
     * @brief Drena completamente el Buffer Serial RX disponible instantáneamente.
     * @return `std::vector<uint8_t>` Vector temporal dinámico con el contenido crudo.
     */
    std::vector<uint8_t> read() override;
    
    // UartStrategy ignores RouteAdd
    void registerRoute(uint8_t id, const std::array<uint8_t, 6>& mac) override {}

private:
    HardwareSerial* _serial; ///< Pointer to the underlying Serial interface.
    uint32_t _baudRate;      ///< Communication speed (bps).
    int8_t _rxPin; ///< Configured RX Pin.
    int8_t _txPin; ///< Configured TX Pin.
};
