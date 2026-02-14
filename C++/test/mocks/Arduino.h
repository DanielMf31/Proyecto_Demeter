#ifndef ARDUINO_H
#define ARDUINO_H

// Force STL includes BEFORE defining macros to avoid conflicts
#include <algorithm>
#include <vector>
#include <functional>
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <cmath>
#include <cstdlib>

// Basic Types
typedef uint8_t byte;
typedef bool boolean;

// Constants
#define HIGH 0x1
#define LOW  0x0

#define INPUT 0x0
#define OUTPUT 0x1
#define INPUT_PULLUP 0x2
#define SERIAL_8N1 0x0

// Serial - Simplified Mock
class HardwareSerial {
public:
    virtual void begin(unsigned long baud, uint32_t config=SERIAL_8N1, int8_t rxPx=-1, int8_t txPin=-1) {}
    virtual void print(const char* s) {}
    virtual void println(const char* s) {}
    virtual void printf(const char* format, ...) {}
    virtual void flush() {}
    virtual int available() { return 0; }
    virtual int read() { return -1; }
    virtual size_t write(uint8_t c) { return 1; }
    virtual size_t write(const uint8_t *buffer, size_t size) { return size; }
};

extern HardwareSerial Serial;

// Time Functions
extern unsigned long millis();
extern void delay(unsigned long ms);

// Mock Time Control
void setMockMillis(unsigned long ms);
void advanceMockMillis(unsigned long ms);

// GPIO Functions
extern void pinMode(uint8_t pin, uint8_t mode);
extern void digitalWrite(uint8_t pin, uint8_t val);
extern int digitalRead(uint8_t pin);

// Math/Utils
// #define min(a,b) ((a)<(b)?(a):(b))
// #define max(a,b) ((a)>(b)?(a):(b))
#define abs(x) ((x)>0?(x):-(x))
#define constrain(amt,low,high) ((amt)<(low)?(low):((amt)>(high)?(high):(amt)))
#define round(x)     ((x)>=0?(long)((x)+0.5):(long)((x)-0.5))
#define radians(deg) ((deg)*DEG_TO_RAD)
#define degrees(rad) ((rad)*RAD_TO_DEG)
#define sq(x) ((x)*(x))

// Mock map function
inline long map(long x, long in_min, long in_max, long out_min, long out_max) {
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

#endif
