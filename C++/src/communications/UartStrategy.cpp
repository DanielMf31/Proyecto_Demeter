#include "communications/UartStrategy.h"

#ifndef ARDUINO
    // Mock Instance for Native Linker
    HardwareSerial Serial;
#endif

UartStrategy::UartStrategy(HardwareSerial* serial, uint32_t baudRate) 
    : _serial(serial), _baudRate(baudRate) {}

void UartStrategy::begin() {
    if (_serial) {
        _serial->begin(_baudRate);
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
        while (_serial->available() > 0) {
            int byte = _serial->read();
            if (byte != -1) {
                buffer.push_back(static_cast<uint8_t>(byte));
            }
        }
    }
    return buffer;
}
