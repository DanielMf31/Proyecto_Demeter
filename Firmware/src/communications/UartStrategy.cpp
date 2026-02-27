#include "communications/UartStrategy.h"

/**
 * @file UartStrategy.cpp
 * @brief Implementación de la Estrategia de Comunicación Serie/UART.
 * 
 * ============================================================================
 * DECISIONES DE ARQUITECTURA Y DISEÑO
 * ============================================================================
 * 1. **Punteros a Interfaces Nativas Arduino:** Recibe `HardwareSerial*`. 
 *    Esto permite que la aplicación inyecte `&Serial` (para debug por USB)
 *    o `&Serial2` (para comunicarse con una Pi por los pines paralelos TX/RX),
 *    sin cambiar esta clase.
 * 2. **Buffer de Drenaje Iterativo:** `read()` ejecuta un bucle `while-available()`.
 *    A diferencia de TCP o ESP-NOW que manejan paquetes indivisibles por bloques MAC,
 *    el protocolo serial es un Stream. Se extraen agresivamente todos los bytes 
 *    existentes en cola para evitar cuellos de botella FIFO. La clase `ProtocolEngine`
 *    se encargará luego de reagrupar y sincronizar basándose en la cabecera del byte magico `0xAA`.
 */

#ifndef ARDUINO
    #include <Arduino.h>
#endif

UartStrategy::UartStrategy(HardwareSerial* serial, uint32_t baudRate, int8_t rxPin, int8_t txPin) 
    : _serial(serial), _baudRate(baudRate), _rxPin(rxPin), _txPin(txPin) {}

UartStrategy::~UartStrategy() {}

void UartStrategy::begin() {
    // If running on actual hardware (Arduino framework), initialize the Serial port
    // with the configured pins. Otherwise (Native Test), just mock the call.
    if (_serial) {
#ifdef ARDUINO
        // Arduino ESP32 implementation of begin(baud, config, rx, tx)
        // Default config is SERIAL_8N1. If pins are valid (>0), use them.
        if (_rxPin != -1 && _txPin != -1) {
            _serial->begin(_baudRate, SERIAL_8N1, _rxPin, _txPin);
        } else {
            _serial->begin(_baudRate);
        }
#else
        // Mock Implementation for Native Tests
        _serial->begin(_baudRate);
#endif
    }
}

void UartStrategy::send(const uint8_t* data, size_t length) {
    if (_serial) {
        _serial->write(data, length);
    }
}

bool UartStrategy::available() {
    if (_serial) {
        return _serial->available() > 0;
    }
    return false;
}

std::vector<uint8_t> UartStrategy::read() {
    std::vector<uint8_t> buffer;
    if (_serial) {
        // Read loop: drain hardware buffer into vector
        while (_serial->available() > 0) {
            int byte = _serial->read();
            if (byte != -1) {
                buffer.push_back(static_cast<uint8_t>(byte));
            }
        }
    }
    return buffer;
}
