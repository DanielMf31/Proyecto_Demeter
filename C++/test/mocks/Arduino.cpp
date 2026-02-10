#include "Arduino.h"
#include <time.h>
#include <unistd.h>
#include <map>

HardwareSerial Serial;

unsigned long millis() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (ts.tv_sec * 1000) + (ts.tv_nsec / 1000000);
}

void delay(unsigned long ms) {
    usleep(ms * 1000);
}

static std::map<uint8_t, uint8_t> _mockPinStates;

void pinMode(uint8_t pin, uint8_t mode) {}

void digitalWrite(uint8_t pin, uint8_t val) {
    _mockPinStates[pin] = val;
}

int digitalRead(uint8_t pin) { 
    return _mockPinStates[pin]; 
}
