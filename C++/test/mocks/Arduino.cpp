#include "Arduino.h"
#include <time.h>
#include <unistd.h>
#include <map>

HardwareSerial Serial;

static unsigned long _mockMillis = 0;
static bool _useMockTime = false;

// Time Functions
unsigned long millis() {
    if (_useMockTime) {
        return _mockMillis;
    }
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (ts.tv_sec * 1000) + (ts.tv_nsec / 1000000);
}

void delay(unsigned long ms) {
    if (_useMockTime) {
        _mockMillis += ms;
    } else {
        usleep(ms * 1000);
    }
}

// Mock Time Control Implementation
void setMockMillis(unsigned long ms) {
    _mockMillis = ms;
    _useMockTime = true;
}

void advanceMockMillis(unsigned long ms) {
    _mockMillis += ms;
    _useMockTime = true;
}

static std::map<uint8_t, uint8_t> _mockPinStates;

void pinMode(uint8_t pin, uint8_t mode) {}

void digitalWrite(uint8_t pin, uint8_t val) {
    _mockPinStates[pin] = val;
}

int digitalRead(uint8_t pin) { 
    return _mockPinStates[pin]; 
}

int mock_get_pin_state(uint8_t pin) {
    return _mockPinStates[pin];
}
